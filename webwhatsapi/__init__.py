"""
WhatsAPI module
"""

import datetime
import time
import os
import sys
import logging
import pickle

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WhatsAPIDriver(object):
    _PROXY = None

    _URL = "https://web.whatsapp.com"

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

    logger = logging.getLogger("whatsapi")
    driver = None
    profile = None

    def save_firefox_profile(self):
        "Function to save the firefox profile to the permanant one"
        self.logger.info("Saving profile from %s to %s" % (self.profile.path, self.profile_path))
        os.system("cp -R " + self.profile.path + " "+ self.profile_path)
        cookie_file = os.path.join(self.profile_path, "cookies.pkl")
        pickle.dump(self.driver.get_cookies() , open(cookie_file,"wb"))

    def set_proxy(self, proxy):
        self.logger.info("Setting proxy to %s" % proxy)
        proxy_address, proxy_port = proxy.split(":")
        self.profile.set_preference("network.proxy.type", 1)
        self.profile.set_preference("network.proxy.http", proxy_address)
        self.profile.set_preference("network.proxy.http_port", int(proxy_port))
        self.profile.set_preference("network.proxy.ssl", proxy_address)
        self.profile.set_preference("network.proxy.ssl_port", int(proxy_port))

    def __init__(self, browser="firefox", username="API", proxy=None):
        "Initialises the webdriver"

        # Get the name of the config folder
        self.config_dir = os.path.join(os.path.expanduser("~"), ".whatsapi")

        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
        except OSError:
            print("Error: Could not create config dir")
            exit(-1)

        self.logger.setLevel(logging.DEBUG)

        # Setting the log message format and log file
        log_file_handler = logging.FileHandler(os.path.join(self.config_dir, "whatsapi.log"))
        log_file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        self.logger.addHandler(log_file_handler)

        self.browser = browser.lower()
        if self.browser == "firefox":
            # TODO: Finish persistant sessions. As of now, persistant sessions do not work for Firefox. You will need to scan each time.
            self.profile_path = os.path.join(self.config_dir, "profile")
            self.logger.info("Checking for profile at %s" % self.profile_path)
            if not os.path.exists(self.profile_path):
                self.logger.info("Profile not found. Creating profile")
                self.profile = webdriver.FirefoxProfile()
                self.save_firefox_profile()
            else:
                self.logger.info("Profile found")
                self.profile = webdriver.FirefoxProfile(self.profile_path)

            if proxy is not None:
                self.set_proxy(proxy)
            self.logger.info("Starting webdriver")
            self.driver = webdriver.Firefox(self.profile)
        elif self.browser == "chrome":
            self.profile = webdriver.chrome.options.Options()
            self.profile_path = os.path.join(self.config_dir, 'chrome_cache')
            self.profile.add_argument("user-data-dir=%s" % self.profile_path)
            if proxy is not None:
                profile.add_argument('--proxy-server=%s' % proxy)
            self.driver = webdriver.Chrome(chrome_options=self.profile)
        else:
            logger.error("Invalid browser: %s" % browser)
            print("Only firefox and chrome work as browser")
        self.username = username
        self.driver.get(self._URL)
        self.driver.implicitly_wait(10)

    def firstrun(self):
        "Saves QRCode and waits for it to go away"
        if "Click to reload QR code" in self.driver.page_source:
            self.reloadQRCode()
        qr = self.driver.find_element_by_css_selector(self._SELECTORS['qrCode'])
        qr.screenshot(self.username + '.png')
        WebDriverWait(self.driver, 30).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, self._SELECTORS['qrCode'])))
        # logger.debug("QR just scanned")

    def view_unread(self):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/get_unread_messages.js"), "r").read()
        Store = self.driver.execute_script(script)
        return Store

    def send_to_whatsapp_id(self, id, message):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/send_message_to_whatsapp_id.js"), "r").read()
        success = self.driver.execute_script(script, id, message)
        return success

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
        success = self.driver.execute_script(script, pno, message)
        return success

    def get_groups(self):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/get_groups.js"), "r").read()
        success = self.driver.execute_script(script)
        return success

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.__unicode__()

    def reload_QR(self):
        self.driver.find_element_by_css_selector(self._SELECTORS['qrCode']).click()

    def create_callback(self, callback_function):
        try:
            while True:
                messages = self.view_unread()
                if messages != []:
                    callback_function(messages)
                time.sleep(5)
        except KeyboardInterrupt:
            logger.debug("Exited")
