# room.py

# The Room class is used as local cache of clientList that contains
#   clientObj, which in turn has the socket property. 
# We need this class since MongoDB does not support storing sockets
#   in the database, and we need a way to reference these sockets in
#   a room directly. For example, when a client sends a normal message
#   over the room, which would then be received by clients (or sockets of
#   these clients) in the same room as the sender client.

class Room:
    def __init__(self, roomCode, roomName='New Room'):
        self.__roomCode = roomCode # unmodifiable, unique
        self.__roomName = roomName
        self.__clientList = []     # each element is a clientObj
    
    def get_room_code(self):
        return self.__roomCode
    
    def get_room_name(self):
        return self.__roomName
    
    def get_client_list(self):
        return self.__clientList
    
    def set_room_name(self, roomName):
        self.__roomName = roomName
        
    def add_client_to_client_list(self, clientSocket):
        self.__clientList.append(clientSocket)
        
    def remove_client_from_client_list(self, address):
        for clientObj in self.__clientList:
            if clientObj.get_address() == address:
                self.__clientList.remove(clientObj)
                break
