# check_op.py

from v3src.server.mongo_db.mongodb_initiator import rooms_collection

# Try match given room code, uuid and username with records in MongDB 
async def check_client_existence_in_db(room_code, uuid, username):
    client = rooms_collection.find_one(
        {
            'roomCode': room_code,
            'clientList': {
                '$elemMatch': {
                    'uuid': uuid,
                    'username': username
                }
            }
        },
        {'clientList.$': 1}
    )
    return True if client is not None else False
