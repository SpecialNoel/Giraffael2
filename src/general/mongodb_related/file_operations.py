# file_operations.py

# Sorts of MongoDB operations used to list, upload, download or delete files in each room.

from pymongo import MongoClient
import gridfs
from bson import ObjectId

# Connect to MongoDB with the connection string for Giraffael2DB
uri = ('mongodb+srv://jianminglin2893:cbVSqJdDMIUnso6Q' + 
       '@ac-os3juge.wu2ivo7.mongodb.net/Giraffael2DB' + 
       '?retryWrites=true&w=majority&tls=true')
mongoClient = MongoClient(uri, serverSelectionTimeoutMS=3000)

db = mongoClient['Giraffael2DB'] 
rooms_collection = db['Rooms'] # the "Rooms" collection
gfs = gridfs.GridFS(db)


# List all files in a room
def list_files(roomCode):
    files = gfs.find({'metadata.roomCode': ObjectId(roomCode)})
    print(f'Files stored in room [{roomCode}]:')
    for file in files:
        print(f'[{file.filename}]')
    print()
    return

# Upload file
def upload_file(filepath, roomCode):
    nameOfFile=filepath.split('/')[-1]
    with open(filepath, 'rb') as f:
        fileID = gfs.put(
            f,
            filename=nameOfFile,
            metadata={'roomCode': ObjectId(roomCode)}
        )
    print(f'Uploaded file [{nameOfFile}] with fileID: [{fileID}].')
    return fileID

# Download file
def download_file(fileID, savepath):
    fileObj = gfs.get(ObjectId(fileID))
    with open(savepath, 'wb') as f:
        f.write(fileObj.read())
    print(f'Downloaded file with fileID [{fileID}], stored at [{savepath}].')
    return

def delete_file(filename):
    
    return
