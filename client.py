#!usr/bin/env python3

import socket
import sys
import command_parser as parser
import json

HOST = "127.0.0.1"
PORT = 8080

userDict = {"nick": None}


def buildPacket(argsDict):
    command = argsDict.get("command")
    if userDict["nick"] == None or command == 'user':
        nick = argsDict.get("nick")
        userDict["nick"] = nick
    nick = userDict["nick"]
    argsDict["nick"] = nick
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
            print("Error: no username set. Please run 'user' command first")
            continue
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect((HOST, PORT))
        except ConnectionRefusedError:
            print("Error: could not connect to server")
            continue
        sock.send(jsonString.encode("utf-8"))
        try:
            message = sock.recv(4096)
        except socket.timeout:
            print("Error: connection to server timed out")
            exit()
        responseDict = json.loads(message)
        response = responseDict.get("response")
        if not response:
            print("Error: received empty response from server")
        else:
            print(response)
        sock.close()
        if args.command == "quit":
            exit()
