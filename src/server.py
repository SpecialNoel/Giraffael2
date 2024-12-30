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
            print(f'Error: {e}. Removed {address} from client sockets.')
        else:
            # Broadcast received message to all clients
            for socket in clientSockets:
                socket.send(msg)


def accept_a_connection(serverSocket, clientSockets, MAX_CLIENT_COUNT):
    # Refuse connection established from client if reached max client count
    if (len(clientSockets) >= MAX_CLIENT_COUNT):
        print(f'Reached max number of clients: {MAX_CLIENT_COUNT}.')
        (conn, address) = serverSocket.accept()
        conn.send(b'');
        conn.close()
        return False
    
    # Accept the connection
    (conn, address) = serverSocket.accept()
    clientSockets.add(conn)
    print(f'Accepted connection request from Client on [{address}].')
    
    # Start a new thread that handles this client only
    t = Thread(target=handle_one_client, args=(conn,address,clientSockets,))
    t.daemon = True # Daemon thread to make it ends when the main thread ends
    t.start()
    
    return True
     
        
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
    
    isAcceptingClient = True
    
    while True:
        # Start accepting connections established by clients
        if isAcceptingClient:
            isAcceptingClient = accept_a_connection(serverSocket, 
                                                    clientSockets, 
                                                    MAX_CLIENT_COUNT)
        
        # If the last connected client disconnects, stop accepting more.
        if not len(clientSockets):
            print('No more Client connected to the channel. Channel closed.')
            break
    
    serverSocket.close()
    print('Server socket closed.')
    