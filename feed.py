from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from time import sleep
import tkinter as tk
from post import scrape_post
from typing import List
import json
import gc

FEED_XPATH = "//div[@role='feed']"
TIME_PARENT_XPATH = ".//div[@role='article']/div/div/div/div[1]/div/div[13]/div/div/div[2]/div/div[2]//div[2]/span/span"
TIME_TOOLTIP_XPATH = "//div[@role='tooltip']//span"
SHARE_BTN_XPATH = ".//div[13]/div/div/div[4]/div/div/div/div/div[2]/div/div[3]/div"
COPY_LINK_BTN_XPATH = "//div[@role='dialog']//span[text()='Copy link']"

def scrape_n_posts(browser: WebDriver, feed: str, n: int, batch_size: int = 100):
    root = tk.Tk()
    root.withdraw()
    browser.get(feed)

    feed_el = browser.find_element(By.XPATH, FEED_XPATH)

    post_class = feed_el.find_elements(By.XPATH, "*")[1].get_attribute("class").strip()

    links_count = 0
    posts_count = 0
    links: List[str] = []
    posts_to_delete = []
    posts_deleted = 0

    while links_count < n:
        all_posts = feed_el.find_elements(By.XPATH, f"*[@class='{post_class}']")
        
        if posts_count < len(all_posts):
            post = all_posts[posts_count]
            print(f"Interacting with post {links_count + 1}...")
            
            try:
                time_parent = post.find_element(By.XPATH, TIME_PARENT_XPATH)

                time_hover = time_parent.find_element(By.XPATH, './/a[@role="link"]')

                actions = ActionChains(driver=browser)
                actions.click_and_hold(time_hover).perform()
                print(time_hover.get_attribute("href"))
                links.append(time_hover.get_attribute("href").split("?")[0])
                links_count += 1
            except Exception as e:
                print(f"Error interacting with post {posts_count}: {e}")

            finally:
                posts_to_delete.append(post)
                posts_count += 1
                if (len(posts_to_delete) >= 5):
                    for post in posts_to_delete:
                        browser.execute_script("arguments[0].remove();", post)
                    posts_deleted += 5
                    posts_to_delete.clear()
                    feed_el = browser.find_element(By.XPATH, FEED_XPATH)
                    all_posts = feed_el.find_elements(By.XPATH, f"*[@class='{post_class}']")
                    posts_count -= 5 
                sleep(1)

                if links_count % batch_size == 0:
                    print(f"Saving batch of {batch_size} links...")
                    with open(f"links_{links_count}.json", "w") as file:
                        json.dump(links, file, indent=4)
                    links.clear()
                    gc.collect()
        else:
            print("No more posts to interact with. Waiting for more posts to load...")
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(3)
            all_posts = feed_el.find_elements(By.XPATH, f"*[@class='{post_class}']")

        sleep(2)

    print(f"Finished interacting with {links_count} posts.")
    print("Saving the last batch of links.")
    with open(f"links_{links_count}.json", "w") as file:
        json.dump(links, file, indent=4)
    links.clear()
    print("Extracting their info...")
    data = []
    for link in links:
        print(f"Extracting from post {links.index(link) + 1}")
        data.append(scrape_post(browser=browser, post=link))
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

    