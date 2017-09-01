class Chat(object):
    def __init__(self, js_obj):
        self.name = js_obj["name"]
        self.chat_id = js_obj["id"]
        self.is_group = js_obj["isGroup"]

        self._raw_js_obj = js_obj["_raw"]

    def __repr__(self):
        return "<Chat - ({type}): {id}>".format(
            name=self.name, type="group" if self.is_group else "user", id=self.chat_id)