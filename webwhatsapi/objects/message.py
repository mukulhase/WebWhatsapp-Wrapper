import mimetypes
import os
from datetime import datetime
from typing import Union

from .contact import Contact
from .whatsapp_object import WhatsappObject
from ..helper import safe_str


def getContacts(x, driver):
    # XXX: why camel case? what is x?
    try:
        contact = driver.get_contact_from_id(x)
        return contact
    except Exception:
        return x


def factory_message(js_obj, driver):
    """Factory function for creating appropriate object given selenium JS object"""
    if js_obj is None:
        return

    if "lat" in js_obj and "lng" in js_obj and js_obj["lat"] and js_obj["lng"]:
        return GeoMessage(js_obj, driver)

    if js_obj["isMedia"]:
        return MediaMessage(js_obj, driver)

    if js_obj["isNotification"]:
        return NotificationMessage(js_obj, driver)

    if "isMMS" in js_obj and js_obj["isMMS"]:
        return MMSMessage(js_obj, driver)

    if js_obj["type"] in ["vcard", "multi_vcard"]:
        return VCardMessage(js_obj, driver)

    return Message(js_obj, driver)


class Message(WhatsappObject):
    sender = Union[Contact, bool]

    def __init__(self, js_obj, driver=None):
        """
        Constructor

        :param js_obj: Raw JS message obj
        :type js_obj: dict
        """
        super(Message, self).__init__(js_obj, driver)

        self.id = js_obj["id"]
        self.type = js_obj["type"]
        self.sender = Contact(js_obj["sender"], driver) if js_obj["sender"] else False
        self.timestamp = datetime.fromtimestamp(js_obj["timestamp"])
        self.chat_id = js_obj["chatId"]

        if js_obj["content"]:
            self.content = js_obj["content"]
            self.safe_content = safe_str(self.content[0:25]) + "..."
        elif self.type == "revoked":
            self.content = ""
            self.safe_content = "..."

    def __repr__(self):
        return "<Message - {type} from {sender} at {timestamp}: {content}>".format(
            type=self.type,
            sender=safe_str(self.sender.get_safe_name()),
            timestamp=self.timestamp,
            content=self.safe_content,
        )


class MediaMessage(Message):
    crypt_keys = {
        "document": "576861747341707020446f63756d656e74204b657973",
        "image": "576861747341707020496d616765204b657973",
        "video": "576861747341707020566964656f204b657973",
        "ptt": "576861747341707020417564696f204b657973",
        "audio": "576861747341707020417564696f204b657973",
    }

    def __init__(self, js_obj, driver=None):
        super(MediaMessage, self).__init__(js_obj, driver)

        self.size = self._js_obj["size"]
        self.mime = self._js_obj["mimetype"]
        if "caption" in self._js_obj:
            self.caption = self._js_obj["caption"] or ""

        self.media_key = self._js_obj.get("mediaKey")
        self.client_url = self._js_obj.get("clientUrl")

        extension = mimetypes.guess_extension(self.mime)
        self.filename = "".join([str(id(self)), extension or ""])

    def save_media(self, path, force_download=False):
        # gets full media
        filename = os.path.join(path, self.filename)
        ioobj = self.driver.download_media(self, force_download)
        with open(filename, "wb") as f:
            f.write(ioobj.getvalue())
        return filename

    def __repr__(self):
        return "<MediaMessage - {type} from {sender} at {timestamp} ({filename})>".format(
            type=self.type,
            sender=safe_str(self.sender.get_safe_name()),
            timestamp=self.timestamp,
            filename=self.filename,
        )


class MMSMessage(MediaMessage):
    """
    Represents MMS messages

    Example of an MMS message: "ptt" (push to talk), voice memo
    """

    def __init__(self, js_obj, driver=None):
        super(MMSMessage, self).__init__(js_obj, driver)

    def __repr__(self):
        return "<MMSMessage - {type} from {sender} at {timestamp}>".format(
            type=self.type,
            sender=safe_str(self.sender.get_safe_name()),
            timestamp=self.timestamp,
        )


class VCardMessage(Message):
    def __init__(self, js_obj, driver=None):
        super(VCardMessage, self).__init__(js_obj, driver)

        self.type = js_obj["type"]
        self.contacts = list()

        if js_obj["content"]:
            self.contacts.append(js_obj["content"].encode("ascii", "ignore"))
        else:
            for card in js_obj["vcardList"]:
                self.contacts.append(card["vcard"].encode("ascii", "ignore"))

    def __repr__(self):
        return "<VCardMessage - {type} from {sender} at {timestamp} ({contacts})>".format(
            type=self.type,
            sender=safe_str(self.sender.get_safe_name()),
            timestamp=self.timestamp,
            contacts=self.contacts,
        )


class GeoMessage(Message):
    def __init__(self, js_obj, driver=None):
        super(GeoMessage, self).__init__(js_obj, driver)

        self.type = js_obj["type"]
        self.latitude = js_obj["lat"]
        self.longitude = js_obj["lng"]

    def __repr__(self):
        return "<GeoMessage - {type} from {sender} at {timestamp} ({lat}, {lng})>".format(
            type=self.type,
            sender=safe_str(self.sender.get_safe_name()),
            timestamp=self.timestamp,
            lat=self.latitude,
            lng=self.longitude,
        )


class NotificationMessage(Message):
    def __init__(self, js_obj, driver=None):
        super(NotificationMessage, self).__init__(js_obj, driver)
        self.type = js_obj["type"]
        self.subtype = js_obj["subtype"]
        if js_obj["recipients"]:
            self.recipients = [getContacts(x, driver) for x in js_obj["recipients"]]

    def __repr__(self):
        readable = {
            "call_log": {"miss": "Missed Call"},
            "e2e_notification": {"encrypt": "Messages now Encrypted"},
            "gp2": {
                "invite": "Joined an invite link",
                "create": "Created group",
                "add": "Added to group",
                "remove": "Removed from group",
                "leave": "Left the group",
            },
        }
        sender = (
            ""
            if not self.sender
            else ("from " + str(safe_str(self.sender.get_safe_name())))
        )
        return "<NotificationMessage - {type} {recip} {sender} at {timestamp}>".format(
            type=readable[self.type][self.subtype],
            sender=sender,
            timestamp=self.timestamp,
            recip=""
            if not hasattr(self, "recipients")
            else "".join([safe_str(x.get_safe_name()) for x in self.recipients]),
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
        safe_chat_name = safe_str(self.chat.name)
        return "<MessageGroup - {num} {messages} in {chat}>".format(
            num=len(self.messages),
            messages="message" if len(self.messages) == 1 else "messages",
            chat=safe_chat_name,
        )
