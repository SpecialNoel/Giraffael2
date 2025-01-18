# recv_from_client.py


from datetime import datetime
from general.file_transmission import (check_metadata_format,
                                      split_metadata, recv_file)
from general.message import rstrip_message, add_prefix
from server_only.room_code_operations import generate_and_send_room_code
from server_only.remove_client import remove_client_from_clients
from server_only.check_client_alive import check_client_alive


def check_room_code_validness(roomCode, roomCodes):
    # Check if the received room code exists in roomCodes
    return roomCode in roomCodes


def check_username_validness(username, charPools, maxUsernameLength):
    # Check if the length of the username is in bound
    if len(username) <= 0 or len(username) > maxUsernameLength:
        return False 
    
    # Check if every character in username is either a letter or a digit
    for char in username:
        if char not in charPools: 
            return False
    return True
    

def get_client_response_on_creating_room(client):
    # Obtain response from client about create or enter room
    # 'C' for create room
    # 'E' for enter room
    msg = rstrip_message(client.recv(2))
    response = msg.decode().upper()
    
    # Repeat until response from client is either 'C' or 'E'
    while response != 'C':
        # Client chooses to enter room
        if response == 'E': return False
        msgToClient = 'Error: Response should only be <C> or <E>. '
        msgToClient += 'Please try again.'
        client.send(msgToClient.encode())
        
        print(f'Error: Client response on creating room: ',
                f'{response}.')
        msg = rstrip_message(client.recv(2))
        response = msg.decode().upper()
    # Client chooses to create room
    return True
    

def handle_client_room_code_message(client, address, roomCodes, roomCodeLength):
    createRoomInstead = False

    # Obtain room code from client
    msg = 'Please enter the room code, OR type <C> to create room.'
    client.send(msg.encode())
    msg = rstrip_message(client.recv(roomCodeLength))
    roomCode = msg.decode()
    
    # Repeat until room code sent by client is valid
    # OR, client chooses to create a room instead
    while not check_room_code_validness(roomCode, roomCodes):
        if roomCode.upper() == 'C':
            createRoomInstead = True
            return (createRoomInstead, 
                    generate_and_send_room_code(client, address))
        
        msgToClient = 'Error: Room code not found. Please try again.'
        client.send(msgToClient.encode())
        
        print(f'Error: Room code: [{roomCode}] does not exist.')
        msg = rstrip_message(client.recv(roomCodeLength))
        roomCode = msg.decode()

    # Need to acknowledge client about valid room code here
    client.send(b'VALID_ROOM_CODE')
    return createRoomInstead, roomCode


def handle_client_username_message(client, charPools, msgContentSize, maxUsernameLength):
    # Obtain username from client
    msg = rstrip_message(client.recv(msgContentSize))
    username = msg.decode()
    
    # Repeat until username sent by client is valid
    while not check_username_validness(username, charPools, maxUsernameLength):
        msgToClient = 'Error: Username is invalid. Please try again.\n'
        msgToClient += f'Username max length: {maxUsernameLength}\n'
        msgToClient += 'Username can be a combination of lower, upper '
        msgToClient += 'cased letters and/or digits.\n'
        client.send(msgToClient.encode())
        
        print(f'Error: Username [{username}] is invalid.')
        msg = rstrip_message(client.recv(msgContentSize))
        username = msg.decode()
        
    # Acknowledge client about username being valid
    client.send(b'VALID_USERNAME')
    return username


def handle_client_normal_message(client, msg, clients, rooms, roomCode):        
    # A list used to remove disconnected client sockets
    clientSocketsToBeRemoved = []
    
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    
    # Broadcast received message to all clients within the same room
    for clientObject in room.get_client_list():
        socket = clientObject.get_socket()
        # If the client has disconnected, remove it
        if not check_client_alive(socket):
            clientSocketsToBeRemoved.append(socket)
            continue
        
        # Otherwise, send received message to this client
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msgWithTime = f'[{date_now} {client.getpeername()}: {msg}]'
        print(msgWithTime+'\n')
        msgWithTimeWithPrefix = add_prefix(msgWithTime.encode(), 0)
        socket.send(msgWithTimeWithPrefix)
        
    # Remove disconnected clients
    for socket in clientSocketsToBeRemoved:
        remove_client_from_clients(socket, clients)
        socket.close()
    return


def recv_file_from_client(client, msgContent, msgContentSize):
    # Obtain metadata
    metadata = msgContent.decode()
    print(f'Metadata: {metadata}.')
    if not check_metadata_format(metadata):
        return
    
    # Split the metadata of the file received from client
    filename, filesize = split_metadata(metadata)

    # Receive the whole file from client
    recv_file(filename, filesize, client, 
             msgContentSize, client.getpeername())
    return