# server.py

'''
To run this script: python3 server.py

Note: Every 'client' instance references to a socket in server.py
'''


import secrets
import socket
import string
from client_obj import Client_Obj
from datetime import datetime
from file_transmission import (get_filepath, check_if_file_exists, 
                              create_metadata, check_metadata_format, 
                              split_metadata, send_file, recv_file)
from message import (rstrip_message, add_prefix,
                     get_prefix_and_content)
from room import Room
from threading import Thread, Event


class Server:
    def __init__(self):
        self.MAX_CLIENT_COUNT = 3
        self.SERVER_IP = '127.0.0.1' # host for testing
        #self.SERVER_IP = self.get_server_ip() # host with private ip
        self.SERVER_PORT = 5001
        
        # Source: https://www.hivesystems.com
        self.ROOM_CODE_LENGTH = 11 # takes about 618k years to crack as of 2024
        self.MAX_USERNAME_LENGTH = 16
        
        self.server = self.init_server() # server socket
        self.clients = [] # a list of 'Client_Obj's
        self.rooms = [] # a dictionary of 'Room's
        self.roomCodes = set() # a set of room codes
        
        self.shutdownEvent = Event() # threading.Event()
        self.threads = [] # all threads that handle each client
        
        # Char pools, containing all Digits, Upper and Lower-case letters
        self.charPools = string.ascii_letters + string.digits
        self.TYPE_PREFIX_SIZE = 1
        self.MSG_CONTENT_SIZE = 1024
        self.CHUNK_SIZE = self.TYPE_PREFIX_SIZE + self.MSG_CONTENT_SIZE        
    
    
    def get_server_ip(self):
        try:
            # Using UDP connection
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Connect to a public IP address (8.8.8.8 is Google's DNS server)
            temp_socket.connect(('8.8.8.8', 80))
            # This returns the private address of server device
            ip = temp_socket.getsockname()[0]
            temp_socket.close()
            return ip
        except Exception as e:
            print(f'Error occurred when getting server ip: {e}')
            # Use localhost as server ip if getting error
            return '127.0.0.1'
        

    def init_server(self):
        # Setup server that uses TCP connection
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow server to reuse the previous [IP, Port number] combination
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the [IP, Port number] combination to the server
        self.server.bind((self.SERVER_IP, self.SERVER_PORT))
        return


    def check_client_alive(self, client):
        try:
            # If able to send an empty message to client without errors,
            #   it means that the client is still connected.
            client.send(b'')
            return True
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            # Otherwise, client has already disconnected.
            print(f'Error: {e}. ',
                  f'Connection with {client} is no longer alive.')
            return False
        

    def remove_client_from_clients(self, client):
        # Get address of client
        address = client.getpeername()
        
        # Remove client from clients based on address
        for clientObj in self.clients:
            if clientObj.get_address() == address:
                self.clients.remove(clientObj)
                break
        return


    def remove_client_from_room(self, client, room):
        # Remove client from the room it was in
        room.remove_client_from_client_list(client)
        return room
        
        
    def handle_client_disconnect_request(self, client, address, roomCode):
        print(f'Client on [{client.getpeername()}] disconnected.')
        
        # Remove client from client list
        self.remove_client_from_clients(client)
        client.close()
        print(f'All connected clients: ',
              f'[{len(self.clients)}/{self.MAX_CLIENT_COUNT}]')
        
        # Remove client from the room it was in
        room = [r for r in self.rooms if r.get_room_code() == roomCode][0]
        room = self.remove_client_from_room(address, room)
        self.print_room_status(room)
        
        # Remove room code from roomCodes if its corresponding room is empty
        if len(room.get_client_list()) == 0:
            self.roomCodes.remove(roomCode)
            print(f'Room [{roomCode}] is empty, removed from room codes.\n')
        return
        
        
    def check_username_validness(self, username):
        # Check if the length of the username is in bound
        if len(username) <= 0 or len(username) > self.MAX_USERNAME_LENGTH:
            return False 
        
        # Check if every character in username is either a letter or a digit
        for char in username:
            if char not in self.charPools: 
                return False
        return True
        
        
    def handle_client_username_message(self, client):
        # Obtain username from client
        msg = rstrip_message(client.recv(self.MSG_CONTENT_SIZE))
        username = msg.decode()
        
        # Repeat until username sent by client is valid
        while not self.check_username_validness(username):
            msgToClient = 'Error: Username is invalid. Please try again.\n'
            msgToClient += f'Username max length: {self.MAX_USERNAME_LENGTH}\n'
            msgToClient += 'Username can be a combination of lower, upper '
            msgToClient += 'cased letters and/or digits.\n'
            client.send(msgToClient.encode())
            
            print(f'Error: Username [{username}] is invalid.')
            msg = rstrip_message(client.recv(self.MSG_CONTENT_SIZE))
            username = msg.decode()
            
        # Acknowledge client about username being valid
        client.send(b'VALID_USERNAME')
        return username


    def check_room_code_validness(self, roomCode):
        # Check if the received room code exists in roomCodes
        return roomCode in self.roomCodes


    def handle_client_room_code_message(self, client, address):
        createRoomInstead = False

        # Obtain room code from client
        msg = 'Please enter the room code, OR type <C> to create room.'
        client.send(msg.encode())
        msg = rstrip_message(client.recv(self.ROOM_CODE_LENGTH))
        roomCode = msg.decode()
        
        # Repeat until room code sent by client is valid
        # OR, client chooses to create a room instead
        while not self.check_room_code_validness(roomCode):
            if roomCode.upper() == 'C':
                createRoomInstead = True
                return (createRoomInstead, 
                        self.generate_and_send_room_code(client, address))
            
            msgToClient = 'Error: Room code not found. Please try again.'
            client.send(msgToClient.encode())
            
            print(f'Error: Room code: [{roomCode}] does not exist.')
            msg = rstrip_message(client.recv(self.ROOM_CODE_LENGTH))
            roomCode = msg.decode()

        # Need to acknowledge client about valid room code here
        client.send(b'VALID_ROOM_CODE')
        return createRoomInstead, roomCode


    def get_client_response_on_creating_room(self, client):
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


    def generate_room_code(self):
        # Generate an unique room code with roomCodeLength characters
        # Each character is either a letter (upper or lower) or a digit
        roomCode = ''.join(secrets.choice(self.charPools) 
                   for _ in range(self.ROOM_CODE_LENGTH))
        while roomCode in self.roomCodes:
            roomCode = ''.join(secrets.choice(self.charPools) 
                       for _ in range(self.ROOM_CODE_LENGTH))
        self.roomCodes.add(roomCode)
        return roomCode


    def generate_and_send_room_code(self, conn, address):
        # Generate an unique room code for this client
        roomCode = self.generate_room_code()
        # Send the generated room code to the client
        conn.send(roomCode.encode())
        print(f'Sent room code [{roomCode}] to client [{address}].')
        return roomCode


    def create_room(self, roomCode):
        room = Room(roomCode)
        self.rooms.append(room)
        print(f'Created room with room code [{roomCode}]') 
        return


    def enter_room(self, clientObj, roomCode):
        room = [r for r in self.rooms if r.get_room_code() == roomCode][0]
        room.add_client_to_client_list(clientObj)
        address = clientObj.get_address()
        print(f'Client [{address}] entered room [{roomCode}].')
        return
        

    def print_room_status(self, room):
        print(f'Connected clients in room [{room.get_room_code()}]:',
              f'{len(room.get_client_list())}')
        for idx, clientObj in enumerate(room.get_client_list()):
            print(f'Client {idx+1}: [{clientObj.get_username()},',
                  f'{clientObj.get_address()}]')
        print('')
        return
    
    
    def recv_file_from_client(self, client, msgContent):
        # Obtain metadata
        metadata = msgContent.decode()
        print(f'Metadata:  {metadata}.')
        if not check_metadata_format(metadata):
            return
        
        # Split the metadata of the file received from client
        filename, filesize = split_metadata(metadata)

        # Receive the whole file from client
        recv_file(filename, filesize, client, 
                 self.MSG_CONTENT_SIZE, client.getpeername())
        return
    
    
    def send_file_to_client(self, client, filename):
        # Create filepath from filename
        filepath = get_filepath(filename)
        if not check_if_file_exists(filepath):
            return
        
        # Create and send metadata to client
        filename, filesize = create_metadata(filepath)
        msg = f'{filename}|{filesize}'
        msgWithPrefix = add_prefix(msg.encode(), 1)
        client.send(msgWithPrefix)        
        
        # Send the whole file to client
        send_file(filepath, filename, client, 
                 self.MSG_CONTENT_SIZE, client.getpeername())
        return


    def handle_client_normal_message(self, client, msg, roomCode):        
        # A list used to remove disconnected client sockets
        clientSocketsToBeRemoved = []
        
        room = [r for r in self.rooms if r.get_room_code() == roomCode][0]
        
        # Broadcast received message to all clients within the same room
        for clientObject in room.get_client_list():
            socket = clientObject.get_socket()
            # If the client has disconnected, remove it
            if not self.check_client_alive(socket):
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
            self.remove_client_from_clients(socket)
            socket.close()
        return


    def handle_one_client(self, clientObj):
        client = clientObj.get_socket()
        address = clientObj.get_address()
        roomCode = clientObj.get_room_code()
        
        while not self.shutdownEvent.is_set():
            try:
                msg = client.recv(self.CHUNK_SIZE) # 1025 bytes
                typePrefix, msgContent = get_prefix_and_content(msg)
                print(f'msg: {msg}')
                print(f'Type Prefix: {typePrefix}')
                print(f'Content: {msgContent}')
                prefix = int.from_bytes(typePrefix, byteorder='big')
                print(f'Prefix: {prefix}')

                # Empty message -> client closed connection
                if not msg:
                    self.handle_client_disconnect_request(client, address, 
                                                          roomCode)
                    break
                
                match prefix:
                    case 0:
                        # Received normal message
                        msgContent = rstrip_message(msgContent.decode())
                        self.handle_client_normal_message(client, msgContent, roomCode)
                    case 1:
                        # Received file-transmission request
                        print(f'client [{address}] is transferring a file.\n')
                        
                        # Try receiving metadata from client
                        msg = client.recv(self.CHUNK_SIZE)
                        typePrefix, msgContent = get_prefix_and_content(msg)
                        self.recv_file_from_client(client, msgContent)
                    case _: 
                        # Received invalid prefix
                        print(f'Received invalid prefix: {typePrefix}.')
            except (BrokenPipeError, 
                    ConnectionResetError, 
                    ConnectionAbortedError) as e:
                # Close connection with this client
                print(f'Error: {e}. ',
                      f'Removed [{address}] from client socket list.')
                self.handle_client_disconnect_request(client, address, roomCode)
                break
        return


    def print_info_when_client_enter_room(self, address, username, roomCode):
        print(f'Accepted connection request from Client on [{address}].')
        print(f'With Username: [{username}], room code: [{roomCode}].')
        print('All connected clients: ',
              f'[{len(self.clients)}/{self.MAX_CLIENT_COUNT}]')
        room = [r for r in self.rooms if r.get_room_code() == roomCode][0]
        self.print_room_status(room)
        return
            
            
    def test_reach_max_client_count(self, conn, address):
        # Disconnect from the connection if reached max client count already
        if len(self.clients) >= self.MAX_CLIENT_COUNT:
            print(f'Max client count [{self.MAX_CLIENT_COUNT}] reached.',
                  f'Refused connection from {address}.\n')
            conn.send(b'-1') # refuse this connection by sending '-1' to client
            conn.close()
            return True
        
        # Otherwise, acknowledge client with 'len(clients)+1'
        msg = str((len(self.clients)+1)) # num of current connected clients+1
        conn.send(msg.encode())
        return False


    def accept_a_connection(self, conn, address):        
        # If reached max client count before this client: 
        #   disconnect, then acknowledge the client about the disconnection
        # Otherwise, acknowledge the client about the successful connection
        if self.test_reach_max_client_count(conn, address):
            return True
        
        # Wait for client to either create or enter room
        wantCreateRoom = self.get_client_response_on_creating_room(conn)
        
        if wantCreateRoom:
            # Client chooses to create a new room
            roomCode = self.generate_and_send_room_code(conn, address)
        else:
            # Client chooses to enter an existing room
            # Wait for client to send valid room code
            createInstead, roomCode = self.handle_client_room_code_message(
                                                    conn, address)
            if createInstead: 
                wantCreateRoom = True

        # Wait for client to send valid username
        username = self.handle_client_username_message(conn)
        
        # Create a client obj for this client
        clientObj = Client_Obj(conn, address, username, roomCode)
        self.clients.append(clientObj)
        
        # Create the room if the client has chosen to do so
        if wantCreateRoom:
            self.create_room(roomCode)

        # Make the client enter the room
        self.enter_room(clientObj, roomCode)
        self.print_info_when_client_enter_room(address, username, roomCode)

        # Start handling this client
        self.handle_one_client(clientObj)
        return


    def run_server(self): 
        # Set up server socket     
        self.init_server()  
        
        # Start listening for connection from clients
        self.server.listen(self.MAX_CLIENT_COUNT)
        print(f'Server socket on [{self.SERVER_IP}: {self.SERVER_PORT}] ',
              f'started listening.')
        print(f'MAX: {self.MAX_CLIENT_COUNT} clients.')
        print(f'All connected clients: ',
              f'[{len(self.clients)}/{self.MAX_CLIENT_COUNT}]\n')

        # Server should be always-on
        while True:
            try:
                # Accept the connection established by a client
                conn, address = self.server.accept()
                
                # Use a separate thread to accept and handle this client
                t = Thread(target=self.accept_a_connection, args=(conn, address,))
                t.daemon = False # Set daemon thread: ends when the main thread ends
                self.threads.append(t)
                t.start()
            except KeyboardInterrupt as e:
                # Server received the [ctrl+c] command while waiting for connection
                print(f'Error: {e}. ',
                       'Disconnected with all clients and exiting now.')
                self.shutdownEvent.set()
                
                # Close connections with all clients
                for clientObj in self.clients:
                    socket = clientObj.get_socket()
                    # Send an empty string to the client as an indicator
                    socket.send(b'')
                    socket.close()
                self.clients.clear()
                break
                
        # Wait until all threads converge
        for t in self.threads:
            t.join()
        print('All threads joined.')
        self.server.close()
        print('Server socket closed.')
        exit()
    

if __name__=='__main__':
    server = Server()
    server.run_server()
