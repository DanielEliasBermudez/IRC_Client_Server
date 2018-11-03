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
list_of_users = []
list_of_rooms = []

# Test json objects
# test_user_dict = {"command": "user", "nick": "Alice", "real_name": "Alice A"}
# test_user_jobj = json.dumps(test_user_dict)
# test_join_dict = {"command": "join", "nick": "Alice", "room": "room1"}
# test_join_jobj = json.dumps(test_join_dict)

# test_userb_dict = {"command": "user", "nick": "Boris", "real_name": "Boris P"}
# test_userb_jobj = json.dumps(test_userb_dict)
# test_joinb_dict = {"command": "join", "nick": "Boris", "room": "room1"}
# test_joinb_jobj = json.dumps(test_joinb_dict)

# test_list_dict = {"command": "list", "nick": "Alice"}
# test_list_jobj = json.dumps(test_list_dict)


def handle_message(msg):
    """
    Will look at the message json object and choose the correct handler based on the 
    command key.
    """
    command = msg["command"]
    nick_name = msg["nick"]
    response = ""

    if command == "user":
        response = handle_user_cmd(msg)
    elif verify_user(nick_name):
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
        elif command == "list":
            response = handle_list_cmd(msg)
    else:
        print("Unknown user {}".format(nick_name))
        reply = "NOT OK - User {} unknown".format(nick_name)
        response = build_json_response(command, nick_name, reply)
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
    command = msg["command"]
    nick_name = msg["nick"]
    if verify_user(nick_name):
        reply = "NOT OK - User {} already on the server".format(nick_name)
        return build_json_response(command, nick_name, reply)

    new_user = user.User(nick_name, msg["real_name"])
    list_of_users.append(new_user)
    reply = "User {} joined the server.".format(nick_name)
    # TODO remove
    # print("Command - User")
    # print("Nick: {}".format(msg["nick"]))
    # print("Real Name: {}".format(msg["real_name"]))
    print("User added")
    return build_json_response(command, nick_name, reply)


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
    command = msg["command"]
    room_name = msg["room"]
    nick_name = msg["nick"]
    new_room = room.Room(room_name)
    new_room.add_user(nick_name)
    list_of_rooms.append(new_room)
    print("Created a room")
    reply = "Room {} created.\nUser {} joined room {}.".format(
        room_name, nick_name, room_name
    )
    # response_msg = {"command": "join", "nick": nick_name, "response": reply}
    # return json.dumps(response_msg)
    return build_json_response(command, nick_name, reply)


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
    command = msg["command"]
    room_name = msg["room"]
    nick_name = msg["nick"]
    room.add_user(nick_name)
    print("Joined existing room")
    reply = "User {} joined room {}.".format(nick_name, room_name)
    # response_msg = {"command": "join", "nick": nick_name, "response": reply}
    # return json.dumps(response_msg)
    return build_json_response(command, nick_name, reply)


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
    # response_msg = {"command": "list", "nick": msg["nick"], "response": room_names}
    # return json.dumps(response_msg)
    return build_json_response(msg["command"], msg["nick"], room_names)


def verify_user(user_nick):
    """
    Return True if the user is already on the server
    """
    for user in list_of_users:
        if user.get_nick() == user_nick:
            return True
    return False


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
    data = types.SimpleNamespace(addr=address, inbound="", outbound="")
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
            data.outbound = handle_message(json.loads(recv_data))
        # else:
        #     # TODO remove
        #     print("closing connection to ", data.addr)
        #     sel.unregister(data_socket)
        #     data_socket.close()
    if mask & selectors.EVENT_WRITE:
        if data.outbound:
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

# conn.send(b"You made a connection. yay!")
# sock.close()
