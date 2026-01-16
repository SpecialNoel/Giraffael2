# handle_request.py

from client_only.handle_client_actions.handle_send_file_request import handle_send_file_request
from client_only.handle_client_actions.handle_recv_file_request import handle_recv_file_request
from general.message import send_msg_with_prefix

def handle_request(msg, client, chunk_size, max_file_size, ext_list): 
    lower_cased_msg = msg.lower()
    if lower_cased_msg == 'send': 
        # Client wants to store a file in the room
        handle_send_file_request(client, chunk_size, max_file_size, ext_list)
    elif lower_cased_msg == 'recv':
        # Client wants to download a file from the room
        handle_recv_file_request(client)
    elif lower_cased_msg == 'msg history':
        # Client wants to display all messages history of this room
        handle_display_history_request(client, 'msg')
    elif lower_cased_msg == 'file history':
        # Client wants to display all file stored in this room
        handle_display_history_request(client, 'file')
    elif lower_cased_msg == 'clear msg history':
        # Client wants to clear all messages history of this room
        handle_clear_history_request(client, 'msg')
    elif lower_cased_msg == 'clear file history':
        # Client wants to clear all file stored in this room
        handle_clear_history_request(client, 'file')
    elif lower_cased_msg == 'clear all history':
        # Client wants to clear both messages and files in this room
        handle_clear_history_request(client, 'all')
    elif lower_cased_msg == 'ai suggestion':
        # Client wants to ask OpenAI model for message suggestions
        handle_suggestion_request(client)
    else:
        # Client wants to send a normal message to the room
        send_msg_with_prefix(client, msg, 1)
    return

def handle_display_history_request(client, history_to_display):
    # Send a request to server for displaying msg history of the room
    #   client is in, and display it only to this client.
    # history_to_display is either 'msg' or 'file'.
    # Prefix for displaying msg/file history: 4.
    send_msg_with_prefix(client, history_to_display, 4)
    # Response is received in recv_from_server(), case 4
    return

def handle_clear_history_request(client, history_to_clear):
    # Send a request to server for deleting msg history of the room
    #   client is in.
    # history_to_clear is either 'msg', 'file' or 'all'.
    # Prefix for clearing msg/file/all history: 5.
    send_msg_with_prefix(client, history_to_clear, 5)
    # Response is received in recv_from_server(), case 5
    return

def handle_suggestion_request(client):
    # Send a request to server for prompting OpenAI model to generate
    #   message suggestions for the client to choose to send to chatroom.
    # Prefix for OpenAI model message suggestion: 6
    send_msg_with_prefix(client, 'ai', 6)
    # Response is received in recv_from_server(), case 6
    return