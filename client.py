#!usr/bin/env python3

import socket
import sys
import command_parser as parser
import json

HOST = "127.0.0.1"
PORT = 8080
NICK = "boris"

def buildPacket(argsDict):
    nick = argsDict.get("nick")
    command = argsDict.get("command")
    if not command or not nick:
        return None
    else:
        return json.dumps(argsDict)

# parse commandline
args = parser.parseCommand(sys.argv)
if args:
    json = buildPacket(vars(args))
    print("json: {}".format(json))
    if not json:
        print("Error: could not serialize command")
        exit()
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Error: could not connect to server")
        exit()
    sock.send(json.encode("utf-8"))
    message = sock.recv(4096)
    print(message.decode("utf-8"))
    sock.close()
