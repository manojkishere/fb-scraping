import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils import login, load_cookies
from feed import scrape_n_posts
from post import scrape_post
from data import scrape_from_links, posts_to_excel
from prettyprinter import cpprint

LOGIN_EMAIL = "dimpdevi503@gmail.com"
LOGIN_PASS = "@facebook42#"

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
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

# cpprint(scrape_post(browser, "https://www.facebook.com/groups/303210285034512/posts/822272676461601/"))
# scrape_n_posts(browser=browser, feed="https://www.facebook.com/groups/303210285034512/?sorting_setting=CHRONOLOGICAL", n=1000, batch_size=50)
# scrape_from_links(browser, 50)
posts_to_excel()