import user


class Room:
    def __init__(self):
        self.list_of_users = []

    def add_user(self, new_user):
        self.list_of_users.append(new_user)

    def list_users(self):
        for user in self.list_of_users:
            print(user)

    def main(self):
        test_room = Room()
        user1 = user.User("test_real_name", "test_nick")
        test_room.add_user(user1)
        test_room.list_users()


if __name__ == "__main__":
    Room().main()
