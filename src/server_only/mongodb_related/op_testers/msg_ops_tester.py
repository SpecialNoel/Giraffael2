# msg_ops_tester.py

from src.server_only.mongodb_related.msg_ops.add_op import add_msg_to_history
from src.server_only.mongodb_related.msg_ops.clear_op import clear_msg_history
from src.server_only.mongodb_related.msg_ops.list_op import list_msg_history

if __name__=='__main__':  
    roomCode = 'f9wa8rq9fqvg0qj'
    roomID = '681e8b495302d5101936aed0'
    
    senderID = 'abc123'
    senderName = 'ARK'
    msg = 'Hello, world.'
    
    #add_msg_to_history(roomCode, senderID, senderName, msg)
    #list_msg_history(roomCode)
    #clear_msg_history(roomCode)
    