class SimpleMemory:
    def __init__(self):
        self.history = []

    def store(self, item):
        self.history.append(item)

    def recall(self):
        return self.history[-3:]
