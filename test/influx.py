import error


def savedata(action, execution_time, database, url, testname, users):
    print("Testname: %s" % (testname))
    if (database):
        data = [
            {
                "points":[[action, execution_time, url, testname['name'], testname['unique'], testname['module'], users]],
                "name": 'data',
                "columns":["action", "execution_time", "portal", "test_name", "test_unique", "test_module",  "number_of_concurrent_users" ]
            }
        ]
        database.write_points(data)

#this function should save the results and errors into influxdb
def saveerror(type, errmesage, database, url, testname, filename = None):
    if (database):
        data = [
            {
                "points":[[type, errmesage, url, testname['name'], testname['unique'], testname['module'], filename]],
                "name": 'errors',
                "columns":["error_type", "error_message", "portal", "test_name", "test_unique", "test_module", "error_file"]
            }
        ]
        database.write_points(data)

def savestatus(testname, module, action, status, message, filename, database):
    if (database):
        data = [
            {
                "points":[[testname['name'], testname['unique'], module, action, status, message, filename,]],
                "name": 'status',
                "columns":["test_name", "test_unique", "test_module", "test_action", "status", "message", "error_filename"]
            }
        ]
        database.write_points(data)

