from whatsapp_object import WhatsappObject, driver_needed
from webwhatsapi.helper import safe_str
import six

class Contact(WhatsappObject):
    def __init__(self, js_obj, driver=None):
        super(Contact, self).__init__(js_obj, driver)
        self.short_name = js_obj["shortName"]
        self.push_name = js_obj["pushname"]
        self.formatted_name = js_obj["formattedName"]

    @driver_needed
    def get_common_groups(self):
        return self.driver.wapi_functions.getCommonGroups(self.id)

    @driver_needed
    def get_chat(self):
        return self.driver.get_chat_from_id(self.id)

    def get_safe_name(self):
        name = (self.name or self.push_name or self.formatted_name)
        if (isinstance(name, six.string_types)):
            safe_name = safe_str(name)
        else:
            safe_name = "Unknown"
        return safe_name

    def __repr__(self):
        safe_name = self.get_safe_name()
        return "<Contact {0} ({1})>".format(safe_name, self.id)
