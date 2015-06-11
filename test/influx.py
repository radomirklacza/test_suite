import error


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
        #print "data sent to db: "

#this function should save the results and errors into influxdb
def saveerror(type, errmesage, database, url, testname, filename = None):
    if (database):
        data = [
            {
                "points":[[type, errmesage, url, testname, filename]],
                "name": 'errors',
                "columns":["error_type", "error_message", "portal", "testname", "error_file"]
            }
        ]
        #print(data)

        database.write_points(data)
        #print "data sent to db: "

