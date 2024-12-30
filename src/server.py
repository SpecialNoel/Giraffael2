# server.py

# To run this script: python3 server.py

# Credit: 
#   https://thepythoncode.com/article/make-a-chat-room-application-in-python

import socket
from threading import Thread


def init_server_socket(serverIP, serverPort):
    # TCP connection
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow server to reuse the previous [IP, Port number] combination
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the [IP, Port number] combination to the serverSocket
    serverSocket.bind((serverIP, serverPort))
    return serverSocket


def handle_one_client(conn, address, clientSockets):
    while True:
        try:
            # Receive message from one client
            msg = conn.recv(1024)
        except Exception as e:
            # Close connection with this client
            conn.close()
            clientSockets.remove(conn)
            print(f'Error: {e}. Removed {address} from client socket list.')
        else:
            # Broadcast received message to all clients
            print(f'Message from {address}:', msg.decode())
            for socket in clientSockets:
                socket.send(msg)


def accept_a_connection(serverSocket, clientSockets, max_client_count):
    # Accept the connection
    (conn, address) = serverSocket.accept()
    
    # Refuse the connection if reached max client count already
    if len(clientSockets) >= max_client_count:
        print(f'Max client count [{max_client_count}] reached.'
             ,f'Refused connection from {address}')
        conn.send(b'0') # refuse this connection by sending an string of 0
        conn.close()
        return
         
    clientSockets.add(conn)
    conn.send(b'1') # accept this connection by sending an string of 1
    print(f'Accepted connection request from Client on [{address}].')
    
    # Start a new thread that handles this client only
    t = Thread(target=handle_one_client, args=(conn,address,clientSockets,))
    t.daemon = True # Daemon thread to make it ends when the main thread ends
    t.start()
         
        
if __name__=='__main__':
    MAX_CLIENT_COUNT = 1
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 5001
    
    serverSocket = init_server_socket(SERVER_IP, SERVER_PORT)
    clientSockets = set()
    
    # Start listening for connection
    serverSocket.listen(MAX_CLIENT_COUNT)
    print(f'Server socket on [{SERVER_IP}: {SERVER_PORT}] started listening.')
    print(f'MAX {MAX_CLIENT_COUNT} Clients.\n')
        
    while True:
        # Start accepting connections established by clients
        accept_a_connection(serverSocket, clientSockets, MAX_CLIENT_COUNT)
        
        # If the last connected client disconnects, stop accepting more.
        if not len(clientSockets):
            print('No more Client connected to the channel. Channel closed.')
            break
    
    serverSocket.close()
    print('Server socket closed.')
    