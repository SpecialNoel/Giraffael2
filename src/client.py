# client.py

# To run this script: python3 client.py
# Note: must be executed when the server is alive.


# Note:
# 'client' is essentially only a socket in client.py

import socket
from threading import Thread


def init_client_socket(serverIP, serverPort):
    try: 
        # TCP connection
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server socket with the [IP, Port number] combination
        client.connect((serverIP, serverPort)) 
        return client
    except ConnectionRefusedError:
        print('Connection refused.')
        return None


def recv_msg_from_channel(client):
    # Receive message from other clients in the channel
    while True:
        if not is_connection_alive(client):
            break
        
        msg = client.recv(1024)
        # Received a message of string 0 (only possible from server)
        # This means that the server wants to close the connection
        #   established by this client b/c of max num of clients reached
        if len(msg) == 0: break 
        print(msg.decode() + '\n')

    
def get_and_send_user_input_msg(client):
    ruleSent = False

    while True:
        if not ruleSent: 
            ruleSent = True
            print('\nType a message to send to the channel, ',
                  'or\nType q to disconnect.\n')
            
        msg = input()
        send_msg_to_server(client, msg)
        if msg.lower() == 'q':
            print('Disconnected from the channel.\n')
            break


def send_msg_to_server(client, msg):
    # Send message to the channel
    if not is_connection_alive(client):
        exit()
    client.send(msg.encode())
    
    
def send_username_to_server(client):
    print('Type in your username: ')
    msg = input()
    send_msg_to_server(client, msg)
    

def send_room_code_to_server(client):
    print('Type in the room code: ')
    msg = input()
    send_msg_to_server(client, msg)
    
    
def check_if_server_reached_max_client_capacity(client):
    msg = client.recv(1024)
    print(f'Init msg from server: {msg.decode()}.')
    
    if msg.decode() == '-1':
        print('Connection refused by server: max client count reached.')
    else:
        print('Connected to server successfully!')
    
    return msg.decode() != '-1'


def is_connection_alive(client):
    try:
        client.send(b'')
        return True
    except (BrokenPipeError, 
            ConnectionResetError, 
            ConnectionAbortedError) as e:
        print(f'Error: {e}. ',
              f'Connection with server is no longer alive.')
        return False


if __name__ == '__main__':
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 5001
    
    client = init_client_socket(SERVER_HOST, SERVER_PORT)
    
    if not check_if_server_reached_max_client_capacity(client):
        exit()
    
    send_username_to_server(client)
    send_room_code_to_server(client)
        
    # Use thread t1 to receive message
    #clientName = input('Enter your username: ')
    t1 = Thread(target=recv_msg_from_channel, args=(client,))
    t1.daemon = True
    t1.start()

    # Use thread t2 to send message
    t2 = Thread(target=get_and_send_user_input_msg, 
                args=(client,))
    t2.daemon = True
    t2.start()
    
    t1.join()
    t2.join()

    client.close()
    print('Client socket closed.')