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


# ------------------------ CHROME SETUP ------------------------

options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

options.add_experimental_option(
    "prefs",
    {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
)

driver = uc.Chrome(options=options, version_main=152)
wait = WebDriverWait(driver, 20)


# ------------------------ LOGIN ------------------------

def login():
    driver.get("https://s.amizone.net/")

    username = wait.until(
        ec.visibility_of_element_located(
            (By.NAME, "_UserName")
        )
    )
    username.send_keys(USER_NAME)

    password = wait.until(
        ec.visibility_of_element_located(
            (By.NAME, "_Password")
        )
    )
    password.send_keys(PASSWORD)

    login_button = wait.until(
        ec.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[type="submit"]')
        )
    )
    login_button.click()

    time.sleep(5)

    print("Current URL:", driver.current_url)

    # Save debug files if login does not work
    driver.save_screenshot("after_login.png")

    with open("after_login.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)


# ------------------------ GET TIMETABLE ------------------------

def get_timetable():
    calendar = wait.until(
        ec.presence_of_element_located(
            (By.ID, "calendar")
        )
    )

    try:
        date = calendar.find_element(
            By.CSS_SELECTOR,
            "div.fc-center h2"
        ).text
    except:
        date = dt.today().strftime("%d %B %Y")

    try:
        day = calendar.find_element(
            By.CSS_SELECTOR,
            "span.fc-list-heading-main"
        ).text
    except:
        day = dt.today().strftime("%A")

    timetable = []

    rows = calendar.find_elements(
        By.CSS_SELECTOR,
        "tr[class^='fc-list-item']"
    )

    for row in rows:
        try:
            class_time = row.find_element(
                By.CSS_SELECTOR,
                "td.fc-list-item-time"
            ).text

            class_name = row.find_element(
                By.CSS_SELECTOR,
                "td.fc-list-item-title > a"
            ).text

            timetable.append(
                f"⏰ {class_time}\n{class_name}\n"
            )

        except:
            continue

    return date, day, timetable


# ------------------------ SEND TELEGRAM MESSAGE ------------------------

def send_message(date, day, timetable):
    message = (
        f"DATE: {date}\n"
        f"DAY: {day}\n"
        f"📆 Today's TimeTable 📆\n\n"
    )

    if not timetable:
        message += "💤 Stay in Bed, it's off today 🛌"

    else:
        message += "\n".join(timetable)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )

    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print("Telegram error:", response.text)


# ------------------------ MAIN ------------------------

try:
    login()
    date, day, timetable = get_timetable()
    send_message(date, day, timetable)

finally:
    driver.quit()
