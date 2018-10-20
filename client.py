#!usr/bin/env python3

import socket

HOST = '127.0.0.1'
PORT = 8080

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
sock.connect((HOST, PORT))
message = sock.recv(4096)
print(str(message))
sock.close()