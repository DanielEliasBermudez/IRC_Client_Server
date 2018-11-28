#!usr/bin/env python3

import socket
import sys
import command_parser as parser
import json
import threading
import datetime

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
    try:
        sock.connect((HOST, PORT))
        receiver = threading.Thread(target=recvDaemon, args=[sock])
        client = threading.Thread(target=clientProcess, args=[receiver])
        receiver.start()
        client.start()
    except ConnectionRefusedError:
        print("Error: could not connect to server")
        exit()
    return sock, receiver, client


def recvDaemon(socket):
    while True:
        e.clear()
        data = socket.recv(4096)
        if not data:
            return
        responseDict = json.loads(data.decode("utf-8"))
        response = responseDict.get("response")
        command = responseDict.get("command")
        if not response:
            if command == "list":
                print("There are no rooms on the server")
            else:
                print("Error: received empty response from server")
            e.set()
            printPrompt()
            continue
        elif response == "ping":
            continue
        else:
            now = datetime.datetime.now()
            print(
                "\n[{}:{}:{}] - {}".format(now.hour, now.minute, now.second, str(response).rstrip())
            )
            e.set()
            printPrompt()

def clientProcess(receiver):
    while True:
        if not receiver.is_alive():
            return
        argv = sys.stdin.readline()
        argv = argv.split()
        args = parser.parseCommand(argv)
        if args:
            jsonString = buildPacket(vars(args))
            if not jsonString:
                print("Error: no username set. Please run 'user' command first")
                printPrompt()
                continue
            sock.sendall(jsonString.encode("utf-8"))
            if args.command == "quit":
                return
            try:
                e.wait(5)
            except:
                print("Error: response from server timed out")
                return
        else:
            printPrompt()
            continue

def printPrompt():
    sys.stdout.write("\n> ")
    sys.stdout.flush()

sock, recvDaemon, client = establishConn()
printPrompt()
while True:
    if not recvDaemon.is_alive():
        if not client.is_alive():
            sys.exit()
        print("Error: connection to server was lost")
        sys.exit()
