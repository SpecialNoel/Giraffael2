# handle_msg_suggestion_request

import os
from openai import OpenAI
from dotenv import load_dotenv

from general.message import send_msg_with_prefix
from server_only.openai_model_settings import (maxTokensPerSuggestion, 
                                               numOfSuggestions, temp)
from server_only.retrieve_secret_from_aws import get_secret_api_key

'''
# Get API key with local server
load_dotenv() 
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
'''

# Get API key with remote server (aws ec2)
client = OpenAI(api_key=get_secret_api_key())

def handle_msg_suggestion_request(client, pastMsgList):
    # Obtain msg suggestions (a string) from OpenAI model
    response = get_msg_suggestion_from_model(pastMsgList)
    # Send the suggestions to client
    send_msg_with_prefix(client, response, 6)
    return

def get_msg_suggestion_from_model(pastMsgList):
    maxTokens = maxTokensPerSuggestion * numOfSuggestions
    msgs = [
            {
                'role': 'developer', 
                'content': 'You are a helpful assistant that ' + 
                           'provides helpful message suggestions to users.'
            },
            {
                'role': 'assistant',
                'content': f'Past messages sent over this room: {pastMsgList}.'
            },
            {
                'role': 'user',
                'content': 'Read the past messages sent over this room, and ' +
                          f'generate {numOfSuggestions} most suitable messages ' + 
                           'for the client to choose to send to the chatroom.' +
                          f'Answer in {maxTokens} tokens.'
            }
           ]
    return generate_msg_suggestion(msgs, maxTokens, temp, numOfSuggestions)

def generate_msg_suggestion(msgs, maxTokens, temp, numOfSuggestions):
    # Predicts and suggests the next possible client message.
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=msgs,
        max_tokens=maxTokens, # Limit the response length
        temperature=temp,     # Control randomness (0 = deterministic, 1 = creative)
        n=numOfSuggestions    # Generate n suggestions
    )
    return response.choices[0].message.content
