#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
import sys
import os

SERVER = 'irc.freenode.net' # irc server
PORT = 6667 # port on in irc server
CHANNEL = '#NanoBot' # channel you want to connect
ADMIN = 'harenson' # Bot's administrator account
NICKNAME = 'HaBot'
PASSWORD = 'helloworld'
REALNAME = 'Harry\'s Bot'
DEBUG = 1 # to show or not messages to console
read_buffer = '' # take the responses from the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('%s' % SERVER, PORT))

def send_pong(request):
    received = request
    if 'PING' in received:
        s.send('%s\r\n' % received.replace('PING', 'PONG'))

def show_debug(text):
    current_date = time.strftime('%A %d %B %Y %I:%M:%S')
    text = str(text)
    if DEBUG:
        print('%s -- %s' % (current_date, text))


def show_help(autor_message):
    help_text = ['%s: say <text> - Reply back with <text>' % NICKNAME,
                 '%s: <hello|hola> - Reply back with "hello" or "hola", ' \
                     'depending of the user input' % NICKNAME,
                 '%s: help - Display all the available commands' % NICKNAME]
    for message in help_text:
        s.send('PRIVMSG %s :%s\r\n' % (autor_message, message))

# auth
show_debug('Sending nick')
s.send('NICK %s\r\n' % NICKNAME)

show_debug('Sending Pong')
send_pong(s.recv(1024))

show_debug('Sending user')
s.send('USER %s localhost %s :%s\r\n' % (NICKNAME, SERVER, REALNAME))

show_debug('Sending identification')
s.send('PRIVMSG nickserv :IDENTIFY %s\r\n' % PASSWORD)

while True:
    try:
        read_buffer += s.recv(1024)
        if not read_buffer.endswith('\r\n'):
                continue # returns the control to the beginning of the while loop

        for line in read_buffer.splitlines():
            show_debug('Received: %s' % line) # console output

            if '001' in line: # '001' means the bot is connected to the server
                show_debug('Joining channel %s' % CHANNEL)
                s.send('JOIN %s\r\n' % CHANNEL) # connect to the channel
                s.send('PRIVMSG %s :Hello everyone >=)\r\n' % CHANNEL) # say hi to channel

            if 'PING' in line: # ping request
                send_pong(line) # send ping response


            # example message => :johndoe!uid3023@gateway/web/irccloud.com/x-wtbebjjfbcoqzjtm PRIVMSG #ChannelName :HaBot: say hello world
            new_message = line.split(':', 3) # new message sent to the channel. Used to listen the commands

            # find(PRIVMSG) is to check that the message comes from an irc channel
            if line.find('PRIVMSG') != -1 and new_message[2] == NICKNAME: # subject of the message
                autor_message = new_message[1][0:new_message[1].find('!')]
                message = new_message[3].strip() # remove the left and right spaces of message text

                try:
                    # separate the command of the parameters
                    (command, parameters) = message.split(' ', 1)
                except ValueError:
                    # if the command doesn't take parameters
                    command = message
                    parameters = ''

                command = str(command).lower()

                if command == 'logout':
                    if autor_message == ADMIN: # this command just can be executed by the Bot's administrator
                        s.send('QUIT\r\n') # close the connection
                    else:
                        s.send('PRIVMSG %s :%s: You\'re not authorized to ' \
                               'execute this command.\r\n' %
                                (CHANNEL, autor_message))
                
                if command == 'help': # send the help text with all the public commands available
                    show_help(autor_message)

                if command == 'say': # Reply back with the autor_message text
                    s.send('PRIVMSG %s :%s\r\n' % (CHANNEL, parameters))

                if command in ['hello', 'hola']: # Reply back with "hello" or "hola", depending of the user input
                    s.send('PRIVMSG %s :%s: %s\r\n' %
                            (CHANNEL, autor_message, command))

        read_buffer = ''
    except KeyboardInterrupt:
        show_debug('Stopped by user')
        s.close()
        exit(0)
    except Exception, e:
        exc_type, exc_message, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # show the exception type, filename and line from where the exception was raised
        show_debug('Exception raised => type: %s, filename: %s, line: %s' %
                    (type(e).__name__, filename, exc_tb.tb_lineno))

        s.close()
        exit(0)



