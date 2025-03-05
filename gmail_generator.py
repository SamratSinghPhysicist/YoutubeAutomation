#Generate Temporary Gmail (google gmail accounts - .gmail.com), using the site emailnator.com
import requests
import json


def generate_bulk_gmail():
    url = "https://gmailnator.p.rapidapi.com/bulk-emails"

    payload = {
    	"limit": 500,
    	"options": [3]
    }
    headers = {
    	"x-rapidapi-key": "29bf2dc8b5msh5daf33e76ed405ap1e23e8jsnb6f7a4034e9e",
    	"x-rapidapi-host": "gmailnator.p.rapidapi.com",
    	"Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    with open('emails.json', 'w') as f:
        json.dump(data, f, indent=2)

def get_inbox(email):
    url = "https://gmailnator.p.rapidapi.com/inbox"

    payload = {
    	"email": f"{email}",
    	"limit": 20
    }
    headers = {
    	"x-rapidapi-key": "29bf2dc8b5msh5daf33e76ed405ap1e23e8jsnb6f7a4034e9e",
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
    	"x-rapidapi-key": "29bf2dc8b5msh5daf33e76ed405ap1e23e8jsnb6f7a4034e9e",
    	"x-rapidapi-host": "gmailnator.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    print(response.json())
    return response.json()
