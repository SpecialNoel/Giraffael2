# file_ops_tester.py

from server_only.mongodb_related.file_ops.upload_op import upload_file
from server_only.mongodb_related.file_ops.download_op import download_file
from server_only.mongodb_related.file_ops.list_op import list_files
from server_only.mongodb_related.file_ops.delete_op import delete_file, delete_all_files

if __name__=='__main__':  
    roomCode = 'f9wa8rq9fqvg0qj'
    roomID = '681e9d269581da6a87579f37'
    filepath = '/Users/jianminglin/test_files/Giraffe.jpg'
    
    filename = 'Giraffe.jpg'
    fileID = '681e9e0c2353582f23e3635b'
    savedir = '/Users/jianminglin/recv_files'
    
    #upload_file(filepath, roomID)
    #download_file(fileID, roomID, savedir)
    #list_files(roomID)
    #delete_file(fileID, roomID)
    #delete_all_files(roomID)
    