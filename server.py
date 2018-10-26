#!usr/bin/env python3
import socket
import json

HOST = "127.0.0.1"
PORT = 8080

# test json object
test_python_dict = {
    "command": "user",
    "name": "Alice",
    "real_name": "Alice A",
    "server": HOST,
}
test_json_obj = json.dumps(test_python_dict)
list_of_users = []


def handle_message(msg):
    """
    Will look at the message json object and choose the correct handler based on the 
    command key.
    """
    if msg["command"] == "user":
        handle_user_cmd(msg)


def handle_user_cmd(msg):
    """
    Handles the user command by adding the user to the list of users.
    User json object example:
    {
        "command" : "user"
        "name" : "name of user",
        "real_name" : "real name of user",
        "server" : "server ip"
    }
    """
    print("Command - User")
    print("Name: {}".format(msg["name"]))
    print("Real Name: {}".format(msg["real_name"]))
    print("Server: {}".format(msg["server"]))


# This will create listening connection TCP socket on localhost:8080
# HOST = "127.0.0.1"
# PORT = 8080
# sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
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
        msg_json = json.loads(test_json_obj)
        handle_message(msg_json)
        conn.send(b"You made a connection. yay!")

# conn.send(b"You made a connection. yay!")
# sock.close()
