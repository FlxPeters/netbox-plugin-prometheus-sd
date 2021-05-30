class Target:
    def __init__(self, address):
        self.targets = [address]
        self.labels = {}

    def add_label(self, name, value):
        self.labels[name] = value
