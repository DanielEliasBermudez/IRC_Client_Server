#!usr/bin/env python3

import socket
import sys
import command_parser as parser
import json
import select
import threading

HOST = "127.0.0.1"
PORT = 8080

userDict = {"nick": None}
e = threading.Event()


def buildPacket(argsDict):
    command = argsDict.get("command")
    if userDict["nick"] == None or command == "user":
        nick = argsDict.get("nick")
        userDict["nick"] = nick
    nick = userDict["nick"]
    argsDict["nick"] = nick
    if not command or not nick:
        return None
    else:
        return json.dumps(argsDict)


def establishConn():
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    #sock.settimeout(5)
    try:
        sock.connect((HOST, PORT))
        t = threading.Thread(target=recvDaemon, args=[sock])
        t.start()
    except ConnectionRefusedError:
        print("Error: could not connect to server")
    return sock

def recvDaemon(socket):
    while True:
        e.clear()
        data = socket.recv(4096)
        responseDict = json.loads(data.decode("utf-8"))
        response = responseDict.get("response")
        if not response:
            print("Error: received empty response from server")
        else:
            print(response)
            e.set()


sock = establishConn()
while True:
    argv = input("> ")
    argv = argv.split()
    args = parser.parseCommand(argv)
    if args:
        jsonString = buildPacket(vars(args))
        if not jsonString:
            print("Error: no username set. Please run 'user' command first")
            continue
        sock.sendall(jsonString.encode("utf-8"))
        e.wait()
        #try:
        #    message = sock.recv(4096)
        #except socket.timeout:
        #    print("Error: connection to server timed out")
        #    exit()
        #responseDict = json.loads(message)
        #response = responseDict.get("response")
        #if not response:
        #    print("Error: received empty response from server")
        #else:
        #    print(response)
        # sock.close()
        #if args.command == "quit":
        #    exit()
