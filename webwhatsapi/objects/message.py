from datetime import datetime
import mimetypes
import os
import pprint
pprint = pprint.PrettyPrinter(indent=4).pprint

from chat import Chat
from contact import Contact


class MessageMetaClass(type):
    """
    Message type factory
    """

    def __call__(cls, js_obj):
        """
        Responsible for returning correct Message subtype

        :param js_obj: Raw message JS
        :return: Instance of appropriate message type
        :rtype: MediaMessage | Message | MMSMessage | VCardMessage
        """
        if js_obj["isMedia"]:
            return type.__call__(MediaMessage, js_obj)

        if js_obj["isMMS"]:
            return type.__call__(MMSMessage, js_obj)

        if js_obj["type"] in ["vcard", "multi_vcard"]:
            return type.__call__(VCardMessage, js_obj)

        return type.__call__(Message, js_obj)


class Message(object):
    __metaclass__ = MessageMetaClass

    def __init__(self, js_obj):
        """
        Constructor

        :param js_obj: Raw JS message obj
        :type js_obj: dict
        """
        self.sender = Contact(js_obj["sender"])
        self.timestamp = datetime.fromtimestamp(js_obj["timestamp"])
        self.content = js_obj["content"]
        self.js_obj = js_obj

    def __repr__(self):
        try:
            safe_content = self.content.decode("ascii")
        except UnicodeEncodeError:
            safe_content = "(unicode content)"

        truncation_length = 20
        safe_content = safe_content[:truncation_length] + (safe_content[truncation_length:] and "...")

        return "<Message - from {sender} at {timestamp}: {content}>".format(
            sender=self.sender.name,
            timestamp=self.timestamp,
            content=safe_content)


class MediaMessage(Message):
    def __init__(self, js_obj):
        super(MediaMessage, self).__init__(js_obj)

        self.type = self.js_obj["type"]
        self.size = self.js_obj["size"]
        self.mime = self.js_obj["mime"]

    def save_media(self, path):
        extension = mimetypes.guess_extension(self.mime)
        filename = "{0}{1}".format(self["__x_filehash"], extension)

        with file(os.path.join(path, filename), "wb") as output:
            output.write(self.content.decode("base64"))

    def __repr__(self):
        return "<MediaMessage - {type} from {sender} at {timestamp}>".format(
            type=self.type,
            sender=self.sender.name,
            timestamp=self.timestamp
        )


class MMSMessage(MediaMessage):
    """
    Represents MMS messages

    Example of an MMS message: "ptt" (push to talk), voice memo
    """
    def __init__(self, js_obj):
        super(MMSMessage, self).__init__(js_obj)

    def __repr__(self):
        return "<MMSMessage - {type} from {sender} at {timestamp}>".format(
            type=self.type,
            sender=self.sender.name,
            timestamp=self.timestamp
        )


class VCardMessage(Message):
    def __init__(self, js_obj):
        super(VCardMessage, self).__init__(js_obj)

        self.type = self["__x_type"]
        self.contacts = self["__x_subtype"].encode("ascii", "ignore")

    def __repr__(self):
        return "<VCardMessage - {type} from {sender} at {timestamp} ({contacts})>".format(
            type=self.type,
            sender=self.sender.name,
            timestamp=self.timestamp,
            contacts=self.contacts
        )


class MessageGroup(object):
    def __init__(self, chat, messages):
        """
        Constructor

        :param chat: Chat that contains messages
        :type chat: chat.Chat
        :param messages: List of messages
        :type messages: list[Message]
        """
        self.chat = chat
        self.messages = messages

    def __repr__(self):
        try:
            safe_chat_name = self.chat.name.decode("ascii")
        except UnicodeEncodeError:
            safe_chat_name = "(unicode name)"

        return "<MessageGroup - {num} {messages} in {chat}>".format(
            num=len(self.messages),
            messages="message" if len(self.messages) == 1 else "messages",
            chat=safe_chat_name)

