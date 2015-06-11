import user
import page
import error
import time as t

## validating user (we will validate fakeuser by piuser)
def validate_user(driver, url, piuser, fakeuser, testname, errordb=None, datadb=None, users = 1, display = None):
    error.notify("Validating user %s" % fakeuser['email'], url, testname, errordb)
    page.requests_action('validate_user', driver, url, piuser, fakeuser, testname, errordb, datadb, users, display)
    return

def reject_user(driver, url, piuser, fakeuser, testname, errordb=None, datadb=None, users = 1, display = None):
    error.notify("Rejecting user %s" % fakeuser['email'], url, testname, errordb)
    page.requests_action('reject_user', driver, url, piuser, fakeuser, testname, errordb, datadb, users, display)
    return

def validate_project(driver, url, piuser, fakeuser, testname, errordb=None, datadb=None, users = 1, display = None):
    error.notify("Validating project", url, testname, errordb)
    return page.requests_action('validate_project', driver, url, piuser, fakeuser, testname, errordb, datadb, users, display)

def delete_project(driver, url, piuser, fakeuser, testname, errordb=None, datadb=None, users = 1, display = None):
    error.notify("Deleting project", url, testname, errordb)
    return page.projects_action('delete_project', driver, url, piuser, fakeuser, testname, errordb, datadb, users, display)


def reject_project(driver, url, piuser, fakeuser, testname, errordb=None, datadb=None, users = 1, display = None):
    error.notify("Rejecting project", url, testname, errordb)
    return page.requests_action('reject_project', driver, url, piuser, fakeuser, testname, errordb, datadb, users, display)

def delete_user(driver, url, piuser, fakeuser, testname, errordb=None, datadb=None, concurrent_users = 1, display = None):

    print("Deleting user")
    return page.users_action('delete_user', driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users, display)

def upgrade_user_to_pi(driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users, display = None):

    print("Upgrading user to PI")
    return page.users_action('upgrade_user', driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users, display)

def downgrade_user_from_pi(driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users, display = None):

    print("Downgrading user")
    return page.users_action('downgrade_user', driver, url, piuser, fakeuser, testname, errordb, datadb, concurrent_users, display)

def reject_institution(driver, url, piuser, institution, testname, errordb=None, datadb=None, users = 1, display = None):
    print("Rejecting institution")

    user.signin(driver, piuser['email'], piuser['password'], url, testname, errordb, datadb, users, display)

    page.load_main_page(driver, url, testname, errordb, datadb, users, display)

    url += '/portal/institution#requests'
    page.load(driver, url, testname, errordb,datadb, '//h2[text() = \'From your authorities\']','xpath', 'pending_requests', users, display)

    print("Rejecting institution: %s" % (institution['name']))

    # find institution on the list
    try:
        driver.find_element_by_xpath("//tr//td//b[text() = '%s']/../preceding-sibling::td//input[@type = 'checkbox']" % (institution['name'])).click()
        exist = 1
    except:
        message = "[%s] TEST FAILED with error: could not find institution on the list: %s " % (str(__name__)+'.reject_institution', institution['name'])
        error.save_and_quit(message, url, testname, driver, errordb, display)

    #... and click validate button
    try:
        driver.find_element_by_id('portal__reject').click()
    except:
        message = "I was not able to find and click 'Validate' button... something wrong"
        error.save_and_quit(message, url, testname, driver, errordb, display)

    counter = 5
    while (exist==1) and (counter > 0):
        t.sleep(3)
        page.load(driver, url, testname, errordb, datadb, '//h2[text() = \'From your authorities\']','xpath','pending_requests', users, display)
        try:
            driver.find_element_by_xpath("//tr//td//b[text() = '%s']" % (institution['name']))
            counter-=1
        except:
            exist = 0

    if (exist):
        message = "[%s] TEST FAILED with error: FAILED: institution has NOT been rejected" % (str(__name__)+'.reject_institution')
        error.save_and_quit(message, url, testname, driver, errordb, display)
    else:
        print("SUCCESS: institution has been rejected")

    return
