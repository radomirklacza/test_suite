__author__ = 'radomirklacza'
from selenium import webdriver
from influxdb import client as inf

driver = None

def display():
    from pyvirtualdisplay import Display
    display = Display(visible=0, size=(800, 600))
    display.start()
    return display

def browser(browser = 'Firefox'):
    if(browser == 'Firefox'):
        driver = webdriver.Firefox()
    elif(browser == 'Chrome'):
        driver = webdriver.Chrome()
    elif(browser == 'Safari'):
        driver = webdriver.Safari()
    elif(browser == 'IE'):
        driver = webdriver.Ie()
    else:
        print "ERROR: This web browser is not supported, please check your config file and environment. Browser requested: %s" % config.runevironment['browser']
        exit()
    return driver

def influxdb(host, port, username, password, database):
    try:
        db = inf.InfluxDBClient(host=host, port=port, username=username, password=password, database=database)
        return db
    except:
        print "It was not able to establish connection into influxdb database"
        exit()

def clean(driv, dis = None):
    driv.close()
    if (dis):
        dis.stop()
