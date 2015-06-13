import datetime
import selenium.webdriver.support.ui as ui
import error
import influx
import user
import re

#this function only to load portal main page
def load(driver, url, testname, errordb, datadb, expected_text, expected_type , info_tag, users, display = None):
    error.notify("Loading url: %s " % (url), url, testname, errordb)

    # wait at maximum 10 seconds, then raise an exception
    driver.wait = ui.WebDriverWait(driver, 40)
    time = datetime.datetime.now()
    try:
        print(url)
        driver.get('https://portal.fed4fire.eu')
        error.notify('current url:', driver.current_url, testname, errordb)
        driver.get(url)
    except:
        try:
            error.notify("got an exception, curent url: %s, desired url: %s" % (str(driver.current_url), url), url, testname, errordb)
            driver.get(url)
        except:
            message = "[%s] TEST FAILED with error: I was not able to load page: %s" % (str(__name__)+'.load', url)
            error.save_error(message, url, testname, driver, errordb)
            return (False, message)


    # waiting link to appear
    if expected_type == 'link_text':
        try:
            error.notify("looking for: %s " % expected_text, url, testname, errordb)
            driver.wait.until(lambda driver: driver.find_element_by_link_text(expected_text))
        except:
            if driver.find_elements_by_xpath("//*[contains(text(), 'Exception Type:')]"):
                message = "[%s] TEST FAILED with Django error" % (str(__name__)+'.load')
                filename = error.save_error(message, url, testname, driver, errordb)
                return (False, message, filename)
            else:
                try:
                    error.notify("got an exception, curent url: %s, desired url: %s" % (str(driver.current_url), url),url, testname, errordb)
                    driver.get(url)
                except:
                    message = "[%s] TEST FAILED with error: link find timeout - I was not able to properly load page: %s (locate element: %s)" % (str(__name__)+'.load', url, expected_text)
                    filename = error.save_error(message, url, testname, driver, errordb)
                    return (False, message, filename)
    elif expected_type == 'xpath':
        try:
            #print("looking for xpath: ", expected_text)
            driver.wait.until(lambda driver: driver.find_element_by_xpath(expected_text))
        except:
            if driver.find_elements_by_xpath("//*[contains(text(), 'Exception Type:')]"):
                message = "[%s] TEST FAILED with Django error" % (str(__name__)+'.load')
                filename = error.save_error(message, url, testname, driver, errordb)
                return (False, message, filename)
            else:
                try:
                    error.notify("got an exception, curent url: %s, desired url: %s" % (str(driver.current_url), url), url, testname, errordb)
                    driver.get(url)
                except:
                    message = "[%s] TEST FAILED with error: xpath find timeout - I was not able to properly load page: %s (locate element: %s)" % (str(__name__)+'.load', url, expected_text)
                    filename = error.save_error(message, url, testname, driver, errordb)
                    return (False, message, filename)

    else:
        error.notify("Could not identify type of searched element: %s " % (expected_type), url, testname, errordb)

    error.notify("Page loaded successfully", url, testname, errordb)

    # save time measuremnts
    exec_time = datetime.datetime.now() - time

    if (datadb):
        influx.savedata("load_time_"+info_tag, exec_time.total_seconds(), datadb, url, testname, users)
    error.notify("Time to load page: %s : %f [s]" % (url, exec_time.total_seconds()), url, testname, errordb)

    return (True, 'Page %s was loaded successfully' % url)

def users_action(action, driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users, display = None):

    # define ID of button objects on the website
    if action == 'delete_user':
        button_id = 'deleteusers'
    elif action == 'upgrade_user':
        button_id = 'makepi'
    elif action == 'downgrade_user':
        button_id = 'removepi'
    else:
        button_id = None
        filename = error.save_error('action unknown in module test.users_action', url, testname, driver, errordb)
        return (False, 'action unknown in module test.users_action', filename)

    # sign-in as PI
    error.notify("Running action: %s" % action, url, testname, errordb)
    status = user.signin(driver, piuser['email'], piuser['password'], url, testname, errordb, datadb, concurrent_users, display)
    if not status[0]:
        filename = error.save_error(status[1], url, testname, driver, errordb)
        return (False, status[1], filename)

    load_main_page(driver, url, testname, errordb, datadb, concurrent_users, display)

    error.notify("Go to users management page", url, testname, errordb)
    url += '/portal/institution#users'
    search_for = "//input[@data-email='%s']" % (piuser['email'])

    status = load(driver, url, testname, errordb, datadb, search_for, 'xpath', 'institution_users', concurrent_users, display)
    if not status[0]:
        filename = error.save_error(status[1], url, testname, driver, errordb)
        return (False, status[1], filename)


    error.notify("Searching user: %s" % (fakeuser['email']), url, testname, errordb)

    # find user on the list
    try:
        driver.find_element_by_xpath("//input[@data-email='%s']" % (fakeuser['email'])).click()
        user_exist = 1
    except:
        message = "[%s] TEST FAILED with error: I could not find user on the list: %s " % (str(__name__)+'.'+str(action), fakeuser['email'])
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    # run action
    try:
        time = datetime.datetime.now()
        driver.find_element_by_id(button_id).click()
    except:
        message = "[%s] TEST FAILED with error: I was not able to find and click button: %s" % (str(__name__)+'.'+str(action), button_id)
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    # Wait for results and handle JS popup message with result message
    try:
        driver.wait = ui.WebDriverWait(driver, 50)
        js_message = driver.wait.until(lambda driver: driver.find_element_by_xpath("//span[@class='message']").text)
        # save time measuremnts
        exec_time = datetime.datetime.now() - time
        if (datadb):
            influx.savedata("processing_time", exec_time.total_seconds(), datadb, url, testname, concurrent_users)
    except:
        message = "[%s] TEST FAILED with error: 20s was not enough to process request %s for user: %s " % (str(__name__)+'.'+str(action), str(action), fakeuser['email'])
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    if 'No action: User had no rights on:' in js_message:
        error.notify('User was NOT PI, portal message: %s' % js_message)
    elif 'Success:' in js_message:
        error.notify("SUCCESS: Action: %s was completed successfully with portal message: '%s'" % (action, js_message), url, testname, errordb)
    else:
        message = "[%s] TEST FAILED for action %s with portal error message: '%s'" % (str(__name__)+'.'+str(action), str(action), js_message)
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    message = "[%s] TEST OK for action %s " % (str(__name__)+'.'+str(action), str(action))
    return (True, message)


def projects_action(action, driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users, display = None):

    # define ID of button objects on the website
    if action == 'delete_project':
        button_id = 'deleteprojects'
    else:
        filename = error.save_error("Unknown action: %s" % action, url, testname, driver, errordb)
        return (False, "Unknown action: %s" % action, filename)

    # sign-in as PI
    error.notify("Running action: %s" % action, url, testname, errordb)

    status = user.signin(driver, piuser['email'], piuser['password'], url, testname, errordb, datadb, concurrent_users, display)
    if not status[0]:
        filename = error.save_error(status[1], url, testname, driver, errordb)
        return (False, status[1], filename)

    status = load_main_page(driver, url, testname, errordb, datadb, concurrent_users, display)
    if not status[0]:
        filename = error.save_error(status[1], url, testname, driver, errordb)
        return (False, status[1], filename)

    error.notify("Go to project management page", url, testname, errordb)
    url += '/portal/institution#projects'

    search_for = "//input[@class='project']"
    status = load(driver, url, testname, errordb, datadb, search_for, 'xpath', 'institution_projects', concurrent_users, display)
    if not status[0]:
        filename = error.save_error(status[1], url, testname, driver, errordb)
        return (False, status[1], filename)

    error.notify("Searching project: %s" % (fakeuser['project']['name']), url, testname, errordb)

    # find user on the list
    try:
        input_box = driver.wait.until(lambda driver: driver.find_element_by_xpath("//tr//td[contains(text(), '%s')]/preceding-sibling::td//input[@type = 'checkbox']" % (fakeuser['project']['name'])))
        input_box.click()
    except:
        message = "[%s] TEST FAILED with error: I could not find project on the list: %s " % (str(__name__)+'.'+str(action), fakeuser['project']['name'])
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    # run action
    try:
        time = datetime.datetime.now()
        driver.find_element_by_id(button_id).click()
    except:
        message = "[%s] TEST FAILED with error: I was not able to find and click button: %s" % (str(__name__)+'.'+str(action), button_id)
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    # Wait for results and handle JS popup message with result message
    try:
        driver.wait = ui.WebDriverWait(driver, 50)
        js_message = driver.wait.until(lambda driver: driver.find_element_by_xpath("//span[@class='message']").text)
        # save time measuremnts
        exec_time = datetime.datetime.now() - time
        if (datadb):
            influx.savedata("processing_time", exec_time.total_seconds(), datadb, url, testname, concurrent_users)
    except:
        message = "[%s] TEST FAILED with error: 50s was not enough to process request %s for project: %s " % (str(__name__)+'.'+str(action), str(action), fakeuser['project']['name'])
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    if 'No action: User had no rights on:' in js_message:
        error.notify('User was NOT PI, portal message: %s' % js_message)
    elif 'Success:' in js_message:
        error.notify("SUCCESS: Action: %s was completed successfully with portal message: '%s'" % (action, js_message), url, testname, errordb)
    else:
        message = "[%s] TEST FAILED for action %s with portal error message: '%s'" % (str(__name__)+'.'+str(action), str(action), js_message)
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    return (True, '[%s] TEST OK' % str(__name__)+'.'+str(action))


def requests_action(action, driver, url, piuser, fakeuser, testname, errordb, datadb, users, display = None):

    status = user.signin(driver, piuser['email'], piuser['password'], url, testname, errordb, datadb, users, display)
    if not status[0]:
        filename = error.save_error(status[1], url, testname, driver, errordb)
        return (False, status[1], filename)

    status = load_main_page(driver, url, testname, errordb, datadb, users, display)
    if not status[0]:
        filename = error.save_error(status[1], url, testname, driver, errordb)
        return (False, status[1], filename)

    error.notify("Go to request page", url, testname, errordb)

    url +='/portal/institution#requests'
    error.notify("This is url: %s" % url, url, testname, errordb)

    status = load(driver, url, testname, errordb,datadb, '//h2[text() = \'From your authorities\']','xpath', 'pending_requests', users, display)
    if not status[0]:
        filename = error.save_error(status[1], url, testname, driver, errordb)
        return (False, status[1], filename)

    # set up the id of the button for the action (Reject or Validate)
    if 'validate' in action:
        button_id = 'portal__validate'
    elif 'reject' in action:
        button_id = 'portal__reject'
    else:
        message = "[%s] TEST FAILED with error: Unknown action" % (str(__name__)+'.'+action)
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    error.notify("%s: %s" % (action, fakeuser['email']))

    # find user on the list
    if 'user' in action:
        look_for = fakeuser['email']
    elif 'project' in action:
        look_for = fakeuser['project']['name']

    try:
        driver.wait = ui.WebDriverWait(driver, 50)
        driver.find_element_by_xpath("//tr//td//*[starts-with(text(), '%s')]/../preceding-sibling::td//input[@type = 'checkbox']" % (look_for)).click()
        # driver.find_element_by_xpath("//tr//td//a[text() = '%s']/../preceding-sibling::td//input[@type = 'checkbox']" % (look_for)).click()
    except:
        message = "[%s] TEST FAILED with error: could not find item on the list: %s " % (str(__name__)+'.'+action, look_for)
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    #... and click validate/reject button
    try:
        driver.find_element_by_id(button_id).click()
        time = datetime.datetime.now()
    except:
        message = "[%s] TEST FAILED with error: I was not able to find and click '%s' button... something wrong, sorry" % (str(__name__)+'.'+action, action)
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    # response message handling
    try:
        driver.wait = ui.WebDriverWait(driver, 50)
        js_status = driver.wait.until(lambda driver: driver.find_element_by_xpath("//tr//td//*[starts-with(text(), '%s')]/../following-sibling::td//span//font" % (look_for)))
        # save time measuremnts
        exec_time = datetime.datetime.now() - time
        if (datadb):
            influx.savedata("processing_time", exec_time.total_seconds(), datadb, url, testname, users)
    except:
        message = "[%s] TEST FAILED with error: I was not able to get any message for 20 seconds" % (str(__name__)+'.'+action)
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)

    if re.compile("^OK$").match(js_status.text.strip()):
        message = "[%s] SUCESS to %s for user: %s" % (str(__name__)+'.'+action, action, fakeuser['email'])
        error.notify(message, url, testname, errordb)
    elif re.compile("^Rejected").match(js_status.text.strip()):
        message = "[%s] SUCESS to %s for user: %s" % (str(__name__)+'.'+action, action, fakeuser['email'])
        error.notify(message, url, testname, errordb)
    else:
        message = "[%s] TEST FAILED with error: for user %s I got an error message from portal: %s" % (str(__name__)+'.'+action, fakeuser['email'], js_status.text)
        filename = error.save_error(message, url, testname, driver, errordb)
        return (False, message, filename)
    return (True, '[%s] TEST OK' % str(__name__)+'.'+action)

def load_main_page(driver, url, testname, errordb, datadb, concurrent_users, display):
    url += '/'
    return load(driver, url, testname, errordb, datadb, "//*[contains(text(), 'Your projects and slices')]", 'xpath','main_page', concurrent_users, display)

