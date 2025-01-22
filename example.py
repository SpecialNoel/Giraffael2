# example.py

from openai import OpenAI
client = OpenAI()

# Developer message example
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system", 
            "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Write a poem about recursion in programming."
        }
    ]
)
print(completion.choices[0].message.content)
print()

# User message example
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user", 
            "content": [
                {
                    "type": "text",
                    "text": "Write a poem about programming."
                }
            ]
        }
    ]
)
print(completion.choices[0].message.content)
