#!usr/bin/env python3
import socket
import json
import user
import room
import selectors
import types

HOST = "127.0.0.1"
PORT = 8080
sel = selectors.DefaultSelector()
# list of user objects
list_of_users = []
# list of room objects
list_of_rooms = []

# Test json objects
# test_user_dict = {"command": "user", "nick": "Alice", "realname": "Alice A"}
# test_user_jobj = json.dumps(test_user_dict)
# test_join_dict = {"command": "join", "nick": "Alice", "room": "room1"}
# test_join_jobj = json.dumps(test_join_dict)

# test_userb_dict = {"command": "user", "nick": "Boris", "realname": "Boris P"}
# test_userb_jobj = json.dumps(test_userb_dict)
# test_joinb_dict = {"command": "join", "nick": "Boris", "room": "room1"}
# test_joinb_jobj = json.dumps(test_joinb_dict)

# test_list_dict = {"command": "list", "nick": "Alice"}
# test_list_jobj = json.dumps(test_list_dict)


def handle_message(msg, data, socket):
    """
    Will look at the message json object and choose the correct handler based on the 
    command key.
    """
    command = msg["command"]
    nick_name = msg["nick"]
    response = ""

    if command == "user":
        response = handle_user_cmd(msg, data)
    elif verify_user(nick_name):
        if command == "join" or command == "create":
            response = handle_join_cmd(msg)
        elif command == "list":
            response = handle_list_cmd(msg)
        elif command == "part":
            response = handle_part_cmd(msg)
        elif command == "privmsg":
            response = handle_privmsg_cmd(msg)
        elif command == "quit":
            handle_quit_cmd(msg, socket)
    else:
        print("Unknown user {}".format(nick_name))
        reply = "NOT OK - User {} unknown".format(nick_name)
        response = build_json_response(command, nick_name, reply)
    return response


def handle_user_cmd(msg, data):
    """
    Handles the user command by adding the user to the list of users.
    User json object example:
    {
        "command" : "user",
        "nick" : "name of user",
        "realname" : "real name of user",
    }
    """
    command = msg["command"]
    nick_name = msg["nick"]
    if verify_user(nick_name):
        reply = "NOT OK - User {} already on the server".format(nick_name)
        return build_json_response(command, nick_name, reply)

    new_user = user.User(nick_name, msg["realname"])
    list_of_users.append(new_user)
    data.user_nick = nick_name
    reply = "User {} joined the server.".format(nick_name)
    # TODO remove
    # print("Command - User")
    # print("Nick: {}".format(msg["nick"]))
    # print("Real Name: {}".format(msg["realname"]))
    print("User added")
    return build_json_response(command, nick_name, reply)


def handle_join_cmd(msg):
    """
    Adds a user to a room. Creates the room if it does not already exist.
    User json object example:
    {
        "command" : "join",
        "room" : "list of rooms"
        "nick" : "name of user",
    }
    """
    command = msg["command"]
    rooms = msg["room"]
    nick_name = msg["nick"]
    # in the case of 1 room passed in, rooms needs to be converted from a string -> list
    rooms = verify_rooms_are_in_a_list(rooms)
    for r in rooms:
        room_exists_value, room_obj = room_exists(r)
        if room_exists_value:
            # join room
            room_obj.add_user(nick_name)
            print("Joined existing room")
            reply = "User {} joined room {}.".format(nick_name, r)
            return build_json_response(command, nick_name, reply)
        else:
            # create room
            new_room = room.Room(r)
            new_room.add_user(nick_name)
            list_of_rooms.append(new_room)
            print("Created a room")
            reply = "Room {} created.\nUser {} joined room {}.".format(r, nick_name, r)
            return build_json_response(command, nick_name, reply)


def room_exists(room_name):
    """
    Return True if the room_name exists in the list of rooms on the server
    """
    for room in list_of_rooms:
        if room.get_name() == room_name:
            return (True, room)
    return (False, None)


def handle_list_cmd(msg):
    """
    List all rooms on the server
    {
        "command" : "list",
        "nick" : "name of user"
    }
    """
    room_names = []
    for r in list_of_rooms:
        room_names.append(r.get_name())
    print("Listing rooms")
    return build_json_response(msg["command"], msg["nick"], room_names)


def handle_part_cmd(msg):
    """
    User removed from specified room
    Part json object example:
    {
        "command" : "part",
        "room" : "list of rooms"
        "nick" : "name of user",
    }
    """
    # TODO update to include message sending
    command = msg["command"]
    rooms = msg["rooms"]
    nick_name = msg["nick"]
    message = msg["message"]
    list_of_rooms_user_left = ""
    map_of_conns = sel.get_map()
    rooms = verify_rooms_are_in_a_list(rooms)

    for room in rooms:
        room_exists_value, room_obj = room_exists(room)
        if room_exists_value:
            print("User leaving room")
            room_obj.delete_user(nick_name)
            list_of_rooms_user_left += room
            list_of_rooms_user_left += ", "
            room_occupants = room_obj.get_list_of_users()
            for conn in map_of_conns.values():
                if (
                    conn.data is not None
                    and conn.data.user_nick in room_occupants
                    and conn.data.user_nick is not nick_name
                ):
                    if message is "":
                        leave_msg = "User {} left room {}.".format(nick_name, room)
                    else:
                        leave_msg = "User {} - {}.".format(nick_name, message)
                    conn.data.outbound += build_json_response(
                        command, conn.data.user_nick, leave_msg
                    )
    reply = "User {} left room(s) {}.".format(nick_name, list_of_rooms_user_left[:-2])
    return build_json_response(command, nick_name, reply)


def handle_privmsg_cmd(msg):
    """
    Send a user or a room a message
    Part json object example:
    {
        "command" : "privmsg",
        "nick" : "name of user",
        "msgtarget" : "target of message",
        "message" : "message"
    }
    """
    command = msg["command"]
    nick_name = msg["nick"]
    target = msg["msgtarget"]
    message = msg["message"]
    map_of_conns = sel.get_map()
    reply = ""
    # target is a list of rooms
    if target[0] == "#":
        rooms = verify_rooms_are_in_a_list(target)
        for room in rooms:
            room_exists_value, room_obj = room_exists(room)
            if room_exists_value:
                room_occupants = room_obj.get_list_of_users()
                for conn in map_of_conns.values():
                    if (
                        conn.data is not None
                        and conn.data.user_nick in room_occupants
                        and conn.data.user_nick is not nick_name
                    ):
                        conn.data.outbound += build_json_response(
                            command, conn.data.user_nick, message
                        )
                        print(message)
        reply = "Message sent."
    else:
        # build a json for target
        for conn in map_of_conns.values():
            if conn.data is not None and conn.data.user_nick == target:
                conn.data.outbound = build_json_response(
                    command, conn.data.user_nick, message
                )
        reply = "Message sent."
    return build_json_response(command, nick_name, reply)


def handle_quit_cmd(msg, sock):
    """
    Close a client connection to the server.
    Removes user from list of users, removes them from rooms, and
    sends a message to the server
    Quit json object example:
    {
        "command" : "quit",
        "nick" : "name of user",
        "message" : "message"
    }
    """
    command = msg["command"]
    nick_name = msg["nick"]
    message = msg["message"]
    map_of_conns = sel.get_map()

    # remove user from rooms
    for room in list_of_rooms:
        room_user_list = room.get_list_of_users()
        for user in room_user_list:
            if nick_name == user:
                quit_msg = "user {} removed from room {}".format(
                    nick_name, room.get_name()
                )
                print(quit_msg)
                room.delete_user(user)

    for user in list_of_users:
        if nick_name == user.get_nick():
            print("user removed")
            list_of_users.remove(user)

    user_left_msg = "User {} left the server".format(nick_name)
    for conn in map_of_conns.values():
        if conn.data is not None and conn.data.user_nick is not nick_name:
            conn.data.outbound = build_json_response(
                command, conn.data.user_nick, user_left_msg
            )

    print("closing connection")
    sel.unregister(sock)
    sock.close()


def verify_user(user_nick):
    """
    Return True if the user is already on the server
    """
    for user in list_of_users:
        if user.get_nick() == user_nick:
            return True
    return False


def verify_rooms_are_in_a_list(rooms):
    """
    Ensure that the comma-separated room list is of type list
    """
    if type(rooms) is not list:
        rooms = [rooms]
    return rooms


def build_json_response(command, nick, reply):
    """
    Build up the response json object
    """
    return json.dumps({"command": command, "nick": nick, "response": reply})


def handle_accept(data_socket):
    """
    Handle accepting a connection to the server
    """
    conn, address = data_socket.accept()
    # TODO remove
    print("accepted connection from ", address)
    conn.setblocking(False)
    # TODO remove
    # data = types.SimpleNamespace(addr=address, inbound="", outbound="", user_nick="")
    data = types.SimpleNamespace(addr=address, outbound="", user_nick="")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    """
    Service a connection waiting to read or write to the server
    """
    data_socket = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = data_socket.recv(1024)
        if recv_data:
            # TODO remove
            # print(key)
            # print(data_socket)
            # map_of_conns = sel.get_map()
            # print(map_of_conns[data_socket])
            # print(map_of_conns[data_socket].data)
            # print(map_of_conns[data_socket].data.outbound)
            data.outbound = handle_message(json.loads(recv_data.decode("utf-8")), data, data_socket)
        # else:
        #     # TODO remove
        #     print("closing connection to ", data.addr)
        #     sel.unregister(data_socket)
        #     data_socket.close()
    if mask & selectors.EVENT_WRITE:
        if data.outbound:
            print(data.outbound)
            data_socket.send(data.outbound.encode("utf-8"))
            data.outbound = ""


# This will create listening connection TCP socket on localhost:8080
def main():
    """
    Run a server on localhost that listens on port 8080
    
    """
    listen_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen()
    # TODO remove
    print("listening on", (HOST, PORT))
    listen_socket.setblocking(False)
    # only register the listening socket for reading
    sel.register(listen_socket, selectors.EVENT_READ, data=None)

    while True:
        events = sel.select(timeout=0)
        for key, mask in events:
            # if key data is empty, then a connection is trying to be established.
            if key.data is None:
                handle_accept(key.fileobj)
            else:
                service_connection(key, mask)

        # with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sock:
        #     sock.bind((HOST, PORT))
        #     sock.listen()
        #     conn, address = sock.accept()
        #     with conn:
        #         print("Connected to {}".format(address))
        #         data = conn.recv(1024)
        #         print(data.decode("utf-8"))
        #         # parse the json here - this should be the json that came thru the data. for
        #         # now I am just using a test json object

        #         # test user command
        #         msg_json = json.loads(test_user_jobj)
        #         response = handle_message(msg_json)
        #         # test create command
        #         msg_json = json.loads(test_join_jobj)
        #         response = handle_message(msg_json)
        #         # test 2nd user
        #         msg_json = json.loads(test_userb_jobj)
        #         response = handle_message(msg_json)
        #         # test join command
        #         msg_json = json.loads(test_joinb_jobj)
        #         response = handle_message(msg_json)
        #         # test list command
        #         msg_json = json.loads(test_list_jobj)
        #         response = handle_message(msg_json)

        #         conn.send(response.encode("utf-8"))
        #         # conn.send(b"You made a connection. yay!")


if __name__ == "__main__":
    main()
