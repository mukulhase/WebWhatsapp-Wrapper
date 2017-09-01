from datetime import datetime


class Message(object):
    def __init__(self, sender, js_obj):
        """
        Constructor

        :param sender: Sender of message
        :type sender: chat.Chat
        :param js_obj: Raw JS message obj
        :type js_obj: dict
        """
        self.sender = sender
        self.timestamp = datetime.fromtimestamp(js_obj["timestamp"])
        self.content = js_obj["content"]

    def __repr__(self):
        return "<Message - from {sender} at {timestamp}>".format(sender=self.sender.name, timestamp=self.timestamp)


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
        return "<MessageGroup - {num} messages>".format(num=len(self.messages))

