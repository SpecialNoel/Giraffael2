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
from threading import Thread, Event


class Server:
    def __init__(self):
        self.MAX_CLIENT_COUNT = 3
        self.SERVER_IP = '127.0.0.1'
        self.SERVER_PORT = 5001
        # Source: https://www.oberlin.edu/cit/bulletins/passwords-matter
        self.ROOM_CODE_LENGTH = 11 # takes about 10 months to crack
        self.MAX_USERNAME_LENGTH = 16
        
        self.server = self.init_server() # server socket
        self.clients = [] # a list of 'Client_Obj's
        self.rooms = [] # a dictionary of 'Room's
        self.roomCodes = set() # a set of room codes
        
        self.shutdownEvent = Event() # threading.Event()
        self.threads = [] # all threads that handle each client
        

    def init_server(self):
        # Setup server that uses TCP connection
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow server to reuse the previous [IP, Port number] combination
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the [IP, Port number] combination to the server
        self.server.bind((self.SERVER_IP, self.SERVER_PORT))
        return


    def is_client_alive(self, client):
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
        

    def remove_a_client_from_clients_by_socket(self, client):
        address = client.getpeername()
        for clientObj in self.clients:
            if clientObj.get_address() == address:
                self.clients.remove(clientObj)
                break
        return


    def remove_a_client_from_room_by_socket(self, client, room):
        room.remove_client_from_client_list(client)
        return room
        
        
    def handle_client_disconnect_request(self, 
                                        client, 
                                        address,
                                        roomCode):
        print(f'Client on [{client.getpeername()}] disconnected.')
        
        # Remove client from client list
        self.remove_a_client_from_clients_by_socket(client)
        client.close()
        print(f'Connected clients: [{len(self.clients)}/{self.MAX_CLIENT_COUNT}]')
        
        # Remove client from the room
        room = [r for r in self.rooms if r.get_room_code() == roomCode][0]
        room = self.remove_a_client_from_room_by_socket(address, room)
        self.print_room_status(room)
        
        # Remove the room code from roomCodes if its corresponding room is empty
        if len(room.get_client_list()) == 0:
            self.roomCodes.remove(roomCode)
        return
        
        
    def check_username_validness(self, username):
        # Check if the length of the username is in bound
        if len(username) <= 0 or len(username) > self.MAX_USERNAME_LENGTH:
            return False 
        
        # Check if every character in username is either a letter or a digit
        charPools = string.ascii_letters + string.digits
        for char in username:
            if char not in charPools: 
                return False
        return True
        
        
    def handle_client_username_message(self, client):
        msg = client.recv(self.MAX_USERNAME_LENGTH)
        username = msg.decode()
        
        while not self.check_username_validness(username):
            msgToClient = 'Error: Username is invalid.'
            msgToClient += '\nPlease try again.'
            client.send(msgToClient.encode())
            print(f'Error: Username {username} is invalid.')
            msg = client.recv(self.MAX_USERNAME_LENGTH)
            username = msg.decode()
            
        # Need to acknowledge client about valid username here
        client.send(b'VALID_USERNAME')
        return username


    def check_room_code_validness(self, roomCode):
        # Check if the received room code exists in roomCodes
        return roomCode in self.roomCodes


    def handle_client_room_code_message(self, client, address):
        createRoomInstead = False

        client.send(b'Please enter the room code.')
        msg = client.recv(self.ROOM_CODE_LENGTH)
        roomCode = msg.decode()

        if msg.upper() == 'C':
            createRoomInstead = True
            return createRoomInstead, self.genrate_and_send_room_code(client, address)

        while not self.check_room_code_validness(roomCode):
            msgToClient = 'Error: Room code does not exist.'
            msgToClient += '\nPlease try again.'
            client.send(msgToClient.encode())
            print(f'Error: Room code: {roomCode} does not exist.')
            msg = client.recv(self.ROOM_CODE_LENGTH)
            roomCode = msg.decode()

        # Need to acknowledge client about valid room code here
        client.send(b'VALID_ROOM_CODE')
        return createRoomInstead, roomCode


    def get_client_response_on_creating_room(self, client):
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


    def generate_an_unique_room_code(self):
        # Generate an unique room code with roomCodeLength characters
        # Each character is either a letter (upper or lower) or a digit
        charPools = string.ascii_letters + string.digits
        roomCode = ''.join(secrets.choice(charPools) 
                        for _ in range(self.ROOM_CODE_LENGTH))
        while roomCode in self.roomCodes:
            roomCode = ''.join(secrets.choice(charPools) 
                            for _ in range(self.ROOM_CODE_LENGTH))
        self.roomCodes.add(roomCode)
        return roomCode


    def genrate_and_send_room_code(self, conn, address):
        # Generate an unique room code for this client
        roomCode = self.generate_an_unique_room_code()
        # Send the generated room code to the client
        conn.send(roomCode.encode())
        print(f'Sent room code [{roomCode}] to client [{address}].')
        return roomCode


    def create_room(self, roomCode):
        room = Room(roomCode)
        self.rooms.append(room) 
        return


    def enter_room(self, clientObj, roomCode):
        room = [r for r in self.rooms if r.get_room_code() == roomCode][0]
        room.add_client_to_client_list(clientObj)
        return
        

    def check_room_exist_with_room_code(self, roomCode):
        for room in self.rooms:
            if room.get_room_code() == roomCode:
                return True
        return False
        

    def print_room_status(self, room):
        print(f'Connected clients in room [{room.get_room_code()}]:',
            f'{len(room.get_client_list())}')
        for idx, clientObj in enumerate(room.get_client_list()):
            print(f'Client {idx+1}: [{clientObj.get_username()},',
                f'{clientObj.get_address()}]')
        print('') 
        return


    def get_message_from_client(self, client):
        # Receive message from one client
        msg = client.recv(1024)
        print(f'Message from {client.getpeername()}:', msg.decode())
        return msg


    def handle_client_normal_message(self, client, decodedMsg, roomCode):
        clientSocketsToBeRemoved = []
        room = [r for r in self.rooms if r.get_room_code() == roomCode][0]
        # Broadcast received message to all clients within the same room
        for clientObject in room.get_client_list():
            socket = clientObject.get_socket()
            # Test if client socket is still alive before sending msg
            # If not, store it to a list for later removal
            if not self.is_client_alive(socket): # this sends an empty string to client
                clientSocketsToBeRemoved.append(socket)
                continue
            
            # Else, send received message to all clients in that room
            date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            msgWithTime = f'[{date_now} {client.getpeername()}: '
            msgWithTime += f'{decodedMsg}]'
            socket.send(msgWithTime.encode())
            
        # Remove disconnected clients
        for socket in clientSocketsToBeRemoved:
            self.remove_a_client_from_clients_by_socket(socket)
            socket.close()
        return


    def close_connection_with_client_when_error(self, error, client, address, roomCode):
        print(f'Error: {error}. Removed {client.getpeername()}', 
                ' from client socket list.')
        self.handle_client_disconnect_request(client, address, roomCode)
        return


    def handle_one_client(self, clientObj):
        client = clientObj.get_socket()
        address = clientObj.get_address()
        roomCode = clientObj.get_room_code()
        while not self.shutdownEvent.is_set():
            try:
                msg = self.get_message_from_client(client) # Buffer size: 1024
                
                # Disconnect from this connection if msg is empty
                if not msg:
                    self.handle_client_disconnect_request(client, address, roomCode)
                    break
                else:
                    decodedMsg = msg.decode()
                    self.handle_client_normal_message(client, decodedMsg, roomCode)
            except (BrokenPipeError, 
                    ConnectionResetError, 
                    ConnectionAbortedError) as e:
                # Close connection with this client
                self.close_connection_with_client_when_error(e, client, address, roomCode)
                break
        return


    def start_handling_one_client(self, clientObj):
        t = Thread(target=self.handle_one_client, args=(clientObj,))
        t.daemon = False # Set daemon thread: ends when the main thread ends
        self.threads.append(t)
        t.start()
        return


    def print_info_when_client_enter_room(self, address, username, roomCode):
        print(f'Accepted connection request from Client on [{address}].')
        print(f'With Username: [{username}], room code: [{roomCode}].')
        print(f'Connected clients: [{len(self.clients)}/{self.MAX_CLIENT_COUNT}]')
        room = [r for r in self.rooms if r.get_room_code() == roomCode][0]
        self.print_room_status(room)
        return
            
            
    def test_reach_max_client_count(self, conn, address):
        # Disconnect from the connection if reached max client count already
        if len(self.clients) >= self.MAX_CLIENT_COUNT:
            print(f'Max client count [{self.MAX_CLIENT_COUNT}] reached.'
                ,f'Refused connection from {address}.\n')
            conn.send(b'-1') # refuse this connection by sending an string of -1
            conn.close()
            return True
        # Otherwise, acknowledge the connection by sending len(clients)+1 to client
        msg = str((len(self.clients)+1))
        conn.send(msg.encode())
        return False


    def accept_a_connection(self):
        try:
            # Accept the connection established by a client
            conn, address = self.server.accept()
            
            # If reached max client count before this client: 
            #   disconnect, then acknowledge the client about the disconnection
            # Otherwise, acknowledge the client about the successful connection
            if self.test_reach_max_client_count(conn, address):
                return True
            
            # Wait for client to either create or enter room
            clientWantsToCreateRoom = self.get_client_response_on_creating_room(conn)
            
            # Client wants to create a new room
            if clientWantsToCreateRoom:
                roomCode = self.genrate_and_send_room_code(conn, address)
            else:
                # Wait for client to send valid room code
                createRoomInstead, roomCode = self.handle_client_room_code_message(
                                                        conn, address)
                if createRoomInstead: 
                    clientWantsToCreateRoom = True

            # Wait for client to send valid username
            username = self.handle_client_username_message(conn)
            
            # Create a client obj for this client
            clientObj = Client_Obj(conn, address, username, roomCode)
            self.clients.append(clientObj)
            
            # Create the room if the client chose to do so
            if clientWantsToCreateRoom:
                self.create_room(roomCode)

            # Make the client enter the Room
            self.enter_room(clientObj, roomCode)
            self.print_info_when_client_enter_room(address, username, roomCode)

            # Start a new thread to handle this client
            self.start_handling_one_client(clientObj)
            return True
        except KeyboardInterrupt as e:
            # server received the [ctrl+c] command while waiting for connection
            print(f'Error: {e}. Disconnected with all clients and exiting now.')
            self.shutdownEvent.set()
            for clientObj in self.clients:
                socket = clientObj.get_socket()
                # Send an empty string to the client as a notification
                socket.send(b'')
                socket.close()
            self.clients.clear()
            return False

    def run_server(self): 
        # Set up server socket     
        self.init_server()  
        # Start listening for connection
        self.server.listen(self.MAX_CLIENT_COUNT)
        print(f'Server socket on [{self.SERVER_IP}: {self.SERVER_PORT}] started listening.')
        print(f'MAX: {self.MAX_CLIENT_COUNT} clients.')
        print(f'Connected clients: [{len(self.clients)}/{self.MAX_CLIENT_COUNT}]\n')

        while True:
            # Start accepting connections established by clients
            if not self.accept_a_connection():
                break
                
        for t in self.threads:
            t.join()
        self.server.close()
        print('Server socket closed.')
        exit()
    

if __name__=='__main__':
    server = Server()
    server.run_server()
