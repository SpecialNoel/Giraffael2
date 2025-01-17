# send_to_server.py


from general.file_transmission import (get_filepath, check_if_file_exists,
                                      create_metadata, send_file)
from general.message import rstrip_message, add_prefix


def get_and_send_user_input_to_server(client, shutdownEvent, msgContentSize):
        # Sent rules to the client console
        print('\nInput a message to send to the channel, ',
            'or\nInput [file] to send a file.\n')
        print('Press [Enter/Return] key to disconnect.\n')

        # Send message to server
        while not shutdownEvent.is_set():            
            msg = rstrip_message(input())
            
            # Empty message -> client closes connection
            if not msg:
                print('Disconnected from the channel.\n')
                shutdownEvent.set()
                client.close() # will be detected by server's 'recv()'
                break
            elif msg.lower() == 'file': # Client wants to send a file to server
                print('Type in filename of the file you want to send:\n')
                filename = rstrip_message(input())
                
                # Informing server that this client wants to send a file
                client.send(add_prefix('file'.encode(), 1))
                
                # Send the file to server
                send_file_to_server(client, filename, msgContentSize)
            else: # Client wants to send a normal message to server
                msgWithPrefix = add_prefix(msg.encode(), 0)
                client.send(msgWithPrefix)
        print('Client sender thread stopped.')
        return


def recv_user_input_and_send_to_server(client, chunkSize):
    msg = rstrip_message(input())
    
    # If client input empty message, make them input again
    while msg == '':
        print('Empty message detected. Please type your message:')
        msg = rstrip_message(input())
    
    # Msg here does not have type prefix, since this function 
    #   should only handles cases of room code and username.
    client.send(msg.encode())
    response = client.recv(chunkSize)
    return msg, response.decode()

    
def send_username_to_server(client, chunkSize):
    print('Input your username:')
    return recv_user_input_and_send_to_server(client, chunkSize)
    

def send_decision_on_room_to_server(client, chunkSize):
    return recv_user_input_and_send_to_server(client, chunkSize)


def send_room_code_to_server(client, chunkSize):
    print('Input room code here:\n')
    return recv_user_input_and_send_to_server(client, chunkSize)


def send_file_to_server(client, filename, msgContentSize):
    # Create filepath from filename
    filepath = get_filepath(filename)
    while not check_if_file_exists(filepath):
        print('\nType in filename of the file you want to send:\n')
        filename = rstrip_message(input())
        filepath = get_filepath(filename)

    # Create and send metadata to server
    filename, filesize = create_metadata(filepath)
    msg = f'{filename}|{filesize}'
    msgWithPrefix = add_prefix(msg.encode(), 1)
    client.send(msgWithPrefix)        
    
    # Send the whole file to server
    send_file(filepath, filename, client, 
             msgContentSize, 'server')
    return