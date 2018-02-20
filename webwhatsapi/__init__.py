"""
WhatsAPI module
"""

import logging
import os
import pickle
import tempfile

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class WhatsAPIDriverStatus(object):
    Unknown = 'Unknown'
    NoDriver = 'NoDriver'
    NotConnected = 'NotConnected'
    NotLoggedIn = 'NotLoggedIn'
    LoggedIn = 'LoggedIn'


from .consts import Selectors, URL
from .objects.chat import Chat, GroupChat, UserChat
from .objects.contact import Contact
from .objects.message import Message, MessageGroup
from webwhatsapi.wapi_js_wrapper import WapiJsWrapper

if __debug__:
    import pprint

    pp = pprint.PrettyPrinter(indent=4)


class WhatsAPI(object):
    _PROXY = None

    _URL = "https://web.whatsapp.com"

    _logfile = "whatsapi.log"

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
        'QRReloader': 'div > span > div[role=\"button\"]'
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

    def __init__(self, client="firefox", username="API", proxy=None, command_executor=None,
                 load_styles=False, profile=None):
        self.logger.setLevel(logging.DEBUG)

        # Setting the log message format and log file
        log_file_handler = logging.FileHandler("whatsapi.log")
        log_file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        self.logger.addHandler(log_file_handler)

        self.client = client

        if profile is not None:
            self._profile_path = profile
            self.logger.info("Checking for profile at %s" % self._profile_path)
            if not os.path.exists(self._profile_path):
                self.logger.error("Could not find profile at %s" % profile)
                exit(-1)
        else:
            self._profile_path = None

        if self._profile_path is not None:
            self._profile = webdriver.FirefoxProfile(self._profile_path)
        else:
            self._profile = webdriver.FirefoxProfile()

        if not load_styles:
            # Disable CSS
            self._profile.set_preference('permissions.default.stylesheet', 2)
            # Disable images
            self._profile.set_preference('permissions.default.image', 2)
            # Disable Flash
            self._profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                         'false')

        if self.client == "firefox":
            if proxy is not None:
                self.set_proxy(proxy)
            self.logger.info("Starting webdriver")
            self.driver = webdriver.Firefox(self._profile)
        elif client == 'remote':
            capabilities = DesiredCapabilities.FIREFOX.copy()
            self.driver = webdriver.Remote(browser_profile=self._profile,
                command_executor=command_executor,
                desired_capabilities=capabilities
            )
        else:
            self.logger.error("Invalid client: %s" % client)
            raise NotImplementedError
        self.wapi_functions = WapiJsWrapper(self.driver)

        self.driver.set_script_timeout(500)
        self.driver.implicitly_wait(10)
        self.driver.get(self._URL)

    def save_firefox_profile(self):
        """
        Function to save the firefox profile to the permanant one
        """
        self.logger.info("Saving profile from %s to %s" % (self._profile.path, self._profile_path))
        os.system("cp -R " + self._profile.path + " " + self._profile_path)
        cookie_file = os.path.join(self._profile_path, "cookies.pkl")
        if self.driver:
            pickle.dump(self.driver.get_cookies(), open(cookie_file, "wb"))

    def set_proxy(self, proxy):
        self.logger.info("Setting proxy to %s" % proxy)
        proxy_address, proxy_port = proxy.split(":")
        self._profile.set_preference("network.proxy.type", 1)
        self._profile.set_preference("network.proxy.http", proxy_address)
        self._profile.set_preference("network.proxy.http_port", int(proxy_port))
        self._profile.set_preference("network.proxy.ssl", proxy_address)
        self._profile.set_preference("network.proxy.ssl_port", int(proxy_port))

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
        fd, fn_png = tempfile.mkstemp(suffix='.png')
        self.logger.debug("QRcode image saved at %s" % fn_png)
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
        :rtype: list[Contact]
        """
        all_contacts = self.wapi_functions.getAllContacts()
        return [Contact(contact, self) for contact in all_contacts]

    def get_all_chats(self):
        # type: (Chat ,bool, bool) -> list(Message)
        """
        Fetches all chats

        :return: List of chats
        :rtype: list[Chat]
        """
        return [Chat(chat, self) for chat in self.wapi_functions.getAllChats()]

    # TODO: Check if deprecated
    def reset_unread(self):
        """
        Resets unread messages list
        """
        self.driver.execute_script("window.WAPI.lastRead = {}")

    def get_unread(self, include_me=False, include_notifications=False):
        # type: (bool, bool) -> list(MessageGroup)
        """
        Fetches unread messages

        :return: List of unread messages grouped by chats
        :rtype: list[MessageGroup]
        """
        raw_message_groups = self.wapi_functions.getUnreadMessages(include_me,
                                                                   include_notifications)

        unread_messages = []
        for raw_message_group in raw_message_groups:
            chat = Chat(raw_message_group)
            messages = [Message(message, self) for message in raw_message_group['messages']]
            unread_messages.append(MessageGroup(chat, messages))

        for message in unread_messages:
            message.chat.driver = self

        return unread_messages

    def get_all_messages_in_chat(self, chat, include_me=False, include_notifications=False):
        # type: (Chat ,bool, bool) -> list(Message)
        """
        Fetches messages in chat

        :return: List of messages in chat
        :rtype: list[Message]
        """
        message_objs = self.wapi_functions.getAllMessagesInChat(chat.id, include_me,
                                                                include_notifications)

        messages = []
        for message in message_objs:
            messages.append(Message(message, driver=self))

        return messages

    def get_contact_from_id(self, contact_id):
        contact = self.wapi_functions.getContact(contact_id)

        assert contact, "Contact {0} not found".format(contact_id)

        return Contact(contact, self)

    def get_chat_from_id(self, chat_id):
        chats = [chat for chat in self.wapi_functions.getAllChats() if chat["id"] == chat_id]

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
        chats = [chat for chat in self.get_all_chats() if (type(chat) is UserChat)]
        return next((contact for contact in chats if (number in contact.id)), None)

    def reload_qr(self):
        """
        If the reload button is there, click it to reload
        :return: success true/false
        """
        elem = self.driver.find_element_by_css_selector(self._SELECTORS['qrCode']).click()
        if elem:
            elem.click()
            return True
        return False

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

    def create_chat(self, phone_number):
        """
        Creates a Chat object, that can be retrieved on success
        This object will die if no messages are sent, so be careful :/
        :param phone_number: str phone number, must be a contact
        """
        url = "{base_URL}/send?phone={phone_number}" \
            .format(base_URL=self._URL, phone_number=phone_number)
        self.driver.get(url)

    def first_message(self, phone_number, message):
        """
        Attempt to start a conversation with phone number, then send a message
        :param phone_number: str phone number with country code
        :param message: unicode message to send
        :return: succes bool
        """

        self.create_chat(phone_number)
