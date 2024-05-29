from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup, Tag
from typing import List
from utils import prefix_str, find_nested
from time import sleep
import re

TIME_PARENT_XPATH = "//div[@role='article']/div/div/div/div[1]/div/div[13]/div/div/div[2]/div/div[2]//div[2]/span/span"
TIME_TOOLTIP_XPATH = "//div[@role='tooltip']//span"
POST_CONTAINER_SELECTOR = "//div[@role='main'][@aria-label='Group content']"
COMMENTS_XPATH = "//div[@role='button']/span[contains(text(), 'comment')]"
SHARES_XPATH = "//div[@role='button']/span[contains(text(), 'share')]"
ARTICLE_SELECTOR = "div[role='article']"
TOOLBAR_SELECTOR = "span[role='toolbar']"
REACTIONS_TABLIST_SELECTOR = "div[role='tablist']"

def get_post_html(browser: WebDriver):
    try:
        return browser.find_element(By.XPATH, POST_CONTAINER_SELECTOR).find_element(By.CSS_SELECTOR, ARTICLE_SELECTOR).get_attribute("innerHTML")
    except Exception as e:
        return f"Failed to fetch the post: {e}"

def get_comments(browser: WebDriver):
    try:
        print("Extracting comments...")
        return browser.find_element(By.XPATH, COMMENTS_XPATH).text.split(" ")[0]
    except:
        return None
    
def get_shares(browser: WebDriver):
    try:
        print("Extracting shares...")
        return browser.find_element(By.XPATH, SHARES_XPATH).text.split(" ")[0]
    except:
        return None

def get_time(browser: WebDriver):
    print("Extracting time...")
    time_parent = browser.find_element(By.XPATH, TIME_PARENT_XPATH)

    try:
        time_hover = time_parent.find_element(By.XPATH, "//span[2]/span/a")
    except:
        time_hover = time_parent.find_element(By.XPATH, "//span[4]/span/a")

    actions = ActionChains(driver=browser)

    actions.move_to_element(time_hover).perform()
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, TIME_TOOLTIP_XPATH)))
    return browser.find_element(By.XPATH, TIME_TOOLTIP_XPATH).text.strip()

def get_reactions(browser: WebDriver):
    print("Extracting reactions...")
    reactions = {}
    try:
        browser.find_element(By.CSS_SELECTOR, TOOLBAR_SELECTOR).click()
    except:
        return reactions
    sleep(2)
    reactions_html = browser.find_elements(By.CSS_SELECTOR, REACTIONS_TABLIST_SELECTOR)[1].get_attribute("innerHTML")
    reactions_soup = BeautifulSoup(reactions_html, features="lxml")
    try:
        reaction_containers: List[Tag] = reactions_soup.select_one("body").find(recursive=False).find_all(recursive=False)[1].find_all(recursive=False)
    except:
        reaction_containers: List[Tag] = reactions_soup.select_one("body").find_all(recursive=False)[1].find_all(recursive=False)
    for reaction_container in reaction_containers:
        reaction = reaction_container.get("aria-label")
        if reaction:
            reactions[reaction.split(',')[0].strip()] = reaction.split(',')[1]
    return reactions

def get_profile(profile_parent: Tag):
    print("Extracting profile...")
    name = profile_parent.find(recursive=False).select_one("strong").find(recursive=False).text
    profile_pic = profile_parent.select_one("g").find(recursive=True).get("xlink:href")
    try:
        profile_url = prefix_str(profile_parent.find(recursive=False).select_one("strong").parent.get("href").split("?")[0], "https://www.facebook.com")
    except:
        profile_url = None
    return {
        "display_name": name,
        "picture": profile_pic,
        "url": profile_url
    }

def get_content(content_parent: Tag):
    is_poster = True if content_parent.find_all(recursive=False)[0].select_one('div[aria-hidden="true"]') else False

    try:
        image_grandparents = content_parent.find_all(recursive=False)[1]
    except:
        image_grandparents = []

    text = ""

    print("Extracting text...")

    if not is_poster:
        try:
            text_grandparents: List[Tag] = find_nested(content_parent.select_one('div[data-ad-comet-preview="message"]'), 3).find_all(recursive=False)
        except:
            text_grandparents: List[Tag] = content_parent.select_one('div[id^=":r"]').parent

        for text_grandparent in text_grandparents:
            text_parents: List[Tag] = text_grandparent.find_all(recursive=False)
            for text_parent in text_parents:
                temp = ""
                text_containers = text_parent.children
                span_containers: List[Tag] = text_parent.find_all(recursive=False)

                i = 0
                for text_container in text_containers:
                    if text_container.text.strip() != "":
                        temp += text_container.text
                    else:
                        try:
                            alt = span_containers[i].find(recursive=False).get("alt")
                            temp += alt
                            print(temp)
                        except:
                            try:
                                temp += span_containers[i].find(recursive=True).text
                            except:
                                pass
                        i += 1
                temp += "\n"
                text += temp
    else:
        text = find_nested(content_parent, 4).find_all(recursive=False)[1].find(recursive=False).find(recursive=False).text
        
    pictures = []

    print("Extracting images...")
            
    for image_grandparent in image_grandparents:
        images: List[Tag] = image_grandparent.find_all('img')
        for image in images:
            pictures.append(image.get("src"))

    return {
        "text": text,
        "pictures": pictures
    }

def scrape_post(browser: WebDriver, post: str):
    print("Loading post...")
    browser.get(post)
    WebDriverWait(driver=browser, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ARTICLE_SELECTOR)))
    # sleep(10)

    post_soup = BeautifulSoup(get_post_html(browser=browser), features="lxml")
    
    post_grandparents: List[Tag] = find_nested(post_soup.select_one("body"), 5).find_all(recursive=False)
    
    post_grandparent: Tag = None

    for post_gp in post_grandparents:
        if not post_gp.get("class"):
            if len(post_gp.find_all(recursive=False)) != 0:
                post_grandparent = post_gp.find(recursive=False)

    post_parent = post_grandparent.find(recursive=False)

    profile_parent: Tag = post_parent.find_all(recursive=False)[1]
    content_parent: Tag = post_parent.find_all(recursive=False)[2]
    
    content = get_content(content_parent)
    profile = get_profile(profile_parent)
    time = get_time(browser)
    comments = get_comments(browser)
    shares = get_shares(browser)
    reactions = get_reactions(browser)


    data = {
        "post": {
            "text": content["text"],
            "pictures": content["pictures"],
            "time": time,
            "reactions": reactions,
            "url": post,
            "comments": comments,
            "shares": shares
        },
        "user": {
            "display_name": profile["display_name"],
            "profile_url": profile["url"],
            "display_picture": profile["picture"]
        }

    }
            
    return data