# client.py

# To run this script: python3 client.py
# Note: must be executed when the server is alive.

# Note:
# 'client' is essentially only a socket in client.py

import socket
from file_transmission import (get_filepath, check_if_file_exists, 
                               create_metadata, send_metadata, 
                               recv_metadata, send_file, recv_file)
from message import (rstrip_message, add_prefix_to_message, 
                     separate_type_prefix_from_message)
from threading import Thread, Event


class Client:
    def __init__(self):
        self.SERVER_IP = '127.0.0.1'
        self.SERVER_PORT = 5001
        
        self.client = self.init_client_socket() # client socket
        
        self.shutdownEvent = Event() # threading.Event()
        self.ruleAboutRoomCodeSent = False
        self.filepath = ''
        self.CHUNK_SIZE = 1024
        

    def init_client_socket(self):
        try: 
            # TCP connection
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to the server socket with [IP, Port number] combination
            self.client.connect((self.SERVER_IP, self.SERVER_PORT)) 
            return self.client
        except ConnectionRefusedError:
            print('Connection refused. Server is not on yet.')
            return None


    def recv_msg_from_channel(self):
        # Receive message from other clients in the channel
        while not self.shutdownEvent.is_set():
            try:
                msg = rstrip_message(self.client.recv(self.CHUNK_SIZE))
                # Received a message of string 0 (only possible from server)
                # This means that the server wants to close this connection
                #   b/c of max clients count reached in server
                if not msg:
                    print('Server has closed the connection.')
                    self.shutdownEvent.set()
                    break
                typePrefix, msgContent = separate_type_prefix_from_message(msg)
                if typePrefix == None: 
                    print('The message received does not have type prefix.')
                    continue
                if typePrefix.decode() == 'NOR':
                    print(msgContent.decode() + '\n')
                elif typePrefix.decode() == 'FIL':
                    print(f'Received file content: {msgContent}\n')
                
            except Exception as e:
                print(f'Error [{e}] occurred when receiving message.')
                break
        self.client.close() # will be detected by server's 'recv()'
        print('Client receiver thread stopped.')
        return

        
    def get_and_send_user_input_msg(self):
        ruleSent = False

        while not self.shutdownEvent.is_set():
            if not ruleSent: 
                ruleSent = True
                print('\nType a message to send to the channel, ',
                    'or\nPress [Enter/Return] key to disconnect.\n')
                print('Type [file] to send a file.\n')
            
            msg = rstrip_message(input())
            if not msg:
                print('Disconnected from the channel.\n')
                self.shutdownEvent.set()
                self.client.close() # will be detected by server's 'recv()'
                break
            elif msg.lower() == 'file':
                print('Type in filename of the file you want to send:\n')
                filename = rstrip_message(input())
                self.send_file_to_server(filename)
            else:
                msg = add_prefix_to_message(msg, 'FIL')
                self.client.send(msg.encode())
        print('Client sender thread stopped.')
        return


    def recv_user_input_and_send_to_server(self):
        msg = rstrip_message(input())
        
        while msg == '':
            print('Empty message detected. Please type your message:')
            msg = rstrip_message(input())
        
        self.client.send(msg.encode())
        response = self.client.recv(self.CHUNK_SIZE)
        return msg, response.decode()

        
    def send_username_to_server(self):
        print('Type in your username:')
        return self.recv_user_input_and_send_to_server()
        

    def send_decision_on_room_to_server(self):
        if not self.ruleAboutRoomCodeSent:
            self.ruleAboutRoomCodeSent = True
            print('Type in a single letter <C> to Create a new room, OR')
            print('Type in a single letter <E> to Enter an existing room.\n')
        return self.recv_user_input_and_send_to_server()


    def send_room_code_to_server(self):
        print('Type in the room code to enter an existing room.\n')
        return self.recv_user_input_and_send_to_server()
    
    
    def send_file_to_server(self, filename):
        self.filepath = get_filepath(filename)
        if not check_if_file_exists(self.filepath):
            return
        
        filename, filesize = create_metadata(self.filepath)
        send_metadata(filename, filesize, self.client)
        send_file(self.filepath, self.client, self.CHUNK_SIZE)
        return

        
    def check_if_server_reached_max_client_capacity(self):
        msg = rstrip_message(self.client.recv(self.CHUNK_SIZE))
        print(f'Init msg from server: {msg.decode()}.')
        
        if msg.decode() == '-1':
            print('Connection refused by server: max client count reached.')
        else:
            print('Connected to server successfully!')
        
        return msg.decode() != '-1'


    def is_connection_alive(self):
        try:
            self.client.send(b'')
            return True
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            print(f'Error: {e}. ',
                  f'Connection with server is no longer alive.')
            return False
        
        
    def run_client(self):
        if self.client == None:
            exit()

        if not self.check_if_server_reached_max_client_capacity():
            exit()
            
        # If msg is 'C', response will be a room code generated by server
        # If msg is 'E', response will be:
        #   1. server generated room code, if received <c> from client
        #   2. 'VALID_ROOM_CODE' sent by server, if the room code is valid
        #   3. an error message sent by server, otherwise
        # Otherwise,     response will be an error message sent by server
        msg, responseOnRoomCode = self.send_decision_on_room_to_server()
        while msg.upper() != 'C':
            print(f'msg: {msg}, response from server: {responseOnRoomCode}')
            if msg.upper() == 'E':
                msg, responseOnRoomCode = self.send_room_code_to_server()
                print(f'msg: {msg}, response from server: {responseOnRoomCode}')
                if msg.upper() == 'C':
                    break
                if responseOnRoomCode == 'VALID_ROOM_CODE':
                    responseOnRoomCode = msg
                    break
            msg, responseOnRoomCode = self.send_decision_on_room_to_server()
            
        print(f'In Room: [{responseOnRoomCode}].\n')
                
        msg, responseOnUsername = self.send_username_to_server()
        while responseOnUsername != 'VALID_USERNAME':
            print(responseOnUsername)
            msg, responseOnUsername = self.send_username_to_server()
            
        # Use thread t1 to receive message
        t1 = Thread(target=self.recv_msg_from_channel, args=())
        t1.daemon = True
        t1.start()

        # Use thread t2 to send message
        t2 = Thread(target=self.get_and_send_user_input_msg, args=())
        t2.daemon = True
        t2.start()
    
        t1.join()
        t2.join()

        print('Client socket closed.')
        exit()
        

if __name__ == '__main__':
    client = Client()
    client.run_client()
    