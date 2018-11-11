class User:
    def __init__(self, nick, real_name):
        self.nick = nick
        self.real_name = real_name
        self.outbound = ""

    def get_nick(self):
        return self.nick

    def get_real_name(self):
        return self.real_name

    def __str__(self):
        return self.real_name
