from whatsapp_object import WhatsappObject, driver_needed


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

    def __repr__(self):
        try:
            safe_name = (self.name or self.push_name or self.formatted_name)
        except UnicodeEncodeError:
            safe_name = "(unicode name)"
        except:
            safe_name = "Unknown"

        return "<Contact {0} ({1})>".format(safe_name, self.id)
