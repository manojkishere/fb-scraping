from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import get_link
import time
import json

start_time = time.time()

FEED_XPATH = "//div[@role='feed']"
TIME_PARENT_XPATH = ".//div[@role='article']/div/div/div/div/div/div[13]/div/div/div[2]/div/div[2]//div[2]/span/span//a"

def scrape_n_posts(browser: WebDriver, feed: str, n: int, batch_size: int):
    browser.get(feed)
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, FEED_XPATH)))
    feed_el = browser.find_element(By.XPATH, FEED_XPATH)

    post_class = feed_el.find_elements(By.XPATH, "*")[1].get_attribute("class").strip()

    links_count = 0
    links = []

    while links_count < n:
        all_posts = feed_el.find_elements(By.XPATH, f"*[@class='{post_class}']")
        
        if len(all_posts) > 0:
            post = all_posts[0]
            print(f"Interacting with post {links_count + 1}...")
            
            try:
                links.append(get_link(browser, post, TIME_PARENT_XPATH).split("?")[0])
                links_count += 1
            except NoSuchElementException as e:
                try:
                    print(f"Couldn't find the link, trying again...")
                    time.sleep(0.5)
                    links.append(get_link(browser, post, TIME_PARENT_XPATH).split("?")[0])
                    links_count += 1
                except:
                    print(f"Couldn't get the link, skipping...")
            except:
                print(f"Couldn't get the link, skipping...")

            finally:
                browser.execute_script("arguments[0].remove();", post)
                browser.execute_script("""
                    let images = document.getElementsByTagName('img');
                    for (let i = 0; i < images.length; i++) {
                        images[i].parentNode.removeChild(images[i]);
                    }
                    let iframes = document.getElementsByTagName('iframe');
                    for (let i = 0; i < iframes.length; i++) {
                        iframes[i].parentNode.removeChild(iframes[i]);
                    }
                """)
                all_posts = feed_el.find_elements(By.XPATH, f"*[@class='{post_class}']")
                if links_count % batch_size == 0:
                    print(f"Saving batch of {batch_size} links...")
                    with open(f"links_{links_count}.json", "w") as file:
                        json.dump(links, file, indent=4)
                    links.clear()
        else:
            try:
                ban_dialog = browser.find_element(By.XPATH, "//div[@role='dialog']")
                ok_btn = ban_dialog.find_element(By.XPATH, ".//div[@role='button']")
                ok_btn.click()
            except:
                print("No more posts to interact with. Waiting for more posts to load...")
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                all_posts = feed_el.find_elements(By.XPATH, f"*[@class='{post_class}']")

    print("--- %s seconds ---" % (time.time() - start_time))
    browser.quit()