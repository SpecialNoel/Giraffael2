# requirements.sh

# To run this script: ./utilities/requirements.sh 
# Note: Have to cd to the src folder for this to work

pip install openai        # for generate_msg_suggestion.py
pip install python-dotenv # for OpenAI API key
pip install boto3         # for accessing AWS Secret Manager
pip install pycryptodome cryptography # for data encryption
pip install Crypto        # for data encryption
pip install pymongo       # for MongoDB
