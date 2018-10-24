class User:
    def __init__(self, real_name, nick):
        self.real_name = real_name
        self.nick = nick

    def get_real_name(self):
        return self.real_name

    def get_nick(self):
        return self.nick

    def __str__(self):
        return self.real_name
