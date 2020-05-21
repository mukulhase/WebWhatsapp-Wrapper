from .whatsapp_object import WhatsappObjectWithId


class NumberStatus(WhatsappObjectWithId):
    """
    Class which represents a User phonenumber status in WhatsApp service.
    """

    def __init__(self, js_obj, driver=None):
        super(NumberStatus, self).__init__(js_obj, driver)

        if "status" in js_obj:
            self.status = js_obj["status"]
        if "isBusiness" in js_obj:
            self.is_business = js_obj["isBusiness"]
        if "canReceiveMessage" in js_obj:
            self.can_receive_message = js_obj["canReceiveMessage"]

    def __repr__(self):
        return "<NumberStatus - {id} (business={is_business}) - status = {status}>".format(
            id=self.id, is_business=self.is_business, status=self.status
        )
