"""
WhatsAPI module
"""


from __future__ import print_function

import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from consts import Selectors, URL
from objects.chat import Chat, GroupChat, UserChat
# def get_groups(self):
#     try:
#         script_path = os.path.dirname(os.path.abspath(__file__))
#     except NameError:
#         script_path = os.getcwd()
#     script = open(os.path.join(script_path, "js_scripts/get_groups.js"), "r").read()
#     success = self.driver.execute_script(script)
#     return success
# =======
from objects.contact import Contact
from objects.message import Message, MessageGroup
from webwhatsapi.wapi_js_wrapper import WapiJsWrapper

import pprint
pp = pprint.PrettyPrinter(indent=4)

# <<<<<<< HEAD:webwhatsapi/__init__.py
# class WhatsAPIDriver(object):
#     _PROXY = None
#
#     _URL = "http://web.whatsapp.com"
#
#     _SELECTORS = {
#         'firstrun': "#wrapper",
#         'qrCode': "img[alt=\"Scan me!\"]",
#         'mainPage': ".app.two",
#         'chatList': ".infinite-list-viewport",
#         'messageList': "#main > div > div:nth-child(1) > div > div.message-list",
#         'unreadMessageBar': "#main > div > div:nth-child(1) > div > div.message-list > div.msg-unread",
#         'searchBar': ".input",
#         'searchCancel': ".icon-search-morph",
#         'chats': ".infinite-list-item",
#         'chatBar': 'div.input',
#         'sendButton': 'button.icon:nth-child(3)',
#         'LoadHistory': '.btn-more',
#         'UnreadBadge': '.icon-meta',
#         'UnreadChatBanner': '.message-list',
#         'ReconnectLink': '.action',
#         'WhatsappQrIcon': 'span.icon:nth-child(2)',
#         'QRReloader': '.qr-wrapper-container'
#     }
#
#     _CLASSES = {
#         'unreadBadge': 'icon-meta',
#         'messageContent': "message-text",
#         'messageList': "msg"
#     }
#
#     driver = None
# def __init__(self, browser='firefox', username="API"):
#     "Initialises the browser"
#     ## Proxy support not currently working
#     # env_proxy = {
#     #     'proxyType': ProxyType.MANUAL,
#     #     'httpProxy': os.environ.get("http_proxy"),
#     #     'httpsProxy': os.environ.get("https_proxy"),
#     #     'ftpProxy': os.environ.get("ftp_proxy"),
#     # }
#     # self._PROXY = Proxy(env_proxy)
#     if browser.lower() == 'firefox':
#         self.driver = webdriver.Firefox()  # trying to add proxy support: webdriver.FirefoxProfile().set_proxy()) #self._PROXY))
#     if browser.lower() == 'chrome':
#         self.chrome_options = Options()
#         self.chrome_options.add_argument("user-data-dir=" + os.path.dirname(sys.argv[0]) + 'chrome_cache' + '/' +  username )
#         self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
#
#     self.username = username
#     self.driver.get(self._URL)
#     self.driver.implicitly_wait(10)
# def firstrun(self):
#     "Saves QRCode and waits for it to go away"
#     if "Click to reload QR code" in self.driver.page_source:
#         self.reloadQRCode()
#     qr = self.driver.find_element_by_css_selector(self._SELECTORS['qrCode'])
#     qr.screenshot(self.username + '.png')
#     WebDriverWait(self.driver, 30).until(
#         EC.invisibility_of_element_located((By.CSS_SELECTOR, self._SELECTORS['qrCode'])))
# def view_unread(self):
#     try:
#         script_path = os.path.dirname(os.path.abspath(__file__))
#     except NameError:
#         script_path = os.getcwd()
#     script = open(os.path.join(script_path, "js_scripts/get_unread_messages.js"), "r").read()
#     Store = self.driver.execute_script(script)
#     return Store
#
# def send_to_whatsapp_id(self, id, message):
#     try:
#         script_path = os.path.dirname(os.path.abspath(__file__))
#     except NameError:
#         script_path = os.getcwd()
#     script = open(os.path.join(script_path, "js_scripts/send_message_to_whatsapp_id.js"), "r").read()
#     success = self.driver.execute_script(script, id, message)
#     return success
# def send_to_contact(self, id, message):
#     return success
# def get_id_from_number(self, name):
#     try:
#         script_path = os.path.dirname(os.path.abspath(__file__))
#     except NameError:
#         script_path = os.getcwd()
#     script = open(os.path.join(script_path, "js_scripts/id_from_name.js"), "r").read()
#     id = self.driver.execute_script(script, name)
#     return id
#
# def send_to_phone_number(self, pno, message):
#     try:
#         script_path = os.path.dirname(os.path.abspath(__file__))
#     except NameError:
#         script_path = os.getcwd()
#     script = open(os.path.join(script_path, "js_scripts/send_message_to_phone_number.js"), "r").read()
#     success = self.driver.execute_script(script, pno, message)
#     return success


class WhatsAPIDriver(object):
    def __init__(self, browser="firefox", username="API", loadstyles=False):
        self.username = username
        self.browser_type = browser

        if self.browser_type.lower() == "firefox":
            self.path = os.path.join(os.getcwd(), "firefox_cache", self.username)

            if not os.path.exists(self.path):
                os.makedirs(self.path)
            self._firefox_profile = webdriver.FirefoxProfile(self.path)
            if loadstyles == False:
                ## Disable CSS
                self._firefox_profile.set_preference('permissions.default.stylesheet', 2)
                ## Disable images
                self._firefox_profile.set_preference('permissions.default.image', 2)
                ## Disable Flash
                self._firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                              'false')
            self._driver = webdriver.Firefox(self._firefox_profile)

        if self.browser_type.lower() == "chrome":
            self._chrome_options = Options()
            self._chrome_options.add_argument(
                "user-data-dir=" + os.path.join(os.getcwd(), "chrome_cache", self.username))
            self._driver = webdriver.Chrome(chrome_options=self._chrome_options)

        self.wapi_functions = WapiJsWrapper(self._driver)

        # Open page
        self._driver.get(URL)
        self._driver.implicitly_wait(10)

        self._driver.set_script_timeout(5)

        WebDriverWait(self._driver, 30).until(
            ec.invisibility_of_element_located((By.CSS_SELECTOR, Selectors.QR_CODE)))

    def first_run(self):
        if "Click to reload QR code" in self._driver.page_source:
            self._reload_qr_code()
        qr = self._driver.find_element_by_css_selector(Selectors.QR_CODE)
        qr.screenshot(self.username + ".png")
        WebDriverWait(self._driver, 30).until(
            ec.invisibility_of_element_located((By.CSS_SELECTOR, Selectors.QR_CODE)))

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
        self._driver.execute_script("window.WAPI.lastRead = {}")

    def get_unread(self):
        """
        Fetches unread messages

        :return: List of unread messages grouped by chats
        :rtype: list[MessageGroup]
        """
        raw_message_groups = self.wapi_functions.getUnreadMessages()

        unread_messages = []
        for raw_message_group in raw_message_groups:
            chat = Chat(raw_message_group)
            pp.pprint(raw_message_group)
            messages = [Message(message) for message in raw_message_group["messages"]]
            unread_messages.append(MessageGroup(chat, messages))

        return unread_messages

    def get_all_messages_in_chat(self, chat, include_me=False):
        message_objs = self.wapi_functions.getAllMessagesInChat(chat.id, include_me)

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
        chats = filter(lambda chat: not chat.is_group, self.get_all_chats())
# >>>>>>> f1373c928cbb1d6c2af4652efdd2b8f04ecc4795:webwhatsapp.py

        return next((contact for contact in chats if contact.id.startswith(number)), None)

    def _reload_qr_code(self):
        self._driver.find_element_by_css_selector(Selectors.QR_RELOADER).click()

    def create_callback(self, callback_function):
        try:
            while True:
                messages = self.get_unread()
                if messages:
                    callback_function(messages)
                time.sleep(5)
        except KeyboardInterrupt:
            print("Exited")
