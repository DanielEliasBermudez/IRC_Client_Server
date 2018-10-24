#!usr/bin/env python3
import socket

HOST = "127.0.0.1"
PORT = 8080

sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
sock.bind((HOST, PORT))

# TODO need to update 1 to another value
# 1 represents numbe of connections accepted by the socket
sock.listen(1)
conn, address = sock.accept()

conn.send(b"You made a connection. yay!")

sock.close()
