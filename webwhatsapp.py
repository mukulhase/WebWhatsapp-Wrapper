import time
import os
from selenium import webdriver
from dateutil.parser import *
import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType

class WhatsAPIDriver(object):

    _PROXY = None

    _URL = "http://web.whatsapp.com"
    _SELECTORS = {
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
        'UnreadChatBanner':'.message-list',
        'ReconnectLink':'.action',
        'WhatsappQrIcon':'span.icon:nth-child(2)',
        'QRReloader':'.qr-container',
    }
    _CLASSES = {
        'unreadBadge':'icon-meta',
        'messageContent':"message-text",
        'messageList':"msg"
    }

    driver = None

    def __init__(self, username="API"):
        "Initialises the browser"
        env_proxy = {
            'proxyType': ProxyType.MANUAL,
            'httpProxy': os.environ.get("http_proxy"),
            'httpsProxy': os.environ.get("https_proxy"),
            'ftpProxy': os.environ.get("ftp_proxy"),
        }
        self._PROXY = Proxy(env_proxy)
        self.driver = webdriver.Firefox(proxy=self._PROXY)
        self.username = username
        self.driver.get(self._URL)
        self.driver.implicitly_wait(10)

    def firstrun(self):
        "Sends QRCode if not registered"
        while True:
            try:
                if "CLICK TO RELOAD QR" in self.driver.page_source:
                    self.reloadQRCode()
                WebDriverWait(self.driver, 30).until(\
                    EC.presence_of_element_located((By.CSS_SELECTOR, self._SELECTORS['WhatsappQrIcon'])))
                self.driver.save_screenshot('WhatsAPI/media/%s.png' %(self.username))
                time.sleep(10)
            except:
                break



    def _press_send(self):
        "Presses the send button"
        self.driver.find_element_by_css_selector(self._SELECTORS['sendButton']).click()

    def _enter_message(self, message):
        "Enters the message onto the chat bar"
        chatbar = self.driver.find_element_by_css_selector(self._SELECTORS['chatBar'])
        chatbar.click()
        chatbar.send_keys(message)

    def select_contact(self, contact, entry=None):
        """
        Searches for the contact, as either name or number. If multiple exists, returns the
        'entry'th contact. If entry is not sent, return all the rows.
        """

        # Focusing before sending keys solves many problems
        searchbar = self.driver.find_element_by_css_selector(self._SELECTORS['searchBar'])
        searchbar.click()
        searchbar.send_keys(" ")
        self.driver.find_element_by_css_selector(self._SELECTORS['searchCancel']).click()

        searchbar.click()
        searchbar.send_keys(contact)
        time.sleep(2)
        # WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, self._SELECTORS['searchCancel'])))
        try:
            result = self.get_user_list()
        except NoSuchElementException:
            return False

        # To get the most recent chat first, we reverse it
        contacts = result.find_elements_by_css_selector(self._SELECTORS['chats'])

        for i, a in enumerate(contacts):
            if a.text == "MESSAGES":
                contacts = contacts[:i]
                break

        contact_list = []
        for i, a in enumerate(contacts):
            if a.text == "CHATS" or a.text == "GROUPS" or a.text == "CONTACTS":
                contacts.pop(i)
            else:
                contact_list += [a.text]
        # time.sleep(2)

        if len(contacts) == 1:
            result.find_elements_by_css_selector(self._SELECTORS['chats'])[0].click()
        elif entry is None:
            self.driver.find_element_by_css_selector(self._SELECTORS['searchCancel']).click()
            return contact_list
        else:
            try:
                contacts[entry].click()
            except IndexError:
                return False
        return True

    def get_user_list(self):
        element = self.driver.find_element_by_css_selector(self._SELECTORS['chatList'])
        return element

    def send(self, contact, message, entry=None):
        val = self.select_contact(contact, entry)
        if val != True:
            return val
        self._enter_message(message)
        self._press_send()
        return True

    def view_unread(self):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "script.js"), "r").read()
        Store = self.driver.execute_script(script)
        return Store

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.__unicode__()

    def reloadQRCode(self):
        self.driver.find_element_by_css_selector(self._SELECTORS['QRReloader']).click()

    def contact_from_number(self, pno):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "contactfromnumber.js"), "r").read()
        script += "return getContactName(\"%d\");" %(pno)
        return self.driver.execute_script(script)

    def send_to_number(self, pno, message):
        contact = self.contact_from_number(pno)
        name = contact[1]
        id = contact[0]
        send_to_id(contact[0], contact[1], message)

    def send_to_id(self, id, name, message):
        index = 0
        found = False
        #optimisation, check if window is already open
        try:
            element = self.driver.find_element_by_class_name(self._CLASSES['messageContent'])
            if id in element.get_attribute('data-id'):
                found = True
        except:
            pass

        while not found:
            if self.select_contact(name, index):
                try:
                    element = self.driver.find_element_by_class_name(self._CLASSES['messageContent'])
                except:
                    index += 1
                    continue
                if id in element.get_attribute('data-id'):
                    found = True
            else:
                break

            index += 1
        if found:
            self._enter_message(message)
            self._press_send()
            return True
        return False

    def create_callback(self, callback_function):
        try:
            while True:
                messages = view_unread()
                if messages != []:
                    callback_function(messages)
                time.sleep(5)
        except KeyboardInterrupt:
            pass
