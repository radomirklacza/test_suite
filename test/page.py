import datetime
import selenium.webdriver.support.ui as ui
import error
import influx
import user

#this function only to load portal main page
def load(driver, url, testname, errodb, datadb, expected_text, expected_type, page_id , users = 1 ):
    error.notify("Loading url: %s " % (url), url, testname, errodb)

    # wait at maximum 10 seconds, then raise an exception
    driver.wait = ui.WebDriverWait(driver, 20)
    time = datetime.datetime.now()
    try:
        driver.get(url)
    except:
        message = "[%s] TEST FAILED with error: I was not able to load page: %s" % (str(__name__)+'.load', url)
        #error.save_error(driver, driver.page_source, testname)
        error.save_and_quit(message, url, testname, driver, errodb)

    # waiting link to appear
    if expected_type == 'link_text':
        try:
            #print("looking for: ", expected_text)
            driver.wait.until(lambda driver: driver.find_element_by_link_text(expected_text))
        except:
            if driver.find_elements_by_xpath("//*[contains(text(), 'Exception Type:')]"):
                message = "[%s] TEST FAILED with Django error" % (str(__name__)+'.load')
            else:
                message = "[%s] TEST FAILED with error: I was not able to locate element: %s" % (str(__name__)+'.load', expected_text)
            #error.save_error(driver, driver.page_source, testname)
            error.save_and_quit(message, url, testname, driver, errodb)

    elif expected_type == 'xpath':
        try:
            #print("looking for xpath: ", expected_text)
            driver.wait.until(lambda driver: driver.find_element_by_xpath(expected_text))
        except:
            if driver.find_elements_by_xpath("//*[contains(text(), 'Exception Type:')]"):
                message = "[%s] TEST FAILED with Django error" % (str(__name__)+'.load')
            else:
                message = "[%s] TEST FAILED with error: I was not able to locate element: %s" % (str(__name__)+'.load', expected_text)
            #error.save_error(driver, driver.page_source, testname)
            error.save_and_quit(message, url, testname, driver, errodb)

    else:
        error.notify("Could not identify type of searched element: %s " % (expected_type), url, testname, errodb)

    error.notify("Page loaded successfully", url, testname, errodb)

    # save time measuremnts
    exec_time = datetime.datetime.now() - time
    if (datadb):
        influx.savedata("load_time", exec_time.total_seconds(), datadb, url, testname, users)
    error.notify("Time to open %s: %f [s]" % (url, exec_time.total_seconds()), url, testname, errodb)

    return

def users_action(action, driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users):

    # define ID of button objects on the website
    if action == 'delete_user':
        button_id = 'deleteusers'
    elif action == 'upgrade_user':
        button_id = 'makepi'
    elif action == 'downgrade_user':
        button_id = 'removepi'
    else:
        button_id = None
        message = "This action: %s is not supported" % action
        error.save_and_quit(message, url, testname, driver, errordb)

    # sign-in as PI
    error.notify("Running action: %s" % action, url, testname, errordb)
    user.signin(driver, piuser['email'], piuser['password'], url, testname, errordb, datadb, concurrent_users)

    load_main_page(driver, url, testname, errordb, datadb, concurrent_users)

    error.notify("Go to users management page", url, testname, errordb)
    url += '/portal/institution#users'
    search_for = "//input[@data-email='%s']" % (piuser['email'])
    load(driver, url, testname, errordb, datadb, search_for, 'xpath', 'institution_users' , concurrent_users)

    error.notify("Searching user: %s" % (fakeuser['email']), url, testname, errordb)

    # find user on the list
    try:
        driver.find_element_by_xpath("//input[@data-email='%s']" % (fakeuser['email'])).click()
        user_exist = 1
    except:
        message = "[%s] TEST FAILED with error: I could not find user on the list: %s " % (str(__name__)+'.'+str(action), fakeuser['email'])
        error.save_and_quit(message, url, testname, driver, errordb)

    # run action
    try:
        time = datetime.datetime.now()
        driver.find_element_by_id(button_id).click()
    except:
        message = "[%s] TEST FAILED with error: I was not able to find and click button: %s" % (str(__name__)+'.'+str(action), button_id)
        error.save_and_quit(message, url, testname, driver, errordb)

    # Wait for results and handle JS popup message with result message
    try:
        driver.wait = ui.WebDriverWait(driver, 20)
        js_message = driver.wait.until(lambda driver: driver.find_element_by_xpath("//span[@class='message']"))
        # save time measuremnts
        exec_time = datetime.datetime.now() - time
        if (datadb):
            influx.savedata("processing_time", exec_time.total_seconds(), datadb, url, testname, concurrent_users)
    except:
        message = "[%s] TEST FAILED with error: 20s was not enough to process request %s for user: %s " % (str(__name__)+'.'+str(action), str(action), fakeuser['email'])
        error.save_and_quit(message, url, testname, driver, errordb)

    if 'No action: User had no rights on:' in js_message.text:
        error.notify('User was NOT PI, portal message: %s' % js_message.text)
    elif 'Success:' in js_message.text:
        error.notify("SUCCESS: Action: %s was completed successfully with portal message: '%s'" % (action, js_message.text), url, testname, errordb)
    else:
        message = "[%s] TEST FAILED for action %s with portal error message: '%s'" % (str(__name__)+'.'+str(action), str(action), js_message.text)
        error.save_and_quit(message, url, testname, driver, errordb)
    return

def requests_action(action, driver, url, piuser, fakeuser, testname, errordb, datadb, users):

    user.signin(driver, piuser['email'], piuser['password'], url, testname, errordb, datadb, users)
    load_main_page(driver, url, testname, errordb, datadb, users)

    error.notify("Go to request page", url, testname, errordb)

    url = url+'/portal/institution#requests'
    load(driver, url, testname, errordb,datadb, '//h2[text() = \'From your authorities\']','xpath', 'pending_requests', users)

    # set up the id of the button for the action (Reject or Validate)
    if 'validate' in action:
        button_id = 'portal__validate'
    elif 'reject' in action:
        button_id = 'portal__reject'
    else:
        message = "[%s] TEST FAILED with error: Unknown action" % (str(__name__)+'.'+action)
        error.save_and_quit(message, url, testname, driver, errordb)

    error.notify("%s: %s" % (action, fakeuser['email']))

    # find user on the list
    if 'user' in action:
        look_for = fakeuser['email']
    elif 'project' in action:
        look_for = fakeuser['project']['name']

    try:
        driver.wait = ui.WebDriverWait(driver, 20)
        driver.find_element_by_xpath("//tr//td//*[starts-with(text(), '%s')]/../preceding-sibling::td//input[@type = 'checkbox']" % (look_for)).click()
        # driver.find_element_by_xpath("//tr//td//a[text() = '%s']/../preceding-sibling::td//input[@type = 'checkbox']" % (look_for)).click()
    except:
        message = "[%s] TEST FAILED with error: could not find item on the list: %s " % (str(__name__)+'.'+action, look_for)
        error.save_and_quit(message, url, testname, driver, errordb)

    #... and click validate/reject button
    try:
        driver.find_element_by_id(button_id).click()
        time = datetime.datetime.now()
    except:
        message = "[%s] TEST FAILED with error: I was not able to find and click '%s' button... something wrong, sorry" % (str(__name__)+'.'+action, action)
        error.save_and_quit(message, url, testname, driver, errordb)

    # response message handling
    try:
        driver.wait = ui.WebDriverWait(driver, 20)
        js_status = driver.wait.until(lambda driver: driver.find_element_by_xpath("//tr//td//a[text() = '%s']/../following-sibling::td//span//font" % (fakeuser['email'])))
        # save time measuremnts
        exec_time = datetime.datetime.now() - time
        if (datadb):
            influx.savedata("processing_time", exec_time.total_seconds(), datadb, url, testname, users)
    except:
        message = "[%s] TEST FAILED with error: I was not able to get any message for 20 seconds" % (str(__name__)+'.'+action)
        error.save_and_quit(message, url, testname, driver, errordb)

    if 'OK' or 'Rejected' in js_status.text:
        message = "[%s] SUCESS to %s for user: %s" % (str(__name__)+'.'+action, action, fakeuser['email'])
        error.notify(message, url, testname, errordb)
    else:
        message = "[%s] TEST FAILED with error: I got an error message from portal: %s" % (str(__name__)+'.'+action, js_status.text)
        error.save_and_quit(message, url, testname, driver, errordb)

    return

def load_main_page(driver, url, testname, errordb, datadb, concurrent_users):
    load(driver, url, testname, errordb, datadb, "//*[contains(text(), 'Your projects and slices')]", 'xpath', 'main_page' , concurrent_users)
    return
