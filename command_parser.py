#!usr/bin/env python3

import argparse
import sys
import re

"""
Initial (very early) proof of concept for command parser. Not sure if this is the best route.
argparse is really useful but has a few issues for our use case, the worst of which is how it handles parsing failures.
As far as I can tell all it does it print the error the stderr and exit. We can wrap it in a try/except to prevent
the process from exiting but i'm not sure if it's possible to capture the error type/message. 
I'll have to look into that further...

Good news is argparse can be fed a list in place of sys.argv, so we could use it to parse commands inside a running
client or server process.
"""
# defines a realname: a string beginning with ':', can include a space (for first name and last name)
def realNameType(arg, pattern=re.compile(r":[A-Za-z0-9]+\s*[A-Za-z0-9]")):
    if not pattern.match(arg):
        raise argparse.ArgumentTypeError("realname must begin with ':'")
    return arg


# defines a room: a string beginning with '#'
def roomType(arg, pattern=re.compile(r"#[A-Za-z0-9]+")):
    if not pattern.match(arg):
        raise argparse.ArgumentTypeError("room must begin with '#'")
    return arg


# Functions to set up parsers for specific IRC commands
def parseUser(userParser, argv):
    userParser.add_argument("nick")
    userParser.add_argument("realname", type=realNameType)
    userParser.add_argument("lastname", nargs="?")
    try:
        args = userParser.parse_args(argv)
    except:
        return None
    if args.lastname:
        args.realname += " " + args.lastname
    del args.lastname
    return args


def parseJoin(joinParser, argv):
    joinParser.add_argument("room", type=roomType)
    try:
        return joinParser.parse_args(argv)
    except:
        return None


def parseList(listParser, argv):
    listParser.add_argument("--rooms")
    listParser.add_argument("--server")
    try:
        return listParser.parse_args(argv)
    except:
        return None


def parsePart(partParser, argv):
    partParser.add_argument("rooms")
    partParser.add_argument("message", nargs="*")
    try:
        args = partParser.parse_args(argv)
    except:
        return None
    args.message = " ".join(args.message)
    return args


def parseQuit(quitParser, argv):
    quitParser.add_argument("message", nargs="*")
    try:
        args = quitParser.parse_args(argv)
    except:
        return None
    args.message = " ".join(args.message)
    return args

def parseNames(namesParser, argv):
    namesParser.add_argument("--rooms")
    try:
        return namesParser.parse_args(argv)
    except:
        return None


ircCommands = {
    "join": parseJoin,
    "list": parseList,
    "part": parsePart,
    "quit": parseQuit,
    "names": parseNames,
    "user": parseUser,
}


def parseCommand(argv):
    if len(argv) > 0:
        commandArg = argv[0]
    else:
        print("no arguments received")
        return None

    command = ircCommands.get(commandArg)
    if command:
        parser = argparse.ArgumentParser(description="parse IRC command")
        parser.add_argument("command", help="a supported IRC command")
        args = command(parser, argv)
        parser.parse_args
    else:
        print("command not supported: {}".format(commandArg))
        return None
    return args


if __name__ == "__main__":
    args = parseCommand(sys.argv[1:])
    print(args)
