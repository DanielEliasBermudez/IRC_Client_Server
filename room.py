import user


class Room:
    def __init__(self, room_name):
        self.name = room_name
        # list of user nick names, not full user objects
        self.list_of_users = []

    def get_name(self):
        return self.name

    def add_user(self, new_user):
        if new_user in self.list_of_users:
            return False
        self.list_of_users.append(new_user)
        return True

    def delete_user(self, user):
        self.list_of_users.remove(user)

    def list_users(self):
        for user in self.list_of_users:
            print(user)

    def get_list_of_users(self):
        return self.list_of_users


def main():
    test_room = Room("test_room")
    user1 = user.User("test_real_name", "test_nick")
    test_room.add_user(user1)
    test_room.list_users()


if __name__ == "__main__":
    main()
