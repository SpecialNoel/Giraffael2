# client.py

'''
To run this script: python3 client.py
Note: must be executed when the server is alive.

Note: 'client' is essentially only a socket in client.py
'''

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[2] # grandparent level
sys.path.append(str(src_folder))

import socket
from client_only.others.get_server_elastic_ip import get_server_elastic_ip
from client_only.client_core.check_server_capacity import check_server_capacity
from client_only.client_core.client_onboarding import handle_room_decision
from client_only.client_core.client_onboarding import handle_username
from client_only.client_core.client_receiver_thread_ops import recv_msg_from_server
from client_only.client_core.client_sender_thread_ops import send_msg_to_server
from client_only.others.tls_management import setup_tls_context
from general.file_transmission import CHUNK_SIZE, MAX_FILE_SIZE, EXT_LIST
from server_only.others.settings import serverIsLocal, usingTLS
from threading import Event, Thread

class Client:
    def __init__(self):
        # Run Local or Remote server
        self.serverIsLocal = serverIsLocal
        self.serverIsRemote = not self.serverIsLocal
        # TLS
        self.usingTLS = usingTLS
        self.context = setup_tls_context() if self.usingTLS else None

        # Parameters of client
        self.SERVER_IP = self.get_server_ip_based_on_mode()
        self.SERVER_PORT = 5001
        self.client = self.init_client_socket() # client socket
        
        # Threads
        self.shutdownEvent = Event() # threading.Event()
        
        self.CHUNK_SIZE = CHUNK_SIZE
        self.MAX_FILE_SIZE = MAX_FILE_SIZE
        self.EXT_LIST = EXT_LIST
    
    def get_server_ip_based_on_mode(self):        
        if self.serverIsLocal:
            return '10.0.0.99' # for local machine
        elif self.serverIsRemote:
            return get_server_elastic_ip() # for remote server 
        else:
            # host for testing in this same machine
            print('Invalid option for remote or local server.\n',
                  'Server IP now set to [127.0.0.1].')
            return '127.0.0.1'

    def init_client_socket(self):
        try: 
            # TCP connection
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to the server socket with [IP, Port number] combination
            self.client.connect((self.SERVER_IP, self.SERVER_PORT)) 
            if self.usingTLS and self.context != None:
                tls_client = self.context.wrap_socket(self.client, server_hostname=self.SERVER_IP)
                print(f'Connected securely to {self.SERVER_IP} with protocol:',
                      f'{tls_client.version()}.')
                return tls_client
            return self.client
        except ConnectionRefusedError:
            print('Connection refused. Server is not on yet.')
            return None
        except Exception as e:
            print(f'Unhandled error in init_client_socket(): [{e}]')
            return None

    def run_client(self):
        # Prevent connection if client socket is not initialized correctly
        if self.client == None:
            exit()
        # Prevent connection if server reached max client capacity
        if not check_server_capacity(self.client, self.CHUNK_SIZE):
            print('Connection failed: server reached max client capacity.')
            exit()
            
        handle_room_decision(self.client, self.CHUNK_SIZE)
        handle_username(self.client, self.CHUNK_SIZE)
            
        # Use thread t1 to receive message from server
        t1 = Thread(target=recv_msg_from_server, 
                    args=(self.client, self.shutdownEvent, 
                          self.CHUNK_SIZE, self.MAX_FILE_SIZE, self.EXT_LIST))
        t1.daemon = True
        t1.start()
        # Use thread t2 to send message to server
        t2 = Thread(target=send_msg_to_server, 
                    args=(self.client, self.shutdownEvent, 
                          self.CHUNK_SIZE, self.MAX_FILE_SIZE, self.EXT_LIST))
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
    