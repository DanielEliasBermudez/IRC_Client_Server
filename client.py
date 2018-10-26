#!usr/bin/env python3

import socket
import sys
import command_parser as parser
import json

HOST = "127.0.0.1"
PORT = 8080

# parse commandline
args = parser.parseCommand(sys.argv)
if args:
    # convert argparse Namespace object to json string and send to server as byte array
    json = json.dumps(vars(args)) 
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print('Error: could not connect to server')
        exit()
    sock.send(json.encode('utf-8'))
    message = sock.recv(4096)
    print(message.decode("utf-8"))
    sock.close()
