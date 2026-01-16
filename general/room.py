# room.py

import os
import shutil
from pathlib import Path

class Room:
    def __init__(self, room_code, room_name='New Room'):
        self.__room_code = room_code # unmodifiable, unique
        self.__room_name = room_name
        self.__client_list = []  # each element is a client_obj
        self.__message_list = [] # used to display msg list to client only
        self.__message_list_for_server = [] # used by server
        self.__stored_files = []
        
        self.__folder_name = str(self.__room_code)
        self.__full_path = self.get_full_path_to_rooms()
    
    def get_room_code(self):
        return self.__room_code
    
    def get_room_name(self):
        return self.__room_name
    
    def get_client_list(self):
        return self.__client_list
    
    def get_message_list(self):
        return self.__message_list
    
    def get_message_list_for_server(self):
        return self.__message_list_for_server
    
    def get_stored_files(self): 
        return self.__stored_files
    
    def get_folder_name(self):
        return self.__folder_name
    
    def get_full_path(self):
        return self.__full_path
        
    def set_room_name(self, room_name):
        self.__room_name = room_name
        
    def add_client_to_client_list(self, client_socket):
        self.__client_list.append(client_socket)
        
    def add_message_to_message_list(self, msg):
        self.__message_list.append(msg)
        
    def add_message_to_message_list_for_server(self, msg):
        self.__message_list_for_server.append(msg)
    
    def add_files_to_stored_files(self, filename):
        self.__stored_files.append(filename)
        
    def get_full_path_to_rooms(self):
        path_to_parent = os.path.abspath('.')
        print(f'path_to_parent: ', path_to_parent)
        parent_folder_name = Path(path_to_parent).resolve().name
        if parent_folder_name != 'upload':
            path_to_rooms = os.path.join(path_to_parent, 'upload' + os.sep + 'rooms')
        else:
            path_to_rooms = os.path.join(path_to_parent, 'rooms')
        print(f'path_to_rooms: ', path_to_rooms)
        full_path = os.path.join(path_to_rooms, self.__folder_name)
        print(f'full_path: ', full_path)
        return full_path
        
    def remove_client_from_client_list(self, address):
        for client_obj in self.__client_list:
            if client_obj.get_address() == address:
                self.__client_list.remove(client_obj)
                break

    def create_file_storing_folder(self):
        try: 
            os.makedirs(self.__full_path, exist_ok=True)
            print(f'Folder [{self.__full_path}] created successfully.')
        except FileNotFoundError:
            print('Error creating file-storing folder for room',
                  f'[{self.__room_code}].')
            print(f'Parent directory for [{self.__full_path}] not found.')
        except Exception as e:
            print('Error creating file-storing folder for room',
                  f'[{self.__room_code}].')

    def delete_file_storing_folder(self):
        # Remove the folder and its contents
        try:
            shutil.rmtree(self.__full_path)
            print(f'Folder [{self.__full_path}] and its contents deleted successfully.')
        except FileNotFoundError:
            print('Error deleting file-storing folder for room',
                  f'[{self.__room_code}].')
            print(f'Folder [{self.__full_path}] does not exist.')
        except Exception as e:
            print(f'Error deleting folder [{self.__full_path}]: [{e}].')
            
    def delete_all_files_in_file_storing_folder(self):
        for filename in os.listdir(self.__full_path):
            file_path = os.path.join(self.__full_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            
    def clear_msg_history(self):
        self.__message_list = []
        self.__message_list_for_server = []
    
    def clear_file_history(self):
        self.__stored_files = []
        self.delete_all_files_in_file_storing_folder()
