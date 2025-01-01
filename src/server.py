# server.py

# To run this script: python3 server.py

# Credit: 
#   https://thepythoncode.com/article/make-a-chat-room-application-in-python

import socket
from datetime import datetime
from threading import Thread


def init_server_socket(serverIP, serverPort):
    # TCP connection
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow server to reuse the previous [IP, Port number] combination
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the [IP, Port number] combination to the serverSocket
    serverSocket.bind((serverIP, serverPort))
    return serverSocket


def is_socket_alive(clientSocket):
    try:
        clientSocket.send(b'')
        return True
    except (BrokenPipeError, 
            ConnectionResetError, 
            ConnectionAbortedError) as e:
        print(f'Error: {e}. ',
              f'Connection with {clientSocket} is no longer alive.')
        return False
    
    
def handle_client_disconnect_request(conn, 
                                     clientSockets, 
                                     max_client_count):
    print(f'Client on [{conn.getpeername()}] disconnected.')
    conn.close()
    clientSockets.remove(conn)
    print(f'Connected clients: [{len(clientSockets)}/{max_client_count}]\n')


def handle_one_client(conn, clientSockets, max_client_count):
    while True:
        try:
            # Receive message from one client
            msg = conn.recv(1024)
            
            # Disconnect from this connection if msg is only 'q'
            decodedMsg = msg.decode()
            print(f'Message from {conn.getpeername()}:', decodedMsg)
            if decodedMsg.lower() == 'q':
                handle_client_disconnect_request(conn, 
                                                 clientSockets, 
                                                 max_client_count)
                break
            
            clientSocketsToBeRemoved = []
            # Broadcast received message to all clients
            for socket in clientSockets:
                # Test if client socket is still alive before sending msg
                # If not, remove it from client socket list
                if not is_socket_alive(socket):
                    clientSocketsToBeRemoved.append(socket)
                    continue
                
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                msgWithTime = f'[{date_now} {socket.conn.getpeername()}: '
                msgWithTime += f'{decodedMsg}]'
                socket.send(msgWithTime.encode())
                
            for socket in clientSocketsToBeRemoved:
                clientSockets.remove(socket)
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            # Close connection with this client
            print(f'Error: {e}. Removed {conn.getpeername()}', 
                  ' from client socket list.')
            conn.close()
            clientSockets.remove(conn)
            print(f'Connected clients: ',
                  f'[{len(clientSockets)}/{max_client_count}]\n')
            break


def accept_a_connection(serverSocket, clientSockets, max_client_count):
    # Accept the connection
    try:
        (conn, address) = serverSocket.accept()
    except (KeyboardInterrupt) as e:
        print(f'Error: {e}. Disconnected with all clients and exiting now.')
        count = len(clientSockets)
        for socket in clientSockets:
            print(f'Removed {socket.getpeername()}', 
                  'from client socket list.')
            socket.close()
            count -= 1
            print(f'Connected clients: [{count}/{max_client_count}]\n')
        exit()
    
    # Refuse the connection if reached max client count already
    if len(clientSockets) >= max_client_count:
        print(f'Max client count [{max_client_count}] reached.'
             ,f'Refused connection from {address}.\n')
        conn.send(b'-1') # refuse this connection by sending an string of -1
        conn.close()
        return
         
    clientSockets.append(conn)
    msg = str(len(clientSockets))
    conn.send(msg.encode()) # accept connection by sending len(clientSockets)
    print(f'Accepted connection request from Client on [{address}].')
    print(f'Connected clients: [{len(clientSockets)}/{max_client_count}]\n')

    # Start a new thread that handles this client only
    t = Thread(target=handle_one_client, args=(conn,
                                               clientSockets,
                                               max_client_count))
    t.daemon = False # Set daemon thread: ends when the main thread ends
    t.start()
         
        
if __name__=='__main__':
    MAX_CLIENT_COUNT = 2
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 5001
    
    serverSocket = init_server_socket(SERVER_IP, SERVER_PORT)
    clientSockets = []
    
    # Start listening for connection
    serverSocket.listen(MAX_CLIENT_COUNT)
    print(f'Server socket on [{SERVER_IP}: {SERVER_PORT}] started listening.')
    print(f'MAX: {MAX_CLIENT_COUNT} clients.')
    print(f'Connected clients: [{len(clientSockets)}/{MAX_CLIENT_COUNT}]\n')
        
    while True:
        # Start accepting connections established by clients
        accept_a_connection(serverSocket, clientSockets, MAX_CLIENT_COUNT)
            
    serverSocket.close()
    print('Server socket closed.')
    