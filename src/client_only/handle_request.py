# handle_request.py

from client_only.handle_send_file_request import handle_send_file_request
from client_only.handle_recv_file_request import handle_recv_file_request
from general.message import send_msg_with_prefix, recv_decoded_content

def handle_request(msg, client, chunkSize, maxFileSize, extList):
    lowerCasedMsg = msg.lower()
    match lowerCasedMsg:
        case 'send':
            # Client wants to store a file in the room
            handle_send_file_request(client, chunkSize, maxFileSize, extList)
        case 'recv':
            # Client wants to download a file from the room
            handle_recv_file_request(client)
        case 'msg history':
            # Client wants to display all messages history of this room
            handle_display_history_request(client, 'msg', chunkSize)
        case 'file history':
            # Client wants to display all file stored in this room
            handle_display_history_request(client, 'file', chunkSize)
        case 'clear msg history':
            # Client wants to clear all messages history of this room
            handle_clear_history_request(client, 'msg', chunkSize)
        case 'clear file history':
            # Client wants to clear all file stored in this room
            handle_clear_history_request(client, 'file', chunkSize)
        case 'clear all history':
            # Client wants to clear both messages and files in this room
            handle_clear_history_request(client, 'all', chunkSize)
        case _:
            # Client wants to send a normal message to the room
            send_msg_with_prefix(client, msg, 1)
    return

def handle_display_history_request(client, historyToDisplay, chunkSize):
    # Send a request to server for displaying msg history of the room
    #   client is in, and display it only to this client.
    # historyToDisplay is either 'msg' or 'file'.
    # Prefix for displaying msg/file history: 4.
    send_msg_with_prefix(client, historyToDisplay, 4)
    response = recv_decoded_content(client, chunkSize)
    print(response)
    return

def handle_clear_history_request(client, historyToClear, chunkSize):
    # Send a request to server for deleting msg history of the room
    #   client is in.
    # historyToClear is either 'msg', 'file' or 'all'.
    # Prefix for clearing msg/file/all history: 5.
    send_msg_with_prefix(client, historyToClear, 5)
    response = recv_decoded_content(client, chunkSize)
    print(response)
    return
