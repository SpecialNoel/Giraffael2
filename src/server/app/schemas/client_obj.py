# client_obj.py

import uuid

class Client_Obj:
    def __init__(self, username):
        self.__uuid = uuid.uuid4() # unmodifiable, unique
        self.__username = username # duplicate-able

    def get_uuid(self):
        return str(self.__uuid)
    
    def get_username(self):
        return self.__username
    
    def set_username(self, username):
        self.__username = username
        
    # Used to store the client object to the database
    def to_dict(self):
        # Need to wrap uuid with str() to make it compatible with bson (database related)
        return {
            'uuid': str(self.__uuid),
            'username': self.__username,
        }
