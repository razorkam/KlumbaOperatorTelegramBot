# storing small and big versions of the same photo
import base64


class Photo:
    data_small = None # raw / encoded
    data_big = None # raw / encoded
    name_small = None
    name_big = None

    def __init__(self, name_small, name_big, data_small, data_big):
        self.data_small = data_small
        self.data_big = data_big
        self.name_small = name_small
        self.name_big = name_big

    def b64_encode(self):
        self.data_small = base64.b64encode(self.data_small).decode('ascii')
        self.data_big = base64.b64encode(self.data_big).decode('ascii')
        return self
