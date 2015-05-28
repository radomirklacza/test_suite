import selenium.webdriver.support.ui as ui
from datetime import datetime
import time as t
import page
import influx
import error
import gemail



def signin(driver, user,  paswd, url, testname, errodb=None, datadb=None, users=1):

    # first load main page
    page.load(driver, url, testname, errodb, datadb, 'Can\'t access your account?', 'link_text','signin_page', users)

    # fill up login form
    error.notify("Singining in user", url, testname, errodb)
    email = driver.find_element_by_name("username")
    email.send_keys(user)
    password = driver.find_element_by_name("password")
    password.send_keys(paswd)

    # ... and submit the form
    time_now = datetime.now()
    password.submit()

    # wait for resluts
    try:
        # waiting 20 seconds until user login and get information about his slice list
        driver.wait = ui.WebDriverWait(driver, 50)
        driver.wait.until(lambda driver: driver.find_elements_by_xpath("//*[contains(text(), 'Your projects and slices')]"))
        exec_time =  datetime.now() - time_now
    except:
        driver.wait = ui.WebDriverWait(driver, 10)
        # check if login/password are correct
        if driver.wait.until(lambda driver: driver.find_element_by_xpath("//span[text() = 'Your username and/or password were incorrect.']")):
            message = "[%s] TEST FAILED with error: I was NOT able to signn-in: %s (User or/and password incorrect)" % (str(__name__)+'.signin', url)
        else:
            message = "[%s] TEST FAILED with error: I was NOT able to signn-in: %s (I was not able to see home-slice-list)" % (str(__name__)+'.signin', url)
        error.save_and_quit(message, url, testname, driver, errodb)

    # save data into influx portal
    if datadb:
        influx.savedata("signin", exec_time.total_seconds(), datadb, url, testname, users)
    error.notify("Time to signin to portal %f [s]" % (exec_time.total_seconds()), url, testname, errodb)


def create(driver, url, testname, fakeuser, organisation, errordb=None, datadb=None, users=1):

    error.notify("Running module: create user", url, testname, errordb)

    # load page
    url = url+'/register'
    page.load(driver, url, testname, errordb, datadb, 'terms and conditions.', 'link_text','create_user', users)

    # delete all old emails for this alias
    gemail.delete_all_emails(fakeuser['trueemail'], fakeuser['password'], fakeuser['email'])

    # fil ou the registration form
    error.notify("Filling up user form on registration page", url, testname, errordb)
    try:
        firstname = driver.find_element_by_name("firstname")
        firstname.send_keys(fakeuser['firstname'])
        lastname = driver.find_element_by_name("lastname")
        lastname.send_keys(fakeuser['lastname'])
        email = driver.find_element_by_name("email")
        email.send_keys(fakeuser['email'])
        agreement = driver.find_element_by_name("agreement")
        agreement.click()
        password = driver.find_element_by_name("password")
        password.send_keys(fakeuser['password'])
        password = driver.find_element_by_name("confirmpassword")
        password.send_keys(fakeuser['password'])
        org = driver.find_element_by_class_name("ui-corner-right")
        org.click()
        organisation = "//li[text() = '"+organisation+"']"
        org = driver.find_element_by_xpath(organisation).click()
        time_now = datetime.now()
        password.submit()
        #error.notify("Submit user form on registration page", url, testname, errordb)
    except Exception, e:

        message = "[%s] TEST FAILED with error: I was not able to properly fill the form on: %s" % (str(__name__)+'.create', url)
        error.save_and_quit(message, url, testname, driver, errordb)

    try:
        driver.wait.until(lambda driver: driver.find_elements_by_xpath("//*[contains(text(), 'Email already registered.')] | //*[contains(text(), 'Exception Type:')] | //*[contains(text(), 'Sign up information received')]"))
    except:
        message = "[%s] TEST FAILED with unknown error: I've not get proper after create-account screen %s" % (str(__name__)+'.create', url)
        error.save_and_quit(message, url, testname, driver, errordb)

    if driver.find_elements_by_xpath("//*[contains(text(), 'Sign up information received')]"):
        error.notify("Registration completed successfully", url, testname, errordb)
    elif driver.find_elements_by_xpath("//*[contains(text(), 'Email already registered.')]"):
        message = "[%s] TEST FAILED with error: Email address already registered %s" % (str(__name__)+'.create', fakeuser['email'])
        return 1
        #error.save_and_quit(message, url, testname, driver, errordb)
    elif driver.find_elements_by_xpath("//*[contains(text(), 'Exception Type:')]") > 0:
        message = "[%s] TEST FAILED with Django error" % (str(__name__)+'.create')
        #error.save_error(driver, driver.page_source, testname)
        error.save_and_quit(message, url, testname, driver, errordb)

    exec_time = datetime.now() - time_now

    if (datadb):
        influx.savedata("create_user_form_submit", exec_time.total_seconds(), datadb, url, testname, users)
    error.notify("Processing the user account request: %s " % (str(exec_time.total_seconds())), url, testname, errordb)

    # TODO - clean up the code needed - for now it is copy paste
    # confirm account with gmail
    try:
        a = 0
        while a < 5: # I try to fetch email 5 times (25s in total):
            try:
                link = gemail.fetch_activation_link(fakeuser['trueemail'], fakeuser['password'], fakeuser['email'])
                if link:
                    error.notify("validation link: %s " % link, url, testname, errordb)
                    break
                else:
                    print("waiting...")
                    a = a+1
                    t.sleep(5)
            except:
                a = a+1
                t.sleep(5)
    except:
        message = "[%s] TEST FAILED with error: I was not able to read email link." % (str(__name__)+'.create')
        error.save_and_quit(message,url, testname, driver, errordb)

    # TODO replace with load() - what text is expected?
    try:
        error.notify("Validating user with link: %s" % link, url, testname, errordb)
        # TODO it is not checking for proper user validation
        page.load(driver, link, testname, errordb, datadb, "//h3[text()='Signup request confirmed.']", 'xpath', 'user_validation_link', users)
        driver.get('https://portal.onelab.eu/')
    except:
        message = "[%s] TEST FAILED with error: I was not able to confirm email link" % (str(__name__)+'.create')
        #error.save_error(driver, driver.page_source, testname)
        error.save_and_quit(message, url, testname, driver, errordb)
    error.notify("User successfully validated with link: %s" % link, url, testname, errordb)
    error.notify("User has been created", url, testname, errordb)

def logout(driver):
    error.notify("logging off")

    try:
        driver.find_element_by_id('logout').click()
        driver.switch_to_alert().accept()
        driver.switch_to.window
    except:
        error.notify("I was not able to logout (could not find the button?)")
    return

def is_pi(driver, url, fakeuser, testname, errordb, datadb, concurrent_users):
    error.notify("Checking if user is PI", url, testname, errordb)

    signin(driver, fakeuser['email'], fakeuser['password'], url, testname, errordb, datadb, concurrent_users)
    url += '/portal/user/'+fakeuser['email']

    #page.load(driver, url, testname, errordb, datadb, "//*[contains(text(), 'User Account')]", 'xpath', concurrent_users)
    page.load(driver, url, testname, errordb, datadb, 'User Account', 'link_text', 'user_account_details', concurrent_users)
    try:
        element = driver.find_element_by_link_text('User Account')
        error.notify("Found 'User Account'", url, testname, errordb)
        element.click()
    except:
        message = "[%s] TEST FAILED: could not find 'User Account' link for: %s" % (str(__name__)+'.is_pi', fakeuser['email'])
        error.save_and_quit(message, url, testname, driver, errordb)

    try:
        #driver.find_element_by_xpath("//button[contains(@name,'dl_onelab.')]")
        driver.find_element_by_xpath("//button[contains(@oldtitle,'Download Authority Credentials')]")
        error.notify('User is PI', url, testname, errordb)
        return True
    except:
        error.notify("User is not PI", url, testname, errordb)
        return False

def reset_password(driver, url, fakeuser, testname, errordb, datadb, concurrent_users):
    error.notify("Reseting users password", url, testname, errordb)

    url += '/portal/pass_reset/'
    page.load(driver, url, testname, errordb, datadb, "//h3[text()='Welcome to the secured password reset wizard']", 'xpath', 'password_reset', concurrent_users)

    try:
        email = driver.find_element_by_name("email")
        email.send_keys(fakeuser['email'])
        element = driver.find_element_by_xpath("//input[contains(@value,'Reset my password')]")
        element.click()
    except:
        message = "[%s] TEST FAILED: could not find proper from to input email address, url: %s" % (str(__name__)+'.reset_password', url)
        error.save_and_quit(message, url, testname, driver, errordb)

    driver.wait = ui.WebDriverWait(driver, 50)
    try:
        driver.wait.until(lambda driver: driver.find_element_by_xpath("//h3[text()='Welcome to the secured password reset wizard']"))
        message = None
    except:
        message = "[%s] TEST FAILED: processing email reset request failed for user: %s" % (str(__name__)+'.reset_password', fakeuser['email'])

    try:
        driver.wait.until(lambda driver: driver.find_element_by_xpath("//li[text()=\"That email address doesn't have an associated user account. Are you sure you've registered?\"]"))
        message = "[%s] TEST FAILED: email has been reported as not existing in database: %s" % (str(__name__)+'.reset_password', fakeuser['email'])
    except:
        message = None

    if message:
        error.save_and_quit(message, url, testname, driver, errordb)

    # TODO #1 - clean up the code needed - for now it is copy paste
    # confirm account with gmail
    try:
        a = 0
        while a < 5: # I try to fetch email 5 times (25s in total):
            try:
                link = gemail.fetch_reset_link(fakeuser['trueemail'], fakeuser['password'], fakeuser['email'])
                if link:
                    error.notify("validation link: %s " % link, url, testname, errordb)
                    break
                else:
                    error.notify("waiting...", url, testname, errordb)
                    a = a+1
                    t.sleep(5)
            except:
                a = a+1
                t.sleep(5)
    except:
        message = "[%s] TEST FAILED with error: I was not able to read email link." % (str(__name__)+'.reset_password')
        error.save_and_quit(message,url, testname, driver, errordb)

    # TODO replace with load() - what text is expected?
    try:
        driver.get(link)
    except:
        message = "[%s] TEST FAILED with error: I was not able to confirm email link" % (str(__name__)+'.reset_password')
        error.save_and_quit(message, url, testname, driver, errordb)

    error.notify("[%s] OK - Reseting password for user: %s" % (str(__name__)+'.reset_password', fakeuser['email']), url, testname, errordb)
    return


