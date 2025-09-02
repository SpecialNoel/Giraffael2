# service_switch.py

import json

async def handle_incoming_message(uuid: str, room_code: str, msg): 
    print(f'Received msg from client [{uuid}] in room [{room_code}]: ', msg)
    return
