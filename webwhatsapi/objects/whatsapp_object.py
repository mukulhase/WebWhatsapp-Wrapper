from weakref import ref


def driver_needed(func):
    """
    Decorator for WhatsappObjectWithId methods that need to communicate with the browser

    It ensures that the object receives a driver instance at construction

    :param func: WhatsappObjectWithId method
    :return: Wrapped method
    """

    def wrapped(self, *args):
        if not self.driver:
            raise AttributeError("No driver passed to object")

        return func(self, *args)

    return wrapped


class WhatsappObject(object):
    """
    Base class for Whatsapp objects

    Intended to wrap JS objects fetched from the browser

    Can also be used as an interface to operations (such as sending messages to chats)
    To enable this functionality the constructor must receive a WhatsAPIDriver instance
    """

    def __init__(self, js_obj, driver=None):
        """
        Constructor

        :param js_obj: Whatsapp JS object to wrap
        :type js_obj: dict
        :param driver: Optional driver instance
        :type driver: WhatsAPIDriver
        """
        self._js_obj = js_obj
        self._driver = ref(driver)

    @property
    def driver(self):
        return self._driver()


class WhatsappObjectWithId(WhatsappObject):
    """
    Base class for Whatsapp objects

    Intended to wrap JS objects fetched from the browser

    Can also be used as an interface to operations (such as sending messages to chats)
    To enable this functionality the constructor must receive a WhatsAPIDriver instance
    """

    def __init__(self, js_obj, driver=None):
        """
        Constructor

        :param js_obj: Whatsapp JS object to wrap
        :type js_obj: dict
        :param driver: Optional driver instance
        :type driver: WhatsAPIDriver
        """
        super(WhatsappObjectWithId, self).__init__(js_obj, driver)
        self.id = js_obj["id"]
        self.name = js_obj["name"]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id
