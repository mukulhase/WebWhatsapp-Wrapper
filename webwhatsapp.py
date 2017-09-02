import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from message import Message, MessageGroup
from chat import Chat
from consts import Selectors, URL
from wapi_js_wrapper import WapiJsWrapper


class WhatsAPIDriver(object):
    def __init__(self, username="API"):
        self._driver = webdriver.Firefox()
        self.wapi_functions = WapiJsWrapper(self._driver)
        self.username = username

        # Open page
        self._driver.get(URL)
        self._driver.implicitly_wait(10)

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

        :return: List of contacts
        :rtype: list[Chat]
        """
        raw_contacts = self.wapi_functions.getContacts()

        contacts = []
        for contact in raw_contacts:
            contacts.append(Chat(contact))

        return contacts

    def reset_unread(self):
        """
        Resets unread messages list
        """
        self._driver.execute_script("window.last_read = {}")

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

            messages = []
            for raw_message in raw_message_group["messages"]:
                message = Message(raw_message)
                messages.append(message)

            unread_messages.append(MessageGroup(chat, messages))

        return unread_messages

    def get_all_messages_in_chat(self, chat, include_me=False):
        message_objs = self.wapi_functions.getAllMessagesInChat(chat.chat_id, include_me)

        messages = []
        for message in message_objs:
            messages.append(Message(message))

        return messages

    def send_message(self, chat, message):
        """
        Sends message using Whatsapp ID

        :param chat: Whatsapp ID
        :type chat: Chat
        :param message: Message to send
        :return: True if succeeded, else False
        :rtype: bool
        """
        return self.wapi_functions.sendMessage(chat.chat_id, message)

    def get_chat_from_id(self, uid):
        return Chat(self.wapi_functions.getChat(uid))

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
        contacts = self.get_contacts()

        chat = next((contact for contact in contacts if contact.chat_id.startswith(number)), None)
        return chat

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
            print "Exited"
