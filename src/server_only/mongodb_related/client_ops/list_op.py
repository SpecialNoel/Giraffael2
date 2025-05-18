# list_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from msg_ops.general_op import roomCode_to_roomID
from mongodb_initiator import rooms_collection

from bson import ObjectId


def list_clients(roomCode):
    roomID = roomCode_to_roomID(roomCode)

    if roomID:
        print(f'Clients in room with roomCode [{roomCode}]:')
        room = rooms_collection.find_one(
            {'_id': ObjectId(roomID)}
        )
        clientList = room['clientList']
        for client in clientList:
            print(f'--uuid:[{client['uuid']}]. address:[{client['address']}]. username:[{client['username']}]')
    else: 
        print(f'Error in add_client_to_list(). Room with roomCode [{roomCode}] does not exist.')
        return
    return 

def get_number_of_clients_from_one_room(roomCode):
    roomID = roomCode_to_roomID(roomCode)
    if roomID:
        room = rooms_collection.find_one(
            {'_id': ObjectId(roomID)}
        )
        clientList = room['clientList']
        return len(clientList)
    else: 
        print('Error in get_number_of_clients_from_one_room(). ' +
             f'Room with roomCode [{roomCode}] does not exist.')
        return -1

def get_all_connecting_clients():
    rooms = rooms_collection.find({}, {"clientList": 1})
    allClient = []
    for room in rooms:
        clientList = room['clientList']
        for client in clientList:
            allClient.append((client['uuid'], client['address'], client['username']))
    return allClient

def get_number_of_clients_from_all_rooms():
    numberOfClients = 0
    
    for room in rooms_collection.find({}, {"clientList": 1}):
        numberOfClients += len(room.get("clientList", []))
    
    return numberOfClients
