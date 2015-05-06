
def savedata(action, execution_time, database, url, testname, users):
    print("Testname: %s" % (testname))
    if (database):
        data = [
            {
                "points":[[action, execution_time, url, testname, users]],
                "name": 'data',
                "columns":["action", "execution_time", "portal", "test_name", "number_of_concurrent_users" ]
            }
        ]
        #print(data)
        database.write_points(data)
        print "data sent to db: "

#this function should save the results and errors into influxdb
def saveerror(errmesage, database, url, testname):
    if (database):
        data = [
            {
                "points":[[errmesage, url, testname]],
                "name": 'errors',
                "columns":["error_message", "portal", "testname" ]
            }
        ]
        #print(data)
        database.write_points(data)
        print "error sent to db: "

