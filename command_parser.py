#!usr/bin/env python3

import argparse

"""
Initial (very early) proof of concept for command parser. Not sure if this is the best route.
argparse is really useful but i don't think we'll really want to be parsing sys.argv (presumably
the client will already be running when the command is issued). Haven't dug deep enough into argparse
yet to know whether it can be leveraged in other ways. Still, this could be a good general framework 
for parsing the IRC commands. Unfortunately there is enough format variance between commands that some 
kind of per-command parsing will probably be necessary... this general pattern might be a good way to do it.
"""

def parseJoin(args):
    print('you parsed JOIN! here are its args: {}'.format(args))
    # ... and then we parse the args for JOIN

def parseList(args):
    print('you parsed LIST! here are its args: {}'.format(args))
    # ... and then we parse the args for LIST

def parsePart(args):
    print('you parsed PART! here are its args: {}'.format(args))
    # ... and then we parse the args for PART

ircCommands = {
    'JOIN': parseJoin,
    'LIST': parseList,
    'PART': parsePart,
}

parser = argparse.ArgumentParser(description='parse IRC command')
parser.add_argument('command', help='a supported IRC command')
parser.add_argument('arguments', nargs='*', help='arguments to the IRC command specified by "command"')
args = parser.parse_args()

command = ircCommands.get(args.command)

if command:
    ircCommands[args.command](args.arguments)
else:
    parser.print_help()
