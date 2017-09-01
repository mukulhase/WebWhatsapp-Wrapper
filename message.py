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
        try:
            safe_content = self.content.decode("ascii")
        except UnicodeEncodeError:
            safe_content = "(unicode content)"

        truncation_length = 20
        truncated_content = safe_content[:truncation_length] + (safe_content[truncation_length:] and "...")

        return "<Message - from {sender} at {timestamp}: {content}>".format(
            sender=self.sender.name,
            timestamp=self.timestamp,
            content=truncated_content)


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

