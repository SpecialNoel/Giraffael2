# msg_ops_tester.py

from server_only.mongodb_related.msg_ops.add_op import add_msg_to_history
from server_only.mongodb_related.msg_ops.clear_op import clear_msg_history
from server_only.mongodb_related.msg_ops.list_op import list_msg_history

if __name__=='__main__':  
    room_code = 'f9wa8rq9fqvg0qj'
    room_id = '681e8b495302d5101936aed0'
    
    sender_id = 'abc123'
    sender_name = 'ARK'
    msg = 'Hello, world.'
    
    #add_msg_to_history(room_code, sender_id, sender_name, msg)
    #list_msg_history(room_code)
    #clear_msg_history(room_code)
    