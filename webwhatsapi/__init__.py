"""
WhatsAPI module
"""


from __future__ import print_function

import datetime
import time
import os
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class WhatsAPIDriver(object):
    _PROXY = None

    _URL = "http://web.whatsapp.com"

    _SELECTORS = {
        'firstrun': "#wrapper",
        'qrCode': "img[alt=\"Scan me!\"]",
        'mainPage': ".app.two",
        'chatList': ".infinite-list-viewport",
        'messageList': "#main > div > div:nth-child(1) > div > div.message-list",
        'unreadMessageBar': "#main > div > div:nth-child(1) > div > div.message-list > div.msg-unread",
        'searchBar': ".input",
        'searchCancel': ".icon-search-morph",
        'chats': ".infinite-list-item",
        'chatBar': 'div.input',
        'sendButton': 'button.icon:nth-child(3)',
        'LoadHistory': '.btn-more',
        'UnreadBadge': '.icon-meta',
        'UnreadChatBanner': '.message-list',
        'ReconnectLink': '.action',
        'WhatsappQrIcon': 'span.icon:nth-child(2)',
        'QRReloader': '.qr-wrapper-container'
    }

    _CLASSES = {
        'unreadBadge': 'icon-meta',
        'messageContent': "message-text",
        'messageList': "msg"
    }

    driver = None

    def __init__(self, browser='firefox', driver_executable_path = None, username="API"):
        "Initialises the browser"
        self.username = username
        self.browser_type = browser
        self.driver_executable_path = driver_executable_path

        ## Proxy support not currently working
        # env_proxy = {
        #     'proxyType': ProxyType.MANUAL,
        #     'httpProxy': os.environ.get("http_proxy"),
        #     'httpsProxy': os.environ.get("https_proxy"),
        #     'ftpProxy': os.environ.get("ftp_proxy"),
        # }
        # self._PROXY = Proxy(env_proxy)
        if browser.lower() == 'firefox':
            # from https://github.com/siddhant-varma/WhatsAPI/blob/master/webwhatsapi/__init__.py
            self.path = os.path.join(os.path.dirname(sys.argv[0]), "firefox_cache", self.username)
            
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            
            self._firefox_profile = webdriver.FirefoxProfile(self.path)
            self._driver = webdriver.Firefox(self._firefox_profile)  # trying to add proxy support: webdriver.FirefoxProfile().set_proxy()) #self._PROXY))
            
        if browser.lower() == 'chrome':
            self._chrome_options = Options()
            self._chrome_options.add_argument(
                "user-data-dir=" + os.path.join(os.path.dirname(sys.argv[0]), "chrome_cache", self.username))
            if driver_executable_path:
                self._driver = webdriver.Chrome(self.driver_executable_path, chrome_options=self._chrome_options)
            else:
                self._driver = webdriver.Chrome(chrome_options=self._chrome_options)

        self._driver.get(self._URL)
        self._driver.implicitly_wait(10)

    def firstrun(self):
        "Saves QRCode and waits for it to go away"
        if "Click to reload QR code" in self._driver.page_source:
            self.reloadQRCode()
        qr = self._driver.find_element_by_css_selector(self._SELECTORS['qrCode'])
        qr.screenshot(self.username + '.png')
        WebDriverWait(self._driver, 30).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, self._SELECTORS['qrCode'])))

    def view_unread(self):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/get_unread_messages.js"), "r").read()
        Store = self._driver.execute_script(script)
        return Store

    def send_to_whatsapp_id(self, id, message):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/send_message_to_whatsapp_id.js"), "r").read()
        success = self._driver.execute_script(script, id, message)
        return success

    # def send_to_contact(self, id, message):
    #     return success

    def get_id_from_number(self, name):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/id_from_name.js"), "r").read()
        id = self.driver.execute_script(script, name)
        return id

    def send_to_phone_number(self, pno, message):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/send_message_to_phone_number.js"), "r").read()
        success = self._driver.execute_script(script, pno, message)
        return success

    def get_groups(self):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/get_groups.js"), "r").read()
        success = self._driver.execute_script(script)
        return success

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.__unicode__()

    def reloadQRCode(self):
        self._driver.find_element_by_css_selector(self._SELECTORS['QRReloader']).click()

    def create_callback(self, callback_function):
        try:
            while True:
                messages = self.view_unread()
                if messages != []:
                    callback_function(messages)
                time.sleep(5)
        except KeyboardInterrupt:
            print("Exited")
