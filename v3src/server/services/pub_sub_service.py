# pub_sub_service.py

from datetime import datetime, timezone
from v3src.server.schemas.definitions import Message

# Redis subscribes to the channel (NOT client subscribe to channel)
async def subscribe_to_channel(redis, active, room_code):
    async def broadcast(room_code, msg_obj: Message):
        clients = active.get(room_code, {})
        for uuid, info in clients.items():
            try:
                await info['websocket'].send_json(msg_obj.model_dump())
                print(f'Sent json message to client [{uuid}].')
            except Exception as e:
                print(f'Failed to send json message to client [{uuid}]. Reason: {e}.')
    
    # Subscribe to channel
    pubsub = redis.pubsub()
    await pubsub.subscribe(f'room_code:{room_code}:channel')
    
    # Note: 'async for' runs indefinitely as a background task.
    async for msg in pubsub.listen():
        # Handle msg (with type of dict, defaulted by pubsub.listen() returns)
        if msg['type'] == 'message':
            msg_obj = Message.model_validate_json(msg['data'].decode())
            await broadcast(room_code, msg_obj)
    return

# Publish Message to channel
async def publish_to_channel(redis, room_code, msg: Message):
    await redis.publish(f'room_code:{room_code}:channel', msg.model_dump_json())
    return     

# Publish chat message to channel
async def publish_chat_msg_to_channel(room_code, uuid, chat_msg):
    msg = Message(
        type='chat',
        room_code=room_code,
        sender=uuid,
        payload={'data': chat_msg},
        timestamp=datetime.now(tz=timezone.utc)
    )
    await publish_to_channel(room_code, msg)
    return
