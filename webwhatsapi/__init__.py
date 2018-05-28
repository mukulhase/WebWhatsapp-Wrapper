"""
WebWhatsAPI module
.. moduleauthor:: Mukul Hase <mukulhase@gmail.com>, Adarsh Sanjeev <adarshsanjeev@gmail.com>
"""

import binascii

import logging
import os
import tempfile
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from axolotl.kdf.hkdfv3 import HKDFv3
from axolotl.util.byteutil import ByteUtil
from base64 import b64decode
from io import BytesIO
from json import dumps, loads
import shutil
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .objects.chat import Chat, UserChat, factory_chat
from .objects.contact import Contact
from .objects.message import MessageGroup, factory_message, Message
from .wapi_js_wrapper import WapiJsWrapper

__version__ = '2.0.3c'


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
        'qrCodePlain': "._2EZ_m",
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
        'QRReloader': 'div > span > div[role=\"button\"]',
        'not_whatsappable': '._3lLzD'
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
        """Function to save the firefox profile to the permanant one"""
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

    def close(self):
        """Closes the selenium instance"""
        self.driver.close()

    def save_profile(self):
        with open(os.path.join(self._profile_path, self._LOCAL_STORAGE_FILE), 'w') as f:
            f.write(dumps(self.get_local_storage()))

    def load_all_messages(self):
        """
        load all messages into cache
        """
        self.wait_for_login()
        for c in self.get_all_chats():
            try:
                c.load_all_earlier_messages()
            except ChatNotFoundError as e:
                self.logger.debug("chat not found", c)

    def __init__(self, client="firefox", username="API", proxy=None, command_executor=None, loadstyles=False,
                 profile=None, headless=False, autoconnect=True, logger=None, extra_params=None, chrome_options=None):

        self.logger = logger or self.logger
        extra_params = extra_params or {}

        self.client = client

        if profile is not None:
            self._profile_path = profile
            self.logger.info("Checking for profile at %s" % self._profile_path)
            if not os.path.exists(self._profile_path):
                self.logger.critical("Could not find profile at %s" % profile)
                raise WhatsAPIException("Could not find profile at %s" % profile)
        else:
            self._profile_path = None

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

            options = FirefoxOptions()

            if headless:
                options.set_headless()

            options.profile = self._profile

            capabilities = DesiredCapabilities.FIREFOX.copy()
            capabilities['webStorageEnabled'] = True

            self.logger.info("Starting webdriver")
            self.driver = webdriver.Firefox(capabilities=capabilities, options=options,
                                            **extra_params)

        elif self.client == "chrome":

            self._profile = webdriver.chrome.options.Options()
            if self._profile_path is not None:
                self._profile.add_argument("user-data-dir=%s" % self._profile_path)
            if proxy is not None:
                profile.add_argument('--proxy-server=%s' % proxy)
            for option in chrome_options:
                self._profile.add_argument(option)
            self.driver = webdriver.Chrome(chrome_options=self._profile, **extra_params)
        elif client == 'remote_chrome' or client == 'remote_firefox':
            if client == 'remote_firefox':
                options = FirefoxOptions()
            else:
                options = ChromeOptions()


        elif client == 'remote':
            if self._profile_path is not None:
                self._profile = webdriver.FirefoxProfile(self._profile_path)
            else:
                self._profile = webdriver.FirefoxProfile()
            capabilities = DesiredCapabilities.FIREFOX.copy()
            self.driver = webdriver.Remote(
                command_executor=command_executor,
                desired_capabilities=capabilities,
                **extra_params
            )
            options = FirefoxOptions()
            if headless:
                options.set_headless()
            options.profile = self._profile

            self.driver = webdriver.Remote(options=options,
                                           command_executor=command_executor,
                                           **extra_params)
        else:
            self.logger.error("Invalid client: %s" % client)
        self.username = username
        self.wapi_functions = WapiJsWrapper(self.driver)

        self.driver.set_script_timeout(30)
        self.driver.implicitly_wait(10)

        if autoconnect:
            self.connect()

    def connect(self):
        self.driver.get(self._URL)
        local_storage_file = os.path.join(self._profile_path, self._LOCAL_STORAGE_FILE)
        if os.path.exists(local_storage_file):
            with open(local_storage_file) as f:
                self.set_local_storage(loads(f.read()))

            self.driver.refresh()

    def is_logged_in(self):
        """Returns if user is logged. Can be used if non-block needed for wait_for_login"""

        # self.driver.find_element_by_css_selector(self._SELECTORS['mainPage'])
        # it becomes ridiculously slow if the element is not found.

        # instead we use this (temporary) solution:
        return 'class="app _3dqpi two"' in self.driver.page_source

    def wait_for_login(self, timeout=90):
        """Waits for the QR to go away"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self._SELECTORS['mainPage']))
        )

    def get_qr_plain(self):
        return self.driver.find_element_by_css_selector(self._SELECTORS['qrCodePlain']).get_attribute("data-ref")

    def get_qr(self, filename=None):
        """Get pairing QR code from client"""
        if "Click to reload QR code" in self.driver.page_source:
            self.reload_qr()
        qr = self.driver.find_element_by_css_selector(self._SELECTORS['qrCode'])
        if filename is None:
            fd, fn_png = tempfile.mkstemp(prefix=self.username, suffix='.png')
        else:
            fd = os.open(filename, os.O_RDWR | os.O_CREAT)
            fn_png = os.path.abspath(filename)
        self.logger.debug("QRcode image saved at %s" % fn_png)
        qr.screenshot(fn_png)
        os.close(fd)
        return fn_png

    def screenshot(self, filename):
        self.driver.get_screenshot_as_file(filename)

    def get_contacts(self, force_phone_number=True):
        """
        Fetches list of all contacts
        This will return chats with people from the address book only
        Use get_all_chats for all chats

        :return: List of contacts
        :rtype: list[Contact]
        """
        raw_contacts = self.wapi_functions.getAllContacts()
        contacts = [Contact(contact, self) for contact in raw_contacts]
        if force_phone_number:
            contacts = filter(lambda x: hasattr(x, 'phone_number'), contacts)
        return contacts

    def get_my_contacts(self):
        """
        Fetches list of added contacts

        :return: List of contacts
        :rtype: list[Contact]
        """
        my_contacts = self.wapi_functions.getMyContacts()
        return [Contact(contact, self) for contact in my_contacts]

    def get_all_chats(self):
        """
        Fetches all chats

        :return: List of chats
        :rtype: list[Chat]
        """
        return [factory_chat(chat, self) for chat in self.wapi_functions.getAllChats()]

    def get_all_chat_ids(self):
        """
        Fetches all chat ids

        :return: List of chat ids
        :rtype: list[str]
        """
        return self.wapi_functions.getAllChatIds()

    def get_unread(self, include_me=False, include_notifications=False, use_unread_count=False):
        """
        Fetches unread messages
        :param include_me: Include user's messages
        :type include_me: bool or None
        :param include_notifications: Include events happening on chat
        :type include_notifications: bool or None
        :param use_unread_count: If set uses chat's 'unreadCount' attribute to fetch last n messages from chat
        :type use_unread_count: bool
        :return: List of unread messages grouped by chats
        :rtype: list[MessageGroup]
        """
        raw_message_groups = self.wapi_functions.getUnreadMessages(include_me, include_notifications, use_unread_count)


        unread_messages = []
        for raw_message_group in raw_message_groups:
            chat = factory_chat(raw_message_group, self)
            messages = [factory_message(message, self) for message in
                        raw_message_group['messages']]
            unread_messages.append(MessageGroup(chat, messages))

        return unread_messages

    def get_unread_messages_in_chat(self,
                                    id,
                                    include_me=False,
                                    include_notifications=False):
        """
        I fetch unread messages from an asked chat.

        :param id: chat id
        :type  id: str
        :param include_me: if user's messages are to be included
        :type  include_me: bool
        :param include_notifications: if events happening on chat are to be included
        :type  include_notifications: bool
        :return: list of unread messages from asked chat
        :rtype: list
        """
        # get unread messages
        messages = self.wapi_functions.getUnreadMessagesInChat(
            id,
            include_me,
            include_notifications
        )

        # process them
        unread = [factory_message(message, self) for message in messages]

        # return them
        return unread

    # get_unread_messages_in_chat()
    def set_unread(self, include_me=False, include_notifications=False):
        # type: (bool, bool) -> list(MessageGroup)
        """
        sets unread messages

        """
        self.wapi_functions.setUnreadMessages()


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
        message_objs = self.wapi_functions.getAllMessagesInChat(chat.id, include_me,
                                                                include_notifications)

        messages = []
        for message in message_objs:
            yield(factory_message(message, self))

    def get_all_message_ids_in_chat(self, chat, include_me=False, include_notifications=False):
        """
        Fetches message ids in chat

        :param include_me: Include user's messages
        :type include_me: bool or None
        :param include_notifications: Include events happening on chat
        :type include_notifications: bool or None
        :return: List of message ids in chat
        :rtype: list[str]
        """
        return self.wapi_functions.getAllMessageIdsInChat(chat.id, include_me, include_notifications)

    def get_message_by_id(self, message_id):
        """
        Fetch a message

        :param message_id: Message ID
        :type message_id: str
        :return: Message or False
        :rtype: Message
        """
        result = self.wapi_functions.getMessageById(message_id)

        if result:
            result = factory_message(result, self)

        return result

    def get_contact_from_id(self, contact_id):
        """
        Fetches a contact given its ID

        :param contact_id: Contact ID
        :type contact_id: str
        :return: Contact or Error
        :rtype: Contact
        """
        contact = self.wapi_functions.getContact(contact_id)

        if contact is None:
            raise ContactNotFoundError("Contact {0} not found".format(contact_id))

        return Contact(contact, self)

    def get_chat_from_id(self, chat_id):
        """
        Fetches a chat given its ID

        :param chat_id: Chat ID
        :type chat_id: str
        :return: Chat or Error
        :rtype: Chat
        """
        chat = self.wapi_functions.getChatById(chat_id)
        if chat:
            return factory_chat(chat, self)

        raise ChatNotFoundError("Chat {0} not found".format(chat_id))

    def get_chat_from_phone_number(self, number, createIfNotFound = False):
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

        number = number.replace('+', '')
        for chat in self.get_all_chats():
            if not isinstance(chat, UserChat) or number not in chat.id:
                continue
            return chat
        if createIfNotFound:
            self.create_chat_by_number(number)
            self.wait_for_login()
            for chat in self.get_all_chats():
                if not isinstance(chat, UserChat) or number not in chat.id:
                    continue
                return chat

        raise ChatNotFoundError('Chat for phone {0} not found'.format(number))

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
        """
        Returns status of the driver

        :return: Status
        :rtype: WhatsAPIDriverStatus
        """
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
        """
        Returns groups common between a user and the contact with given id.

        :return: Contact or Error
        :rtype: Contact
        """
        for group in self.wapi_functions.getCommonGroups(contact_id):
            yield factory_chat(group, self)

    def chat_send_message(self, chat_id, message):
        result = self.wapi_functions.sendMessage(chat_id, message)
        if not isinstance(result, bool):
            return factory_message(result, self)
        return result

    def chat_reply_message(self, message_id, message):
        result = self.wapi_functions.ReplyMessage(message_id, message)

        if not isinstance(result, bool):
            return factory_message(result, self)
        return result

    def send_message_to_id(self, recipient, message):
        """
        Send a message to a chat given its ID

        :param recipient: Chat ID
        :type recipient: str
        :param message: Plain-text message to be sent.
        :type message: str
        """
        return self.wapi_functions.sendMessageToID(recipient, message)

    def chat_send_seen(self, chat_id):
        """
        Send a seen to a chat given its ID

        :param chat_id: Chat ID
        :type chat_id: str
        """
        return self.wapi_functions.sendSeen(chat_id)

    def chat_get_messages(self, chat_id, include_me=False, include_notifications=False):
        message_objs = self.wapi_functions.getAllMessagesInChat(chat_id, include_me,
                                                                include_notifications)
        for message in message_objs:
            yield factory_message(message, self)


    def chat_load_earlier_messages(self, chat_id):
        self.wapi_functions.loadEarlierMessages(chat_id)

    def get_all_messages_after(self, unix_timestamp, text_only=True):
        """
        load all messages that occurred after unix_timestamp
        :param unix_timestamp: int
        :param text_only: bool, only include text messages
        :return: Message
        """
        raw_messages = self.wapi_functions.getAllMessagesAfter(unix_timestamp)

        messages = []
        for message in raw_messages:
            msg_obj = factory_message(message, self)
            if not text_only:
                messages.append(msg_obj)
            elif type(msg_obj) is Message:
                messages.append(msg_obj)
        return messages

    def chat_load_all_earlier_messages(self, chat_id):
        self.wapi_functions.loadAllEarlierMessages(chat_id)

    def async_chat_load_all_earlier_messages(self, chat_id):
        self.wapi_functions.asyncLoadAllEarlierMessages(chat_id)

    def are_all_messages_loaded(self, chat_id):
        return self.wapi_functions.areAllMessagesLoaded(chat_id)

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
                                            binascii.unhexlify(
                                                media_msg.crypt_keys[media_msg.type]),
                                            112)

        parts = ByteUtil.split(derivative, 16, 32)
        iv = parts[0]
        cipher_key = parts[1]
        e_file = file_data[:-10]

        cr_obj = Cipher(algorithms.AES(cipher_key), modes.CBC(iv), backend=default_backend())
        decryptor = cr_obj.decryptor()
        return BytesIO(decryptor.update(e_file) + decryptor.finalize())

    def mark_default_unread_messages(self):
        """
        Look for the latest unreplied messages received and mark them as unread.

        """
        self.wapi_functions.markDefaultUnreadMessages()

    def get_battery_level(self):
        """
        Check the battery level of device

        :return: int: Battery level
        """
        return self.wapi_functions.getBatteryLevel()

    def leave_group(self, chat_id):
        """
        Leave a group

        :param chat_id: id of group
        :return:
        """
        return self.wapi_functions.leaveGroup(chat_id)

    def delete_chat(self, chat_id):
        """
        Delete a chat

        :param chat_id: id of chat
        :return:
        """
        return self.wapi_functions.deleteConversation(chat_id)

    def quit(self):
        self.driver.quit()

    def create_chat_by_number(self, number):
        url = self._URL + "/send?phone=" + number
        self.driver.get(url)

    def create_chat(self, phone_number):
        """
        Creates a Chat object, that can be retrieved on success
        This object will die if no messages are sent, so be careful :/
        :param phone_number: str phone number, must be a contact
        """
        url = "{base_URL}/send?phone={phone_number}" \
            .format(base_URL=self._URL, phone_number=phone_number)
        self.driver.get(url)

    def check_number_whatsappable(self, phone_number):
        """
        Check if number is whatsappable, note that the number HAS to be a contact on the phone
        :param phone_number:
            str
        :return:
            bool whether or not the number is whatsappable
        """
        try:
            return self.get_chat_from_phone_number(phone_number) is not None
        except ChatNotFoundError:
            self.create_chat(phone_number)
            self.wait_for_login()
            try:
                popup = self.driver.find_element_by_css_selector(
                    self._SELECTORS['not_whatsappable'])
                return False
            except NoSuchElementException:
                # popup didn't show so the number does exist
                return True
            except WebDriverException as wd:
                logging.warning(wd)
