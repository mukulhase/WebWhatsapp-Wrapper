from .whatsapp_object import WhatsappObjectWithId, driver_needed
from ..helper import safe_str


def factory_chat(js_obj, driver=None):
    if js_obj["kind"] not in ["chat", "group", "broadcast"]:
        raise AssertionError("Expected chat, group or broadcast object, got {0}".format(js_obj["kind"]))

    if js_obj["isGroup"]:
        return GroupChat(js_obj, driver)

    if js_obj["kind"] == "broadcast":
        return BroadcastChat(js_obj, driver)

    return UserChat(js_obj, driver)


class Chat(WhatsappObjectWithId):

    def __init__(self, js_obj, driver=None):
        super(Chat, self).__init__(js_obj, driver)

    @driver_needed
    def send_message(self, message):
        return self.driver.chat_send_message(self.id, message)

    def get_messages(self, include_me=False, include_notifications=False):
        return list(self.driver.chat_get_messages(self.id, include_me, include_notifications))

    def load_earlier_messages(self):
        self.driver.chat_load_earlier_messages(self.id)

    def load_all_earlier_messages(self):
        self.driver.chat_load_all_earlier_messages(self.id)


class UserChat(Chat):
    def __init__(self, js_obj, driver=None):
        super(UserChat, self).__init__(js_obj, driver)

    def __repr__(self):
        safe_name = safe_str(self.name)

        return "<User chat - {name}: {id}>".format(
            name=safe_name,
            id=self.id)


class BroadcastChat(Chat):
    def __init__(self, js_obj, driver=None):
        super(BroadcastChat, self).__init__(js_obj, driver)

    def __repr__(self):
        safe_name = safe_str(self.name)
        return "<Broadcast chat - {name}: {id}>".format(
            name=safe_name,
            id=self.id)


class GroupChat(Chat):
    def __init__(self, js_obj, driver=None):
        super(GroupChat, self).__init__(js_obj, driver)

    @driver_needed
    def get_participants_ids(self):
        return self.driver.wapi_functions.getGroupParticipantIDs(self.id)

    @driver_needed
    def get_participants(self):
        return list(self.driver.group_get_participants(self.id))

    @driver_needed
    def get_admins(self):
        return list(self.driver.group_get_admins(self.id))

    def __repr__(self):
        safe_name = safe_str(self.name)
        return "<Group chat - {name}: {id}, {participants} participants>".format(
            name=safe_name,
            id=self.id,
            participants=len(self.get_participants_ids()))
