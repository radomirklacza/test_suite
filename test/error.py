import influx
import io
import time as t

#raise and exception and save error to db
from setup import environment


def save_and_quit(message, url, testname, driver, errordb = None ):
    save_error(driver, testname)
    if (errordb):
        influx.saveerror("ERROR: " + str(message), errordb, url, testname)
    print(message)
    environment.clean(driver)
    exit()

def save_error(driver, testname):

    dir = 'saved_pages/'
    filename = 'error_django_'+testname+'_'+str(t.time())
    f = io.open(dir+filename+'.html', 'wb')
    f.write((driver.page_source).encode('utf-8'))
    f.close()
    print("HTML File location with error: %s" % filename+'.html')
    driver.save_screenshot(dir+filename+'.png')
    print("HTML File location with error: %s" % filename+'.png')
    return filename

def notify(message, url = None, testname = None, errordb = None):
    print(str(message))
    if (errordb):
        influx.saveerror("NOTIFY: " + str(message), errordb, url, testname)
    return
