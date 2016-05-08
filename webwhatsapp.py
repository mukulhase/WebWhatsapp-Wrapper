from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
import time
import os
driver = webdriver.Firefox()
url="http://web.whatsapp.com"
selectors = {
    'firstrun':"#wrapper",
    'qrCode':"#window > div.entry-main > div.qrcode > img",
    'mainPage':".app.two",
    'chatList':".infinite-list-viewport",
    'messageList':"#main > div > div:nth-child(1) > div > div.message-list",
    'unreadMessageBar':"#main > div > div:nth-child(1) > div > div.message-list > div.msg-unread"
}
def init():
    driver.get(url)
    driver.implicitly_wait(10)
    while True:
        try:
            time.sleep(1)
            element = driver.find_element_by_css_selector(selectors['mainPage'])
        except:
            firstrun()
            continue
        break
    run()

def firstrun():
    print "first run"
    screen = driver.save_screenshot('temp.png')
    ok = input("waiting")

    pass

def press_send():
    pass

def enter_message():
    pass

def get_user_list():
    pass

def run():
    pass

init()
driver.quit()