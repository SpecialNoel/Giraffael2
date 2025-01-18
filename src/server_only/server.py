# server.py


'''
To run this script: python3 server.py

Note: Every 'client' instance references to a socket in server.py
'''


import socket
import string
from server_only.accept_connection import accept_a_connection
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
        
        
    def get_server_ip():
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
                t = Thread(target=accept_a_connection, 
                           args=(conn, address, 
                                 self.clients,
                                 self.rooms,
                                 self.roomCodes,
                                 self.charPools,
                                 self.shutdownEvent,
                                 self.MSG_CONTENT_SIZE,
                                 self.CHUNK_SIZE,
                                 self.ROOM_CODE_LENGTH,
                                 self.MAX_USERNAME_LENGTH,
                                 self.MAX_CLIENT_COUNT))
                t.daemon = False # thread ends when the main thread ends
                self.threads.append(t)
                t.start()
            except KeyboardInterrupt as e:
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
