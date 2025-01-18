# send_to_server.py


from general.file_transmission import (get_valid_filepath,
                                      create_metadata, send_metadata,
                                      send_file)
from general.message import rstrip_message, add_prefix


def display_rule():
    print('\nInput message to send to the chatroom, ',
            'or\nInput [send] to send a file.')
    print('Press [Enter/Return] key to disconnect.\n')
    return


def send_msg_to_server(client, shutdownEvent, msgContentSize):
        # Sent rules to the client console
        display_rule()

        # Send message to server
        while not shutdownEvent.is_set():            
            msg = rstrip_message(input())
            
            # Empty message -> client closes connection
            if not msg:
                print('Disconnected from the channel.\n')
                shutdownEvent.set()
                client.close() # will be detected by server's 'recv()'
                break
            elif msg.lower() == 'send': # Client wants to send a file to server
                handle_send_file_request(client, msgContentSize)
            else: # Client wants to send a normal message to server
                msgWithPrefix = add_prefix(msg.encode(), 0)
                client.send(msgWithPrefix)
        print('Client sender thread stopped.')
        return
    
    
def handle_send_file_request(client, msgContentSize):
    print('Type in filepath of the file you want to send.')
    print('OR, type <exit> to stop sending file.\n')
    filename = rstrip_message(input())
    
    # Client does not want to send the file anymore
    if filename.lower() == 'exit':
        print('Stopped sending file.')
        display_rule()
        return
    
    # Create filepath from filename
    filepath = get_valid_filepath(filename)
    
    if filepath == None:
        print('Stopped sending file.')
        display_rule()
        return
    
    # Inform server that this client wants to send a file
    client.send(add_prefix(''.encode(), 1))
    # Send the file to server
    send_file_to_server(client, filepath, msgContentSize)
    return
    
    
def send_file_to_server(client, filepath, msgContentSize):
    # Create and send metadata to server
    filename, filesize = create_metadata(filepath)
    send_metadata(client, filename, filesize)
    
    # Send the whole file to server
    send_file(filepath, filename, client, 
             msgContentSize, 'server')
    return
        
    
def recv_user_input():
    msg = rstrip_message(input())
    # If client input empty message, make them input again
    while msg == '':
        print('Empty message detected. Please type your message:')
        msg = rstrip_message(input())
    return msg


def send_user_input(client, msg, chunkSize):    
    # Msg here does not have type prefix, since this function 
    #   should only handles cases of room code and username.
    client.send(msg.encode())
    response = client.recv(chunkSize)
    return msg, response.decode()

    
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
