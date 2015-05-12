import datetime
import time as t
import page
import influx
import error

def create(driver, url, project, testname, errordb, datadb, concurrent_users, by_piuser = False):
    print("Creating project")

    url += '/portal/project_request/'
    page.load(driver, url, testname, errordb, datadb, 'Create new Project', 'text_link', concurrent_users)
    try:
        projectname = driver.find_element_by_name('project_name')
        projectname.send_keys(project['name']+'_'+t.time())
        purpose = driver.find_element_by_name('purpose')
        purpose.send_keys(project['description'])
        button = driver.find_element_by_xpath("//button[@type='submit']")
        time_now = datetime.datetime.now()
        button.click()
    except:
        message = "[%s] TEST FAILED with error: I was not able to properly fill the form on: %s" % (str(__name__)+'.create', url)
        error.save_and_quit(message, url, testname, driver, errordb)

    try:
        import selenium.webdriver.support.ui as ui
        driver.wait = ui.WebDriverWait(driver, 10)
        if by_piuser:
            driver.wait.until(lambda driver: driver.find_element_by_xpath("//h1[text()='Success']"))
        else:
            driver.wait.until(lambda driver: driver.find_element_by_xpath("//h1[text()='Success']"))
        exec_time =  datetime.datetime.now() - time_now
    except:
        message = "[%s] TEST FAILED: processing new project creation failed for project: %s" % (str(__name__)+'.create', project['name'])
        error.save_and_quit(message, url, testname, driver, errordb)

    if datadb:
        influx.savedata("project_create", exec_time.total_seconds(), datadb, url, testname, concurrent_users)
    print ("[%s] OK - Time to process project request: %f [s]" % (str(__name__)+'.create', exec_time.total_seconds()))


