# chat_app.py

# To run this script: python3 chat_app.py

from server_only.server_core.server import Server

class Chat_App:
    def __init__(self):
        server = Server()
        server.run_server()
     
if __name__=='__main__':  
    Chat_App()
