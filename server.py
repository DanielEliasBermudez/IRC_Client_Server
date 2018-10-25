#!usr/bin/env python3
import socket
import json

# test json object
test_python_dict = {
    "command": "list",
    "user": "Alice",
    "target": "room1",
    "response": "",
}
test_json_obj = json.dumps(test_python_dict)

# This will create listening connection TCP socket on localhost:8080
HOST = "127.0.0.1"
PORT = 8080
# sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sock:
    sock.bind((HOST, PORT))
    sock.listen()
    conn, address = sock.accept()
    with conn:
        print("Connected to {}".format(address))
        data = conn.recv(1024)
        print(data.decode("utf-8"))
        # parse the json here
        msg_json = json.loads(test_json_obj)
        print(msg_json)
        conn.send(b"You made a connection. yay!")
# conn.send(b"You made a connection. yay!")
# sock.close()
