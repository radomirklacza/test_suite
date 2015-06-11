#!env python
import setup.environment
import setup.analyze
import config
import test.user
import test.page
import test.piuser
import test.institution
import test.project
import test.error as error
import datetime as t


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
        dis = setup.environment.display()
    else:
        dis = None
    driver = setup.environment.browser()


    concurrent_users = config.basic['number_of_users']
    testname = config.basic['testname']

    error.notify("Starting scenario %s" % testname, config.portal['url'], testname, errordb)

    test_status = []


    #### CREATE USER TEST ####

    user_create = test.user.create(driver, config.portal['url'], testname, fakeuser, 'onelab.test', errordb, datadb, concurrent_users, display=dis)
    test_status.append({'user.create': user_create[0], 'message': user_create[1]})

    if test_status[0]['user.create']:
        test.user.logout(driver)
        test.piuser.validate_user(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
        test.user.logout(driver)
    else:
        fakeuser['email']= config.existuser['email']
        fakeuser['password']= config.existuser['password']
    #### END ####


    #### Checking if user is PI and downgrade/upgrade process is working ####

    is_pi = test.user.is_pi(driver, config.portal['url'], fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
    test_status.append({'user.is_pi.check': is_pi[0], 'message': is_pi[1]})
    if is_pi[0]:
        test.user.logout(driver)
        if is_pi[1]:
            status = test.piuser.downgrade_user_from_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
            test_status.append({'user.downgrade_from_pi': status[0], 'message': status[1]})
            test.user.logout(driver)
            status = test.piuser.upgrade_user_to_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
            test.user.logout(driver)
            test_status.append({'user.upgrade_to_pi': status[0], 'message': status[1]})
        else:
            status = test.piuser.upgrade_user_to_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
            test_status.append({'user.upgrade_to_pi': status[0], 'message': status[1]})
            test.user.logout(driver)
            status = test.piuser.downgrade_user_from_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
            test_status.append({'user.downgrade_from_pi': status[0], 'message': status[1]})
            test.user.logout(driver)
    #### END ####

    #### TESTING PROJECT ####
    status = test.user.signin(driver, fakeuser['email'], fakeuser['password'], config.portal['url'], testname, errordb, datadb, concurrent_users, display=dis)
    if status[0]:
        test_status.append({'signin.user' : status[0], 'message': status[1]})
        status = test.project.create(driver, config.portal['url'], fakeuser['project'], testname, errordb, datadb, concurrent_users, display=dis)
        test_status.append({'project.create' : status[0], 'message': status[1]})
        test.user.logout(driver)
    if status[0]:
        status = test.piuser.validate_project(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
        test_status.append({'project.validate' : status[0], 'message': status[1]})
        test.user.logout(driver)
    if status[0]:
        status = test.piuser.delete_project(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
        test_status.append({'project.delete' : status[0], 'message': status[1]})
        test.user.logout(driver)
    ### END ###

    ### TEST INSTIUTION ###
    # #test.institution.create(driver, config.portal['url'], testname, config.institution, config.fakeuser, errordb, datadb, concurrent_users)
    # #test.piuser.reject_institution(driver, config.portal['url'], piuser, config.institution, testname, errordb, datadb, concurrent_users)
    ### END ###

    ### CLEAN UP ###
    # delete user only
    if filter(lambda test: test['user.create'] if 'user.create' in test else False, test_status):
        status = test.piuser.delete_user(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
        test_status.append({'user.delete' : status[0], 'message': status[1]})

    setup.environment.clean(driver, dis)
    print ('TEST COMPLETED')
    print(test_status)

if __name__ == "__main__":
    simpletest()


