# file_ops_tester.py

from server_only.mongodb_related.file_ops.upload_op import upload_file
from server_only.mongodb_related.file_ops.download_op import download_file
from server_only.mongodb_related.file_ops.list_op import list_files
from server_only.mongodb_related.file_ops.delete_op import delete_file, delete_all_files

if __name__=='__main__':  
    room_code = 'f9wa8rq9fqvg0qj'
    room_id = '681e9d269581da6a87579f37'
    file_path = '/Users/jianminglin/test_files/Giraffe.jpg'
    
    filename = 'Giraffe.jpg'
    file_id = '681e9e0c2353582f23e3635b'
    save_dir = '/Users/jianminglin/recv_files'
    
    #upload_file(file_path, room_id)
    #download_file(file_id, room_id, save_dir)
    #list_files(room_id)
    #delete_file(file_id, room_id)
    #delete_all_files(room_id)
    