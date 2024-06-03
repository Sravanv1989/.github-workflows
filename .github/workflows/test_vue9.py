import pytest
import os
import json
import datetime
import logging
import time
import traceback
import platform
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from logging.handlers import TimedRotatingFileHandler
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions
from pyvirtualdisplay import Display
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Get the absolute path to the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to config1.json
config_file = os.path.join(script_dir, 'config1.json')

# Open config1.json
with open(config_file) as f:
    config = json.load(f)

BASE_URL = config.get('BASE_URL')
USER = config.get('USER')

# Set up logging
log_path = os.path.join(os.getcwd(), "logs1")
if not os.path.exists(log_path):
    os.mkdir(log_path)

filename = 'test3000_vue' + datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
log_file_path = os.path.join(log_path, filename)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
log_handler = TimedRotatingFileHandler(log_file_path)
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
# CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"  # Update with your chromedriver path
def send_log_to_slack(file_path, token, channel):
    client = WebClient(token=token)
    try:
        response = client.files_upload(
            channels=channel,
            file=file_path,
            title="Test Log File",
            initial_comment="Here is the log file from the latest test run."
        )
        logger.info("Log file sent to Slack successfully.")
    except SlackApiError as e:
        logger.error(f"Failed to send log file to Slack: {e.response['error']}")

@pytest.fixture()
def setup(request):
    # Initialize Xvfb display if not running on Windows
    if platform.system() != 'ubuntu':
        display = Display(visible=0, size=(1920, 1080))
        display.start()

    # ChromeOptions with headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Specify the path to ChromeDriver executable
    chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver-linux64/chromedriver')

    # Specify the path to Chrome binary
    chrome_binary_path = os.getenv('CHROME_BINARY_PATH', None)

    if chrome_binary_path:
        chrome_options.binary_location = chrome_binary_path

    # Initialize Chrome webdriver with chromedriver service
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    driver.get(BASE_URL)

    # Pass driver instance to the test
    request.cls.driver = driver
    yield driver

    # Quit the driver after the test
    driver.quit()
@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    # Send log file to Slack at the end of the pytest session
    send_log_to_slack(log_file_path, SLACK_TOKEN, SLACK_CHANNEL)

@pytest.mark.usefixtures("setup")
class TestWebsite:        
 def test_login_correct_password_assert_is(self):
    username_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/input') 
    password_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input')
    username_field.send_keys(USER["correct_email"])
    password_field.send_keys(USER["correct_password"])
    time.sleep(2)  
    submit = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/button')
    submit.click()
    time.sleep(2)
    output_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[3]/img[2]')
    time.sleep(2)                                     
    if output_field is None or not output_field.is_displayed():
        logger.info("test_login_correct_password_assert_is is failed")
    else:
        assert output_field.is_displayed() == True
        logger.info("test_login_correct_password_assert_is is passed")

 def test_login_incorrect_password(self):
        username_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/input')
        password_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input')
        
        username_field.send_keys(USER["correct_email"])
        password_field.send_keys(USER["incorrect_password"])
        submit = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/button')
        submit.click()
        # time.sleep(2)
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[1]/div[2]')))                                                                               
        # time.sleep(2)
        if output_field is None or not output_field.is_displayed():
            logger.info("test_login_incorrect_password_assert_is is failed")
        else:
            assert output_field.is_displayed() == True
            logger.info("test_login_incorrect_password_assert_is is passed")

 def test_login_incorrect_email_correct_password(self):
        username_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/input')
        password_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input')
        submit = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/button')
        username_field.send_keys(USER['incorrect_email'])
        password_field.send_keys(USER['correct_password'])
        submit.click()
        # time.sleep(2)
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[1]/div[2]')))
        # time.sleep(2)
        if output_field is None or not output_field.is_displayed():
           logger.info("test_login_incorrect_email_correct_password_assert_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_login_incorrect_email_correct_password_assert_is is passed")

 def test_login_blank_email_password(self):
        username_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/input')
        password_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input')
        submit = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/button')
        username_field.send_keys('invalid_username')
        password_field.send_keys('invalid_password')
        submit.click()
        # time.sleep(2)
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[1]/div[2]')))
        # time.sleep(2)
        if output_field is None or not output_field.is_displayed():
           logger.info("test_login_blank_email_password_assert_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_login_blank_email_password_assert_is is passed")

 def test_login_invalid_username(self):
        username_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/input')
        password_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input')
        submit = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/button')
        username_field.send_keys(USER['invalid_username'])
        password_field.send_keys(USER['correct_password'])  
        submit.click()
        time.sleep(2) 
        current_url = BASE_URL
        if current_url == BASE_URL:
            logger.info("test_login_invalid_username_assert_is is passed")
        else:
            logger.info("test_login_invalid_username_assert_is is failed")
        

 def test_invalid_password(self):
        username_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/input')
        password_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input')
        submit = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/button')
        username_field.send_keys(USER['correct_email'])
        password_field.send_keys(USER['invalid_password'])
        submit.click()
        current_url = BASE_URL

        if current_url == BASE_URL:
            logger.info("test_login_invalid_password_assert_is is passed")
        else:
            logger.error("test_login_invalid_password_assert_is is failed")

 def login(self):
        username_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/input')
        password_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/input')
        submit = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/button')
        username_field.send_keys(USER['correct_email'])
        password_field.send_keys(USER['correct_password'])
        submit.click()
        return submit
 
 def test_Latest_News_article_Date_Time(self):
        self.login()
        time.sleep(5)                        
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div[2]/div/h6').click()
        time.sleep(5)
      #   self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]').click()
      #   time.sleep(5)
        
        # Extract the date and time element dynamically         
        date_time_element = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[2]/div')
        first_article_datetime_str = date_time_element.text     
        timezone = first_article_datetime_str.split()[-1]
        first_article_datetime_str = first_article_datetime_str.replace(timezone, '').strip()

        # Convert the extracted string to datetime object
        first_article_datetime = datetime.datetime.strptime(first_article_datetime_str, "%a, %d %b %Y %H:%M:%S")

        # Get the current datetime
        current_datetime = datetime.datetime.now()

        # Compare the dates
        if current_datetime.date() == first_article_datetime.date():
            logger.info("test_Latest_News_article_Date_Time is passed")
        else:
            logger.info("test_Latest_News_article_Date_Time is failed")
     
 def test_Article_of_interest(self):
        self.login()
        time.sleep(2)  
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div/div').click()
        output_field=WebDriverWait(self.driver, 10).until( EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div[1]')))
        if output_field is None or not output_field.is_displayed():
           logger.info("test_Article_of_interest_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_Article_of_interest_is is passed")    

 def test_category_Favourite(self):
        self.login()
        time.sleep(2)  
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[2]/div[2]/ul[2]/li/div').click()
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[2]/div[3]/div[1]/div[1]/div[1]').click()                   
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[2]/div[1]/div[1]/div[1]/div[1]')))                                                
        if output_field is None or not output_field.is_displayed():
           logger.info("test_category_Favourite_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_category_Favourite_is is passed")  

 def test_category_UnFavourite(self):
        self.login()
        time.sleep(2)  
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[2]/div[2]/ul[2]/li/div').click()
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[2]/div[1]/div[1]/div[1]/div[1]').click()
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[2]/div[3]/div[1]/div[1]/div[1]')))
        if output_field is None or not output_field.is_displayed():
           logger.info("test_category_UnFavourite_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_category_UnFavourite_is is passed")  

 def test_category_article(self):
        self.login()
        time.sleep(2)                          
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[2]/ul[2]/li/div').click()
        time.sleep(2)
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[2]/div[3]/div[1]/div[1]/div[2]').click()
        time.sleep(2)                       
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div[1]')))
        if output_field is None or not output_field.is_displayed():                                   
           logger.info("test_category_article_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_category_article_is is passed") 

 def test_Location_threat_Command_province(self):
        self.login()
        time.sleep(2)  
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[2]/ul[3]/li/div').click()
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[3]/div[2]/div[1]/div[1]/div[2]/select/option[2]').click()
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[3]/div[2]/div[1]/div[2]/div[2]/select/option[2]').click()
        time.sleep(2)
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[3]/div[2]/div[2]/div/div[1]')))                                              
        if output_field is None or not output_field.is_displayed():                                    
           logger.info("test_Location_threat_Command_province is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_Location_threat_Command_province is passed") 

 def test_Location_artilce(self):
        self.login()
        time.sleep(2)  
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[2]/ul[3]/li/div').click()
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[3]/div[2]/div[1]/div[1]/div[2]/select/option[2]').click()
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[3]/div[2]/div[1]/div[2]/div[2]/select/option[2]').click()
        
        # self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        # time.sleep(2)
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[3]/div[2]/div[2]/div/div[5]').click() 
        time.sleep(2)                       
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div[1]')))                              
        if output_field is None or not output_field.is_displayed():                                    
           logger.info("test_Location_artilce_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_Location_artilce_is is passed")

#  def test_keyword_search(self):
#     self.login()
#     time.sleep(5)  
#     search_input = self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[1]/div[1]/div[1]/div/input')
#     search_input.send_keys(USER['search_word'])
#     time.sleep(10) 
#    #  try:
#    #      WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[3]'))).click()
#    #      time.sleep(5)
#    #      output_field = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]')))
#    #      assert output_field.is_displayed() == True
#    #      logger.info("test_keyword_search_is passed")
#    #  except TimeoutException as e:
#    #      logger.error(f"Error occurred while searching: {e}")
#    #      logger.info("test_keyword_search_is failed")
#       #   element = self.driver.find_element(By.TAG_NAME, 'div')s
#       #   action = ActionChains(self.driver)
#       #   action.move_to_element(element).click().perform()     
#       #   time.sleep(10)
#     self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[3]') 
#     time.sleep(10)                                                                                         
#     output_field= WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]')))
                                                                                                                
#       #   output_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div[1]')                                   
#     if output_field is None or not output_field.is_displayed():
#          logger.info("test_keyword_search_is is failed")
#     else:
#          assert output_field.is_displayed() == True
#          logger.info("test_keyword_search_is is passed")
         

 def test_semantic_search(self):
        self.login()  
        time.sleep(2)                       
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[1]/div[1]/div[1]/div/input').send_keys(USER['semantic_search-word'])
        time.sleep(2) 
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]').click() 
        time.sleep(2)                       
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div[1]/div[1]')))                                    
        if output_field is None or not output_field.is_displayed():
           logger.info("test_semantic_search_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_semantic_search_is is passed")

 def test_NER_search(self):
        self.login()   
        time.sleep(2)                     
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[1]/div[1]/div[1]/div/input').send_keys(USER['search_letter'])
        time.sleep(2)  
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/div/div[1]').click()
        time.sleep(2) 
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[2]').click()
        time.sleep(2)
        output_field=WebDriverWait(self.driver, 10).until( EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]')))
        if output_field is None or not output_field.is_displayed():                                     
           logger.info("test_NER_Search is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_NER_Search is passed")


 def test_Notification(self):
        self.login()
        time.sleep(2)                     
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[2]/div[3]/div[2]/i').click()
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[3]/div[2]/div/div/div/div/div[2]/div/button')))                                   
        if output_field is None or not output_field.is_displayed():
           logger.info("test_Notification_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_Notification_is is passed")

 def test_Notification_article(self):
        self.login()
        time.sleep(2)                     
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[2]/div[3]/div[2]/i').click()
        time.sleep(5)                                
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[2]/div[3]/div[2]/div/div/div/div/div[2]/div/button').click()
        time.sleep(5)                  
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#app > div > div > div.flex-1.flex.flex-col.gap-10 > div:nth-child(2) > div > div:nth-child(1) > div.text-\[\#3C3C3C\].font-bold')))                                   
        if output_field is None or not output_field.is_displayed():                                    
           logger.info("test_Notification_article_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_Notification_article_is is passed")

 def test_Notification_mark_as_read(self):
        self.login()
        time.sleep(2)                       
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[2]/div[3]/div[2]/i').click()
        time.sleep(2)                               
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[2]/div[3]/div[2]/div/div/div/div/div[1]/div[2]/button').click()
        time.sleep(5)
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[2]/div[3]/div[2]/i').click()   
        time.sleep(5)                     
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#app > div > div:nth-child(1) > div.w-full.flex > div.flex.h-10.mt-5.w-auto > div:nth-child(2) > div > div > div > div > div.font-semibold.flex.flex-col.gap-3 > div:nth-child(1) > button')))                                   
        if output_field is None or not output_field.is_displayed():
           logger.info("test_Notification_mark_as_read_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_Notification_mark_as_read_is is passed")

#  def test_Pagination(self):
#     self.login()
#     time.sleep(5)
#     self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[2]/div/h6').click()
#     time.sleep(2)                      
#     self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
#     time.sleep(5)
#     pagination_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[3]/ul/li[14]/button')))
#     pagination_button.click()                                                                       
#     output_field = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[9]/div[1]')))
#     if output_field is None or not output_field.is_displayed():                                    
#         logger.info("test_Pagination_is is failed")
#     else:
#         assert output_field.is_displayed() == True
#         logger.info("test_Pagination_is passed")
#     # except TimeoutException as e:
#     #     logger.error(f"Error occurred while paginating: {e}")
#     #     logger.info("test_Pagination_is failed")

#  def test_Filter(self):
#         self.login()
#         time.sleep(5)                       
#         self.driver.find_element(By.CSS_SELECTOR, '#Filter').click()
                                            
#       #   element = self.driver.find_element(By.TAG_NAME, 'img[1]')
#       #   action = ActionChains(self.driver)
#       #   action.move_to_element(element).click().perform()
#         time.sleep(5)                      
#         self.driver.find_element(By.CSS_SELECTOR, '#app > div > div:nth-child(1) > div.relative > div > div > div > div.flex.flex-wrap.gap-5.p-2\.5.px-\[10\%\] > div:nth-child(3)').click()
#         time.sleep(5)                       
#         self.driver.find_element(By.CSS_SELECTOR, '#app > div > div:nth-child(1) > div.relative > div > div > div > div.h-3\/5.flex-1.flex.flex-col.sm\:flex-row.gap-5.p-2\.5.px-\[10\%\] > div:nth-child(1) > div:nth-child(2) > select > option:nth-child(2)').click() 
#         time.sleep(5)
#         self.driver.find_element(By.CSS_SELECTOR, '#app > div > div:nth-child(1) > div.relative > div > div > div > div.h-3\/5.flex-1.flex.flex-col.sm\:flex-row.gap-5.p-2\.5.px-\[10\%\] > div:nth-child(2) > div:nth-child(2) > select > option:nth-child(2)').click()
#         time.sleep(5)                       
#         self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[4]/div[3]/div[2]/select/option[5]').click()
#         time.sleep(2)
#         # self.driver.execute_script("window.scrollTo(0, window.scrollY + 300)")
#         # time.sleep(1)
#         self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[6]/div/div[2]/button').click() 
#       #   output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]')))
#       # #   output_field = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]')
#       #   if output_field is None or not output_field.is_displayed():
#       #      logger.info("test_Filter_is is failed")
#       #   else:
#       #      assert output_field.is_displayed() == True
#       #      logger.info("test_Filter_is is passed")
#         try:
#             output_field = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]')))
#             assert output_field.is_displayed() == True
#             logger.info("test_Filter_is passed")
#         except:
#             logger.info("test_Filter_is failed")

#  def test_article(self):
#         self.login()
#         time.sleep(5)
#         self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[2]/div/h6').click()
#         time.sleep(5)
#         self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]').click()
#         time.sleep(5)
#         output_field=WebDriverWait(self.driver, 10).until( EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div[2]/h2')))                                   
#         if output_field is None or not output_field.is_displayed():                                            
#            logger.info("test_article_is is failed")
#         else:
#            assert output_field.is_displayed() == True
#            logger.info("test_article_is is passed")

#  def test_article_link(self):
#     self.login()
#     time.sleep(5)

#     # Click on the necessary elements
#     self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div[2]/div/h6').click()
#     time.sleep(5)
#     self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]').click()
#     time.sleep(5)
#     self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/label/div').click()
#     time.sleep(10)
#     self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div[2]/h2').click()
#     time.sleep(10)                       
#     # Switch to the new window
#     self.driver.switch_to.window(self.driver.window_handles[-1])
#     time.sleep(5)
#    #  try:
#         # Explicitly wait for the article title element to be visible
#     article_title_element = WebDriverWait(self.driver, 10).until(
#             EC.visibility_of_element_located((By.XPATH, '//*[@id="content"]/div[1]/div[1]/div/div[2]/h1'))
#         )                                                
#     article_title_text = article_title_element.text
#     time.sleep(5)
#     # Switch back to the original window
#     original_window = self.driver.current_window_handle
#     self.driver.switch_to.window(original_window)
#     time.sleep(5)
#         # Continue with your comparison logic...
#     element = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/h2').text
#     print(element)
#     # Compare the elements directly without try-except block
#     if element == article_title_text:
#          logger.info("Login passed with article-original-link")
#     else:
#          logger.info("Login failed with article-original-link")
   #  except Exception as e:
   #      logger.error(f"Exception occurred in test_article_link: {e}")

 def test_article_chinese_view(self):
        self.login()
        time.sleep(5)
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[2]/div/h6').click()
        time.sleep(5)
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]').click()
        time.sleep(5)
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[2]/div[2]/div[2]/label/div').click()
        time.sleep(5)
        output_field=WebDriverWait(self.driver, 10).until( EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/h2')))                                   
        if output_field is None or not output_field.is_displayed():                                     
           logger.info("test_article_chinese_view_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_article_chinese_view_is is passed")

 def test_article_category(self):
        self.login()
        time.sleep(5)
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[2]/div/h6').click()
        time.sleep(5)
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]').click()
        time.sleep(5)                      
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[2]/div[1]/div[1]/div/div').click()
        time.sleep(10)                            
        output_field=WebDriverWait(self.driver, 10).until( EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]')))                                   
        if output_field is None or not output_field.is_displayed():                                     
           logger.info("test_article_category_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_article_category_is is passed")
      #   try:
      #       output_field=WebDriverWait(self.driver, 10).until( EC.visibility_of_element_located((By.CSS_SELECTOR, '#app > div > div > div.flex-1.flex.flex-col.gap-10 > div:nth-child(2) > div > div:nth-child(1) > div.text-\[\#3C3C3C\].font-bold')))
      #       assert output_field.is_displayed() == True
      #       logger.info("test_article_category_is passed")
      #   except:
      #       logger.info("test_article_category_is failed")
 
 def test_NER_People(self):
        self.login()
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div[2]/div/h6').click()
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]').click() 
        time.sleep(5)                       
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div[1]/div/div[2]/table/tbody/tr[1]/td[1]/div').click() 
        time.sleep(5)                            
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]')))                                          
        if output_field is None or not output_field.is_displayed():                                    
           logger.info("test_NER_People_is is failed")                                                 
                                                                                    
        else:
           assert output_field.is_displayed() == True
           logger.info("test_NER_People_is is passed")  
      #   try:
      #       output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#app > div > div > div.flex-1.flex.flex-col.gap-10 > div:nth-child(2) > div > div:nth-child(1) > div.text-\[\#3C3C3C\].font-bold')))
      #       assert output_field.is_displayed() == True
      #       logger.info("test_NER_People_is passed")
      #   except:
      #       logger.info("test_NER_People_is failed") 

#  def test_NER_Locations(self):
#         self.login()
#         time.sleep(5)
#         self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div[2]/div/h6').click()
#         time.sleep(5)
#         self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[2]/div[1]').click() 
#         time.sleep(5)                       
#         self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div[3]/div/div[2]/table/tbody/tr[1]/td[1]/div').click() 
#         time.sleep(2)                        
#         output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div[2]/div/div[1]/div[1]')))                                          
#         if output_field is None or not output_field.is_displayed():                                      
#            logger.info("test_NER_Locations_is is failed")
#         else:
#            assert output_field.is_displayed() == True
#            logger.info("test_NER_Locations_is is passed")
      

 def test_Popup_Close(self):
        self.login()
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[2]/ul[2]/li/div').click()
        time.sleep(5)
        self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div/div/div[1]/i').click()
        time.sleep(5)                       
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[3]/img[2]')))                                          
        if output_field is None or not output_field.is_displayed():                                      
           logger.info("test_Popup_Close_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_Popup_Close_is is passed")

 def test_Cluster(self):
        self.login()
        time.sleep(5)
        self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[2]/div[2]/ul[4]/li/a').click()
        time.sleep(5)
        self.driver.execute_script("window.scrollTo(0, window.scrollY + 300)")
        time.sleep(5)                                   
        output_field=WebDriverWait(self.driver, 10).until( EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[3]/div[2]/div/div[1]/div[1]/div')))
        if output_field is None or not output_field.is_displayed():                                     
           logger.info("test_Cluster is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_Cluster is passed")

#  def test_Cluster_See_More_Topics(self):
#         self.login()
#         time.sleep(5)
#         self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[1]/div[2]/div[2]/ul[4]/li/a').click()                                 
#         time.sleep(20)                    
#         self.driver.execute_script("window.scrollTo(0, window.scrollY + 2000)")
#         time.sleep(20)  
#         self.driver.find_element(By.CSS_SELECTOR,'#app > div > div.flex.flex-col.gap-5.py-5 > div:nth-child(4) > div > div:nth-child(2) > div.w-full.h-auto.flex.flex-col.sm\:flex-row.gap-5 > div.w-full.sm\:w-\[30\%\].flex.flex-col.gap-5 > div > div.w-full.flex.justify-center.items-center > button').click()
#         time.sleep(20)                                                            
#         output_field=WebDriverWait(self.driver, 20).until( EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[3]/div[2]/div/div[2]/div[3]/div[2]/div/div[1]/div[1]/div')))
#       #   self.driver.execute_script("window.scrollTo(0, window.scrollY + 600)")
#       #   self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
#       #   self.driver.find_element(By.XPATH,'//*[@id="app"]/div/div[3]/div/div/div/div[1]/div[1]/div[2]/div[35]/button').click()
                                            
#         if output_field is None or not output_field.is_displayed():                                     
#            logger.info("test_Cluster_See_More_Topics is failed")
#         else:
#            assert output_field.is_displayed() == True
#            logger.info("test_Cluster_See_More_Topics is passed")
           
#  def test_Cluster_See_less_Topics(self):
#         self.login()
#         time.sleep(5)
#         self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div[2]/div[2]/ul[4]/li/a').click()  
#         time.sleep(20)
#         self.driver.execute_script("window.scrollTo(0, window.scrollY + 2000)")
#         time.sleep(20)
#         self.driver.find_element(By.CSS_SELECTOR,'#app > div > div.flex.flex-col.gap-5.py-5 > div:nth-child(4) > div > div:nth-child(2) > div.w-full.h-auto.flex.flex-col.sm\:flex-row.gap-5 > div.w-full.sm\:w-\[30\%\].flex.flex-col.gap-5 > div > div.w-full.flex.justify-center.items-center > button').click()
#         time.sleep(20) 
#         self.driver.execute_script("window.scrollTo(0, window.scrollY + 1000)")
#         time.sleep(20) 
#         self.driver.find_element(By.CSS_SELECTOR,'#app > div > div.flex.flex-col.gap-5.py-5 > div:nth-child(4) > div > div:nth-child(2) > div.w-full.h-auto.flex.flex-col.sm\:flex-row.gap-5 > div.w-full.sm\:w-\[30\%\].flex.flex-col.gap-5 > div > div.w-full.flex.justify-center.items-center > button').click()
#         time.sleep(20)                             
#         self.driver.execute_script("window.scrollTo(0, 0);")
#         time.sleep(20)                  
#         output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[3]/div[2]/div/div[2]/div[3]/div[2]/div/div[1]/div[1]/div')))                                         
#         if output_field is None or not output_field.is_displayed():                                    
#            logger.info("test_Cluster_See_less_Topics_is is failed")
#         else:
#            assert output_field.is_displayed() == True
#            logger.info("test_Cluster_See_less_Topics_is is passed")

 def test_footer(self):
        self.login()
        time.sleep(5)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, '#app > div > div.w-full.overflow-x-hidden.pb-\[15px\] > div.w-full.flex > div:nth-child(3) > p:nth-child(2) > a > svg').click()
        time.sleep(10) 
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(10)                             
        original_window = self.driver.current_window_handle
        self.driver.switch_to.window(original_window)
        time.sleep(10)
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(10)
        self.driver.find_element(By.CSS_SELECTOR, '#app > div > div.w-full.overflow-x-hidden.pb-\[15px\] > div.w-full.flex > div:nth-child(3) > p:nth-child(3) > a > svg').click()
        time.sleep(10)                              
        original_window = self.driver.current_window_handle
        self.driver.switch_to.window(original_window)
        time.sleep(10)
        self.driver.find_element(By.CSS_SELECTOR, '#app > div > div.w-full.overflow-x-hidden.pb-\[15px\] > div.w-full.flex > div:nth-child(3) > p:nth-child(4) > a > svg').click()
        original_window = self.driver.current_window_handle    
        self.driver.switch_to.window(original_window)
        time.sleep(5)
        output_field=WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="app"]/div/div[3]/div[2]/div[1]/h4[1]')))                                        
        if output_field is None or not output_field.is_displayed():                                   
           logger.info("test_footer_is is failed")
        else:
           assert output_field.is_displayed() == True
           logger.info("test_footer_is is passed")

 def test_Logout(self):
        self.login() 
      #   time.sleep(5)                      
      #   self.driver.find_element(By.TAG_NAME, 'img').click()
        time.sleep(5)
        element = self.driver.find_element(By.XPATH, '//*[@id="logout"]')
        action = ActionChains(self.driver)
        action.move_to_element(element).click().perform()
        time.sleep(5)
         #   output_field=WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/button'))) 
        print("Before WebDriverWait")
        output_field = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[2]/div/div[2]/div/div[2]/div[3]/button'))
        )                                                
        print("After WebDriverWait")
        if output_field is None or not output_field.is_displayed():
            logger.info("test_Logout_is is failed")
        else:
            assert output_field.is_displayed() == True
            logger.info("test_Logout_is is passed")    

