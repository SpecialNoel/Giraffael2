# client_obj.py

import uuid

class Client_Obj:
    def __init__(self, socket, address, username, room_code):
        self.__uuid = uuid.uuid4() # unmodifiable, unique
        self.__socket = socket     # unmodifiable, unique
        self.__address = address   # unmodifiable, unique
        self.__username = username # duplicate-able
        self.__room_code = room_code # unique

    def get_uuid(self):
        return self.__uuid
        
    def get_socket(self): 
        return self.__socket
    
    def get_address(self):
        return self.__address
    
    def get_username(self):
        return self.__username

    def get_room_code(self):
        return self.__room_code
    
    def set_username(self, username):
        self.__username = username
        
    def set_room_code(self, room_code):
        self.__room_code = room_code
        
    # Used to store the client object to the database
    def to_dict(self):
        # Need to wrap uuid with str() to make it compatible with bson (database related)
        # Note: this does not include self.__room_code, as the client will be added
        #       only to the target room (and no rooms else).
        return {
            'uuid': str(self.__uuid),
            'address': self.__address,
            'username': self.__username,
        }
