# check_op.py

from src.server.app.db.mongo.mongodb_initiator import rooms_collection
from src.server.app.db.mongo.msg_ops.general_op import room_code_exists_in_collection

# Check whether room with given room code exist in MongoDB
def check_room_existence_in_db(room_code):
    if not room_code_exists_in_collection(room_code):
        print(f'Room [{room_code}] does not exist in MongoDB.')
        return False
    print(f'Room [{room_code}] exists in MongoDB.')
    return True

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
    print(f'\nClient: [{client}]\n')
    return True if client is not None else False
