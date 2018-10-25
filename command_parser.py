#!usr/bin/env python3

import argparse
import sys

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
    joinParser.add_argument('channels', nargs=1, help='comma-separated list of channels to join')
    joinParser.add_argument('--keys', nargs='?', help='optional keys to channels in "channels"')

def parseList(listParser):
    listParser.add_argument('--channels', nargs='?', help='optional comma-separated list of channels to list')
    listParser.add_argument('--server', nargs='?', help='optional server to forward command to')

def parsePart(partParser):
    partParser.add_argument('channels', nargs=1, help='comma-separated list of channels to join')
    partParser.add_argument('--message', nargs='?', help='optional message')

ircCommands = {
    'JOIN': parseJoin,
    'LIST': parseList,
    'PART': parsePart,
}

if len(sys.argv) > 1:
    commandArg = sys.argv[1]
else:
    print('no arguments received')
    exit()

command = ircCommands.get(commandArg)
if command:
    parser = argparse.ArgumentParser(description='parse IRC command')
    parser.add_argument('command', help='a supported IRC command')
    command(parser)
    args = parser.parse_args()
    print('you parsed {}! here are its args: {}'.format(commandArg, args))
else:
    print('command not supported: {}'.format(commandArg))
