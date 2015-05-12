#!env python
import setup.environment
import setup.analyze
import config
import test.user
import test.page
import test.piuser
import test.institution
import test.project
from config import fakeuser, piuser


def simpletest(fakeemail=None, configuration=None):
    print("Starting tests")

    testtorun = config.mytest

    #setting up email
    if (fakeemail is not None):
        fakeuser['email'] = fakeemail

    #setup influxdb session

    print "Influx is needed, setting up connection"

    try:
        errordb = setup.environment.influxdb(config.influxconf['host'], config.influxconf['port'], config.influxconf['username'], config.influxconf['password'], config.influxconf['error_database'])
        datadb = setup.environment.influxdb(config.influxconf['host'], config.influxconf['port'], config.influxconf['username'], config.influxconf['password'], config.influxconf['data_database'])
    except:
        print("It was not able to set connection to influxdb, please check your config file")
        return

    #setup basic environment with browser
    print("Setting up the environment (X environment and browser)")
    if(config.runevironment['virtual'] == 'YES'):
        setup.environment.display()
    driver = setup.environment.browser()
    concurrent_users = 1
    testname = "mytest10_rad"

    print("Starting scenario")
    #test.page.load(driver, config.portal['url'], testname , errordb, datadb, 'access your account?', concurrent_users)

    #test.user.signin(driver, fakeuser['email'], fakeuser['password'], config.portal['url'], testname, errordb, datadb, concurrent_users)
    #
    #test.user.create(driver, config.portal['url'], testname, fakeuser, 'Universite Pierre et Marie Curie', errordb, datadb, concurrent_users)
    #test.user.logout(driver)
    #test.piuser.validate_user(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    #test.user.logout(driver)
    #test.piuser.upgrade_user_to_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    #test.user.logout(driver)
    #test.user.signin(driver, fakeuser['email'], fakeuser['password'], config.portal['url'], testname, errordb, datadb, concurrent_users)
    #test.user.logout(driver)
    #test.user.is_pi(driver, config.portal['url'], fakeuser, testname, errordb, datadb, concurrent_users)
    #test.user.logout(driver)
    #test.piuser.downgrade_user_from_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    #test.user.logout(driver)
    #test.user.is_pi(driver, config.portal['url'], fakeuser, testname, errordb, datadb, concurrent_users)
    #test.user.logout(driver)
    #test.user.signin(driver, fakeuser['email'], fakeuser['password'], config.portal['url'], testname, errordb, datadb, concurrent_users)
    #test.piuser.delete_user(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users)
    #test.institution.create(driver, config.portal['url'], testname, config.institution, config.fakeuser, errordb, datadb, concurrent_users)
    #test.piuser.reject_institution(driver, config.portal['url'], piuser, config.institution, testname, errordb, datadb, concurrent_users)

    #test.user.reset_password(driver, config.portal['url'],fakeuser, testname, errordb, datadb, concurrent_users)
    test.user.signin(driver, fakeuser['email'], fakeuser['password'], config.portal['url'], testname, errordb, datadb, concurrent_users)
    test.project.create(driver, config.portal['url'], config.project, testname, errordb, datadb, concurrent_users)

    setup.environment.clean(driver)

if __name__=="__main__":
    simpletest()


