from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
import time
import os
from bs4 import BeautifulSoup

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
        'UnreadChatlistIden':'.icon-meta',
        'UnreadChatBanner':'.message-list',
    }

    driver = None

    def __init__(self):
        self.driver = webdriver.Firefox()
        "Initialises the browser"
        self.driver.get(self.URL)
        self.driver.implicitly_wait(10)
        while True:
            if len(self.driver.find_elements_by_css_selector(self.SELECTORS['mainPage']))==0:
                self.firstrun()
                continue
            else:
                break
        self.run()

    def firstrun(self):
        "Sends QRCode if not registered"
        print "first run"
        screen = self.driver.save_screenshot('temp.png')
        while True:
            if len(self.driver.find_elements_by_css_selector(self.SELECTORS['mainPage']))==0:
                continue
            else:
                break

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
        self.select_contact(contact, entry)
        self.enter_message(message)
        self.press_send()

    def update_unread(self):
        listelement = self.get_user_list()
        list = listelement.find_elements_by_css_selector(self.SELECTORS['chats'])
        unreadlist =[]
        for contact in reversed(list):
            if len(contact.find_elements_by_css_selector(self.SELECTORS['UnreadChatlistIden']))==0:
                break
            else:
                unreadlist.append(contact)

        ##SCOPE FOR OPTIMISATION IF SINGLE MESSAGE NO NEED TO OPEN CHAT(Unless we have to remove the read
        for chat in unreadlist:
            print chat.text
            #for testing
            #Iterate here

    def read_message(self, contact_element):
        contact_element.click()
        messages_html = self.driver.find_elements_by_css_selector(self.SELECTORS['messageList']).get_attribute('innerHTML')
        soup = BeautifulSoup(messages_html, 'html.parser')
        soup.select('.messageList')

    def run(self):
        pass
