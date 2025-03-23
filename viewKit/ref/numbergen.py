class IncrementalNumberGenerator:
    def __init__(self, start=0):
        self.last = start - 1  # next で最初にインクリメントしているので

    def next(self):
        self.last += 1
        return self.last
