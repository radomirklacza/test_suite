__author__ = 'radomirklacza'

#returns 1 if one want to store information in influxdb
def ifdbisneeded(config):
    if 'DB' in config.values():
        return 1
    else:
        return 0

#return 1 if open session is needed for test
def ifsessionisneeded(config):
    return 1
