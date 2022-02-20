import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import enum
from credentials import user

class Codes(enum.Enum):
    SUCCESS_CODE = 0
    FAIL_CODE = 1
    SUCCESS_RESULT_CODE = "Ekleme İşlemi Başarılı"
    FAIL_RESULT_CODE = "VAL06"
    TAKEN_RESULT_CODE = "VAL03"
    OUT_OF_DATE_RESULT_CODE = "VAL02"
    
# !!! YOU HAVE TO PROVIDE username, password and crn. 
username = user["username"] # instead of this, you can simply type your username = "abcd17"
password = user["password"] # and your password as password = "{your_password}"
crns = ["20791"]  # crn of the course that you want to take (i.e: ["20791","20792"])

INTERVAL_TIME = 15 # try to take the course with given interval_time. (unit type is second)
# you have to supply credentials and specify a crn.

url_login = "https://kepler-beta.itu.edu.tr/"
url_post = 'https://kepler-beta.itu.edu.tr/api/ders-kayit/v2' # this endpoint can be changed every term
url_token = 'https://kepler-beta.itu.edu.tr/ogrenci/auth/jwt'

# add options in order to prevent irrelevant errors from appearing in the console.
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get(url_login)
time.sleep(1) # wait for the page to load

driver.find_element(By.NAME, "ctl00$ContentPlaceHolder1$tbUserName").send_keys(username)
driver.find_element(By.NAME, "ctl00$ContentPlaceHolder1$tbPassword").send_keys(password)

driver.find_element(By.NAME, "ctl00$ContentPlaceHolder1$btnLogin").click()


print("Logged in succesfully")

driver.get(url_token)

access_token = driver.find_element(By.TAG_NAME, "pre").text # Token was fetched 

count = 1

while True:
    # send post request to the endpoint with crn and access token.
    response = requests.post(url_post,
                            headers={'Content-Type': 'application/json',
                                    'Authorization': 'Bearer {}'.format(access_token)}, 
                                    json={"ECRN": crns, "SCRN": []})

    json_response = response.json()

    ecrnResultList = json_response.get('ecrnResultList')  # ecrnResultList is list typed now

    ecrnResultDict = ecrnResultList[0]  # ecrnResult converted to dict

    statusCode = ecrnResultDict["statusCode"]
    resultCode = ecrnResultDict["resultCode"]
    
    print(count)
    
    if statusCode == Codes.SUCCESS_CODE.value:
        print('Course successfully taken !')
        break
    elif statusCode == Codes.FAIL_CODE.value and resultCode == Codes.OUT_OF_DATE_RESULT_CODE.value:
        print('You cannot enroll in a course right now.')
    elif statusCode == Codes.FAIL_CODE.value and resultCode == Codes.FAIL_RESULT_CODE.value:
        print('Insufficient quota.')
    else:
        print("A new error was encountered")
        print(statusCode, resultCode)
        break
        
    count += 1
    
    time.sleep(INTERVAL_TIME)




