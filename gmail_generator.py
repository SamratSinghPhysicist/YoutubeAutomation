#Generate Temporary Gmail (google gmail accounts - .gmail.com), using the site emailnator.com
import requests
import json

"""
def generate_bulk_gmail():
    url = "https://gmailnator.p.rapidapi.com/bulk-emails"

    payload = {
    	"limit": 500,
    	"options": [3]
    }
    headers = {
    	"x-rapidapi-key": "e5af10b750msh631719d398fe970p1e98e9jsnb0fc2dfa6393",
    	"x-rapidapi-host": "gmailnator.p.rapidapi.com",
    	"Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    with open('emails.json', 'w') as f:
        json.dump(data, f, indent=2)
"""
def generate_gmail():

    url = "https://gmailnator.p.rapidapi.com/generate-email"

    payload = { "options": [3] }
    headers = {
    	"x-rapidapi-key": "bc7cb2c378mshf1f88c9c7e37d36p1c4039jsn6697d765a2bb",
    	"x-rapidapi-host": "gmailnator.p.rapidapi.com",
    	"Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.json())
    return response.json()["email"]        
        
def get_inbox(email):
    url = "https://gmailnator.p.rapidapi.com/inbox"

    payload = {
    	"email": f"{email}",
    	"limit": 20
    }
    headers = {
    	"x-rapidapi-key": "bc7cb2c378mshf1f88c9c7e37d36p1c4039jsn6697d765a2bb",
    	"x-rapidapi-host": "gmailnator.p.rapidapi.com",
    	"Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.json())
    return response.json()

def get_message(message_id):
    url = "https://gmailnator.p.rapidapi.com/messageid"

    querystring = {"id":f"{message_id}"}

    headers = {
    	"x-rapidapi-key": "bc7cb2c378mshf1f88c9c7e37d36p1c4039jsn6697d765a2bb",
    	"x-rapidapi-host": "gmailnator.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    print(response.json())
    return response.json()


def get_email_accounts():
    """Read email list from gmails.txt."""
    try:
        with open("gmails.txt", "r") as file:
            emails = file.read().splitlines()
        return emails
    except Exception as e:
        print(f"Error reading email file: {e}")
        return []
