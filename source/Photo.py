# storing small and big versions of the same photo
class Photo:
    encoded_data_small = None
    encoded_data_big = None
    name_small = None
    name_big = None

    def __init__(self, name_small, name_big, data_small, data_big):
        self.encoded_data_small = data_small
        self.encoded_data_big = data_big
        self.name_small = name_small
        self.name_big = name_big
