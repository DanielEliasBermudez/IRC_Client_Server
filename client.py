#!usr/bin/env python3

import socket
import sys
import command_parser as parser
import json

HOST = "127.0.0.1"
PORT = 8080

userDict = {"nick": None}


def buildPacket(argsDict):
    if userDict["nick"] == None:
        nick = argsDict.get("nick")
        userDict["nick"] = nick
    nick = userDict["nick"]
    argsDict["nick"] = nick
    command = argsDict.get("command")
    if not command or not nick:
        return None
    else:
        return json.dumps(argsDict)


while True:
    argv = input("> ")
    argv = argv.split()
    args = parser.parseCommand(argv)
    if args:
        jsonString = buildPacket(vars(args))
        if not jsonString:
            print("Error: could not serialize command")
            exit()
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        try:
            sock.connect((HOST, PORT))
        except ConnectionRefusedError:
            print("Error: could not connect to server")
            exit()
        sock.send(jsonString.encode("utf-8"))
        message = sock.recv(4096)
        responseDict = json.loads(message)
        print(responseDict["response"])
        sock.close()
