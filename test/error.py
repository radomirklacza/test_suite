import influx
import io
import time as t
import datetime

#raise and exception and save error to db
from setup import environment


def save_and_quit(message, url, testname, driver, errordb = None, display = None ):
    save_error(driver, testname, message, url, errordb)
    print(str(datetime.datetime.now()) +' - ' + message)
    environment.clean(driver, display)
    exit()

def save_error(message, url, testname, driver, errordb = None):
    # saving screenshot
    dir = 'saved_pages/'
    filename = 'error_django_'+testname+'_'+str(t.time())
    f = io.open(dir+filename+'.html', 'wb')
    f.write((driver.page_source).encode('utf-8'))
    f.close()
    print("HTML File location with error: %s" % filename+'.html')
    driver.save_screenshot(dir+filename+'.png')
    print("HTML File location with error: %s" % filename+'.png')

    # saving to influx
    if (errordb):
        influx.saveerror("FATAL", "ERROR: " + str(message), errordb, url, testname, filename)

    return filename

def notify(message, url = None, testname = None, errordb = None):
    print(str(datetime.datetime.now())  +' - ' + message)
    if (errordb):
        influx.saveerror("NOTIFY", "NOTIFY: " + str(message), errordb, url, testname)
    return
