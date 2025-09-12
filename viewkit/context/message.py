import logging

# supported messages
MAIN_WINDOW_RELOADED = "main_window_reloaded"


class ContextMessageReceiver():
    def __init__(self, func):
        self.func = func

    def receive(self, params):
        self.func(params)


class ContextMessageHandler():
    def __init__(self):
        self.receiver_table = {}
        self.logger = logging.getLogger(__name__)

    def registerReceiver(self, key, receiver):
        if key not in self.receiver_table:
            self.receiver_table[key] = []
        self.receiver_table[key].append(receiver)
        self.logger.debug("context message receiver for %s has been registered: %s" % (key, receiver))

    def send(self, key, params=None):
        self.logger.debug("context message %s has been sent with parameters: %s" % (key, params))
        if key not in self.receiver_table:
            return
        for receiver in self.receiver_table[key]:
            self.logger.debug("sending message to %s" % (receiver))
            receiver.receive(params)
