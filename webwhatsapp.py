from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
import time
import os

URL="http://web.whatsapp.com"
SELECTORS = {
    'firstrun':"#wrapper",
    'qrCode':"#window > div.entry-main > div.qrcode > img",
    'mainPage':".app.two",
    'chatList':".infinite-list-viewport",
    'messageList':"#main > div > div:nth-child(1) > div > div.message-list",
    'unreadMessageBar':"#main > div > div:nth-child(1) > div > div.message-list > div.msg-unread",
    'searchBar':"#side > div.search-container > div > label > input",
    'chats':".infinite-list-item"
}
driver = webdriver.Firefox()

def init():
    driver.get(URL)
    driver.implicitly_wait(10)
    while True:
        try:
            time.sleep(1)
            element = driver.find_element_by_css_selector(SELECTORS['mainPage'])
        except:
            firstrun()
            continue
        break
    run()

def firstrun():
    print "first run"
    screen = driver.save_screenshot('temp.png')
    ok = input("waiting")

def press_send():
    pass

def enter_message():
    pass

def select_contact(contact):
    element = driver.find_element_by_css_selector(SELECTORS['searchBar']).send_keys(contact)
    time.sleep(1)
    result = get_user_list()
    print result.find_elements_by_css_selector(SELECTORS['chats'])
    if len(result.find_elements_by_css_selector(SELECTORS['chats']))>0:
        result.find_elements_by_css_selector(SELECTORS['chats'])[0].click()
        pass


def get_user_list():
    element = driver.find_element_by_css_selector(SELECTORS['chatList'])
    return element

def run():
    pass

init()
if __name__ == "__main__":
    time.sleep(1)
    get_user_list()
    time.sleep(1)
    select_contact("9704170702")
