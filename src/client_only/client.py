# client.py

'''
To run this script: python3 client.py
Note: must be executed when the server is alive.

Note: 'client' is essentially only a socket in client.py
'''

import socket
from check_server_capacity import check_server_capacity
from handle_room_decision import handle_room_decision
from handle_username import handle_username
from recv_from_server import recv_msg_from_server
from send_to_server import send_msg_to_server
from threading import Event, Thread

class Client:
    def __init__(self):
        self.SERVER_IP = '127.0.0.1' # depending on server ip
        self.SERVER_PORT = 5001
        
        self.client = self.init_client_socket() # client socket
        
        self.shutdownEvent = Event() # threading.Event()
        self.ruleAboutRoomCodeSent = False
        
        self.CHUNK_SIZE = 1025

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
                          self.CHUNK_SIZE))
        t1.daemon = True
        t1.start()
        # Use thread t2 to send message to server
        t2 = Thread(target=send_msg_to_server, 
                    args=(self.client, self.shutdownEvent, 
                          self.CHUNK_SIZE))
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
    