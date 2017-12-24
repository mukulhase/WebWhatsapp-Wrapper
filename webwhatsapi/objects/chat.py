from whatsapp_object import WhatsappObject, driver_needed


##TODO: Fix relative imports for Python3
class ChatMetaClass(type):
    """
    Chat type factory
    """

    def __call__(cls, js_obj, driver=None):
        """
        Responsible for returning correct Chat subtype

        :param js_obj: Raw message JS
        :return: Instance of appropriate chat type
        :rtype: Chat | UserChat | GroupChat | BroadcastChat
        """
        assert js_obj["kind"] in ["chat", "group", "broadcast"], "Expected chat or group object, got {0}".format(
            js_obj["kind"])

        if js_obj["isGroup"]:
            return type.__call__(GroupChat, js_obj, driver)

        if js_obj["kind"] == "broadcast":
            return type.__call__(BroadcastChat, js_obj, driver)

        return type.__call__(UserChat, js_obj, driver)


class Chat(WhatsappObject):
    __metaclass__ = ChatMetaClass

    def __init__(self, js_obj, driver=None):
        super(Chat, self).__init__(js_obj, driver)

    @driver_needed
    def send_message(self, message):
        return self.driver.wapi_functions.sendMessage(self.id, message)

        ## TODO: Get messages directly


class UserChat(Chat):
    def __init__(self, js_obj, driver=None):
        super(UserChat, self).__init__(js_obj, driver)

    def __repr__(self):
        try:
            safe_name = self.name.decode("ascii")
        except UnicodeEncodeError:
            safe_name = "(unicode name)"
        except AttributeError:
            safe_name = "(none)"

        return "<User chat - {name}: {id}>".format(
            name=safe_name,
            id=self.id)


class BroadcastChat(Chat):
    def __init__(self, js_obj, driver=None):
        super(BroadcastChat, self).__init__(js_obj, driver)

    def __repr__(self):
        try:
            safe_name = self.name.decode("ascii")
        except UnicodeEncodeError:
            safe_name = "(unicode name)"
        except AttributeError:
            safe_name = "(none)"

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
        participant_ids = self.get_participants_ids()

        participants = []
        for participant_id in participant_ids:
            participants.append(self.driver.get_contact_from_id(participant_id))

        return participants

    @driver_needed
    def get_admins(self):
        admin_ids = self.driver.wapi_functions.getGroupAdmins(self.id)

        admins = []
        for admin_id in admin_ids:
            admins.append(self.driver.get_contact_from_id(admin_id))

        return admins

    def __repr__(self):
        try:
            safe_name = self.name.decode("ascii")
        except UnicodeEncodeError:
            safe_name = "(unicode name)"
        except AttributeError:
            safe_name = "(none)"
        return "<Group chat - {name}: {id}, {participants} participants>".format(
            name=safe_name,
            id=self.id,
            participants=len(self.get_participants_ids()))
