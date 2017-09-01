import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from message import Message, MessageGroup
from chat import Chat
from consts import Selectors, URL


class WhatsAPIDriver(object):
    _PROXY = None

    driver = None

    def __init__(self, username="API"):
        self.driver = webdriver.Firefox()
        self.username = username
        self.driver.get(URL)
        self.driver.implicitly_wait(10)

    @staticmethod
    def _get_script_path(script_file):
        """
        Resolves location of js_scripts folder and returns full path to given script

        :param script_file: Filename of script
        :return: Full path to script
        """
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()

        return os.path.join(script_path, script_file)

    def _execute_script(self, script_name):
        """
        Runs a js file from the js_scripts folder

        :param script_name: Name of script (without extension)
        :return: Script output
        """
        with file(WhatsAPIDriver._get_script_path(script_name + ".js"), "rb") as script:
            return self.driver.execute_script(script)

    def first_run(self):
        if "Click to reload QR code" in self.driver.page_source:
            self._reload_qr_code()
        qr = self.driver.find_element_by_css_selector(Selectors.QR_CODE)
        qr.screenshot(self.username)
        WebDriverWait(self.driver, 30).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, Selectors.QR_CODE)))

    def reset_unread(self):
        """
        Resets unread messages list
        """
        self._execute_script("reset_unread_messages")

    def view_unread(self):
        raw_message_groups = self._execute_script("get_unread_messages")

        unread_messages = []
        for raw_message_group in raw_message_groups:
            chat = Chat(
                raw_message_group["name"], raw_message_group["id"], raw_message_group["isGroup"])
            messages = [
                Message(
                    Chat(raw_message["sender"]["name"], raw_message["sender"]["id"], False),
                    raw_message["timestamp"],
                    raw_message["content"])
                for raw_message in raw_message_group["messages"]
            ]

            unread_messages.append(MessageGroup(chat, messages))

        return unread_messages

    def send_to_whatsapp_id(self, id, message):
        return self._execute_script("send_message_to_whatsapp_id")

    def send_to_phone_number(self, pno, message):
        return self._execute_script("send_message_to_phone_number")

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.__unicode__()

    def _reload_qr_code(self):
        self.driver.find_element_by_css_selector(Selectors.QR_RELOADER).click()

    def create_callback(self, callback_function):
        try:
            while True:
                messages = self.view_unread()
                if messages:
                    callback_function(messages)
                time.sleep(5)
        except KeyboardInterrupt:
            print "Exited"
