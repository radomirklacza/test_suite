#!env python
import setup.environment
import setup.analyze
import config
import test.user
import test.page
import test.piuser
import test.institution
import test.project
from config import piuser
import test.error as error


def simpletest(fakeuser=None, piuser=None):

    # setting up email
    if (fakeuser is None):
        fakeuser = config.fakeuser

    if (piuser is None):
        piuser = config.piuser

    #setup influxdb session
    # print "Influx is needed, setting up connection"
    try:
        errordb = setup.environment.influxdb(config.influxconf['host'], config.influxconf['port'], config.influxconf['username'], config.influxconf['password'], config.influxconf['error_database'])
        datadb = setup.environment.influxdb(config.influxconf['host'], config.influxconf['port'], config.influxconf['username'], config.influxconf['password'], config.influxconf['data_database'])
    except:
        print("It was not able to set connection to influxdb, please check your config file")
        return

    #setup basic environment with browser
    error.notify("Setting up the environment (X environment and browser)")
    if(config.runevironment['virtual'] == 'YES'):
        setup.environment.display()
    driver = setup.environment.browser()


    concurrent_users = config.basic['number_of_users']
    testname = config.basic['testname']

    error.notify("Starting scenario %s" % testname, config.portal['url'], testname, errordb)

    #test.page.load(driver, config.portal['url'], testname , errordb, datadb, 'access your account?', concurrent_users)

    #test.user.signin(driver, fakeuser['email'], fakeuser['password'], config.portal['url'], testname, errordb, datadb, concurrent_users)
    #
    # main test
    # if test.user.create(driver, config.portal['url'], testname, fakeuser, fakeuser['institution'], errordb, datadb, concurrent_users) == 1:
    #      test.piuser.delete_user(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    #      test.user.create(driver, config.portal['url'], testname, fakeuser, fakeuser['institution'], errordb, datadb, concurrent_users)
    # test.user.logout(driver)
    # test.piuser.reject_user(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    # test.user.logout(driver)
    test.user.create(driver, config.portal['url'], testname, fakeuser, 'onelab.test', errordb, datadb, concurrent_users)
    test.user.logout(driver)
    test.piuser.validate_user(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    test.user.logout(driver)
    test.piuser.upgrade_user_to_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    test.user.logout(driver)
    test.user.signin(driver, fakeuser['email'], fakeuser['password'], config.portal['url'], testname, errordb, datadb, concurrent_users)
    test.user.logout(driver)
    test.user.is_pi(driver, config.portal['url'], fakeuser, testname, errordb, datadb, concurrent_users)
    test.user.logout(driver)
    test.piuser.downgrade_user_from_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    test.user.logout(driver)
    if test.user.is_pi(driver, config.portal['url'], fakeuser, testname, errordb, datadb, concurrent_users):
        print("user is PI, trying to downgrade again")
        test.piuser.downgrade_user_from_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    test.user.logout(driver)
    #
    # #test.user.reset_password(driver, config.portal['url'], fakeuser, testname, errordb, datadb, concurrent_users)
    #
    test.user.signin(driver, fakeuser['email'], fakeuser['password'], config.portal['url'], testname, errordb, datadb, concurrent_users)
    test.project.create(driver, config.portal['url'], fakeuser['project'], testname, errordb, datadb, concurrent_users)
    test.user.logout(driver)
    test.piuser.validate_project(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    test.user.logout(driver)
    test.piuser.delete_project(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    test.user.logout(driver)
    # # clean up
    #
    test.piuser.delete_user(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    test.user.logout(driver)

    #test.user.logout(driver)
    ##test.user.signin(driver, fakeuser['email'], fakeuser['password'], config.portal['url'], testname, errordb, datadb, concurrent_users)
    #test.piuser.delete_user(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    #test.user.logout(driver)
    #test.institution.create(driver, config.portal['url'], testname, config.institution, config.fakeuser, errordb, datadb, concurrent_users)
    #test.piuser.reject_institution(driver, config.portal['url'], piuser, config.institution, testname, errordb, datadb, concurrent_users)

    setup.environment.clean(driver)

if __name__ == "__main__":
    simpletest()


