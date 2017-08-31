from datetime import datetime


class Message(object):
    def __init__(self, sender, timestamp, content):
        self.sender = sender
        self.timestamp = datetime.fromtimestamp(timestamp)
        self.content = content

    def __repr__(self):
        return "<Message - from {sender} at {timestamp}>".format(sender=self.sender.name, timestamp=self.timestamp)


class MessageGroup(object):
    def __init__(self, chat, messages):
        self.chat = chat
        self.messages = messages

    def __repr__(self):
        return "<MessageGroup - {num} messages>".format(num=len(self.messages))

