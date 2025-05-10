# server.py

'''
To run this script: python3 server.py

Note: Every 'client' instance references to a socket in server.py
'''

import socket
import string
from general.file_transmission import CHUNK_SIZE, MAX_FILE_SIZE, EXT_LIST
from server_only.accept_connection import accept_a_connection
from server_only.retrieve_secret_from_aws import setup_tls_context_remote
from server_only.tls_management import setup_tls_context_locally
from server_only.settings import serverIsLocal, usingOpenAI, usingTLS
from threading import Thread, Event

class Server:
    def __init__(self):
        # Run Local or Remote server
        self.usingLocalServer = serverIsLocal
        self.usingRemoteServer = not self.usingLocalServer
        # OpenAI
        self.usingOpenAI = usingOpenAI
        # TLS
        self.usingTLS = usingTLS
        self.context = None
        if self.usingTLS:
            self.context = setup_tls_context_locally() if self.usingLocalServer else setup_tls_context_remote()
        
        # Parameters of server
        self.SERVER_IP = self.get_server_ip_based_on_mode()
        self.SERVER_PORT = 5001
        self.server = None # server socket
        self.MAX_CLIENT_COUNT = 3
        self.ROOM_CODE_LENGTH = 11
        self.MAX_USERNAME_LENGTH = 16
        self.clients = [] # a list of 'Client_Obj's
        self.rooms = [] # a dictionary of 'Room's
        self.roomCodes = set() # a set of room codes
        
        # Threads
        self.shutdownEvent = Event() # threading.Event()
        self.threads = [] # all threads that handle each client
        
        # Char pools: contains all Digits, Upper and Lower-case letters
        self.CHAR_POOLS = string.ascii_letters + string.digits
        self.CHUNK_SIZE = CHUNK_SIZE # size of each chunk to send/receive
        self.MAX_FILE_SIZE = MAX_FILE_SIZE # limit of file size to send/receive
        self.EXT_LIST = EXT_LIST # valid file extensions for file transmission
        
    def get_server_ip_based_on_mode(self):
        def get_server_private_ip():
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
                print(f'Error occurred when getting server ip: [{e}]')
                # Use localhost as server ip if getting error
                return '127.0.0.1'
    
        if self.usingLocalServer:
            # host with private ip for testing locally
            return get_server_private_ip()
        elif self.usingRemoteServer:
            # host remote server on aws ec2
            return '0.0.0.0'
        else:
            # host for testing in this same machine
            print('Invalid option for remote or local server.\n',
                  'Server IP now set to [127.0.0.1].')
            return '127.0.0.1'
    
    def init_server(self):
        # Setup server that uses TCP connection
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow server to reuse the previous [IP, Port number] combination
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the [IP, Port number] combination to the server
        self.server.bind((self.SERVER_IP, self.SERVER_PORT))
        return 
    
    def start_listening(self):
        self.server.listen(self.MAX_CLIENT_COUNT)
        print(f'Server socket on [{self.SERVER_IP}: {self.SERVER_PORT}] ',
              f'started listening.')
        print(f'MAX: [{self.MAX_CLIENT_COUNT}] clients.')
        print(f'All connected clients: ',
              f'[{len(self.clients)}/{self.MAX_CLIENT_COUNT}]\n')
        return
        
    def start_accepting(self, server):
        # Accept the connection established by a client
        conn, address = server.accept()
        
        # Use a separate thread to accept and handle this client
        t = Thread(target=accept_a_connection, 
                args=(conn, address, self.clients, self.rooms,
                      self.roomCodes, self.CHAR_POOLS,
                      self.shutdownEvent, self.CHUNK_SIZE,
                      self.ROOM_CODE_LENGTH,
                      self.MAX_USERNAME_LENGTH,
                      self.MAX_CLIENT_COUNT,
                      self.MAX_FILE_SIZE, self.EXT_LIST, self.usingOpenAI))
        t.daemon = False # thread ends when the main thread ends
        self.threads.append(t)
        t.start()
        return
        
    def run_server(self): 
        def print_server_parameters():
            print('Server parameters:\n',
                  f'- Server is hosted locally: {self.usingLocalServer}\n',
                  f'- Server is using OpenAI:   {self.usingOpenAI}\n',
                  f'- Server is using TLS:      {self.usingTLS}\n')
            return 
        
        def run_server_loop(server):
            # Server should be always-on
            while True:
                try:
                    self.start_accepting(server)
                except KeyboardInterrupt as e:
                    handle_keyboard_interrupt(e)
                    break
            return        

        def handle_keyboard_interrupt(e):
            print(f'Error: [{e}]. Disconnected with all clients and exiting now.')
            self.shutdownEvent.set()
            
            # Close connections with all clients
            for clientObj in self.clients:
                socket = clientObj.get_socket()
                # Send an empty string to the client as an indicator
                socket.send(b'')
                socket.close()
            self.clients.clear()
            return
        
        def handle_end_server():
            # Wait until all threads converge
            for t in self.threads:
                t.join()
            print('All threads joined.')
            self.server.close()
            print('Server socket closed.')
            exit()
            return
        
        # Set up server socket     
        self.init_server() 
        print_server_parameters()
        # Start listening for connection from clients
        self.start_listening()
        # Run server with or without TLS
        if self.usingTLS and self.context != None:
            with self.context.wrap_socket(self.server, server_side=True) as tls_server:
                run_server_loop(tls_server)
        else:
            run_server_loop(self.server)
        # Close the server and release all existing histories (clients, files, messages)
        handle_end_server()
        return
    
if __name__=='__main__':
    server = Server()
    server.run_server()
