# client_ops_tester.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[3] # grand-grandparent level
sys.path.append(str(src_folder))
from general.client_obj import Client_Obj
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from client_ops.add_op import add_client_to_list
from client_ops.list_op import list_clients
from client_ops.delete_op import delete_client_from_list

import socket

if __name__=='__main__':
    roomCode = 'f9wa8rq9fqvg0qj'
    roomID = '6828aa65117eaf7acd9826ec'
    
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = ('127.0.0.1', 54321)
    username = 'ARK'
    clientSocket = Client_Obj(socket, address, username, roomCode)
    
    add_client_to_list(clientSocket, roomCode)
    #list_clients(roomCode)
    #delete_client_from_list(clientSocket.get_address(), roomCode)
