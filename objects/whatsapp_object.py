def driver_needed(func):
    def wrapped(self, *args):
        if not self._driver:
            raise AttributeError("No driver passed to object")

        return func(self, *args)

    return wrapped


class WhatsappObject(object):
    def __init__(self, js_obj, driver=None):
        self.id = js_obj["id"]
        self.name = js_obj["name"]

        self._js_obj = js_obj
        self._driver = driver