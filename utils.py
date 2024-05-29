import pickle
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from bs4 import Tag

def login(browser: WebDriver, email: str, password: str):
    browser.get("https://www.facebook.com/login")
    browser.find_element(By.CSS_SELECTOR, "input#email").send_keys(email)
    browser.find_element(By.CSS_SELECTOR, "input#pass").send_keys(password)
    browser.find_element(By.CSS_SELECTOR, "button#loginbutton").click()
    pickle.dump(browser.get_cookies(), open("cookies.pkl", "wb"))

def load_cookies(browser: WebDriver):
    browser.get("https://www.facebook.com/")
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)

def prefix_str(string: str, prefix: str):
    return prefix + string

def find_nested(element: Tag, depth: int):
    current_element = element
    for _ in range(depth):
        current_element = current_element.find(recursive=False)
    return current_element