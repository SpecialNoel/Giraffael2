# create_op.py

import datetime
from v3src.server.mongo_db.mongodb_initiator import rooms_collection

def create_room_in_db(room_code, uuid, username, roomName='NewRoom'):
    try: 
        current_time = datetime.datetime.now(tz=datetime.timezone.utc)
        
        # Room default template
        room_data = {
            'roomCode': room_code,
            'roomName': roomName,
            'clientList': [],
            'msgList': [],
            'fileList': [],
            'creationDate': current_time
        }
        
        # Add the 'room creator' to the room
        room_creator_data = {'uuid': uuid, 
                             'username': username}
        room_data['clientList'].append(room_creator_data)
        
        # Add room to the room collection
        rooms_collection.insert_one(room_data)
        print(f'Created room in DB with room code [{room_code}]. ')
        return True
    except: 
        print(f'Error in create_room_in_db() with room code [{room_code}].')
        return False
