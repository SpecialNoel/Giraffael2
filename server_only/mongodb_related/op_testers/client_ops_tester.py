# client_ops_tester.py

import socket
from general.client_obj import Client_Obj
from server_only.mongodb_related.client_ops.add_op import add_client_to_list
from server_only.mongodb_related.client_ops.list_op import list_clients
from server_only.mongodb_related.client_ops.delete_op import delete_client_to_list

if __name__=='__main__':
    room_code = 'f9wa8rq9fqvg0qj'
    room_id = '681e9d269581da6a87579f37'
    
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = ('127.0.0.1', 54321)
    username = 'ARK'
    client_socket = Client_Obj(socket, address, username, room_code)
    
    #add_client_to_list(client_socket, room_code)
    #list_clients(room_code)
    #delete_client_to_list(client_socket.get_address(), room_code)
