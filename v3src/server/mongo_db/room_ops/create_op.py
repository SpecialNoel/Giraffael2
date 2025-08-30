# create_op.py

import datetime
from v3src.server.mongo_db.mongodb_initiator import rooms_collection, user_statuses_collection

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
            
        # Room for presence default template
        room_data_for_online_status = {
            'roomCode': room_code,
            'userStatuses': [],
            'creationDate': current_time
        }
        
        # Add it to the user status collection
        user_statuses_collection.insert_one(room_data_for_online_status)
        
        # Add the 'room creator's status as well
        user_statuses_collection.update_one(
            {'roomCode': room_code},
            {
                '$push':{
                    'userStatuses': {
                        'uuid': uuid,
                        'last_activity_timestamp': current_time,
                        'is_online': True
                    }
                }
            }
        )
        print(f'Created user status list in room [{room_code}].')
        return True
    except: 
        print(f'Error in create_room_in_db() with room code [{room_code}].')
        return False

'''
# Update:
user_statuses_collection.update_one(
    {'roomCode': room_code,
     'userStatuses.uuid': uuid},
     {
         $set:{
             'userStatuses.$.is_online': False
         }
     }
)

# Query: 
user_statuses_collection.find_one(
    {'roomCode': room_code,
     'userStatuses.uuid': uuid},
    {
        "userStatuses.$": 1   # only return the matching element in the list
    }
     
)
'''
