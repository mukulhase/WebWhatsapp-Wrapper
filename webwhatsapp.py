import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from message import Message, MessageGroup
from chat import Chat
from consts import Selectors, URL, JSFunctions
from js_arg import JSArg


class WhatsAPIDriver(object):
    def __init__(self, username="API"):
        self._driver = webdriver.Firefox()
        self.username = username

        # Open page
        self._driver.get(URL)
        self._driver.implicitly_wait(10)

        # Add common functions to scope
        self._reload_common_script()

    @staticmethod
    def _get_script_path(script_file):
        """
        Resolves location of js_scripts folder and returns full path to given script

        :param script_file: Filename of script
        :return: Full path to script
        :rtype: str
        """
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()

        return os.path.join(script_path, "js_scripts", script_file)

    def _reload_common_script(self):
        """
        Adds common js utility functions to scope
        """
        self._execute_script("common")

    def _execute_script(self, script_name, *args):
        """
        Runs a js file from the js_scripts folder

        :param script_name: Name of script (without extension)
        :return: Script output
        """
        with file(WhatsAPIDriver._get_script_path(script_name + ".js"), "rb") as script:
            return self._driver.execute_script(script.read(), *args)

    def _call_js_function(self, function_name, *args):
        if len(args):
            command = "return WAPI.{0}({1})".format(function_name, ",".join([str(JSArg(arg)) for arg in args]))
        else:
            command = "return WAPI.{0}()".format(function_name)

        print args
        print command

        return self._driver.execute_script(command)

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
        raw_contacts = self._call_js_function(JSFunctions.GET_CONTACTS)

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
        raw_message_groups = self._execute_script("get_unread_messages")

        unread_messages = []
        for raw_message_group in raw_message_groups:
            chat = Chat(raw_message_group)

            messages = []
            for raw_message in raw_message_group["messages"]:
                message = Message(raw_message)
                messages.append(message)

            unread_messages.append(MessageGroup(chat, messages))

        return unread_messages

    def get_all_messages(self, chat, include_me=False):
        group_objs = self._call_js_function(JSFunctions.GET_ALL_MESSAGES, chat.chat_id, include_me)

        groups = []
        for group_obj in group_objs:

            group_messages = []
            for message in group_obj["messages"]:
                group_messages.append(Message(message))

            groups.append(MessageGroup(Chat(group_obj), group_messages))

        return groups

    def get_all_messages_in_chat(self, chat, include_me=False):
        message_objs = self._call_js_function(JSFunctions.GET_ALL_MESSAGES, chat.chat_id, include_me)

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
        return self._execute_script("send_message_to_whatsapp_id", chat.chat_id, message)

    def get_chat_from_id(self, uid):
        return Chat(self._call_js_function(JSFunctions.GET_CHAT, uid))

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
