# room.py

# The Room class is used as local cache of clientList that contains
#   clientObj, which in turn has the socket property. 
# We need this class since MongoDB does not support storing sockets
#   in the database, and we need a way to reference these sockets in
#   a room directly. For example, when a client sends a normal message
#   over the room, which would (and should) then be received by clients 
#   (or, sockets of these clients) in the same room as the sender client.

class Room:
    def __init__(self, roomCode):
        self.__roomCode = roomCode # unmodifiable, unique
        self.__clientList = {}     # a dict whose elements are (uuid: clientObj)
    
    def get_room_code(self):
        return self.__roomCode
    
    def get_client_list(self):
        return self.__clientList
    
    def add_client_to_list(self, uuid, clientSocket):
        self.__clientList[uuid] = clientSocket
        
    def remove_client_from_list_by_uuid(self, uuid):
        del self.__clientList[uuid]
