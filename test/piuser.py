import user
import page
import error
import time as t

## validating user (we will validate fakeuser by piuser)
def validate_user(driver, url, piuser, fakeuser, testname, errordb=None, datadb=None, users = 1):
    error.notify("Validating user", url, testname, errordb)
    page.requests_action('validate_user', driver, url, piuser, fakeuser, testname, errordb, datadb, users)
    return

def reject_user(driver, url, piuser, fakeuser, testname, errordb=None, datadb=None, users = 1):
    error.notify("Rejecting user", url, testname, errordb)
    page.requests_action('reject_user', driver, url, piuser, fakeuser, testname, errordb, datadb, users)
    return

def reject_institution(driver, url, piuser, institution, testname, errordb=None, datadb=None, users = 1):
    print("Rejecting institution")

    user.signin(driver, piuser['email'], piuser['password'], url, testname, errordb, datadb, users)

    page.load_main_page(driver, url, testname, errordb, datadb, users)

    url += '/portal/institution#requests'
    page.load(driver, url, testname, errordb,datadb, '//h2[text() = \'From your authorities\']','xpath', 'pending_requests', users)

    print("Rejecting institution: %s" % (institution['name']))

    # find institution on the list
    try:
        driver.find_element_by_xpath("//tr//td//b[text() = '%s']/../preceding-sibling::td//input[@type = 'checkbox']" % (institution['name'])).click()
        exist = 1
    except:
        message = "[%s] TEST FAILED with error: could not find institution on the list: %s " % (str(__name__)+'.reject_institution', institution['name'])
        error.save_and_quit(message, url, testname, driver, errordb)

    #... and click validate button
    try:
        driver.find_element_by_id('portal__reject').click()
    except:
        message = "I was not able to find and click 'Validate' button... something wrong"
        error.save_and_quit(message, url, testname, driver, errordb)

    counter = 5
    while (exist==1) and (counter > 0):
        t.sleep(3)
        page.load(driver, url, testname, errordb, datadb, '//h2[text() = \'From your authorities\']','xpath','pending_requests', users)
        try:
            driver.find_element_by_xpath("//tr//td//b[text() = '%s']" % (institution['name']))
            counter-=1
        except:
            exist = 0

    if (exist):
        message = "[%s] TEST FAILED with error: FAILED: institution has NOT been rejected" % (str(__name__)+'.reject_institution')
        error.save_and_quit(message, url, testname, driver, errordb)
    else:
        print("SUCCESS: institution has been rejected")

    return

def delete_user(driver, url, piuser, fakeuser, testname, errordb=None, datadb=None, concurrent_users = 1):

    print("Deleting user")
    page.users_action('delete_user', driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    return

def upgrade_user_to_pi(driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users):

    print("Upgrading user to PI")
    page.users_action('upgrade_user', driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    return

def downgrade_user_from_pi(driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users):

    print("Downgrading user")
    page.users_action('downgrade_user', driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    return
