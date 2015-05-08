

class blockSignals(object):

    """Allow to use with statement to block signals.

    with object.blockSignals:
        object.do_stuff()

    """

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        self._status = self.obj.blockSignals(True)
        return self.obj

    def __exit__(self, *args, **kwargs):
        self.obj.blockSignals(self._status)
