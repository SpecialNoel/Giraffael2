# handle_download_request.py

from general.file_transmission import *

def handle_download_file_request(client):
    # Step1: prompt client where to store the file
    directory = get_client_directory()
    if directory == None:
        return
    directory = validate_client_directory(directory)
    if directory == None:
        return
    print(f'Directory [{directory}] is valid.')
    
    # Step2: prompt client which file to receive/download
    filename = get_client_filename()
    if filename == None:
        return
    filename = validate_client_filename(filename)
    if filename == None:
        return
    print(f'Filename [{filename}] is valid.')
    
    # Step3: start receiving metadata and file chunks if file exists on server
    # Inform server that this client wants to receive a file
    send_directory_and_filename(client, directory, filename)
    print('Download request sent.')
    return

def get_client_directory():
    print('Type in directory where you want to store the file.')
    print('OR, type <exit> to stop receiving file.\n')
    directory = rstrip_message(input())
    
    # Client does not want to receive the file anymore
    if directory.lower() == 'exit':
        print('Stopped receiving file.')
        display_rule()
        return None
    return directory
    
def validate_client_directory(directory):
    while not check_if_directory_exists(directory):
        print('Type in directory where you want to store the file.')
        print('OR, type <exit> to stop receiving file.\n')
        
        directory = rstrip_message(input())
        # Client does not want to receive the file anymore
        if directory.lower() == 'exit':
            print('Stopped receiving file.')
            display_rule()
            return None
    return directory

def get_client_filename():
    print('Type in name of the file you want to receive.')
    print('OR, type <exit> to stop receiving file.\n')
    filename = rstrip_message(input())
    
    # Client does not want to receive the file anymore
    if filename.lower() == 'exit':
        print('Stopped receiving file.')
        display_rule()
        return None
    return filename

def validate_client_filename(filename):
    while not check_if_filename_is_valid(filename):
        print('Type in name of the file you want to receive.')
        print('OR, type <exit> to stop receiving file.\n')
        
        filename = rstrip_message(input())
        # Client does not want to receive the file anymore
        if filename.lower() == 'exit':
            print('Stopped receiving file.')
            display_rule()
            return None
    return filename
