# requirements.sh

# To run this script: ./v3src/utilities/requirements.sh 
# If run into permission denied: 
#  use command 'chmod u+x v3src/utilities/requirements.sh' to give execute permission to this file.

pip install fastapi          # for server front-end operations
pip install uvicorn          # for hosting server with given IP and port number
pip install websockets       # for client utilizing WebSocket
pip install python-multipart # for client-side prompt of uploading file
pip install redis>=4.6       # for redis pub/sub service
