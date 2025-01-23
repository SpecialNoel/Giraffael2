# send_to_server.py

from general.file_transmission import (check_if_directory_exists,
                                      check_if_filename_is_valid,
                                      create_metadata, display_rule, 
                                      get_valid_filepath,
                                      send_file, send_filepath_and_filename,
                                      send_metadata)
from general.message import (rstrip_message, send_msg_with_prefix, 
                             recv_decoded_content)

def send_msg_to_server(client, shutdownEvent, chunkSize):
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
                handle_send_file_request(client, chunkSize)
            elif msg.lower() == 'recv': # Client wants to recv a file to server
                handle_recv_file_request(client)
            else: # Client wants to send a normal message to server
                send_msg_with_prefix(client, msg, 1)
        print('Client sender thread stopped.')
        return

def handle_send_file_request(client, chunkSize):
    def send_file_to_server(client, filepath, chunkSize):
        # Create and send metadata to server
        filename, filesize = create_metadata(filepath)
        send_metadata(client, filename, filesize)
        
        # Send the whole file to server
        send_file(filepath, filename, client, 
                chunkSize, 'server')
        
        display_rule()
        return
    
    print('Type in filepath of the file you want to send.')
    print('OR, type <exit> to stop sending file.\n')
    filepath = rstrip_message(input())
    
    # Client does not want to send the file anymore
    if filepath.lower() == 'exit':
        print('Stopped sending file.')
        display_rule()
        return
    
    # Check if filepath is valid
    filepath = get_valid_filepath(filepath)
    
    if filepath == None:
        print('Stopped sending file.')
        display_rule()
        return
    
    # Inform server that this client wants to send a file
    send_msg_with_prefix(client, '', 2)
    # Send the file to server
    send_file_to_server(client, filepath, chunkSize)
    return

def handle_recv_file_request(client):
    def get_client_filepath():
        print('Type in filepath where you want to store the file.')
        print('OR, type <exit> to stop receiving file.\n')
        filepath = rstrip_message(input())
        
        # Client does not want to receive the file anymore
        if filepath.lower() == 'exit':
            print('Stopped receiving file.')
            display_rule()
            return None
        return filepath
        
    def validate_client_filepath(filepath):
        while not check_if_directory_exists(filepath):
            print('Type in filepath where you want to store the file.')
            print('OR, type <exit> to stop receiving file.\n')
            
            filepath = rstrip_message(input())
            # Client does not want to receive the file anymore
            if filepath.lower() == 'exit':
                print('Stopped receiving file.')
                display_rule()
                return None
        return filepath
    
    def get_client_filename():
        print('Type in name of the file you want to receive.')
        print('OR, type <exit> to stop receiving file.\n')
        filename = rstrip_message(input())
        
        # Client does not want to receive the file anymore
        if filename.lower() == 'exit':
            print('Stopped receiving file.')
            display_rule()
            return None
        return filename
    
    def validate_client_filename(filename):
        while not check_if_filename_is_valid(filename):
            print('Type in name of the file you want to receive.')
            print('OR, type <exit> to stop receiving file.\n')
            
            filename = rstrip_message(input())
            # Client does not want to receive the file anymore
            if filename.lower() == 'exit':
                print('Stopped receiving file.')
                display_rule()
                return None
        return filename
        
    # Step1: prompt client where to store the file
    filepath = get_client_filepath()
    if filepath == None:
        return
    
    # Validate the filepath    
    filepath = validate_client_filepath(filepath)
    if filepath == None:
        return
    
    # Step2: prompt client which file to receive/download
    filename = get_client_filename()
    if filename == None:
        return
     
    filename = validate_client_filename(filename)
    if filename == None:
        return
    
    # Step3: start receiving metadata and file chunks if file exists on server
    # Inform server that this client wants to receive a file
    send_filepath_and_filename(client, filepath, filename)
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
