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

    def registerReceiver(self, key, receiver):
        if key not in self.receiver_table:
            self.receiver_table[key] = []
        self.receiver_table[key].append(receiver)

    def send(self, key, params=None):
        if key not in self.receiver_table: return
        for receiver in self.receiver_table[key]:
            receiver.receive(params)
