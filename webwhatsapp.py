import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from message import Message, MessageGroup
from chat import Chat
from consts import Selectors, URL, JSFunctions


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

    def first_run(self):
        if "Click to reload QR code" in self._driver.page_source:
            self._reload_qr_code()
        qr = self._driver.find_element_by_css_selector(Selectors.QR_CODE)
        qr.screenshot(self.username + ".png")
        WebDriverWait(self._driver, 30).until(
            ec.invisibility_of_element_located((By.CSS_SELECTOR, Selectors.QR_CODE)))

    def get_contacts(self):
        raw_contacts = self._driver.execute_script(JSFunctions.GET_CONTACTS)

        contacts = []
        for contact in raw_contacts:
            contacts.append(Chat(contact))

    def reset_unread(self):
        """
        Resets unread messages list
        """
        self._driver.execute_script(JSFunctions.RESET_UNREAD_MESSAGES)

    def view_unread(self):
        """
        Fetches unread messages

        :return: List of unread messages grouped by chats
        :rtype: list[MessageGroup]
        """
        raw_message_groups = self._execute_script("get_unread_messages")

        unread_messages = []
        for raw_message_group in raw_message_groups:
            chat = Chat(raw_message_group)

            messages = [
                Message(Chat(raw_message["sender"]), raw_message)
                for raw_message in raw_message_group["messages"]
            ]

            unread_messages.append(MessageGroup(chat, messages))

        return unread_messages

    def send_to_whatsapp_id(self, uid, message):
        """
        Sends message using Whatsapp ID

        :param uid: Whatsapp ID
        :param message: Message to send
        :return: True if succeeded, else False
        :rtype: bool
        """
        return self._execute_script("send_message_to_whatsapp_id", uid, message)

    def send_to_phone_number(self, number, message):
        """
        Sends message using phone number

        Number format should be as it appears in Whatsapp ID
        For example, for the number:
            +972-51-234-5678
        This function would receive:
            972512345678

        :param number: Phone number
        :param message: Message to send
        :return: True if succeeded, else False
        :rtype: bool
        """
        return self._execute_script("send_message_to_phone_number", number, message)

    def _reload_qr_code(self):
        self._driver.find_element_by_css_selector(Selectors.QR_RELOADER).click()

    def create_callback(self, callback_function):
        try:
            while True:
                messages = self.view_unread()
                if messages:
                    callback_function(messages)
                time.sleep(5)
        except KeyboardInterrupt:
            print "Exited"
