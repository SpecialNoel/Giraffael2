# delete_op.py

from v3src.server.mongo_db.mongodb_initiator import rooms_collection

async def delete_client_from_redis(room_Code, uuid):
    try:
        
        return True
    except:
        return False
    
async def delete_client_permanently_from_db(room_code, uuid):
    
    return
