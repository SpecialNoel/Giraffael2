# create_json.py

# .json: javascript object notation files

import json

data = {'name': 'Alice', 'age': 25, 'city': 'New York'}
with open('./test_files/example.json', 'w') as file:
    json.dump(data, file)

print('Created example.json')
