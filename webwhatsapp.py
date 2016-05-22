from selenium import webdriver
from dateutil.parser import *
import time
import os
from bs4 import BeautifulSoup
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WhatsAPIDriver():
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
        'UnreadBadge':'.icon-meta',
    }
    CLASSES = {
        'unreadBadge':'icon-meta',
        'messageContent':"message-text",
        'messageList':"msg"
    }

    driver = None

    def __init__(self):
        "Initialises the browser"
        self.driver = webdriver.Firefox()
        self.driver.get(self.URL)
        self.driver.implicitly_wait(10)

    def firstrun(self):
        "Sends QRCode if not registered"
        WebDriverWait(self.driver, 30).until(\
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['WhatsappQrIcon'])))
        print "NOT WAITING NOW"
        screen = self.driver.save_screenshot('media/%s.png' %(self.username))

    def press_send(self):
        "Presses the send button"
        self.driver.find_element_by_css_selector(self.SELECTORS['sendButton']).click()

    def enter_message(self, message):
        "Enters the message onto the chat bar"
        self.driver.find_element_by_css_selector(self.SELECTORS['chatBar']).send_keys(message)

    def select_contact(self, contact, entry = None):
        """
        Searches for the contact, as either name or number. If multiple exists, returns the
        'entry'th contact. If entry is not sent, return all the rows.
        """

        # Focusing before sending keys solves many problems
        self.driver.find_element_by_css_selector(self.SELECTORS['searchBar']).click()

        element = self.driver.find_element_by_css_selector(self.SELECTORS['searchBar']).send_keys(contact)
        time.sleep(1)

        try:
            result = self.get_user_list()
        except NoSuchElementException:
            return False

        # To get the most recent chat first, we reverse it
        contacts = result.find_elements_by_css_selector(self.SELECTORS['chats'])[::-1]
        time.sleep(1)

        if len(contacts) == 1:
            result.find_elements_by_css_selector(self.SELECTORS['chats'])[0].click()
        elif entry is None:
            self.driver.find_element_by_css_selector(self.SELECTORS['searchCancel']).click()
            return contacts
        else:
            contacts[entry].click()
        return True

    def get_user_list(self):
        element = self.driver.find_element_by_css_selector(self.SELECTORS['chatList'])
        return element

    def send_message(self, contact, message, entry=None):
        val = self.select_contact(contact, entry)
        if val != True:
            return val
        self.enter_message(message)
        self.press_send()

    def check_unread(self,contact):
        ##more reliable unread check -> store timestamps
        ##to use combination of both, timestamp and badge
        html = contact.get_attribute('innerHTML')
        return CLASSES["unreadBadge"] in html

    def update_unread(self):
        listelement = self.get_user_list()
        list = listelement.find_elements_by_css_selector(SELECTORS['chats'])
        unreadlist =[]
        for contact in list:
            if check_unread(contact):
                unreadlist.append(contact)

        messages=[]
        ##SCOPE FOR OPTIMISATION IF SINGLE MESSAGE NO NEED TO OPEN CHAT(Unless we have to remove the read)
        for contact in unreadlist:
            contact_name=contact.text.split("\n")
            msg={}
            msg["contact"]=contact_name
            msg["messages"]=read_message(contact)
            messages.append(msg)
            #Iterate here

        return messages

    def read_message(contact_element):
        contact_element.click()
        messages_html = self.driver.find_element_by_css_selector(SELECTORS['messageList']).get_attribute('innerHTML')
        soup = BeautifulSoup("<html>"+messages_html+"</html>", 'html.parser')
        message_list = soup.find_all("div",class_=CLASSES["messageList"])
        messages=[]
        for message in message_list:
            msg = {}
            message_content = message.find_all(class_=CLASSES["messageContent"])
            if len(message_content)!=0:
                ##need to add group message support
                text = message_content[0].text
                separated = "".join(text.split(u"\u2060")).split(u"\xa0")
                msg["timestamp"] = parse(separated[0][1:-1])
                msg["contact"] = separated[1][:-1]
                msg["text"] = separated[2]
                messages.append(msg)
        return messages

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.__unicode__()

    def run(self):
        pass
