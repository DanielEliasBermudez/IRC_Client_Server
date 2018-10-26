#!usr/bin/env python3
import socket
import json
import user
import room

test_user_dict = {"command": "user", "nick": "Alice", "real_name": "Alice A"}
test_user_jobj = json.dumps(test_user_dict)
test_join_dict = {"command": "join", "room": "test_room", "nick": "Alice"}
test_join_jobj = json.dumps(test_join_dict)

list_of_users = []
list_of_rooms = []


def handle_message(msg):
    """
    Will look at the message json object and choose the correct handler based on the 
    command key.
    """
    command = msg["command"]
    user = msg["nick"]

    if command == "user":
        handle_user_cmd(msg)
    if verify_user(user):
        if command == "join":
            room = msg["room"]
            if room in list_of_rooms:
                handle_join_cmd(msg)
            else:
                handle_create_cmd(msg)
        # elif command == "list":
        #     # handle list call
    else:
        # TODO add exception for unknown user?
        print("Unknown user")


def handle_user_cmd(msg):
    """
    Handles the user command by adding the user to the list of users.
    User json object example:
    {
        "command" : "user",
        "nick" : "name of user",
        "real_name" : "real name of user",
    }
    """
    print("Command - User")
    print("Nick: {}".format(msg["nick"]))
    print("Real Name: {}".format(msg["real_name"]))
    new_user = user.User(msg["nick"], msg["real_name"])
    list_of_users.append(new_user)
    print("User added")


def handle_create_cmd(msg):
    """
    Creates a room when a user tries to join a room that does not exist.
    User json object example:
    {
        "command" : "join",
        "room" : "name of room"
        "nick" : "name of user",
    }
    """
    new_room = room.Room(msg["room"])
    new_room.add_user(msg["nick"])
    print("Created a room")


# TODO update
def handle_join_cmd(msg):
    pass


def verify_user(user):
    if user in list_of_users:
        return True
    return False


# This will create listening connection TCP socket on localhost:8080
def main():
    """
    Run a server on localhost that listens on port 8080
    
    """
    HOST = "127.0.0.1"
    PORT = 8080
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        conn, address = sock.accept()
        with conn:
            print("Connected to {}".format(address))
            data = conn.recv(1024)
            print(data.decode("utf-8"))
            # parse the json here - this should be the json that came thru the data. for
            # now I am just using a test json object
            msg_json = json.loads(test_user_jobj)
            handle_message(msg_json)
            msg_json = json.loads(test_join_jobj)
            handle_message(msg_json)
            conn.send(b"You made a connection. yay!")


if __name__ == "__main__":
    main()

# conn.send(b"You made a connection. yay!")
# sock.close()
