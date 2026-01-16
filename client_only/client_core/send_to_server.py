# send_to_server.py

from client_only.client_core.handle_request import handle_request
from general.file_transmission import *
from general.message import (rstrip_message, 
                             send_msg_with_prefix, 
                             recv_decoded_content)

def send_msg_to_server(client, shutdown_event, chunk_size, 
                       max_file_size, ext_list):
    # Send rules to the client console
    display_rule()

    # Send message to server
    while not shutdown_event.is_set():            
        msg = rstrip_message(input())
        
        if not msg:
            # Empty message -> client closes connection
            print('Disconnected from the channel.\n')
            shutdown_event.set()
            client.close() # will be detected by server's 'recv()'
            break
        
        handle_request(msg, client, chunk_size, max_file_size, ext_list)
    print('Client sender thread stopped.')
    return
    
def recv_user_input():
    msg = rstrip_message(input())
    # If client input empty message, make them input again
    while msg == '':
        print('Empty message detected. Please type your message:')
        msg = rstrip_message(input())
    return msg

def send_user_input(client, msg, chunk_size):    
    send_msg_with_prefix(client, msg, 0)
    response = recv_decoded_content(client, chunk_size)
    return msg, response
 
def send_username(client, chunk_size):
    print('Input your username:')
    username = recv_user_input()
    return send_user_input(client, username, chunk_size)
    
def send_decision_on_room(client, chunk_size):
    msg = recv_user_input()
    return send_user_input(client, msg, chunk_size)

def send_room_code(client, chunk_size):
    print('Input room code here:\n')
    room_code = recv_user_input()
    return send_user_input(client, room_code, chunk_size)
