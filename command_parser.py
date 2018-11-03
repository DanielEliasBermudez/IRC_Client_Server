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
# this works but i can't get argparse to tolerate spaces... gonna look into it more tommorow
def realNameType(arg, pattern=re.compile(r":[A-Za-z0-9]+\s*[A-Za-z0-9]")):
    if not pattern.match(arg):
        raise argparse.ArgumentTypeError
    return arg


# Doesn't work yet
# def roomType(arg, pattern=re.compile(r"#[A-Za-z0-9]+")):
#    if not pattern.match(arg):
#        raise argparse.ArgumentTypeError
#    return arg

# Functions to set up parsers for specific IRC commands
def parseUser(userParser):
    userParser.add_argument("nick")
    userParser.add_argument("realname", type=realNameType)


def parseJoin(joinParser):
    joinParser.add_argument("room")


def parseList(listParser):
    listParser.add_argument("--rooms")
    listParser.add_argument("--server")


def parsePart(partParser):
    partParser.add_argument("rooms")
    partParser.add_argument("message")


def parseQuit(quitParser):
    quitParser.add_argument("message")


def parseNames(namesParser):
    namesParser.add_argument("--rooms")


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
        command(parser)
        args = parser.parse_args(argv)
    #        print("you parsed {}! here are its args: {}".format(commandArg, args))
    else:
        print("command not supported: {}".format(commandArg))
        return None
    return args


if __name__ == "__main__":
    parseCommand(sys.argv)
