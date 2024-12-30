# client.py

# To run this script: python3 client.py
# Note: must be executed when the server is alive.

import socket
from datetime import datetime
from threading import Thread


def init_client_socket(serverIP, serverPort):
    try: 
        # TCP connection
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server socket with the [IP, Port number] combination
        clientSocket.connect((serverIP, serverPort)) 
        print(f'Connected to server on [{serverIP, serverPort}] successfully!')
        return clientSocket
    except ConnectionRefusedError:
        print('Connection refused.')
        return None


def recv_msg_from_channel(clientSocket):
    # Receive message from other clients in the channel
    while True:
        msg = clientSocket.recv(1024)
        # Received a message with length 0 (only possible from server)
        # This means that the server wants to close the connection
        #   established by this client b/c of max num of clients reached
        if len(msg) == 0: break 
        print('\n' + msg.decode())

    
def get_and_send_user_input_msg(clientSocket, clientName):
    print('\nType a message to send to the channel, or\nType q to disconnect.')
    while True:
        msg = input()
        if msg.lower() == 'q':
            print('\nDisconnected from the channel.')
            break
        send_msg_to_channel(clientSocket, clientName, msg)


def send_msg_to_channel(clientSocket, clientName, msg):
    # Send message with current time to the channel
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg = f'[{date_now} {clientName}:{msg}]'
    clientSocket.send(msg.encode())
    
    
def check_if_connection_is_alive(clientSocket):
    try:
        clientSocket.sendall(b'Is this connection alive?')
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 5001
    
    clientSocket = init_client_socket(SERVER_HOST, SERVER_PORT)

    if not check_if_connection_is_alive(clientSocket):
        exit()
        
    # Use thread t1 to receive message
    clientName = input('Enter your username: ')
    t1 = Thread(target=recv_msg_from_channel, args=(clientSocket,))
    t1.daemon = True
    t1.start()

    # Use thread t2 to send message
    t2 = Thread(target=get_and_send_user_input_msg, 
                args=(clientSocket,clientName,))
    t2.daemon = True
    t2.start()
    
    t1.join()
    t2.join()

    clientSocket.close()
    print('Client socket closed.')