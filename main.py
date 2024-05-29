import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils import login, load_cookies
from post import scrape_post
from feed import scrape_n_posts
from prettyprinter import cpprint

LOGIN_EMAIL = "cuzbackupneeded@gmail.com"
LOGIN_PASS = "@facebook42#"

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument('--disable-application-cache')
options.add_argument('--disable-gpu')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--disable-images")
options.add_experimental_option(
    "prefs", {"profile.default_content_setting_values.notifications": 2}
)

browser = webdriver.Chrome(options=options)

if not os.path.exists("cookies.pkl"):
    login(browser=browser, email=LOGIN_EMAIL, password=LOGIN_PASS)

load_cookies(browser=browser)

# cpprint(scrape_post(browser=browser, post='https://www.facebook.com/groups/303210285034512/permalink/824321939590008/'))
scrape_n_posts(browser=browser, feed="https://www.facebook.com/groups/303210285034512/?sorting_setting=CHRONOLOGICAL", n=100)