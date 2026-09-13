from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import time
from datetime import datetime as dt
import os

# ------------------------ MY CREDENTIALS ----------------------------
USER_NAME = os.environ.get('USER_NAME')
PASSWORD = os.environ.get('PASSWORD')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# ------------------------ SETTING UP CHROME -------------------------
chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_experimental_option('prefs', {
    "credentials_enable_service": False, 
    "profile.password_manager_enabled": False 
})

chrome_options.add_experimental_option('prefs', {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False
})

driver = uc.Chrome(options=chrome_options, version_main=152)
driver.get('https://s.amizone.net/')
time.sleep(2)

wait = WebDriverWait(driver, 10)

# ------------------------ NETWORK RESELIANCE --------------------------


def retry(func, retries=3, description=None):
    for i in range(retries):
        print(f"Trying {description}. Attempt: {i + 1}")
        try:
            return func()
        except TimeoutException:
            if i == retries - 1:
                raise
            time.sleep(1)

# ------------------------- LOGIN --------------------------------------


def login():
    user_name_input = wait.until(ec.visibility_of_element_located((By.NAME, '_UserName')))
    user_name_input.clear()
    user_name_input.send_keys(USER_NAME)

    password_input = wait.until(ec.visibility_of_element_located((By.NAME, '_Password')))
    password_input.clear()
    password_input.send_keys(PASSWORD)

    # give time to captcha
    time.sleep(3)

    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_button.click()

    print("You are logged in.")

    time.sleep(2)
    
    wait.until(
        ec.presence_of_element_located((By.ID, 'calendar'))
    )


retry(login, description="to Connect.")
# ------------------------ REMOVE POP UP ---------------------------------


driver.execute_script("""
    var modals = document.querySelectorAll('.modal, .modal-backdrop, [class*="popup"], [id*="popup"], div[style*="z-index"]');
    for (var i = 0; i < modals.length; i++) {
        modals[i].remove();
    }
""")
time.sleep(1)

# ------------------------- GO TO THE TIME TABLE SECTION -------------------
calendar = wait.until(ec.visibility_of_element_located((By.ID, 'calendar')))

date = calendar.find_element(By.CSS_SELECTOR, 'div.fc-center h2').text

try:
    day = calendar.find_element(By.CSS_SELECTOR, 'span.fc-list-heading-main').text
except NoSuchElementException:
    today = dt.today()
    day = today.strftime("%A")


time_table_elements = calendar.find_elements(By.CSS_SELECTOR, 'tr[class^="fc-list-item"]')

time_table = []
if time_table_elements:
    for classes in time_table_elements:
        time_table_info = {
            classes.find_element(By.CSS_SELECTOR, 'td.fc-list-item-time').text:
                classes.find_element(By.CSS_SELECTOR, 'td.fc-list-item-title > a').text
        }
        time_table.append(time_table_info)


driver.quit()
# ------------------------------ SENDING THE DATA TO TELEGRAM ------------------------------
# if the time table is empty it is day off no classes
message = f"DATE:{date}\nDAY:{day}\n📆 Today's TimeTable 📆\n\n"
if not time_table:
    message += f"💤Stay in Bed it's off Today 🛌\n"
else:
    for entry in time_table:
        for time, details in entry.items():
            message += f"⏰ {time} \n {details}\n\n"

# endpoint URL
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


data = {
    "chat_id": CHAT_ID,
    "text": message,
    "parse_mode": "Markdown"
}
response = requests.post(url=URL, json=data)
if response.status_code == 200:
    print("Message Sent Successfully.")
else:
    print(f"❌Failed to Send Message. Error {response.text}")


