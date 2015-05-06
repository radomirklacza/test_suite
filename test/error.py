import influx
import io
import time as t

#raise and exception and save error to db
from setup import environment


def save_and_quit(message, url, testname, driver, errodb = None ):
    if (errodb):
        influx.saveerror(message, errodb, url, testname)
    print(message)
    environment.clean(driver)
    exit()

def save_html(data, testname):
    dir = 'saved_pages/'
    filename = 'error_django_'+testname+'_'+str(t.time())+'.html'
    f = io.open(dir+filename, 'wb')
    f.write((data).encode('utf-8'))
    f.close()
    print("File location with error: %s" % filename)
