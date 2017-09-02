class JSArg(object):
    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        if type(self.obj) in [str, unicode]:
            return repr(str(self.obj))

        if type(self.obj) == bool:
            return str(self.obj).lower()

        return str(self.obj)
