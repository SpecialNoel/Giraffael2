# requirements.sh

# To run this script: ./utilities/requirements.sh 
# Note: Have to cd to the src folder for this to work

pip install openpyxl   # for create_excel.py
pip install pillow     # for create_img.py
pip install reportlab  # for create_pdf.py
pip install openai     # for generate_msg_suggestion.py
pip install python-dotenv # for OpenAI API key
pip install boto3      # for accessing AWS Secret Manager
pip install pycryptodome cryptography # for E2EE
pip install Crypto     # for E2EE
pip install pymongo    # for MongoDB
