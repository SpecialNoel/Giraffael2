# list_op.py

from src.server.app.db.mongo.msg_ops.general_op import room_code_exists_in_collection
from src.server.app.db.mongo.mongodb_initiator import rooms_collection

def list_clients(roomCode):
    if room_code_exists_in_collection(roomCode):
        print(f'Clients in room with roomCode [{roomCode}]:')
        room = rooms_collection.find_one(
            {'roomCode': roomCode},
        )
        clientList = room['clientList']
        for client in clientList:
            print(f'--uuid:[{client['uuid']}]. address:[{client['address']}]. username:[{client['username']}]')
    else: 
        print(f'Error in list_clients(). Room with room code [{roomCode}] does not exist.')
        return
    return 

def get_number_of_clients_from_one_room(roomCode):
    if room_code_exists_in_collection(roomCode):
        room = rooms_collection.find_one(
            {'roomCode': roomCode},
        )
        clientList = room['clientList']
        return len(clientList)
    else: 
        print('Error in get_number_of_clients_from_one_room(). ' +
             f'Room with room code [{roomCode}] does not exist.')
        return -1

def get_all_connecting_clients():
    rooms = rooms_collection.find({}, {'clientList': 1})
    allClient = []
    for room in rooms:
        clientList = room['clientList']
        for client in clientList:
            allClient.append((client['uuid'], client['address'], client['username']))
    return allClient

def get_number_of_clients_from_all_rooms():
    numberOfClients = 0
    
    for room in rooms_collection.find({}, {'clientList': 1}):
        numberOfClients += len(room.get('clientList', []))
    
    return numberOfClients
