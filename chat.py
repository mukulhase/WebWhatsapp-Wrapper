class Chat(object):
    def __init__(self, name, chat_id, is_group):
        self.name = name
        self.chat_id = chat_id
        self.is_group = is_group

    def __repr__(self):
        return "<Chat - ({type}): {id}>".format(
            name=self.name, type="group" if self.is_group else "user", id=self.chat_id)