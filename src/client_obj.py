# client_obj.py

class Client_Obj:
    def __init__(self, socket, username, roomCode):
        self.__socket = socket # Unmodifiable, unique
        self.__username = username
        self.__roomCode = roomCode
        
    def get_socket(self):
        return self.__socket
    
    def get_username(self):
        return self.__username

    def get_room_code(self):
        return self.__roomCode
    
    def set_username(self, username):
        self.__username = username
        
    def set_roomCode(self, roomCode):
        self.__roomCode = roomCode
