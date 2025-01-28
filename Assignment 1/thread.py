import threading

class ThreadC(threading.Thread):
    def __init__(self, **kwargs):
        super(self).__init__()
        self.inputs = kwargs

    