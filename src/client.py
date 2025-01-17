# client.py

'''
To run this script: python3 client.py
Note: must be executed when the server is alive.

Note: 'client' is essentially only a socket in client.py
'''


import socket
from file_transmission import (get_filepath, check_if_file_exists, 
                              create_metadata, check_metadata_format, 
                              split_metadata, send_file, recv_file)
from message import (rstrip_message, add_prefix,
                     get_prefix_and_content)
from threading import Thread, Event


class Client:
    def __init__(self):
        self.SERVER_IP = '127.0.0.1' # depending on server ip
        self.SERVER_PORT = 5001
        
        self.client = self.init_client_socket() # client socket
        
        self.shutdownEvent = Event() # threading.Event()
        self.ruleAboutRoomCodeSent = False
        
        self.TYPE_PREFIX_SIZE = 1
        self.MSG_CONTENT_SIZE = 1024
        self.CHUNK_SIZE = self.TYPE_PREFIX_SIZE + self.MSG_CONTENT_SIZE


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
        # Receive message from server
        while not self.shutdownEvent.is_set():
            try:
                msg = self.client.recv(self.CHUNK_SIZE) # 1025 bytes
                
                # Empty message received -> server closed connection
                if not msg:
                    print('Server has closed the connection.')
                    self.shutdownEvent.set()
                    break
                
                typePrefix, msgContent = get_prefix_and_content(msg)
                prefix = int.from_bytes(typePrefix, byteorder='big')

                match prefix:
                    case 0: # normal message
                        msgContent = rstrip_message(msgContent)
                        print(msgContent.decode() + '\n')
                    case 1: # file content
                        # msgContent is metadata of the file
                        self.recv_file_from_server(msgContent)
                    case _: # invalid prefix
                        print(f'Received invalid prefix: {typePrefix}.')
            except Exception as e:
                print(f'Error [{e}] occurred when receiving message.')
                break
        self.client.close() # will be detected by server's 'recv()'
        print('Client receiver thread stopped.')
        return

        
    def get_and_send_user_input_msg(self):
        # Sent rules to the client console
        print('\nInput a message to send to the channel, ',
            'or\nInput [file] to send a file.\n')
        print('Press [Enter/Return] key to disconnect.\n')

        # Send message to server
        while not self.shutdownEvent.is_set():            
            msg = rstrip_message(input())
            
            # Empty message -> client closes connection
            if not msg:
                print('Disconnected from the channel.\n')
                self.shutdownEvent.set()
                self.client.close() # will be detected by server's 'recv()'
                break
            elif msg.lower() == 'file': # Client wants to send a file to server
                print('Type in filename of the file you want to send:\n')
                filename = rstrip_message(input())
                
                # Informing server that this client wants to send a file
                self.client.send(add_prefix('file'.encode(), 1))
                
                # Send the file to server
                self.send_file_to_server(filename)
            else: # Client wants to send a normal message to server
                msgWithPrefix = add_prefix(msg.encode(), 0)
                self.client.send(msgWithPrefix)
        print('Client sender thread stopped.')
        return


    def recv_user_input_and_send_to_server(self):
        msg = rstrip_message(input())
        
        # If client input empty message, make them input again
        while msg == '':
            print('Empty message detected. Please type your message:')
            msg = rstrip_message(input())
        
        # Msg here does not have type prefix, since this function 
        #   should only handles cases of room code and username.
        self.client.send(msg.encode())
        response = self.client.recv(self.CHUNK_SIZE)
        return msg, response.decode()

        
    def send_username_to_server(self):
        print('Input your username:')
        return self.recv_user_input_and_send_to_server()
        

    def send_decision_on_room_to_server(self):
        return self.recv_user_input_and_send_to_server()


    def send_room_code_to_server(self):
        print('Input room code here:\n')
        return self.recv_user_input_and_send_to_server()
    
    
    def recv_file_from_server(self, msgContent):
        # Obtain metadata
        metadata = msgContent.decode()
        print(f'Metadata:  {metadata}.')
        if not check_metadata_format(metadata):
            return
                
        # Split the metadata of the file received from server
        filename, filesize = split_metadata(metadata)
        
        # Receive the whole file from server
        recv_file(filename, filesize, self.client, 
                 self.MSG_CONTENT_SIZE, 'server')
        return
    
    
    def send_file_to_server(self, filename):
        # Create filepath from filename
        filepath = get_filepath(filename)
        if not check_if_file_exists(filepath):
            return
        
        # Create and send metadata to server
        filename, filesize = create_metadata(filepath)
        msg = f'{filename}|{filesize}'
        msgWithPrefix = add_prefix(msg.encode(), 1)
        self.client.send(msgWithPrefix)        
        
        # Send the whole file to server
        send_file(filepath, filename, self.client, 
                 self.MSG_CONTENT_SIZE, 'server')
        return

        
    def check_if_server_reached_max_client_capacity(self):
        # When trying to connect to server, if server sent '-1', it means that
        #  server has reached the max number of clients.
        # Thus the connection should fail.
        msg = rstrip_message(self.client.recv(self.MSG_CONTENT_SIZE)).decode()
        print(f'Init msg from server: {msg}.')
        
        if msg == '-1':
            print('Connection refused by server: max client count reached.')
        else:
            print('Connected to server successfully!')
        
        return msg != '-1'

        
    def run_client(self):
        # Prevent connection if client socket is not initialized correctly
        if self.client == None:
            exit()
        # Prevent connection if server reached max client capacity
        if not self.check_if_server_reached_max_client_capacity():
            print('Connection failed: server reached max client capacity.')
            exit()
            
        # Try sending client decision on room to server
        # If msg is 'C', response will be a room code generated by server
        # If msg is 'E', response will be:
        #   1. server generated room code, if received <c> from client
        #   2. 'VALID_ROOM_CODE' sent by server, if the room code is valid
        #   3. an error message sent by server, otherwise
        # Otherwise,     response will be an error message sent by server
        print('Input <C> to Create a new room, OR')
        print('Input <E> to Enter an existing room.\n')
        msg, response = self.send_decision_on_room_to_server()
        while msg.upper() != 'C':
            print(f'msg: {msg}, response from server: {response}')
            if msg.upper() == 'E':
                msg, response = self.send_room_code_to_server()
                print(f'msg: {msg}, response from server: {response}')
                if msg.upper() == 'C':
                    break
                if response == 'VALID_ROOM_CODE':
                    response = msg
                    break
            msg, response = self.send_decision_on_room_to_server()
        print(f'In Room: [{response}].\n')
        
        # Try sending client username to server
        msg, response = self.send_username_to_server()
        while response != 'VALID_USERNAME':
            print(f'msg: {msg}, response from server: {response}')
            msg, response = self.send_username_to_server()
            
        # Use thread t1 to receive message from server
        t1 = Thread(target=self.recv_msg_from_channel, args=())
        t1.daemon = True
        t1.start()

        # Use thread t2 to send message to server
        t2 = Thread(target=self.get_and_send_user_input_msg, args=())
        t2.daemon = True
        t2.start()
    
        # Wait until t1 and t2 converges
        t1.join()
        t2.join()
        print('All threads joined.')
        print('Client socket closed.')
        exit()
        

if __name__ == '__main__':
    client = Client()
    client.run_client()
    