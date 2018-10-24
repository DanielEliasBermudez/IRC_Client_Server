#!usr/bin/env python3

import argparse

"""
Initial (very early) proof of concept for command parser. Not sure if this is the best route.
argparse is really useful but has a few issues for our use case, the worst of which is how it handles parsing failures.
As far as I can tell all it does it print the error the stderr and exit. We can wrap it in a try/except to prevent
the process from exiting but i'm not sure if it's possible to capture the error type/message. 
I'll have to look into that further...

Good news is argparse can be fed a list in place of sys.argv, so we could use it to parse commands inside a running
client or server process.
"""

def parseJoin(joinParser):
    joinParser.add_argument('command', nargs=1, type=str, help='the join command')
    joinParser.add_argument('channels', nargs=1, type=str, help='comma-separated list of channels to join')
    joinParser.add_argument('keys', nargs='?', help='optional keys to channels in "channels"')
    args = joinParser.parse_args()
    print('you parsed JOIN! here are its args: {}'.format(args))

def parseList(listParser):
    print('you parsed LIST! here are its args: {}'.format(args))
    # ... and then we parse the args for LIST

def parsePart(partParser):
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
    subparsers = parser.add_subparsers()
    commandParser = subparsers.add_parser(args.command)
    ircCommands[args.command](commandParser)
else:
    parser.print_help()
