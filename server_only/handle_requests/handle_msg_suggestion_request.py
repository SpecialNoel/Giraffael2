# handle_msg_suggestion_request

import os
from openai import OpenAI
from dotenv import load_dotenv

from general.message import send_msg_with_prefix
from server_only.others.openai_model_settings import (max_tokens_per_suggestion, 
                                                      num_of_suggestions, temp)
from server_only.others.retrieve_secret_from_aws import get_api_key
from server_only.others.settings import server_is_local

if server_is_local:
    # Get API key with local server
    load_dotenv() 
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
else:
    # Get API key with remote server (aws ec2)
    client = OpenAI(api_key=get_api_key())

def handle_msg_suggestion_request(client, past_msg_list, using_open_ai):
    if using_open_ai:
        # Obtain msg suggestions (a string) from OpenAI model
        response = get_msg_suggestion_from_model(past_msg_list)
        send_msg_with_prefix(client, response, 6)
        # Send the suggestions to client
    else:
        response = 'Open AI is not enabled by server.'
        send_msg_with_prefix(client, response, 1)
    return

def get_msg_suggestion_from_model(past_msg_list):
    max_tokens = max_tokens_per_suggestion * num_of_suggestions
    msgs = [
            {
                'role': 'developer', 
                'content': 'You are a helpful assistant that ' + 
                           'provides helpful message suggestions to users.'
            },
            {
                'role': 'assistant',
                'content': f'Past messages sent over this room: {past_msg_list}.'
            },
            {
                'role': 'user',
                'content': 'Read the past messages sent over this room, and ' +
                          f'generate {num_of_suggestions} most suitable messages ' + 
                           'for the client to choose to send to the chatroom.' +
                          f'Answer in {max_tokens} tokens.'
            }
           ]
    return generate_msg_suggestion(msgs, max_tokens, temp, num_of_suggestions)

def generate_msg_suggestion(msgs, max_tokens, temp, num_of_suggestions):
    # Predicts and suggests the next possible client message.
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=msgs,
        max_tokens=max_tokens, # Limit the response length
        temperature=temp,     # Control randomness (0 = deterministic, 1 = creative)
        n=num_of_suggestions    # Generate n suggestions
    )
    return response.choices[0].message.content
