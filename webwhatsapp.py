import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from message import Message, MessageGroup
from chat import Chat


class WhatsAPIDriver(object):
    _PROXY = None

    _URL = "http://web.whatsapp.com"
    _SELECTORS = {
        "firstrun": "#wrapper",
        "qrCode": ".qrcode > img:nth-child(4)",
        "mainPage": ".app.two",
        "chatList": ".infinite-list-viewport",
        "messageList": "#main > div > div:nth-child(1) > div > div.message-list",
        "unreadMessageBar": "#main > div > div:nth-child(1) > div > div.message-list > div.msg-unread",
        "searchBar": ".input",
        "searchCancel": ".icon-search-morph",
        "chats": ".infinite-list-item",
        "chatBar": "div.input",
        "sendButton": "button.icon:nth-chld(3)",
        "LoadHistory": ".btn-more",
        "UnreadBadge": ".icon-meta",
        "UnreadChatBanner": ".message-list",
        "ReconnectLink": ".action",
        "WhatsappQrIcon": "span.icon:nth-child(2)",
        "QRReloader": ".qr-wrapper-container"
    }

    _CLASSES = {
        "unreadBadge": "icon-meta",
        "messageContent": "message-text",
        "messageList": "msg"
    }

    driver = None

    def __init__(self, username="API"):
        self.driver = webdriver.Firefox()
        self.username = username
        self.driver.get(self._URL)
        self.driver.implicitly_wait(10)

    def first_run(self):
        if "Click to reload QR code" in self.driver.page_source:
            self.reload_qr_code()
        qr = self.driver.find_element_by_css_selector(self._SELECTORS["qrCode"])
        qr.screenshot(self.username)
        WebDriverWait(self.driver, 30).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, self._SELECTORS["qrCode"])))

    def view_unread(self):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/get_unread_messages.js"), "r").read()

        raw_message_groups = self.driver.execute_script(script)

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
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/send_message_to_whatsapp_id.js"), "r").read()
        success = self.driver.execute_script(script, id, message)
        return success

    def send_to_phone_number(self, pno, message):
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()
        script = open(os.path.join(script_path, "js_scripts/send_message_to_phone_number.js"), "r").read()
        success = self.driver.execute_script(script, pno, message)
        return success

    def __unicode__(self):
        return self.username

    def __str__(self):
        return self.__unicode__()

    def reload_qr_code(self):
        self.driver.find_element_by_css_selector(self._SELECTORS["QRReloader"]).click()

    def create_callback(self, callback_function):
        try:
            while True:
                messages = self.view_unread()
                if messages != []:
                    callback_function(messages)
                time.sleep(5)
        except KeyboardInterrupt:
            print "Exited"
