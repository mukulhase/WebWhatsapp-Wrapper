from selenium import webdriver
from dateutil.parser import *

import selenium
from selenium.webdriver.common.by import By
import time
import os
from bs4 import BeautifulSoup
import datetime

URL="http://web.whatsapp.com"
SELECTORS = {
    'firstrun':"#wrapper",
    'qrCode':"#window > div.entry-main > div.qrcode > img",
    'mainPage':".app.two",
    'chatList':".infinite-list-viewport",
    'messageList':"#main > div > div:nth-child(1) > div > div.message-list",
    'unreadMessageBar':"#main > div > div:nth-child(1) > div > div.message-list > div.msg-unread",
    'searchBar':"#side > div.search-container > div > label > input",
    'searchCancel':".icon-search-morph",
    'chats':".infinite-list-item",
    'chatBar':'div.input',
    'sendButton':'button.icon:nth-child(3)',
    'LoadHistory':'.btn-more',
    'UnreadChatlistIden':'.icon-meta',
    'UnreadChatBanner':'.message-list',
}

driver = webdriver.Firefox()

def init():
    "Initialises the browser"
    driver.get(URL)
    driver.implicitly_wait(10)
    while True:
        if len(driver.find_elements_by_css_selector(SELECTORS['mainPage']))==0:
            firstrun()
            continue
        else:
            break
    run()

def firstrun():
    "Sends QRCode if not registered"
    print "first run"
    screen = driver.save_screenshot('temp.png')
    while True:
        if len(driver.find_elements_by_css_selector(SELECTORS['mainPage']))==0:
            continue
        else:
            break

def press_send():
    "Presses the send button"
    driver.find_element_by_css_selector(SELECTORS['sendButton']).click()

def enter_message(message):
    "Enters the message onto the chat bar"
    driver.find_element_by_css_selector(SELECTORS['chatBar']).send_keys(message)

def select_contact(contact, entry = None):
    """
    Searches for the contact, as either name or number. If multiple exists, returns the
    'entry'th contact. If entry is not sent, return all the rows.
    """

    # Focusing before sending keys solves many problems
    driver.find_element_by_css_selector(SELECTORS['searchBar']).click()

    element = driver.find_element_by_css_selector(SELECTORS['searchBar']).send_keys(contact)
    time.sleep(1)

    try:
        result = get_user_list()
    except NoSuchElementException:
        return False

    # To get the most recent chat first, we reverse it
    contacts = result.find_elements_by_css_selector(SELECTORS['chats'])[::-1]
    time.sleep(1)

    if len(contacts) == 1:
        result.find_elements_by_css_selector(SELECTORS['chats'])[0].click()
    elif entry is None:
        driver.find_element_by_css_selector(SELECTORS['searchCancel']).click()
        return contacts
    else:
        contacts[entry].click()
    return True

def get_user_list():
    element = driver.find_element_by_css_selector(SELECTORS['chatList'])
    return element

def send_message(contact, message):
    select_contact(contact)
    enter_message(message)
    press_send()

def check_unread(contact):
    html = contact.get_attribute('innerHTML')
    return 'icon-meta' in html

def update_unread():
    listelement = get_user_list()
    list = listelement.find_elements_by_css_selector(SELECTORS['chats'])
    unreadlist =[]
    for contact in list:
        if check_unread(contact):
            unreadlist.append(contact)

    messages=[]
    ##SCOPE FOR OPTIMISATION IF SINGLE MESSAGE NO NEED TO OPEN CHAT(Unless we have to remove the read
    for contact in unreadlist:
        contact_name=contact.text.split("\n")
        msg={}
        msg["contact"]=contact_name
        msg["message"]=read_message(contact)
        messages.append(msg)
        #for testing
        #Iterate here

    return messages



def read_message(contact_element):
    contact_element.click()
    messages_html = driver.find_element_by_css_selector(SELECTORS['messageList']).get_attribute('innerHTML')
    soup = BeautifulSoup("<html>"+messages_html+"</html>", 'html.parser')
    message_list = soup.find_all("div",class_="msg")
    messages=[]
    for message in message_list:
        msg = {}
        ##print(message.text)
        message_content = message.find_all(class_="message-text")
        if len(message_content)!=0:
            text = message_content[0].text
            separated = "".join(text.split(u"\u2060")).split(u"\xa0")
            msg["timestamp"] = parse(separated[0][1:-1])
            msg["contact"] = separated[1]
            msg["text"] = separated[2]
            messages.append(msg)
    return messages

def run():
    pass

init()
print update_unread()
driver.close()