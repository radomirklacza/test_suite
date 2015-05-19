import selenium.webdriver.support.ui as ui
import datetime

import page
import error
import influx
import gemail


def create(driver, url, testname, institution, fakeuser, errordb, datadb, concurrent_users):
    print('Creating new institution')

    url += '/portal/join'
    page.load(driver, url, testname, errordb, datadb, 'terms and conditions.', 'link_text', 'main-page', concurrent_users)

    gemail.delete_all_emails(fakeuser['trueemail'], fakeuser['password'], fakeuser['email'])

    try:
        # institution side
        site_name = driver.find_element_by_id('site_name')
        site_name.send_keys(institution['name'])
        address_city = driver.find_element_by_id('address_city')
        address_city.send_keys(institution['city'])
        address_country = driver.find_element_by_id('address_country')
        address_country.send_keys(institution['country'])
        site_abbreviated_name = driver.find_element_by_id('site_abbreviated_name')
        site_abbreviated_name.send_keys(institution['short_name'])
        site_url = driver.find_element_by_id('site_url')
        site_url.send_keys(institution['http_address'])

        # user side
        pi_first_name = driver.find_element_by_id('pi_first_name')
        pi_first_name.send_keys(fakeuser['firstname'])
        pi_last_name = driver.find_element_by_id('pi_last_name')
        pi_last_name.send_keys(fakeuser['lastname'])
        pi_email = driver.find_element_by_id('pi_email')
        pi_email.send_keys(fakeuser['email'])
        pi_phone = driver.find_element_by_id('pi_phone')
        pi_phone.send_keys(fakeuser['phone_number'])
        password = driver.find_element_by_id('password')
        password.send_keys(fakeuser['password'])
        password = driver.find_element_by_name("confirmpassword")
        password.send_keys(fakeuser['password'])

        # agree conditions
        agreement = driver.find_element_by_name("agreement")
        agreement.click()

        button = driver.find_element_by_xpath("//button[@type='submit']")
        time = datetime.datetime.now()
        button.click()
    except:
        message = "[%s] TEST FAILED with error: I was not able to properly fill the form on: %s" % (str(__name__)+'.create', url)
        error.save_and_quit(message, url, testname, driver, errordb)

    try:
        driver.wait = ui.WebDriverWait(driver, 10)
        driver.wait.until(lambda driver: driver.find_elements_by_xpath("//*[contains(text(), 'Organization information received')]"))
    except:
        message = "[%s] TEST FAILED with error: I've not get proper after create-institution screen %s" % (str(__name__)+'.create', url)
        error.save_and_quit(message, url, testname, driver, errordb)

    exec_time = datetime.datetime.now() - time

    if (datadb):
        influx.savedata("create_institution_form_submit", exec_time.total_seconds(), datadb, url, testname, concurrent_users)

    return

