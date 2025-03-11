#Generate Temporary Gmail (google gmail accounts - .gmail.com), using the site emailnator.com
import requests
import json
import time
from typing import List, Dict, Any, Optional

# List of API keys to use with fallback mechanism
API_KEYS = [
    "e5af10b750msh631719d398fe970p1e98e9jsnb0fc2dfa6393",  # samratddypppis@gmail.com
    "bc7cb2c378mshf1f88c9c7e37d36p1c4039jsn6697d765a2bb",  # samrat1212study2@gmail.com
    "29bf2dc8b5msh5daf33e76ed405ap1e23e8jsnb6f7a4034e9e",   # sam1212factz@gmail.com
    "768dc06d1fmsheea28e657087c5ap112e78jsn3300b36bc217"   # sam1212yt1@gmail.com
]

def make_api_request(url: str, method: str = "post", payload: Optional[Dict[str, Any]] = None, 
                    params: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Dict[str, Any]:
    """
    Make an API request with automatic retry using multiple API keys.
    
    Args:
        url: The API endpoint URL
        method: HTTP method ("post" or "get")
        payload: JSON payload for POST requests
        params: Query parameters for GET requests
        max_retries: Maximum number of retries with different API keys
    
    Returns:
        API response as a dictionary
    
    Raises:
        Exception: If all API keys fail
    """
    errors = []
    
    # Try each API key until one works or we run out of keys
    for i, api_key in enumerate(API_KEYS):
        try:
            headers = {
                "x-rapidapi-key": api_key,
                "x-rapidapi-host": "gmailnator.p.rapidapi.com",
                "Content-Type": "application/json"
            }
            
            if method.lower() == "post":
                response = requests.post(url, json=payload, headers=headers)
            else:  # GET
                response = requests.get(url, headers=headers, params=params)
            
            response_data = response.json()
            
            # Check if the response indicates an API key quota error
            if isinstance(response_data, dict) and response_data.get("message") and "exceeded" in response_data.get("message", "").lower():
                error_msg = f"API key {i+1} quota exceeded: {response_data['message']}"
                print(error_msg)
                errors.append(error_msg)
                continue  # Try the next API key
            
            # If we got here, the request was successful
            print(f"Successfully used API key {i+1}")
            return response_data
            
        except Exception as e:
            error_msg = f"Error with API key {i+1}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)
    
    # If we've tried all API keys and all failed
    error_message = f"All API keys failed. Errors: {', '.join(errors)}"
    print(error_message)
    raise Exception(error_message)

def generate_gmail():
    """
    Generate a temporary Gmail address using the gmailnator API with fallback mechanism.
    
    Returns:
        A temporary Gmail address
    """
    url = "https://gmailnator.p.rapidapi.com/generate-email"
    payload = {"options": [3]}
    
    response_data = make_api_request(url=url, method="post", payload=payload)
    print(response_data)
    return response_data["email"]        
        
def get_inbox(email):
    """
    Get the inbox contents for a given email address using the gmailnator API with fallback mechanism.
    
    Args:
        email: The email address to check
        
    Returns:
        Inbox contents as a dictionary
    """
    url = "https://gmailnator.p.rapidapi.com/inbox"
    payload = {
        "email": f"{email}",
        "limit": 20
    }
    
    response_data = make_api_request(url=url, method="post", payload=payload)
    print(response_data)
    return response_data

def get_message(message_id):
    """
    Get a specific message by ID using the gmailnator API with fallback mechanism.
    
    Args:
        message_id: The ID of the message to retrieve
        
    Returns:
        Message content as a dictionary
    """
    url = "https://gmailnator.p.rapidapi.com/messageid"
    params = {"id": f"{message_id}"}
    
    response_data = make_api_request(url=url, method="get", params=params)
    print(response_data)
    return response_data


def get_email_accounts():
    """Read email list from gmails.txt."""
    try:
        with open("gmails.txt", "r") as file:
            emails = file.read().splitlines()
        return emails
    except Exception as e:
        print(f"Error reading email file: {e}")
        return []
