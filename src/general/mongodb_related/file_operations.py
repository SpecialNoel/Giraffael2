# file_operations.py

# Sorts of MongoDB operations used to list, upload, download or delete files in each room.

from pymongo import MongoClient
import gridfs
from bson import ObjectId
import os

# Connect to MongoDB with the connection string for Giraffael2DB
uri = ('mongodb+srv://jianminglin2893:cbVSqJdDMIUnso6Q' + 
       '@ac-os3juge.wu2ivo7.mongodb.net/Giraffael2DB' + 
       '?retryWrites=true&w=majority&tls=true')
mongoClient = MongoClient(uri, serverSelectionTimeoutMS=3000)

db = mongoClient['Giraffael2DB'] 
rooms_collection = db['Rooms'] # the "Rooms" collection
gfs = gridfs.GridFS(db)


# Upload file
def upload_file(filepath, roomCode):
    room = rooms_collection.find_one(
        {'roomCode': roomCode}
    )
    if room: 
        nameOfFile=filepath.split('/')[-1]
        with open(filepath, 'rb') as f:
            fileID = gfs.put(
                f,
                filename=nameOfFile,
                metadata={'roomCode': roomCode}
            )
        rooms_collection.update_one(
            {'roomCode': roomCode},
            {'$push': {'filelist': nameOfFile}}
        )
        print(f'Uploaded file [{nameOfFile}] with fileID: [{fileID}].')
        return fileID
    else:
        print(f'Error in upload_file(). Room with roomCode [{roomCode}] does not exist.')
        return -1

# Download file
# TO-DO: make the filename more robust so that if an existing file in savedir
#        with the same filename as the target file, it will add an indicator 
#        (e.g. (1), (2), and so on) before downloading the file.
def download_file(fileID, savedir):
    fileObj = gfs.get(ObjectId(fileID))
    filename = fileObj.filename 
    savepath = os.path.join(savedir, filename)
    with open(savepath, 'wb') as f:
        f.write(fileObj.read())
    print(f'Downloaded file with fileID [{fileID}], stored at [{savepath}].')
    return

# List all files in a room
def list_files(roomCode):
    files = gfs.find({'metadata.roomCode': roomCode})
    print(f'Files stored in room [{roomCode}]:')
    for file in files:
        print(f'[{file.filename}]')
    return

# Delete a file based on given fileID
# TO-DO: after deleting the file successfully, need to update the "filelist"
#        of the room the file was stored before. To update it, 
#        remove the filename, specified by the fileID, from "filelist".
def delete_file(fileID):
    file = gfs.find_one({"_id": ObjectId(fileID)})
    print(file)
    gfs.delete(ObjectId(fileID))
    print(f'Successfully deleted file with fileID: [{fileID}].')
    # Used to show any remaining files exist with that fileID
    # for file in gfs.find():
    #     print(file.filename, file._id)
    return

if __name__=='__main__':  
    roomCode = 'f9wa8rq9fqvg0qj'
    filepath = '/Users/jianminglin/test_files/Giraffe.jpg'
    fileID = '68181d869304c7898b995781'
    savedir = '/Users/jianminglin/recv_files'
    
    # upload_file(filepath, roomCode)
    # delete_file(fileID)
    # download_file(fileID, savedir)
    # list_files(roomCode)

    # TO-DO: 
    # 1. convert every appearance of roomCode with Object id
    # 2. work on TO-DOs (download_file, delete_file)
    # 3. work on client_list_operations
    # 4. make use of mongodb operations in the G2 project
    