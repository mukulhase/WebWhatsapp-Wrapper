import os


class WapiJsWrapper(object):
    def __init__(self, driver):
        self.driver = driver

    def __getattr__(self, item):
        wapi_functions = dir(self)

        if item not in wapi_functions:
            raise AttributeError("Function {0} doesn't exist".format(item))

        return JsFunction(item, self.driver)

    def __dir__(self):
        with file(os.path.join("js", "wapi.js"), "rb") as script:
            self.driver.execute_script(script.read())

        return self.driver.execute_script("return window.WAPI").keys()


class JsArg(object):
    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        if type(self.obj) in [str, unicode]:
            return repr(str(self.obj))

        if type(self.obj) == bool:
            return str(self.obj).lower()

        return str(self.obj)


class JsFunction(object):
    def __init__(self, function_name, driver):
        self.driver = driver
        self.function_name = function_name

    def __call__(self, *args, **kwargs):
        if len(args):
            command = "return WAPI.{0}({1})".format(self.function_name, ",".join([str(JsArg(arg)) for arg in args]))
        else:
            command = "return WAPI.{0}()".format(self.function_name)

        return self.driver.execute_script(command)
