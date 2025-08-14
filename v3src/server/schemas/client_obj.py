# client_obj.py

import uuid

class Client_Obj:
    def __init__(self, socket, address, username, roomCode):
        self.__uuid = uuid.uuid4() # unmodifiable, unique
        self.__socket = socket     # unmodifiable, unique
        self.__address = address   # unmodifiable, unique
        self.__username = username # duplicate-able

    def get_uuid(self):
        return str(self.__uuid)
        
    def get_socket(self): 
        return self.__socket
    
    def get_address(self):
        return self.__address
    
    def get_username(self):
        return self.__username
    
    def set_username(self, username):
        self.__username = username
        
    # Used to store the client object to the database
    def to_dict(self):
        # Need to wrap uuid with str() to make it compatible with bson (database related)
        # Note: this does not include self.__roomCode, as the client will be added
        #       only to the target room (and no rooms else).
        return {
            'uuid': str(self.__uuid),
            'address': self.__address,
            'username': self.__username,
        }
