import datetime
import time as t
import selenium.webdriver.support.ui as ui
import error
import influx
import user

#this function only to load portal main page
def load(driver, url, testname, errodb, datadb, expected_text, expected_type, page_id , users = 1 ):
    print("Loading url: %s " % (url))

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
            print("looking for: ", expected_text)
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
            print("looking for xpath: ", expected_text)
            driver.wait.until(lambda driver: driver.find_element_by_xpath(expected_text))
        except:
            if driver.find_elements_by_xpath("//*[contains(text(), 'Exception Type:')]"):
                message = "[%s] TEST FAILED with Django error" % (str(__name__)+'.load')
            else:
                message = "[%s] TEST FAILED with error: I was not able to locate element: %s" % (str(__name__)+'.load', expected_text)
            #error.save_error(driver, driver.page_source, testname)
            error.save_and_quit(message, url, testname, driver, errodb)

    else:
        print("Could not identify type of searched element: %s " % (expected_type))

    exec_time = datetime.datetime.now() - time
    print("Page loaded successfully")
    if (datadb):
        influx.savedata("load_time", exec_time.total_seconds(), datadb, url, testname, users)
    print ("Time to open %s: %f [s]" % (url, exec_time.total_seconds()))

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
    print("Running action: %s" % action)
    user.signin(driver, piuser['email'], piuser['password'], url, testname, errordb, datadb, concurrent_users)
    load(driver, url, testname, errordb, datadb, "//*[contains(text(), 'Your projects and slices')]", 'xpath', 'main_page' , concurrent_users)
    print("Go to users management page")
    url += '/portal/institution#users'
    search_for = "//input[@data-email='%s']" % (piuser['email'])
    load(driver, url, testname, errordb, datadb, search_for, 'xpath', 'institution_users' , concurrent_users)

    print("Searching user: %s" % (fakeuser['email']))

    # find user on the list
    try:
        driver.find_element_by_xpath("//input[@data-email='%s']" % (fakeuser['email'])).click()
        user_exist = 1
    except:
        message = "could not find user on the list: %s " % (fakeuser['email'])
        #error.save_error(driver, driver.page_source, testname)
        error.save_and_quit(message, url, testname, driver, errordb)

    # run action
    try:
        driver.find_element_by_id(button_id).click()
    except:
        message = "I was not able to find and click button: %s" % button_id
        #error.save_error(driver, driver.page_source, testname)
        error.save_and_quit(message, url, testname, driver, errordb)

    # TODO - wait for results - handle JS popup

    print("SUCCESS: Action: %s was completed successfully:" % action)
    return

def requests_action():
    return
