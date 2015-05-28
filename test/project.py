import datetime
import time as t
import page
import influx
import error
import selenium.webdriver.support.ui as ui

def create(driver, url, project, testname, errordb, datadb, concurrent_users, by_piuser = False):
    print("Creating project")
    page.load_main_page(driver, url, testname, errordb, datadb, concurrent_users)
    url += '/portal/project_request/'
    page.load(driver, url, testname, errordb, datadb, 'Create new Project', 'link_text', 'create_project', concurrent_users)
    try:
        p = project['name'] + "_" + str(t.time())
        print p
        projectname = driver.find_element_by_name("project_name")
        projectname.send_keys(p)
        purpose = driver.find_element_by_name("purpose")
        purpose.send_keys(project['description'])
        button = driver.find_element_by_xpath("//button[@type='submit']")
        time_now = datetime.datetime.now()
        button.click()
    except:
        message = "[%s] TEST FAILED with error: I was not able to properly fill the form on: %s" % (str(__name__)+'.create', url)
        error.save_and_quit(message, url, testname, driver, errordb)

    try:
        driver.wait = ui.WebDriverWait(driver, 50)
        if by_piuser:
            driver.wait.until(lambda driver: driver.find_element_by_xpath("//h1[text()='Success']"))
        else:
            driver.wait.until(lambda driver: driver.find_element_by_xpath("//h1[text()='Project request sent']"))

        exec_time =  datetime.datetime.now() - time_now
    except:
        message = "[%s] TEST FAILED: processing new project creation failed for project: %s" % (str(__name__)+'.create', project['name'])
        error.save_and_quit(message, url, testname, driver, errordb)

    if datadb:
        influx.savedata("project_create", exec_time.total_seconds(), datadb, url, testname, concurrent_users)
    print ("[%s] OK - Time to process process request: %f [s]" % (str(__name__)+'.create', exec_time.total_seconds()))

