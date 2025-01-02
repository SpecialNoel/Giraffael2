# room.py

class Room:
    def __init__(self, roomCode, roomName='New Room'):
        self.__roomCode = roomCode # unmodifiable, unique
        self.__roomName = roomName
        self.__clientList = []
    
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
