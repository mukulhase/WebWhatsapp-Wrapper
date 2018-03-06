"""
WebWhatsAPI module

.. moduleauthor:: Mukul Hase <mukulhase@gmail.com>, Adarsh Sanjeev <adarshsanjeev@gmail.com>

"""

import binascii
import logging
from json import dumps, loads

import os
import shutil
import tempfile
from Crypto.Cipher import AES
from axolotl.kdf.hkdfv3 import HKDFv3
from axolotl.util.byteutil import ByteUtil
from base64 import b64decode
from io import BytesIO
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .objects.chat import UserChat, factory_chat
from .objects.contact import Contact
from .objects.message import MessageGroup, factory_message
from .wapi_js_wrapper import WapiJsWrapper

__version__ = '2.0.2'


class WhatsAPIDriverStatus(object):
    Unknown = 'Unknown'
    NoDriver = 'NoDriver'
    NotConnected = 'NotConnected'
    NotLoggedIn = 'NotLoggedIn'
    LoggedIn = 'LoggedIn'


class WhatsAPIException(Exception):
    pass


class ChatNotFoundError(WhatsAPIException):
    pass


class ContactNotFoundError(WhatsAPIException):
    pass


class WhatsAPIDriver(object):
    """
    This is our main driver objects.

        .. note::

           Runs its own instance of selenium

        """
    _PROXY = None

    _URL = "https://web.whatsapp.com"

    _LOCAL_STORAGE_FILE = 'localStorage.json'

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

    logger = logging.getLogger(__name__)
    driver = None

    # Profile points to the Firefox profile for firefox and Chrome cache for chrome
    # Do not alter this
    _profile = None

    def get_local_storage(self):
        return self.driver.execute_script('return window.localStorage;')

    def set_local_storage(self, data):
        self.driver.execute_script(''.join(["window.localStorage.setItem('{}', '{}');".format(k, v)
                                            for k, v in data.items()]))

    def save_firefox_profile(self, remove_old=False):
        "Function to save the firefox profile to the permanant one"
        self.logger.info("Saving profile from %s to %s" % (self._profile.path, self._profile_path))

        if remove_old:
            if os.path.exists(self._profile_path):
                try:
                    shutil.rmtree(self._profile_path)
                except OSError:
                    pass

            shutil.copytree(os.path.join(self._profile.path), self._profile_path,
                            ignore=shutil.ignore_patterns("parent.lock", "lock", ".parentlock"))
        else:
            for item in os.listdir(self._profile.path):
                if item in ["parent.lock", "lock", ".parentlock"]:
                    continue
                s = os.path.join(self._profile.path, item)
                d = os.path.join(self._profile_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d,
                                    ignore=shutil.ignore_patterns("parent.lock", "lock", ".parentlock"))
                else:
                    shutil.copy2(s, d)

        with open(os.path.join(self._profile_path, self._LOCAL_STORAGE_FILE), 'w') as f:
            f.write(dumps(self.get_local_storage()))

    def set_proxy(self, proxy):
        self.logger.info("Setting proxy to %s" % proxy)
        proxy_address, proxy_port = proxy.split(":")
        self._profile.set_preference("network.proxy.type", 1)
        self._profile.set_preference("network.proxy.http", proxy_address)
        self._profile.set_preference("network.proxy.http_port", int(proxy_port))
        self._profile.set_preference("network.proxy.ssl", proxy_address)
        self._profile.set_preference("network.proxy.ssl_port", int(proxy_port))

    def __init__(self, client="firefox", username="API", proxy=None, command_executor=None, loadstyles=False,
                 profile=None, headless=False, autoconnect=True, logger=None, extra_params=None):
        "Initialises the webdriver"

        self.logger = logger or self.logger
        extra_params = extra_params or {}

        if profile is not None:
            self._profile_path = profile
            self.logger.info("Checking for profile at %s" % self._profile_path)
            if not os.path.exists(self._profile_path):
                self.logger.critical("Could not find profile at %s" % profile)
                raise WhatsAPIException("Could not find profile at %s" % profile)
        else:
            self._profile_path = None

        self.client = client.lower()
        if self.client == "firefox":
            if self._profile_path is not None:
                self._profile = webdriver.FirefoxProfile(self._profile_path)
            else:
                self._profile = webdriver.FirefoxProfile()
            if not loadstyles:
                # Disable CSS
                self._profile.set_preference('permissions.default.stylesheet', 2)
                # Disable images
                self._profile.set_preference('permissions.default.image', 2)
                # Disable Flash
                self._profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so',
                                             'false')
            if proxy is not None:
                self.set_proxy(proxy)

            options = Options()

            if headless:
                options.set_headless()

            options.profile = self._profile

            capabilities = DesiredCapabilities.FIREFOX.copy()
            capabilities['webStorageEnabled'] = True

            self.logger.info("Starting webdriver")
            self.driver = webdriver.Firefox(capabilities=capabilities, options=options, **extra_params)

        elif self.client == "chrome":
            self._profile = webdriver.chrome.options.Options()
            if self._profile_path is not None:
                self._profile.add_argument("user-data-dir=%s" % self._profile_path)
            if proxy is not None:
                profile.add_argument('--proxy-server=%s' % proxy)
            self.driver = webdriver.Chrome(chrome_options=self._profile, **extra_params)

        elif client == 'remote':
            capabilities = DesiredCapabilities.FIREFOX.copy()
            self.driver = webdriver.Remote(
                command_executor=command_executor,
                desired_capabilities=capabilities,
                **extra_params
            )

        else:
            self.logger.error("Invalid client: %s" % client)
        self.username = username
        self.wapi_functions = WapiJsWrapper(self.driver)

        self.driver.set_script_timeout(500)
        self.driver.implicitly_wait(10)

        if autoconnect:
            self.connect()

    def connect(self):
        self.driver.get(self._URL)

        local_storage_file = os.path.join(self._profile.path, self._LOCAL_STORAGE_FILE)
        if os.path.exists(local_storage_file):
            with open(local_storage_file) as f:
                self.set_local_storage(loads(f.read()))

            self.driver.refresh()

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
        """
        Fetches all chats

        :return: List of chats
        :rtype: list[Chat]
        """
        return [factory_chat(chat, self) for chat in self.wapi_functions.getAllChats()]

    def get_unread(self, include_me=False, include_notifications=False):
        """
        Fetches unread messages

        :param include_me: Include user's messages
        :type include_me: bool or None
        :param include_notifications: Include events happening on chat
        :type include_notifications: bool or None
        :return: List of unread messages grouped by chats
        :rtype: list[MessageGroup]
        """
        raw_message_groups = self.wapi_functions.getUnreadMessages(include_me, include_notifications)

        unread_messages = []
        for raw_message_group in raw_message_groups:
            chat = factory_chat(raw_message_group, self)
            messages = [factory_message(message, self) for message in raw_message_group['messages']]
            unread_messages.append(MessageGroup(chat, messages))

        return unread_messages

    def get_all_messages_in_chat(self, chat, include_me=False, include_notifications=False):
        """
        Fetches messages in chat

        :param include_me: Include user's messages
        :type include_me: bool or None
        :param include_notifications: Include events happening on chat
        :type include_notifications: bool or None
        :return: List of messages in chat
        :rtype: list[Message]
        """
        message_objs = self.wapi_functions.getAllMessagesInChat(chat.id, include_me, include_notifications)

        messages = []
        for message in message_objs:
            messages.append(factory_message(message, self))

        return messages

    def get_contact_from_id(self, contact_id):
        contact = self.wapi_functions.getContact(contact_id)

        if contact is None:
            raise ContactNotFoundError("Contact {0} not found".format(contact_id))

        return Contact(contact, self)

    def get_chat_from_id(self, chat_id):
        for chat in self.wapi_functions.getAllChats():
            if chat["id"] == chat_id:
                return factory_chat(chat, self)

        raise ChatNotFoundError("Chat {0} not found".format(chat_id))

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
        for chat in self.get_all_chats():
            if not isinstance(chat, UserChat) or number not in chat.id:
                continue
            return chat

        raise ChatNotFoundError('Chat for phone {0} not found'.format(number))

    def reload_qr(self):
        self.driver.find_element_by_css_selector(self._SELECTORS['qrCode']).click()

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

    def contact_get_common_groups(self, contact_id):
        for group in self.wapi_functions.getCommonGroups(contact_id):
            yield factory_chat(group, self)

    def chat_send_message(self, chat_id, message):
        return self.wapi_functions.sendMessage(chat_id, message)

    def chat_get_messages(self, chat_id, include_me=False, include_notifications=False):
        message_objs = self.wapi_functions.getAllMessagesInChat(chat_id, include_me, include_notifications)
        for message in message_objs:
            yield factory_message(message, self)

    def chat_load_earlier_messages(self, chat_id):
        self.wapi_functions.loadEarlierMessages(chat_id)

    def chat_load_all_earlier_messages(self, chat_id):
        self.wapi_functions.loadAllEarlierMessages(chat_id)

    def group_get_participants_ids(self, group_id):
        return self.wapi_functions.getGroupParticipantIDs(group_id)

    def group_get_participants(self, group_id):
        participant_ids = self.group_get_participants_ids(group_id)

        for participant_id in participant_ids:
            yield self.get_contact_from_id(participant_id)

    def group_get_admin_ids(self, group_id):
        return self.wapi_functions.getGroupAdmins(group_id)

    def group_get_admins(self, group_id):
        admin_ids = self.group_get_admin_ids(group_id)

        for admin_id in admin_ids:
            yield self.get_contact_from_id(admin_id)

    def download_file(self, url):
        return b64decode(self.wapi_functions.downloadFile(url))

    def download_media(self, media_msg):
        try:
            if media_msg.content:
                return BytesIO(b64decode(self.content))
        except AttributeError:
            pass

        file_data = self.download_file(media_msg.client_url)

        media_key = b64decode(media_msg.media_key)
        derivative = HKDFv3().deriveSecrets(media_key,
                                            binascii.unhexlify(media_msg.crypt_keys[media_msg.type]),
                                            112)

        parts = ByteUtil.split(derivative, 16, 32)
        iv = parts[0]
        cipher_key = parts[1]
        e_file = file_data[:-10]

        AES.key_size = 128
        cr_obj = AES.new(key=cipher_key, mode=AES.MODE_CBC, IV=iv)

        return BytesIO(cr_obj.decrypt(e_file))

    def quit(self):
        self.driver.quit()
