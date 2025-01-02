# server.py

# To run this script: python3 server.py

# Credit: 
#   https://thepythoncode.com/article/make-a-chat-room-application-in-python

import socket
from datetime import datetime
from threading import Thread
from client_obj import Client_Obj
from room import Room


def init_server(serverIP, serverPort):
    # TCP connection
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow server to reuse the previous [IP, Port number] combination
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the [IP, Port number] combination to the server
    server.bind((serverIP, serverPort))
    return server


def is_client_alive(client):
    try:
        # If able to send an empty message to client without causing errors,
        #   then the client is still connected.
        client.send(b'')
        return True
    except (BrokenPipeError, 
            ConnectionResetError, 
            ConnectionAbortedError) as e:
        print(f'Error: {e}. ',
              f'Connection with {client} is no longer alive.')
        return False
    
    
def handle_client_disconnect_request(client, 
                                     clients, 
                                     maxClientCount):
    print(f'Client on [{client.getpeername()}] disconnected.')
    client.close()
    clients.remove(client)
    print(f'Connected clients: [{len(clients)}/{maxClientCount}]\n')
    
    
def handle_client_username_message(clientSocket):
    # Add restrictions here to make client input only desired username
    msg = clientSocket.recv(10)
    username = msg.decode()
    return username
    

def handle_client_room_code_message(clientSocket):
    # Add restrictions here to make client input only desired room code
    msg = clientSocket.recv(6)
    roomCode = msg.decode()
    return roomCode
    

def create_room(roomCode, rooms):
    room = Room(roomCode)
    rooms.append(room)
    enter_room(roomCode, rooms)


def enter_room(client, roomCode, rooms):
    # Check if room code is valid
    foundRoom = False
    
    for room in rooms:
        if room.get_room_code() == roomCode:
            foundRoom = True
            room.add_client_to_client_list()
    
    return foundRoom
    
    
def remove_a_client_from_clients_by_socket(socket, clients):
    address = socket.getpeername()
    for clientObject in clients:
        if clientObject.get_socket().getpeername() == address:
            clients.remove(socket)
            break
    return clients
    

def handle_one_client(clientObj, clients, maxClientCount):
    clientSocket = clientObj.get_socket()
    while True:
        try:
            # Receive message from one client
            msg = clientSocket.recv(1024)
            
            # Disconnect from this connection if msg is only 'q'
            decodedMsg = msg.decode()
            print(f'Message from {clientSocket.getpeername()}:', decodedMsg)
            if decodedMsg.lower() == 'q':
                handle_client_disconnect_request(clientObj, 
                                                 clients, 
                                                 maxClientCount)
                break
            
            clientSocketsToBeRemoved = []
            # Broadcast received message to all clients
            for clientObject in clients:
                socket = clientObject.get_socket()
                # Test if client socket is still alive before sending msg
                # If not, remove it from client socket list
                if not is_client_alive(socket):
                    clientSocketsToBeRemoved.append(socket)
                    continue
                
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                msgWithTime = f'[{date_now} {socket.getpeername()}: '
                msgWithTime += f'{decodedMsg}]'
                socket.send(msgWithTime.encode())
                
            for socket in clientSocketsToBeRemoved:
                clients = remove_a_client_from_clients_by_socket(socket, 
                                                                 clients)
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            # Close connection with this client
            print(f'Error: {e}. Removed {clientSocket.getpeername()}', 
                  ' from client socket list.')
            clientSocket.close()
            clients = remove_a_client_from_clients_by_socket(clientSocket, 
                                                             clients)
            print(f'Connected clients: ',
                  f'[{len(clients)}/{maxClientCount}]\n')
            break


def accept_a_connection(server, clients, maxClientCount):
    # Accept the connection established by a client
    try:
        (conn, address) = server.accept()
    except (KeyboardInterrupt) as e:
        # server received the [ctrl+c] command while waiting for connection
        print(f'Error: {e}. Disconnected with all clients and exiting now.')        
        for clientObj in clients:
            socket = clientObj.get_socket()
            socket.close()
        clients.clear()
        exit()
    
    # Disconnect from the connection if reached max client count already
    if len(clients) >= maxClientCount:
        print(f'Max client count [{maxClientCount}] reached.'
             ,f'Refused connection from {address}.\n')
        conn.send(b'-1') # refuse this connection by sending an string of -1
        conn.close()
        return
    
    # Wait for client to send valid username
    username = handle_client_username_message(conn)
    # Wait for client to enter room code
    roomCode = handle_client_room_code_message(conn)
    clientObj = Client_Obj(conn, username, roomCode)
    clients.append(clientObj)
    msg = str(len(clients))
    conn.send(msg.encode()) # accept connection by sending len(clients)
    print(f'Accepted connection request from Client on [{address}].')
    print(f'Connected clients: [{len(clients)}/{maxClientCount}]\n')

    # Start a new thread to handle this client
    t = Thread(target=handle_one_client, args=(clientObj,
                                               clients,
                                               maxClientCount))
    t.daemon = False # Set daemon thread: ends when the main thread ends
    t.start()
         
        
if __name__=='__main__':
    MAX_CLIENT_COUNT = 5
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 5001
    
    server = init_server(SERVER_IP, SERVER_PORT) # server socket
    clients = [] # a list of 'Client_Obj's
    rooms = {} # a dictionary of 'Room's
    
    # Start listening for connection
    server.listen(MAX_CLIENT_COUNT)
    print(f'Server socket on [{SERVER_IP}: {SERVER_PORT}] started listening.')
    print(f'MAX: {MAX_CLIENT_COUNT} clients.')
    print(f'Connected clients: [{len(clients)}/{MAX_CLIENT_COUNT}]\n')
        
    while True:
        # Start accepting connections established by clients
        accept_a_connection(server, clients, MAX_CLIENT_COUNT)
            
    server.close()
    print('Server socket closed.')
    