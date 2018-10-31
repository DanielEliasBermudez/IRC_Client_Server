#!usr/bin/env python3
import socket
import json
import user
import room

test_user_dict = {"command": "user", "nick": "Alice", "real_name": "Alice A"}
test_user_jobj = json.dumps(test_user_dict)
test_join_dict = {"command": "join", "nick": "Alice", "room": "room1"}
test_join_jobj = json.dumps(test_join_dict)

test_userb_dict = {"command": "user", "nick": "Boris", "real_name": "Boris P"}
test_userb_jobj = json.dumps(test_userb_dict)
test_joinb_dict = {"command": "join", "nick": "Boris", "room": "room1"}
test_joinb_jobj = json.dumps(test_joinb_dict)

list_of_users = []
list_of_rooms = []


def handle_message(msg):
    """
    Will look at the message json object and choose the correct handler based on the 
    command key.
    """
    command = msg["command"]
    user = msg["nick"]
    response = ""

    if command == "user":
        response = handle_user_cmd(msg)
    elif verify_user(user):
        if command == "join":
            room = msg["room"]
            room_found = False
            room_in_list = None
            for room_in_list in list_of_rooms:
                if room_in_list.get_name() == room:
                    room_found = True
                    break
            if room_found:
                response = handle_join_cmd(msg, room_in_list)
            else:
                response = handle_create_cmd(msg)
        # elif command == "list":
        #     # handle list call
    else:
        # TODO add exception for unknown user?
        # TODO add "NOT OK" response
        print("Unknown user {}".format(user))
    return response


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
    nick_name = msg["nick"]
    # verify that user nick is not already in use
    if verify_user(nick_name):
        reply = "NOT OK - User {} already on the server".format(nick_name)
        response_msg = {"command": "user", "nick": nick_name, "response": reply}
        return json.dumps(response_msg)

    new_user = user.User(nick_name, msg["real_name"])
    list_of_users.append(new_user)
    reply = "User {} joined the server.".format(nick_name)
    response_msg = {"command": "user", "nick": nick_name, "response": reply}
    # TODO remove
    # print("Command - User")
    # print("Nick: {}".format(msg["nick"]))
    # print("Real Name: {}".format(msg["real_name"]))
    print("User added")
    return json.dumps(response_msg)


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
    room_name = msg["room"]
    nick_name = msg["nick"]
    new_room = room.Room(room_name)
    new_room.add_user(nick_name)
    list_of_rooms.append(new_room)
    print("Created a room")
    reply = "Room {} created.\nUser {} joined room {}.".format(
        room_name, nick_name, room_name
    )
    response_msg = {"command": "join", "nick": nick_name, "response": reply}
    return json.dumps(response_msg)


def handle_join_cmd(msg, room):
    """
    Adds a user to the exisiting room.
    User json object example:
    {
        "command" : "join",
        "room" : "name of room"
        "nick" : "name of user",
    }
    """
    room_name = msg["room"]
    nick_name = msg["nick"]
    room.add_user(msg["nick"])
    print("Joined existing room")
    reply = "User {} joined room {}.".format(nick_name, room_name)
    response_msg = {"command": "join", "nick": nick_name, "response": reply}
    return json.dumps(response_msg)


def verify_user(user_nick):
    for user in list_of_users:
        if user.get_nick() == user_nick:
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
            response = handle_message(msg_json)
            msg_json = json.loads(test_join_jobj)
            response = handle_message(msg_json)

            msg_json = json.loads(test_userb_jobj)
            response = handle_message(msg_json)
            msg_json = json.loads(test_joinb_jobj)
            response = handle_message(msg_json)
            conn.send(response.encode("utf-8"))
            # conn.send(b"You made a connection. yay!")


if __name__ == "__main__":
    main()

# conn.send(b"You made a connection. yay!")
# sock.close()
