# send_to_server.py

from client_only.handle_request import handle_request
from general.file_transmission import *
from general.message import (rstrip_message, send_msg_with_prefix, 
                             recv_decoded_content)

def send_msg_to_server(client, shutdownEvent, chunkSize, 
                       maxFileSize, extList):
        # Send rules to the client console
        display_rule()

        # Send message to server
        while not shutdownEvent.is_set():            
            msg = rstrip_message(input())
            
            if not msg:
                # Empty message -> client closes connection
                print('Disconnected from the channel.\n')
                shutdownEvent.set()
                client.close() # will be detected by server's 'recv()'
                break
            
            handle_request(msg, client, chunkSize, maxFileSize, extList)
        print('Client sender thread stopped.')
        return
    
def recv_user_input():
    msg = rstrip_message(input())
    # If client input empty message, make them input again
    while msg == '':
        print('Empty message detected. Please type your message:')
        msg = rstrip_message(input())
    return msg

def send_user_input(client, msg, chunkSize):    
    send_msg_with_prefix(client, msg, 0)
    response = recv_decoded_content(client, chunkSize)
    return msg, response
 
def send_username(client, chunkSize):
    print('Input your username:')
    username = recv_user_input()
    return send_user_input(client, username, chunkSize)
    
def send_decision_on_room(client, chunkSize):
    msg = recv_user_input()
    return send_user_input(client, msg, chunkSize)

def send_room_code(client, chunkSize):
    print('Input room code here:\n')
    roomCode = recv_user_input()
    return send_user_input(client, roomCode, chunkSize)
