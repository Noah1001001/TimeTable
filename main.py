import os
import time
import requests
import undetected_chromedriver as uc

from datetime import datetime as dt
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException


# ------------------------ CREDENTIALS ------------------------

USER_NAME = os.environ["USER_NAME"]
PASSWORD = os.environ["PASSWORD"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


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

wait = WebDriverWait(driver, 30)


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
    print("Starting login function...")

    driver.execute_script("""
        var event = new MouseEvent('mousemove', {
            'view': window,
            'bubbles': true,
            'cancelable': true
        });
        document.dispatchEvent(event);
    """)
    
    time.sleep(1)

    # Fill Username
    user_name_input = wait.until(ec.visibility_of_element_located((By.NAME, '_UserName')))
    user_name_input.clear()
    user_name_input.send_keys(USER_NAME)
    print("Username filled.")

    # Fill Password
    password_input = wait.until(ec.visibility_of_element_located((By.NAME, '_Password')))
    password_input.clear()
    password_input.send_keys(PASSWORD)
    print("Password filled.")

    time.sleep(1)

    # Click submit via JavaScript to avoid overlay interference
    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    driver.execute_script("arguments[0].click();", login_button)
    print("Login button clicked via JS.")

    # Wait for session auth & force-navigate to Home dashboard
    time.sleep(5)
    driver.get("https://s.amizone.net/Home")

    # Catch failure explicitly to guarantee artifacts are saved
    try:
        wait.until(ec.presence_of_element_located((By.ID, 'calendar')))
        print("Logged in successfully. Calendar found.")
    except TimeoutException:
        print("❌ Calendar not found. Saving debug files...")
        driver.save_screenshot("debug_failure.png")
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"Current Page URL: {driver.current_url}")
        print(f"Current Page Title: {driver.title}")
        raise

    # driver.execute_script("""
    #     var modals = document.querySelectorAll('.modal, .modal-backdrop, [class*="popup"], [id*="popup"], div[style*="z-index"]');
    #     for (var i = 0; i < modals.length; i++) {
    #         modals[i].remove();
    #     }
    # """)

    # time.sleep(2)


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
try:
    calendar = wait.until(ec.presence_of_element_located((By.ID, 'calendar')))
except TimeoutException:
    # Take a screenshot to inspect what the browser is actually seeing
    driver.save_screenshot("debug_failure.png")

    # Save the current page HTML
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    print(f"Current Page URL: {driver.current_url}")
    print(f"Current Page Title: {driver.title}")
    raise

# calendar = wait.until(ec.presence_of_element_located((By.ID, 'calendar')))

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
