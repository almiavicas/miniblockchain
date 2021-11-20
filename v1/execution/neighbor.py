class Neighbor:
    def __init__(self, name, port, pub_key):
        self.name = name
        self.port = port
        self.pub_key = pub_key
        self.is_active = False

    def send_message(self, message):
        pass