# room.py

import os
from pathlib import Path
import shutil

class Room:
    def __init__(self, roomCode, roomName='New Room'):
        self.__roomCode = roomCode # unmodifiable, unique
        self.__roomName = roomName
        self.__clientList = []  # each element is a client_obj
        self.__messageList = [] # used to display msg list to client only
        self.__messageListForServer = [] # used by server
        self.__storedFiles = []
        
        self.__folderName = str(self.__roomCode)
        self.__fullpath = self.get_fullpath_to_rooms()
    
    def get_room_code(self):
        return self.__roomCode
    
    def get_room_name(self):
        return self.__roomName
    
    def get_client_list(self):
        return self.__clientList
    
    def get_message_list(self):
        return self.__messageList
    
    def get_message_list_for_server(self):
        return self.__messageListForServer
    
    def get_stored_files(self): 
        return self.__storedFiles
    
    def get_folderName(self):
        return self.__folderName
    
    def get_fullpath(self):
        return self.__fullpath
        
    def set_room_name(self, roomName):
        self.__roomName = roomName
        
    def add_client_to_client_list(self, clientSocket):
        self.__clientList.append(clientSocket)
        
    def add_message_to_message_list(self, msg):
        self.__messageList.append(msg)
        
    def add_message_to_message_list_for_server(self, msg):
        self.__messageListForServer.append(msg)
    
    def add_files_to_stored_files(self, filename):
        self.__storedFiles.append(filename)
        
    def get_fullpath_to_rooms(self):
        pathToParent = os.path.abspath('.')
        print(f'pathToParent: ', pathToParent)
        parentFolderName = Path(pathToParent).resolve().name
        if parentFolderName != 'src':
            pathToRooms = os.path.join(pathToParent, 'src' + os.sep + 'rooms')
        else:
            pathToRooms = os.path.join(pathToParent, 'rooms')
        print(f'pathToRooms: ', pathToRooms)
        fullpath = os.path.join(pathToRooms, self.__folderName)
        print(f'fullpath: ', fullpath)
        return fullpath
        
    def remove_client_from_client_list(self, address):
        for clientObj in self.__clientList:
            if clientObj.get_address() == address:
                self.__clientList.remove(clientObj)
                break

    def create_file_storing_folder(self):
        try: 
            os.makedirs(self.__fullpath, exist_ok=True)
            print(f'Folder [{self.__fullpath}] created successfully.')
        except FileNotFoundError:
            print('Error creating file-storing folder for room',
                  f'[{self.__roomCode}].')
            print(f"Parent directory for '{self.__fullpath}' not found.")
        except Exception as e:
            print('Error creating file-storing folder for room',
                  f'[{self.__roomCode}].')

    def delete_file_storing_folder(self):
        # Remove the folder and its contents
        try:
            shutil.rmtree(self.__fullpath)
            print(f'Folder [{self.__fullpath}] and its contents deleted successfully.')
        except FileNotFoundError:
            print('Error deleting file-storing folder for room',
                  f'[{self.__roomCode}].')
            print(f'Folder [{self.__fullpath}] does not exist.')
        except Exception as e:
            print(f'Error deleting folder [{self.__fullpath}]: [{e}].')
            
    def delete_all_files_in_file_storing_folder(self):
        for filename in os.listdir(self.__fullpath):
            file_path = os.path.join(self.__fullpath, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            
    def clearMsgHistory(self):
        self.__messageList = []
        self.__messageListForServer = []
    
    def clearFileHistory(self):
        self.__storedFiles = []
        self.delete_all_files_in_file_storing_folder()
