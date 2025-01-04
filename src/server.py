# server.py

# To run this script: python3 server.py

# Credit: 
#   https://thepythoncode.com/article/make-a-chat-room-application-in-python


# Note: 
# 1. Every 'client' instance references to a socket in server.py
# 2. Each 'Client_Obj' instance contains:
#   1) a socket, 
#   2) an username, and 
#   3) a room code
# 3. Each 'Room' instance contains:
#   1) a room code,
#   2) a room name, and
#   3) a list of Client_Obj

import secrets
import socket
import string
from client_obj import Client_Obj
from datetime import datetime
from room import Room
from threading import Thread


def init_server(serverIP, serverPort):
    # Setup server that uses TCP connection
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
    

def remove_a_client_from_clients_by_socket(client, clients):
    address = client.getpeername()
    for clientObj in clients:
        if clientObj.get_socket().getpeername() == address:
            clients.remove(clientObj)
            break
    return clients
    
    
def handle_client_disconnect_request(client, 
                                     clients, 
                                     roomCode,
                                     maxClientCount):
    print(f'Client on [{client.getpeername()}] disconnected.')
    clients = remove_a_client_from_clients_by_socket(client, clients)
    client.close()
    print(f'Connected clients: [{len(clients)}/{maxClientCount}]')
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    print_room_status(room)
    return
    
    
def handle_client_username_message(client, maxUsernameLength):
    msg = client.recv(maxUsernameLength)
    username = msg.decode()
    return username


def check_username_validness(username, maxUsernameLength):
    # Check if the length of the username is in bound
    if len(username) <= 0 or len(username) > maxUsernameLength:
        return False 
    
    # Check if every character in username is either a letter or a digit
    charPools = string.ascii_letters + string.digits
    for char in username:
        if char not in charPools: 
            return False
    return True


def handle_client_room_code_message(client, roomCodeLength):
    msg = client.recv(roomCodeLength)
    roomCode = msg.decode()
    return roomCode


def check_room_code_validness(roomCode, roomCodes):
    # Check if the received room code exists in roomCodes
    return roomCode in roomCodes


def get_client_response_on_creating_room(client):
    # 'C' for create room
    # 'E' for enter room
    msg = client.recv(1)
    decodedMsg = msg.decode()
    if decodedMsg != 'C' or decodedMsg != 'E':
        client.send(b'Error: Client response should only be <C> or <E>.')
        raise ValueError('Error: Client response should only be <C> or <E>.')
    return msg.decode() == 'C'


def generate_an_unique_room_code(roomCodeLength, roomCodes):
    # Generate an unique room code with roomCodeLength characters
    # Each character is either a letter (upper or lower) or a digit
    charPools = string.ascii_letters + string.digits
    roomCode = ''.join(secrets.choice(charPools) 
                       for _ in range(roomCodeLength))
    while roomCode in roomCodes:
        roomCode = ''.join(secrets.choice(charPools) 
                           for _ in range(roomCodeLength))
    roomCodes.append(roomCode)
    return roomCode


def create_room(roomCode, rooms):
    room = Room(roomCode)
    rooms.append(room) 
    return


def enter_room(clientObj, roomCode, rooms):
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    room.add_client_to_client_list(clientObj)
    return
    

def check_room_exist_with_room_code(roomCode, rooms):
    for room in rooms:
        if room.get_room_code() == roomCode:
            return True
    return False
    

def print_room_status(room):
    print(f'Connected clients in room [{room.get_room_code()}]:',
          f'{len(room.get_client_list())}')
    for idx, clientObj in enumerate(room.get_client_list()):
        print(f'Client {idx+1}: [{clientObj.get_username()},',
              f'{clientObj.get_socket().getpeername()}]')
    print('') 
    return


def handle_one_client(clientObj, clients, rooms, maxClientCount):
    client = clientObj.get_socket()
    while True:
        try:
            # Receive message from one client
            msg = client.recv(1024)
            
            # Disconnect from this connection if msg is only 'q'
            decodedMsg = msg.decode()
            print(f'Message from {client.getpeername()}:', decodedMsg)
            
            roomCode = clientObj.get_room_code()
            if decodedMsg.lower() == 'q':
                handle_client_disconnect_request(client, 
                                                 clients,
                                                 roomCode,
                                                 maxClientCount)
                break
            
            clientSocketsToBeRemoved = []
            room = [r for r in rooms if r.get_room_code() == roomCode][0]
            # Broadcast received message to all clients within the same room
            for clientObject in room.get_client_list():
                socket = clientObject.get_socket()
                # Test if client socket is still alive before sending msg
                # If not, remove it from client socket list
                if not is_client_alive(socket):
                    clientSocketsToBeRemoved.append(socket)
                    continue
                
                # If socket is the same as clientObj.get_socket(), skip.
                # This prevents the client receiving messages sent by 
                #   themselves.
                # if socket.getpeername() == client.getpeername():
                #     continue
                
                # Else, print out received message to the room the client is in
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                msgWithTime = f'[{date_now} {client.getpeername()}: '
                msgWithTime += f'{decodedMsg}]'
                socket.send(msgWithTime.encode())
                
            for socket in clientSocketsToBeRemoved:
                clients = remove_a_client_from_clients_by_socket(socket, 
                                                                 clients)
                socket.close()
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            # Close connection with this client
            print(f'Error: {e}. Removed {client.getpeername()}', 
                  ' from client socket list.')
            clients = remove_a_client_from_clients_by_socket(client, 
                                                             clients)
            client.close()
            print(f'Connected clients: [{len(clients)}/{maxClientCount}]')
            room = [r for r in rooms if r.get_room_code() == roomCode][0]
            print_room_status(room)
            break


def accept_a_connection(server, clients, rooms, maxClientCount, 
                        roomCodeLength, maxUsernameLength, roomCodes):
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
    
    msg = str(len(clients))
    conn.send(msg.encode()) # accept connection by sending len(clients)
    
    # Wait for client to either create or enter room
    clientWantsToCreateRoom = get_client_response_on_creating_room(conn)
    
    # Client wants to create a new room
    if clientWantsToCreateRoom:
        # Generate an unique room code for this client
        roomCode = generate_an_unique_room_code(roomCodeLength, roomCodes) 
    else:
        # Wait for client to send the room code
        roomCode = handle_client_room_code_message(conn, roomCodeLength)
        if not check_room_code_validness(roomCode, roomCodes): 
            conn.send(b'Error: Room code does not exist.')
            raise ValueError(f'Error: Room code: {roomCode} does not exist.')

    # Wait for client to send valid username
    username = handle_client_username_message(conn, maxUsernameLength)
    if not check_username_validness(username, maxUsernameLength):
        conn.send(b'Error: Username is invalid.')
        raise ValueError(f'Error: Username {username} is invalid.')
    
    # Create a client obj for this client
    clientObj = Client_Obj(conn, username, roomCode)
    clients.append(clientObj)
    
    # Create the room if the client wants to do so
    if clientWantsToCreateRoom:
        create_room(roomCode, rooms)
    
    # Make the client enter the Room
    enter_room(clientObj, roomCode, rooms)
        
    print(f'Accepted connection request from Client on [{address}].')
    print(f'With Username: [{username}], room code: [{roomCode}].')
    print(f'Connected clients: [{len(clients)}/{maxClientCount}]')
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    print_room_status(room)

    # Start a new thread to handle this client
    t = Thread(target=handle_one_client, args=(clientObj,
                                               clients,
                                               rooms,
                                               maxClientCount))
    t.daemon = False # Set daemon thread: ends when the main thread ends
    t.start()
         
        
if __name__=='__main__':
    MAX_CLIENT_COUNT = 5
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 5001
    # Source: https://www.oberlin.edu/cit/bulletins/passwords-matter
    ROOM_CODE_LENGTH = 11 # cost about 10 months to crack
    MAX_USERNAME_LENGTH = 16
    
    server = init_server(SERVER_IP, SERVER_PORT) # server socket
    clients = [] # a list of 'Client_Obj's
    rooms = [] # a dictionary of 'Room's
    roomCodes = set() # a set of room codes
    
    # Start listening for connection
    server.listen(MAX_CLIENT_COUNT)
    print(f'Server socket on [{SERVER_IP}: {SERVER_PORT}] started listening.')
    print(f'MAX: {MAX_CLIENT_COUNT} clients.')
    print(f'Connected clients: [{len(clients)}/{MAX_CLIENT_COUNT}]\n')
        
    while True:
        # Start accepting connections established by clients
        accept_a_connection(server, clients, rooms, MAX_CLIENT_COUNT, 
                            ROOM_CODE_LENGTH, MAX_USERNAME_LENGTH, roomCodes)
            
    server.close()
    print('Server socket closed.')
    