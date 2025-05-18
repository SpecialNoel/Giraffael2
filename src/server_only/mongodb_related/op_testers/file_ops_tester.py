# file_ops_tester.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))

from file_ops.upload_op import upload_file
from file_ops.download_op import download_file
from file_ops.list_op import get_file_history
from file_ops.delete_op import delete_file, delete_all_files

if __name__=='__main__':  
    roomCode = 'f9wa8rq9fqvg0qj'
    roomID = '681e9d269581da6a87579f37'
    filepath = '/Users/jianminglin/test_files/Giraffe.jpg'
    
    filename = 'Giraffe.jpg'
    fileID = '681e9e0c2353582f23e3635b'
    savedir = '/Users/jianminglin/recv_files'
    
    #upload_file(filepath, roomCode)
    #download_file(fileID, roomCode, savedir)
    #get_file_history(roomCode)
    #delete_file(fileID, roomCode)
    #delete_all_files(roomCode)
    