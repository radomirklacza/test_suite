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
import sqlite3
import time
import test.influx as inf


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
    testname = {'name': config.basic['testname'], 'unique': str(t.datetime.now().isoformat()), 'module' : ''}

    error.notify("Starting scenario %s" % testname['name'], config.portal['url'], testname, errordb)

    test_status = []


    #### CREATE USER TEST ####
    testname['module'] = 'create_user'
    user_create = test.user.create(driver, config.portal['url'], testname, fakeuser, fakeuser['institution'], errordb, datadb, concurrent_users, display=dis)
    test_status.append({'module': testname['module'], 'action': 'user.create', 'status': user_create[0], 'message': user_create[1], 'filename': user_create[2] if user_create.__len__() > 2 else None})

    if test_status[0]['status']:
        test.user.logout(driver)
        test.piuser.validate_user(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
        test.user.logout(driver)
    else:
        fakeuser['email']= config.existuser['email']
        fakeuser['password']= config.existuser['password']
    testname['module'] = ''
    #### END ####


    #### Checking if user is PI and downgrade/upgrade process is working ####
    testname['module'] = 'check_pi'
    is_pi = test.user.is_pi(driver, config.portal['url'], fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
    res = {'module': testname['module'], 'action': 'user.is_pi.check', 'status': is_pi[0], 'message': is_pi[1], 'filename': is_pi[2] if is_pi.__len__() > 2 else None}
    print res
    test_status.append(res)

    if is_pi[0]:
        test.user.logout(driver)
        if is_pi[1]:
            status = test.piuser.downgrade_user_from_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
            test_status.append({'module': testname['module'], 'action': 'user.downgrade_from_pi','status': status[0], 'message': status[1], 'filename': status[2] if status.__len__() > 2 else None})
            test.user.logout(driver)
            status = test.piuser.upgrade_user_to_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
            test.user.logout(driver)
            test_status.append({'module': testname['module'], 'action': 'user.upgrade_to_pi', 'status': status[0], 'message': status[1], 'filename': status[2] if status.__len__() > 2 else None})
        else:
            status = test.piuser.upgrade_user_to_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
            test_status.append({'module': testname['module'], 'action': 'user.upgrade_to_pi', 'status': status[0], 'message': status[1], 'filename': status[2] if status.__len__() > 2 else None})
            test.user.logout(driver)
            status = test.piuser.downgrade_user_from_pi(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
            test_status.append({'module': testname['module'], 'action': 'user.downgrade_from_pi', 'status': status[0], 'message': status[1], 'filename': status[2] if status.__len__() > 2 else None})
            test.user.logout(driver)
    testname['module'] = ''
    #### END ####

    #### TESTING PROJECT ####
    testname['module'] = 'test_project'
    status = test.user.signin(driver, fakeuser['email'], fakeuser['password'], config.portal['url'], testname, errordb, datadb, concurrent_users, display=dis)
    if status[0]:
        test_status.append({'module': testname['module'], 'action': 'signin.user', 'status': status[0], 'message': status[1], 'filename': status[2] if status.__len__() > 2 else None})
        status = test.project.create(driver, config.portal['url'], fakeuser['project'], testname, errordb, datadb, concurrent_users, display=dis)
        test_status.append({'module': testname['module'], 'action': 'project.create', 'status': status[0], 'message': status[1], 'filename': status[2] if status.__len__() > 2 else None})
        test.user.logout(driver)
    if status[0]:
        status = test.piuser.validate_project(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
        test_status.append({'module': testname['module'], 'action': 'project.validate', 'status': status[0], 'message': status[1], 'filename': status[2] if status.__len__() > 2 else None})
        test.user.logout(driver)
    if status[0]:
        status = test.piuser.delete_project(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
        test_status.append({'module': testname['module'], 'action': 'project.delete', 'status': status[0], 'message': status[1], 'filename': status[2] if status.__len__() > 2 else None})
        test.user.logout(driver)
    testname['module'] = ''
    ### END ###

    ### TEST INSTIUTION ###
    # #test.institution.create(driver, config.portal['url'], testname, config.institution, config.fakeuser, errordb, datadb, concurrent_users)
    # #test.piuser.reject_institution(driver, config.portal['url'], piuser, config.institution, testname, errordb, datadb, concurrent_users)
    ### END ###

    ### CLEAN UP ###
    # delete user only
    #if filter(lambda test: test['status'] if 'user.create' in test else False, test_status):
    # status = test.piuser.delete_user(driver, config.portal['url'], piuser, fakeuser, testname, errordb, datadb, concurrent_users, display=dis)
    #     test_status.append({'action': 'user.delete', 'status': status[0], 'message': status[1], 'filename': status[2] if status.__len__() > 2 else None})

    setup.environment.clean(driver, dis)
    print ('TEST COMPLETED')
    print(test_status)

    # if config.django['database']:
    #     ### hadnling data with sqlite3 ###
    #     def adapt_datetime(ts):
    #         return time.mktime(ts.timetuple())
    #     sqlite3.register_adapter(t.datetime, adapt_datetime)
    #     ### end crapy code###
    #
    #     conn = sqlite3.connect(config.django['database'])
    #     c = conn.cursor()
    #     for item in test_status:
    #         c.execute("INSERT OR REPLACE INTO stats_status(action, status, message, filename, date) VALUES (? , ?, ?, ?, ?)", (item['action'], item['status'], item['message'], item['filename'] if item['filename'] else 'none', t.datetime.now()))
    #         conn.commit()
    #     conn.close()
    for item in test_status:
        inf.savestatus(testname, item['action'], item['status'], item['message'], item['filename'], errordb)


if __name__ == "__main__":
    simpletest()


