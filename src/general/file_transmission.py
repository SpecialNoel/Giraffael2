# file_transmission.py

import os
from pathlib import Path
from general.message import rstrip_message, add_prefix

'''
Functions here are used by clients or server to transfer 
  different kinds of files (.jpg, .pdf, .txt, .csv, etc.).
'''


def get_filepath(filename):
    '''
    Used by the sender to get the filepath of a file from the current directory.

    @param filename: the string name of the file
    @return: filepath
    '''
    return Path.cwd() / filename


def check_if_file_exists(filepath):
    '''
    Used by the sender to check if the file exists or not.

    @param filepath: the filepath of the file
    @return: True if the filepath is a file; False otherwise 
    '''
    try:
        directory = os.path.dirname(filepath)
        if not directory:
            directory = '.'
        if not os.path.exists(directory):
            print("Invalid filepath: directory does not exist.")
            return False
        if not os.access(directory, os.W_OK):
            print("Invalid filepath: directory is not writable.")
            return False
        if not os.path.basename(filepath):
            print("Invalid filepath: filename is missing.")
            return False
        if not os.path.splitext(filepath)[1]:
            print("Invalid filepath: filename does not have an extension.")
            return False
        if os.path.isfile(filepath):
            print(f'Filepath [{filepath}] exits.')
        else:
            print(f'Filepath [{filepath}] does not exists.')
        return os.path.isfile(filepath)
    except Exception as e:
        print(f"Error validating filepath: {e}")
        print(f'Filepath [{filepath}] exits: {os.path.isfile(filepath)}.')
        return os.path.isfile(filepath)


def get_valid_filepath(filename):    
    filepath = get_filepath(filename)
    while not check_if_file_exists(filepath):
        print('\nType in filename of the file you want to send:')
        print('OR, type <exit> to stop sending file.\n')
        filename = rstrip_message(input())
        # Client does not want to send the file anymore
        if filename.lower() == 'exit':
            return None        
        filepath = get_filepath(filename)
    return filepath


def create_metadata(filepath):
    '''
    Used by the sender to create the associate metadata of the file.
    The metadata will be sent to the recipient before receiving 
    the original file.

    @param filepath: the filepath of the file
    @return: filename, filesize
    '''
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    print(f'Filename: {filename}, filesize: {filesize}.\n')
    return filename, filesize


def send_metadata(socket, filename, filesize):
    msg = f'{filename}|{filesize}'
    msgWithPrefix = add_prefix(msg.encode(), 1)
    socket.send(msgWithPrefix)


def check_metadata_format(msg):
    if msg.split('|')[0] == msg:
        print('Invalid metadata format.')
        return False
    print('Metadata format valid.')
    return True


def split_metadata(metadata):
    filename = metadata.split('|')[0]
    filesize = int(metadata.split('|')[1])
    print(f'Filename: {filename}, filesize: {filesize}.')
    return filename, filesize


def send_file(filepath, filename, socket, chunk_size, recipient):
    '''
    Used by the sender to send the file to the recipient.
    
    @param filepath: the filepath of the file
    @param socket: the socket used to send the file; the sender socket
    @param chunk_size: number of bytes to send to the recipient each time
    @param recipient: either 'server' or address of a client; indicates the receiver side
    @return: None
    '''
    try:
        with open(filepath, 'rb') as file:
            while chunk := file.read(chunk_size):
                socket.send(chunk)
        print(f'Successfully sent file [{filename}] to [{recipient}].\n')
    except FileNotFoundError:
        print(f'File with path [{filepath}] not found.')
    except Exception as e:
        print(f'Error occurred in send_file(): {e}.')
    return


def recv_file(filename, filesize, socket, chunk_size, sender):
    '''
    Used by the recipient to receive the file from the sender.
    Received content will be stored in the "received_files" folder
      with the same filename as the received filename.
    
    @param filename: the string name of the file
    @param filesize: the size of the file
    @param socket: the socket used to receive the file; the receiver socket
    @param chunk_size: number of bytes to receive from the sender each time
    @param sender: either 'server' or address of a client; indicates the sender side
    @return: None
    '''
    if sender == 'server':
        print(f'Stored in filepath: {filename}')
    else:
        filepath_prefix = 'received_files/'
        filename = filepath_prefix + filename
        print(f'Stored in filepath: {filename}')
    
    try:
        with open(filename, 'wb') as file:
            received_len = 0
            while received_len < filesize:
                data = socket.recv(chunk_size)
                if not data:
                    break
                file.write(data)
                received_len += len(data)
        print(f'Successfully received file [{filename}] from [{sender}].\n')
    except Exception as e: 
        print(f'Error occurred in recv_file(): {e}.')
    return