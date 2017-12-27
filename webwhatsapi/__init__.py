"""
WhatsAPI module
"""


from __future__ import print_function

import sys
import datetime
import time
import os
import sys
import logging
import pickle
import tempfile

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException


class WhatsAPIDriverStatus(object):
    Unknown = 'Unknown'
    NoDriver = 'NoDriver'
    NotConnected = 'NotConnected'
    NotLoggedIn = 'NotLoggedIn'
    LoggedIn = 'LoggedIn'

from consts import Selectors, URL
from objects.chat import Chat, GroupChat, UserChat
from objects.contact import Contact
from objects.message import Message, MessageGroup
from webwhatsapi.wapi_js_wrapper import WapiJsWrapper

if __debug__:
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

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

    # Profile points to the Firefox profile for firefox and Chrome cache for chrome
    # Do not alter this
    _profile = None

    def save_firefox_profile(self):
        "Function to save the firefox profile to the permanant one"
        self.logger.info("Saving profile from %s to %s" % (self._profile.path, self._profile_path))
        os.system("cp -R " + self._profile.path + " "+ self._profile_path)
        cookie_file = os.path.join(self._profile_path, "cookies.pkl")
        if self.driver:
            pickle.dump(self.driver.get_cookies() , open(cookie_file,"wb"))

    def set_proxy(self, proxy):
        self.logger.info("Setting proxy to %s" % proxy)
        proxy_address, proxy_port = proxy.split(":")
        self._profile.set_preference("network.proxy.type", 1)
        self._profile.set_preference("network.proxy.http", proxy_address)
        self._profile.set_preference("network.proxy.http_port", int(proxy_port))
        self._profile.set_preference("network.proxy.ssl", proxy_address)
        self._profile.set_preference("network.proxy.ssl_port", int(proxy_port))

    def __init__(self, client="firefox", username="API", proxy=None, command_executor=None, loadstyles=False, profile=None):
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

        if profile is not None:
            self._profile_path = profile
            self.logger.info("Checking for profile at %s" % self._profile_path)
            if not os.path.exists(self._profile_path):
                print("Could not find profile at %s" % profile)
                self.logger.error("Could not find profile at %s" % profile)
                exit(-1)
        else:
            self._profile_path = None

        self.client = client.lower()
        if self.client == "firefox":
            if self._profile_path is not None:
                self._profile = webdriver.FirefoxProfile(self._profile_path)
            else:
                self._profile = webdriver.FirefoxProfile()
            if loadstyles == False:
                # Disable CSS
                self._profile.set_preference('permissions.default.stylesheet', 2)
                ## Disable images
                self._profile.set_preference('permissions.default.image', 2)
                ## Disable Flash
                self._profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                              'false')
            if proxy is not None:
                self.set_proxy(proxy)
            self.logger.info("Starting webdriver")
            self.driver = webdriver.Firefox(self._profile)

        elif self.client == "chrome":
            self._profile = webdriver.chrome.options.Options()
            if self._profile_path is not None:
                self._profile.add_argument("user-data-dir=%s" % self._profile_path)
            if proxy is not None:
                profile.add_argument('--proxy-server=%s' % proxy)
            self.driver = webdriver.Chrome(chrome_options=self._profile)

        elif client == 'remote':
            capabilities = DesiredCapabilities.FIREFOX.copy()
            self.driver = webdriver.Remote(
                command_executor=command_executor,
                desired_capabilities=capabilities
            )

        else:
            self.logger.error("Invalid client: %s" % client)
            print("Enter a valid client name")
        self.username = username
        self.wapi_functions = WapiJsWrapper(self.driver)

        self.driver.set_script_timeout(5)
        self.driver.implicitly_wait(10)
        self.driver.get(self._URL)

    def wait_for_login(self):
        """Waits for the QR to go away"""
        WebDriverWait(self.driver, 90).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self._SELECTORS['mainPage']))
        )

    def get_qr(self):
        """Get pairing QR code from client"""
        if "Click to reload QR code" in self.driver.page_source:
            self.reload_qr()
        qr = self.driver.find_element_by_css_selector(self._SELECTORS['qrCode'])
        fd, fn_png = tempfile.mkstemp(prefix=self.username, suffix='.png')
        self.logger.debug("QRcode image saved at %s" % fn_png)
        print(fn_png)
        qr.screenshot(fn_png)
        os.close(fd)
        return fn_png

    def screenshot(self, filename):
        self.driver.get_screenshot_as_file(filename)

    def get_contacts(self):
        """
        Fetches list of all contacts

        This will return chats with people from the address book only
        Use get_all_chats for all chats

        :return: List of contacts
        :rtype: list[Chat]
        """
        all_contacts = self.wapi_functions.getAllContacts()
        return [Contact(contact, self) for contact in all_contacts]

    def get_all_chats(self):
        return [Chat(chat, self) for chat in self.wapi_functions.getAllChats()]

    def reset_unread(self):
        """
        Resets unread messages list
        """
        self.driver.execute_script("window.WAPI.lastRead = {}")

    def get_unread(self, include_me=False, include_notifications=False):
        """
        Fetches unread messages

        :return: List of unread messages grouped by chats
        :rtype: list[MessageGroup]
        """
        raw_message_groups = self.wapi_functions.getUnreadMessages(include_me, include_notifications)

        unread_messages = []
        for raw_message_group in raw_message_groups:
            chat = Chat(raw_message_group)
            messages = [Message(message) for message in raw_message_group["messages"]]
            unread_messages.append(MessageGroup(chat, messages))

        for message in unread_messages:
            message.chat.driver = self

        return unread_messages

    def get_all_messages_in_chat(self, chat, include_me=False, include_notifications=False):
        message_objs = self.wapi_functions.getAllMessagesInChat(chat.id, include_me, include_notifications)

        messages = []
        for message in message_objs:
            messages.append(Message(message))

        return messages

    def get_contact_from_id(self, contact_id):
        contact = self.wapi_functions.getContact(contact_id)

        assert contact, "Contact {0} not found".format(contact_id)

        return Contact(contact)

    def get_chat_from_id(self, chat_id):
        chats = filter(
            lambda chat: chat["id"] == chat_id,
            self.wapi_functions.getAllChats()
        )

        assert len(chats) == 1, "Chat {0} not found".format(chat_id)

        return Chat(chats[0], self)

    def get_chat_from_phone_number(self, number):
        """
        Gets chat by phone number

        Number format should be as it appears in Whatsapp ID
        For example, for the number:
            +972-51-234-5678
        This function would receive:
            972512345678

        :param number: Phone number
        :return: Chat
        :rtype: Chat
        """
        chats = filter(lambda chat:(type(chat) is UserChat), self.get_all_chats())
        return next((contact for contact in chats if (number in contact.id)), None)

    def reload_qr(self):
        self.driver.find_element_by_css_selector(self._SELECTORS['qrCode']).click()

    def create_callback(self, callback_function):
        try:
            while True:
                messages = self.get_unread()
                if messages:
                    callback_function(messages)
                time.sleep(5)
        except KeyboardInterrupt:
            self.logger.debug("Exited")

    def get_status(self):
        if self.driver is None:
            return WhatsAPIDriverStatus.NotConnected
        if self.driver.session_id is None:
            return WhatsAPIDriverStatus.NotConnected
        try:
            self.driver.find_element_by_css_selector(self._SELECTORS['mainPage'])
            return WhatsAPIDriverStatus.LoggedIn
        except NoSuchElementException:
            pass
        try:
            self.driver.find_element_by_css_selector(self._SELECTORS['qrCode'])
            return WhatsAPIDriverStatus.NotLoggedIn
        except NoSuchElementException:
            pass
        return WhatsAPIDriverStatus.Unknown
