#!usr/bin/env python3

import socket
import sys
import command_parser as parser
import json

HOST = "127.0.0.1"
PORT = 8080
NICK = "boris"


def buildPacket(argsDict):
    packetDict = {}
    dataDict = {}
    packetDict["nick"] = NICK
    packetDict["command"] = argsDict.pop("command", None)
    if not packetDict["command"]:
        return -1
    else:
        for key in argsDict:
            dataDict[key] = argsDict[key]
        packetDict["data"] = argsDict
        return json.dumps(packetDict)


# parse commandline
args = parser.parseCommand(sys.argv)
if args:
    # convert argparse Namespace object to json string and send to server as byte array
    # print('vars: {}'.format(vars(args)))
    # json = json.dumps(vars(args))
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
