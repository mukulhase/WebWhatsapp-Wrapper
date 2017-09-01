class Chat(object):
    def __init__(self, name, chat_id, is_group, raw_js_obj=None):
        self.name = name
        self.chat_id = chat_id
        self.is_group = is_group
        self.raw_js_obj = raw_js_obj

    def __repr__(self):
        return "<Chat - ({type}): {id}>".format(
            name=self.name, type="group" if self.is_group else "user", id=self.chat_id)