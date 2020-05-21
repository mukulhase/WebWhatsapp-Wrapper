from six import string_types

from .whatsapp_object import WhatsappObjectWithId, driver_needed
from ..helper import safe_str


class Contact(WhatsappObjectWithId):
    """
    Class which represents a Contact on user's phone
    """

    def __init__(self, js_obj, driver=None):
        """

        :param js_obj:
        :param driver:
        :type driver: WhatsAPIDriver
        """

        self.short_name = None
        self.push_name = None
        self.formatted_name = None
        self.profile_pic = None
        self.verified_name = None
        self.is_business = False

        super(Contact, self).__init__(js_obj, driver)
        if "shortName" in js_obj:
            self.short_name = js_obj["shortName"]
        if "pushname" in js_obj:
            self.push_name = js_obj["pushname"]
        if "formattedName" in js_obj:
            self.formatted_name = js_obj["formattedName"]
        if "profilePicThumbObj" in js_obj:
            self.profile_pic = js_obj["profilePicThumbObj"].get("eurl", None)
        if "verifiedName" in js_obj:
            self.verified_name = js_obj["verifiedName"]
            self.is_business = js_obj["isBusiness"]

    @driver_needed
    def get_common_groups(self):
        return list(self.driver.contact_get_common_groups(self.id))

    @driver_needed
    def get_chat(self):
        return self.driver.get_chat_from_id(self.id)

    def get_safe_name(self):
        """

        :return: String used for representation of the Contact

        :rtype: String

        """
        name = self.short_name or self.push_name or self.formatted_name
        if isinstance(name, string_types):
            if self.is_business:
                safe_name = self.verified_name
            else:
                safe_name = safe_str(name)
        else:
            safe_name = "Unknown"
        return safe_name

    def __repr__(self):
        safe_name = self.get_safe_name()
        return "<Contact {0} ({1})>".format(safe_name, self.id)
