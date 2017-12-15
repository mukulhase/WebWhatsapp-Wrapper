"""
WhatsAPI module
"""


from __future__ import print_function

import datetime
import time
import os
import sys
import tempfile

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


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

    status = {
        'Unknown' : 'Unknown',
        'NoDriver' : 'NoDriver',
        'NotConnected' : 'NotConnected',
        'NotLoggedIn' : 'NotLoggedIn',
        'LoggedIn' : 'LoggedIn'
    }

    driver = None

    def __init__(self, client='firefox', username="API", command_executor=None):
        "Initialises the client"
        ## Proxy support not currently working
        # env_proxy = {
        #     'proxyType': ProxyType.MANUAL,
        #     'httpProxy': os.environ.get("http_proxy"),
        #     'httpsProxy': os.environ.get("https_proxy"),
        #     'ftpProxy': os.environ.get("ftp_proxy"),
        # }
        # self._PROXY = Proxy(env_proxy)
        if client.lower() == 'firefox':
            self.driver = webdriver.Firefox()  # trying to add proxy support: webdriver.FirefoxProfile().set_proxy()) #self._PROXY))
        elif client.lower() == 'chrome':
            self.chrome_options = Options()
            self.chrome_options.add_argument("user-data-dir=" + os.path.dirname(sys.argv[0]) + 'chrome_cache' + '/' +  username )
            self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        elif client.lower() == 'remote':
            capabilities = DesiredCapabilities.FIREFOX.copy()
            self.driver = webdriver.Remote(
                command_executor=command_executor,
                desired_capabilities=capabilities
            )

        self.username = username
        self.driver.get(self._URL)
        self.driver.implicitly_wait(10)

    def firstrun(self):
        """Saves QRCode and waits for it to go away"""
        self.get_qrcode()
        WebDriverWait(self.driver, 90).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self._SELECTORS['mainPage']))
        )
    
    def get_qrcode(self):
        """Get pairing QR code from browser"""
        if "Click to reload QR code" in self.driver.page_source:
            self.reloadQRCode()
        qr = self.driver.find_element_by_css_selector(self._SELECTORS['qrCode'])
        fd, fn_png = tempfile.mkstemp(prefix=self.username, suffix='.png')
        print( fn_png )
        qr.screenshot(fn_png)
        os.close(fd)
        return fn_png

    def screenshot(self,filename):
        self.driver.get_screenshot_as_file( filename )

    def view_unread(self):
        return self.view_messages(unread_only=True)

    def view_messages(self, unread_only=False):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/get_messages.js"), "r").read()
        Store = self.driver.execute_script(script, unread_only)
        return Store

    def send_to_whatsapp_id(self, id, message):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/send_message_to_whatsapp_id.js"), "r").read()
        success = self.driver.execute_script(script, id, message)
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

    def reloadQRCode(self):
        self.driver.find_element_by_css_selector(self._SELECTORS['QRReloader']).click()

    def create_callback(self, callback_function):
        try:
            while True:
                messages = self.view_unread()
                if messages != []:
                    callback_function(messages)
                time.sleep(5)
        except KeyboardInterrupt:
            print("Exited")

        def get_status(self):
        if self.driver is None:
            return self.status[ 'NotConnected' ]
        if self.driver.session_id is None:
            return self.status[ 'NotConnected' ]
        try:
            self.driver.find_element_by_css_selector(self._SELECTORS['mainPage'])
            return self.status[ 'LoggedIn' ]
        except NoSuchElementException:
            pass
        try:
            self.driver.find_element_by_css_selector(self._SELECTORS['qrCode'])
            return self.status[ 'NotLoggedIn' ]
        except NoSuchElementException:
            pass
        return self.status[ 'Unknown' ]

