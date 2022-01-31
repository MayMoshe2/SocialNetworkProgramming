from ast import Or
from asyncio.windows_events import NULL
from tarfile import NUL
import chromedriver_binary
import time
import logging
import sys
import os
import re
from dataclasses import dataclass
from typing import Dict, Set
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
import chromedriver_binary
import winsound
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# מאי !!! ככה מדפיסים את השם הייחודי של המשתמש שאותו נרצה למחוק !!!
# logger.info('First param:'+sys.argv[1]+'#')

logger = logging.getLogger("bot")


def set_chrome_options(headless: bool = False) -> None:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    if headless is True:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options  # testing credentials (blame asher)


@dataclass
class User:
    name: str
    email: str
    password: str

class WithdrawConnectionsTracker:
    def __init__(self, filename):
        self.filename = filename
        self.already_sent = set()
        self.update_withdrawConnections_users()

    def update_withdrawConnections_users(self):
        with open(self.filename) as f:
            user_full_names = [user_full_name.strip() for user_full_name in f]
        self.already_sent.update(user_full_names)

    def get_withdrawConnections_users(self) -> Set:
        return self.already_sent

    def add_user_to_withdrawConnections_list(self, full_name: str):
        if full_name not in self.already_sent:
            self.already_sent.add(full_name)
            with open(self.filename, "a") as f:
                f.write(f"{full_name}\n")

    def already_withdrawConnections(self, full_name) -> bool:
        return full_name in self.already_sent

def get_email_and_password():
    # g = open("data/users.json")
    # f = open("data/detailsFromUser.json")
    # data = json.load(f)
    # users = json.load(g)
    cred = credentials.Certificate(
        "socialnetworksbots-firebase-adminsdk-ckg7j-0ed2aef80b.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    emp_ref = db.collection('users')
    docs = emp_ref.stream()

    pointer = sys.argv[1]
    for doc in docs:
        value = int(doc.get('value'))
        # logger.info(value)
        # logger.info(id_user)
        if value == pointer:
            email = doc.get('username')
            password = doc.get('password')
        else:
            logger.info("No success")

    # email = users[pointer]["userName"]
    # password = users[pointer]["password"]
    return email, password


def setup(driver, fullscreen=False):
    # go to linkedin
    driver.get(
        "https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")
    if fullscreen is True:
        driver.maximize_window()
    else:
        driver.set_window_size(1920, 1080)

    # waits for some time
    driver.implicitly_wait(40)
    return driver


def login(driver, email, password):
    # enter phone/email
    email_element = driver.find_element_by_xpath("//*[@id='username']")
    email_element.send_keys(email)

    # enter password
    password_element = driver.find_element_by_xpath("//*[@id='password']")
    password_element.send_keys(password)
    time.sleep(1)

    # Submits credentials
    driver.find_element_by_xpath(
        "//*[@id='organic-div']/form/div[3]/button").click()

    time.sleep(2)
    driver.implicitly_wait(5)


def apply_filter(driver, user_filter):
    # goes to search page and applies filter
    driver.get(user_filter)


def prompt_user():
    email, password, numOfConnections, startFrom = get_email_and_password()
    return email, password, numOfConnections, startFrom


def initialize_linkedin():
    email, password, numOfConnections, startFrom = prompt_user()
    user_filter = "https://www.linkedin.com/mynetwork/invitation-manager/sent/"

    driver = webdriver.Chrome(options=set_chrome_options())
    setup(driver, fullscreen=True)
    login(driver, email=email, password=password)
    logger.info("logged in")
    apply_filter(driver, user_filter=user_filter)
    return driver, user_filter, numOfConnections, startFrom


def initialize_logger():
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handlers = [logging.StreamHandler(
        sys.stdout), logging.FileHandler(filename=f"logs/output.log")]
    for handler in handlers:
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def main():
    withdrawConnections_tracker_filename = os.path.join("logs", "withdrawConnections_tracker.csv")
    print("withdrawConnections_tracker_filename: withdrawConnections_tracker_filename:",
          withdrawConnections_tracker_filename)
    initialize_logger()
    driver, user_filter, numOfConnections, startFrom = initialize_linkedin()
    time.sleep(4)
    xpathWelcome = """//section/p[text()="No sent invitations"]"""
    if driver.find_element_by_xpath(xpathWelcome) != None:
        logger.info("There are no people you can withdraw")
        return

    try:
        element_list_container = driver.find_element_by_xpath(
            "//*/section/div[2]/ul")
        numberOfPeople = element_list_container.find_elements_by_css_selector(
            "li")
    except Exception as exc:
        logger.exception("failed to find buttons", exc_info=exc)

    logger.info(f"Found {len(numberOfPeople)} users on this page")

    try:
        for x in range(1, numberOfPeople):
            time.sleep(2)
            fullName = "//ul/li[1]/div/div[z]/div/a/span[2]"
            fullName = fullName.replace("z", str(x))
            fullName = driver.find_element_by_xpath(fullName) 
            WithdrawConnectionsTracker.add_user_to_withdrawConnections_list(fullName)
            print("im here")
            xpath = "//li[x]//div/button[text()]"
            xpath = xpath.replace("x", str(x))
            driver.find_element_by_xpath(xpath).click()

    except Exception as exc:
        logger.exception("failed", exc_info=exc)
        driver.get_screenshot_as_file("logs/crash.png")
        driver.close()
    logger.info("Done")


if __name__ == "__main__":
    main()
