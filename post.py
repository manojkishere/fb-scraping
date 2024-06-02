from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup, Tag
from typing import List
from utils import find_nested
from time import sleep
from datetime import datetime

TIME_PARENT_XPATH = "//div[@role='article']/div/div/div/div[1]/div/div[13]/div/div/div[2]/div/div[2]//div[2]/span/span"
TIME_TOOLTIP_XPATH = "//div[@role='tooltip']//span"
POST_CONTAINER_SELECTOR = "//div[@role='main'][@aria-label='Group content']"
COMMENTS_XPATH = "//div[@role='button']/span[contains(text(), 'comment')]"
SHARES_XPATH = "//div[@role='button']/span[contains(text(), 'share')]"
ARTICLE_SELECTOR = "div[role='article']"
TOOLBAR_SELECTOR = "span[role='toolbar']"
REACTIONS_TABLIST_SELECTOR = "div[role='tablist']"
MORE_COMMENTS_XPATH = "//div[@role='button']//span[text()='View more comments']"
VIEW_REPLIES_XPATH = "//div[@role='button']//span[starts-with(text(), 'View all') and contains(text(), 'replies')]/../.."
VIEW_REPLY_XPATH = "//div[@role='button']//span[starts-with(text(), 'View') and contains(text(), 'reply')]/../.."
NAVIGATION_BAR_XPATH = "div[role='banner']"
GROUP_BAR_XPATH = "div[class='x9f619 x1ja2u2z x1xzczws x7wzq59']"
COMMENT_PARENT_XPATH = "//div[@class='x1y1aw1k xn6708d xwib8y2 x1ye3gou']"
COMMENT_AUTHOR_XPATH = ".//span[@class='x3nfvp2']/span"
COMMENT_TEXT_XPATH = ".//div[@class='xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs']/div"
PROFILE_PIC_XPATH = "//*[@role='img' and not(@aria-label='Your profile')]"
DIALOG_SELECTOR = "div[role='dialog']"
COMMENTS_ORDER_PARENT_XPATH = "//div[@role='button' and @class='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1n2onr6 x87ps6o x1lku1pv x1a2a7pz']"
ALL_COMMENTS_XPATH = "//div[@role='menu']//div[@role='menuitem'][3]"

def get_post_html(browser: WebDriver):
    try:
        return browser.find_element(By.XPATH, POST_CONTAINER_SELECTOR).find_element(By.CSS_SELECTOR, ARTICLE_SELECTOR).get_attribute("innerHTML")
    except Exception as e:
        return f"Failed to fetch the post: {e}"

def get_post_parent(post_soup: BeautifulSoup):
    post_grandparents: List[Tag] = find_nested(post_soup.select_one("body"), 5).find_all(recursive=False)
    
    post_grandparent: Tag = None

    for post_gp in post_grandparents:
        if not post_gp.get("class"):
            if len(post_gp.find_all(recursive=False)) != 0:
                post_grandparent = post_gp.find(recursive=False)

    return post_grandparent.find(recursive=False)

def get_comments_no(browser: WebDriver):
    try:
        print("Extracting comments...")
        return browser.find_element(By.XPATH, COMMENTS_XPATH).text.split(" ")[0]
    except:
        return None
    
def get_shares_no(browser: WebDriver):
    try:
        print("Extracting shares...")
        return browser.find_element(By.XPATH, SHARES_XPATH).text.split(" ")[0]
    except:
        return None

def get_date(browser: WebDriver):
    print("Extracting date...")
    
    try:
        time_parent = browser.find_element(By.XPATH, TIME_PARENT_XPATH)
        time_hover = time_parent.find_element(By.XPATH, './/a[@role="link"]')
    except:
        return None

    actions = ActionChains(driver=browser)

    actions.click_and_hold(time_hover).perform()
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, TIME_TOOLTIP_XPATH)))
    try:
        time = browser.find_element(By.XPATH, TIME_TOOLTIP_XPATH).text.strip().split(" at ")[0].strip()
        date_obj = datetime.strptime(time, "%A %d %B %Y")
        formatted_date_str = date_obj.strftime("%d-%m-%Y")
        return formatted_date_str
    except:
        return None

def get_reactions(browser: WebDriver):
    print("Extracting reactions...")
    try:
        return browser.find_element(By.CSS_SELECTOR, TOOLBAR_SELECTOR).find_element(By.XPATH, "../div/span/div/span[2]/span/span").text
    except:
        return None

def get_author(profile_parent: Tag):
    print("Extracting author...")
    try:
        return profile_parent.find(recursive=False).select_one("strong").find(recursive=False).text
    except:
        return None

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

def get_comments(browser: WebDriver):
    browser.implicitly_wait(3)
    print("Extracting comments...")
    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located, ((By.XPATH, COMMENTS_ORDER_PARENT_XPATH)))
        browser.find_element(By.XPATH, COMMENTS_ORDER_PARENT_XPATH).click()
        WebDriverWait(browser, 10).until(EC.presence_of_element_located, ((By.XPATH, ALL_COMMENTS_XPATH)))
        browser.find_element(By.XPATH, ALL_COMMENTS_XPATH).click()
    except:
        pass
    try:
        more_comments_btn = browser.find_element(By.XPATH, MORE_COMMENTS_XPATH)
        more_comments_btn.click()
    except:
        pass
    try:
        comments = []
        no_replies_left(browser=browser)
        see_more_btns = browser.find_elements(By.XPATH, "//div[@role='button' and text()='See more']")
        for btn in see_more_btns:
            browser.execute_script("arguments[0].scrollIntoView(false)", btn)
            btn.click()
        comments_parents = browser.find_elements(By.XPATH, COMMENT_PARENT_XPATH)
        for comment in comments_parents:
            try:
                browser.execute_script("arguments[0].scrollIntoView(false)", comment)
                sleep(0.5)
                author = comment.find_element(By.XPATH, COMMENT_AUTHOR_XPATH).text.strip()
                text = comment.find_element(By.XPATH, COMMENT_TEXT_XPATH).text.strip()
                if text:
                    comments.append(f"{author} - {text}")
            except:
                continue
        return comments
    except Exception as e:
        print(e)
        return []
    
def no_replies_left(browser: WebDriver):
    view_replies_btns = browser.find_elements(By.XPATH, VIEW_REPLIES_XPATH)
    view_reply_btns = browser.find_elements(By.XPATH, VIEW_REPLY_XPATH)
    browser.implicitly_wait(2)
    for btn in view_replies_btns:
        browser.execute_script("arguments[0].scrollIntoView(false)", btn)
        sleep(0.3)
        btn.click()
    for btn in view_reply_btns:
        browser.execute_script("arguments[0].scrollIntoView(false);", btn)
        sleep(0.3)
        btn.click()

    if len(view_reply_btns) == 0 and len(view_replies_btns) == 0:
        return True
    else:
        sleep(2)
        return no_replies_left(browser)

def scrape_post(browser: WebDriver, post: str):
    print(f"Loading post: {post}")
    browser.get(post)

    sleep(2)

    css_rules = """
    div[role='dialog'] {
        display: none;
    }
    div[role='banner'] {
        display: none;
    }
    div[class='x9f619 x1ja2u2z x1xzczws x7wzq59'] {
        display: none;
    }
    """.replace('\n', '\\n').replace('"', '\\"').replace("'", "\\'")

    script = f"""
    var style = document.createElement('style');
    style.type = 'text/css';
    style.appendChild(document.createTextNode("{css_rules}"));
    document.head.appendChild(style);
    """

    try:
        browser.execute_script(script)
    except:
        print("Couldn't inject CSS...")
        pass

    post_soup = BeautifulSoup(get_post_html(browser=browser), features="lxml")
    
    try:
        post_parent = get_post_parent(post_soup)
    except:
        try:
            post_parent = get_post_parent(post_soup)
        except:
            return None
        
    try:
        profile_parent: Tag = post_parent.find_all(recursive=False)[1]
        content_parent: Tag = post_parent.find_all(recursive=False)[2]
    except:
        return {}

    content = get_content(content_parent)
    author = get_author(profile_parent)
    date = get_date(browser)
    comments_no = get_comments_no(browser)
    shares_no = get_shares_no(browser)
    reactions = get_reactions(browser)
    comments = get_comments(browser)

    data = {
        "date": date,
        "author": author,
        "text": content["text"],
        "image": content["pictures"],
        "shares_no": shares_no,
        "comments_no": comments_no,
        "reactions": reactions,
        "comments": comments,
        "url": post,
    }

    browser.get("about:blank")
            
    return data