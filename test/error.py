import influx
import io
import time as t

#raise and exception and save error to db
from setup import environment


def save_and_quit(message, url, testname, driver, errodb = None ):
    save_error(driver, testname)
    if (errodb):
        influx.saveerror(message, errodb, url, testname)
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

