# server.py

# To run this script: python3 server.py

# Credit: 
#   https://thepythoncode.com/article/make-a-chat-room-application-in-python


# Note: 
# 1. Every 'client' instance references to a socket in server.py
# 2. Each 'Client_Obj' instance contains:
#   1) a socket, 
#   2) address of the socket
#   3) an username, and 
#   4) a room code
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
        if clientObj.get_address() == address:
            clients.remove(clientObj)
            break
    return clients


def remove_a_client_from_room_by_socket(client, room):
    room.remove_client_from_client_list(client)
    return room
    
    
def handle_client_disconnect_request(client, 
                                     clients, 
                                     address,
                                     rooms,
                                     roomCode,
                                     maxClientCount,
                                     roomCodes):
    print(f'Client on [{client.getpeername()}] disconnected.')
    
    # Remove client from client list
    clients = remove_a_client_from_clients_by_socket(client, clients)
    client.close()
    print(f'Connected clients: [{len(clients)}/{maxClientCount}]')
    
    # Remove client from the room
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    room = remove_a_client_from_room_by_socket(address, room)
    print_room_status(room)
    
    # Remove the room code from roomCodes if its corresponding room is empty
    if len(room.get_client_list()) == 0:
        roomCodes.remove(roomCode)
    return
    
    
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
    
    
def handle_client_username_message(client, maxUsernameLength):
    msg = client.recv(maxUsernameLength)
    username = msg.decode()
    
    while not check_username_validness(username, maxUsernameLength):
        msgToClient = 'Error: Username is invalid.'
        msgToClient += '\nPlease try again.'
        client.send(msgToClient.encode())
        print(f'Error: Username {username} is invalid.')
        msg = client.recv(maxUsernameLength)
        username = msg.decode()
        
    # Need to acknowledge client about valid username here
    client.send(b'VALID_USERNAME')
    return username


def check_room_code_validness(roomCode, roomCodes):
    # Check if the received room code exists in roomCodes
    return roomCode in roomCodes


def handle_client_room_code_message(client, roomCodeLength, roomCodes):
    client.send(b'Please enter the room code.')
    msg = client.recv(roomCodeLength)
    roomCode = msg.decode()
    
    while not check_room_code_validness(roomCode, roomCodes):
        msgToClient = 'Error: Room code does not exist.'
        msgToClient += '\nPlease try again.'
        client.send(msgToClient.encode())
        print(f'Error: Room code: {roomCode} does not exist.')
        msg = client.recv(roomCodeLength)
        roomCode = msg.decode()
    
    # Need to acknowledge client about valid room code here
    client.send(b'VALID_ROOM_CODE')
    return roomCode


def get_client_response_on_creating_room(client):
    # 'C' for create room
    # 'E' for enter room
    msg = client.recv(2)
    upperedDecodedMsg = msg.decode().upper()
    
    # Repeat this step if client responds with invalid message
    while upperedDecodedMsg != 'C':
        if upperedDecodedMsg == 'E': return False
        msgToClient = 'Error: Client response should only be <C> or <E>.'
        msgToClient += '\nPlease try again.'
        client.send(msgToClient.encode())
        print(f'Error: Client response on creating room: {upperedDecodedMsg}.')
        msg = client.recv(1024)
        upperedDecodedMsg = msg.decode().upper()
    return True


def generate_an_unique_room_code(roomCodeLength, roomCodes):
    # Generate an unique room code with roomCodeLength characters
    # Each character is either a letter (upper or lower) or a digit
    charPools = string.ascii_letters + string.digits
    roomCode = ''.join(secrets.choice(charPools) 
                       for _ in range(roomCodeLength))
    while roomCode in roomCodes:
        roomCode = ''.join(secrets.choice(charPools) 
                           for _ in range(roomCodeLength))
    roomCodes.add(roomCode)
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
              f'{clientObj.get_address()}]')
    print('') 
    return


def get_message_from_client(client):
    # Receive message from one client
    msg = client.recv(1024)
    print(f'Message from {client.getpeername()}:', msg.decode())
    return msg


def handle_client_normal_message(client, decodedMsg, clients, 
                                         rooms, roomCode):
    clientSocketsToBeRemoved = []
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    # Broadcast received message to all clients within the same room
    for clientObject in room.get_client_list():
        socket = clientObject.get_socket()
        # Test if client socket is still alive before sending msg
        # If not, store it to a list for later removal
        if not is_client_alive(socket): # this sends an empty string to client
            clientSocketsToBeRemoved.append(socket)
            continue
        
        # Else, send received message to all clients in that room
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msgWithTime = f'[{date_now} {client.getpeername()}: '
        msgWithTime += f'{decodedMsg}]'
        socket.send(msgWithTime.encode())
        
    # Remove disconnected clients
    for socket in clientSocketsToBeRemoved:
        clients = remove_a_client_from_clients_by_socket(socket, clients)
        socket.close()
    return


def close_connection_with_client_when_error(e, client, clients, address,
                                            maxClientCount, rooms, 
                                            roomCode):
    print(f'Error: {e}. Removed {client.getpeername()}', 
            ' from client socket list.')
    handle_client_disconnect_request(client, clients, address, rooms,
                                     roomCode, maxClientCount, roomCodes)
    return


def handle_one_client(clientObj, clients, rooms, maxClientCount, roomCodes):
    client = clientObj.get_socket()
    address = clientObj.get_address()
    roomCode = clientObj.get_room_code()
    while True:
        try:
            msg = get_message_from_client(client) # Buffer size: 1024
            
            # Disconnect from this connection if msg is empty
            if not msg:
                handle_client_disconnect_request(client, clients, address, 
                                                 rooms, roomCode, 
                                                 maxClientCount, roomCodes)
                break
            else:
                decodedMsg = msg.decode()
                handle_client_normal_message(client, decodedMsg, clients, 
                                             rooms, roomCode)
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            # Close connection with this client
            close_connection_with_client_when_error(e, client, clients, 
                                                    address, maxClientCount, 
                                                    rooms, roomCode)
            break


def start_handling_one_client(clientObj, clients, rooms, 
                              maxClientCount, roomCodes):
    t = Thread(target=handle_one_client, args=(clientObj,
                                               clients,
                                               rooms,
                                               maxClientCount,
                                               roomCodes))
    t.daemon = False # Set daemon thread: ends when the main thread ends
    t.start()
    return


def print_info_when_client_enter_room(address, username, roomCode, 
                                      clients, maxClientCount):
    print(f'Accepted connection request from Client on [{address}].')
    print(f'With Username: [{username}], room code: [{roomCode}].')
    print(f'Connected clients: [{len(clients)}/{maxClientCount}]')
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    print_room_status(room)
    return
        
        
def test_reach_max_client_count(clients, maxClientCount, conn, address):
    # Disconnect from the connection if reached max client count already
    if len(clients) >= maxClientCount:
        print(f'Max client count [{maxClientCount}] reached.'
             ,f'Refused connection from {address}.\n')
        conn.send(b'-1') # refuse this connection by sending an string of -1
        conn.close()
        return True
    # Otherwise, acknowledge the connection by sending len(clients)+1 to client
    msg = str((len(clients)+1))
    conn.send(msg.encode())
    return False


def try_accept_a_connection(server, clients):
    try:
        (conn, address) = server.accept()
        return conn, address
    except (KeyboardInterrupt) as e:
        # server received the [ctrl+c] command while waiting for connection
        print(f'Error: {e}. Disconnected with all clients and exiting now.')
        for clientObj in clients:
            socket = clientObj.get_socket()
            # handle server actively disconnect all clients' connection here (by sending an empty string to socket)
            socket.close()
        clients.clear()
        exit()


def accept_a_connection(server, clients, rooms, maxClientCount, 
                        roomCodeLength, maxUsernameLength, roomCodes):
    # Accept the connection established by a client
    conn, address = try_accept_a_connection(server, clients)
    
    # If reached max client count before this client: 
    #   disconnect, then acknowledge the client about the disconnection
    # Otherwise, acknowledge the client about the successful connection
    if test_reach_max_client_count(clients, maxClientCount, conn, address):
        return
    
    # Wait for client to either create or enter room
    clientWantsToCreateRoom = get_client_response_on_creating_room(conn)
    
    # Client wants to create a new room
    if clientWantsToCreateRoom:
        # Generate an unique room code for this client
        roomCode = generate_an_unique_room_code(roomCodeLength, roomCodes)
        # Send the generated room code to the client
        conn.send(roomCode.encode())
        print(f'Sent room code [{roomCode}] to client [{address}].')
    else:
        # Wait for client to send valid room code
        roomCode = handle_client_room_code_message(conn, roomCodeLength, 
                                                   roomCodes)

    # Wait for client to send valid username
    username = handle_client_username_message(conn, maxUsernameLength)
    
    # Create a client obj for this client
    clientObj = Client_Obj(conn, address, username, roomCode)
    clients.append(clientObj)
    
    # Create the room if the client chose to do so
    if clientWantsToCreateRoom:
        create_room(roomCode, rooms)
    
    # Make the client enter the Room
    enter_room(clientObj, roomCode, rooms)
    print_info_when_client_enter_room(address, username, roomCode, 
                                      clients, maxClientCount)

    # Start a new thread to handle this client
    start_handling_one_client(clientObj, clients, rooms, 
                              maxClientCount, roomCodes)
    return

  
if __name__=='__main__':
    MAX_CLIENT_COUNT = 3
    SERVER_IP = '127.0.0.1'
    SERVER_PORT = 5001
    # Source: https://www.oberlin.edu/cit/bulletins/passwords-matter
    ROOM_CODE_LENGTH = 11 # takes about 10 months to crack
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
    exit()
    