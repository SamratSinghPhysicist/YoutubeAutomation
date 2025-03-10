#Generate Temporary Gmail (google gmail accounts - .gmail.com), using the site emailnator.com
import requests
import json

RAPID_API_KEYS = ["e5af10b750msh631719d398fe970p1e98e9jsnb0fc2dfa6393", "bc7cb2c378mshf1f88c9c7e37d36p1c4039jsn6697d765a2bb", "29bf2dc8b5msh5daf33e76ed405ap1e23e8jsnb6f7a4034e9e"]

def generate_gmail():

    url = "https://gmailnator.p.rapidapi.com/generate-email"

    payload = { "options": [3] }
    def header_api_setter(rapid_api_key):
        headers = {
        	"x-rapidapi-key": f"{rapid_api_key}",
        	"x-rapidapi-host": "gmailnator.p.rapidapi.com",
        	"Content-Type": "application/json"
        }

        return headers
    
    for i, rapid_api_key in enumerate(RAPID_API_KEYS):
        print(f"{i+1}th Rapid API key out of {len(RAPID_API_KEYS)} Keys is being used")
        response = requests.post(url, json=payload, headers=header_api_setter(RAPID_API_KEYS[i]))

        try:
            if response.json()["error"]:
                print(f"{i+1}th Rapid API key QUOTA LIMIT REACHED")
                print(response.json())
                print(f"Trying to use {i+2}th Rapid API key")
                continue
            else:
                print(response.json())
                return response.json()["email"]
                break
        except:
            print(response.json())
            return response.json()["email"]
    print(response.json())       
        
def get_inbox(email):
    url = "https://gmailnator.p.rapidapi.com/inbox"

    payload = {
    	"email": f"{email}",
    	"limit": 20
    }
    def header_api_setter(rapid_api_key):
        headers = {
        	"x-rapidapi-key": f"{rapid_api_key}",
        	"x-rapidapi-host": "gmailnator.p.rapidapi.com",
        	"Content-Type": "application/json"
        }

        return headers
    
    for i, rapid_api_key in enumerate(RAPID_API_KEYS):
        print(f"{i+1}th Rapid API key out of {len(RAPID_API_KEYS)} Keys is being used")
        response = requests.post(url, json=payload, headers=header_api_setter(RAPID_API_KEYS[i]))

        try:
            if response.json()["error"]:
                print(f"{i+1}th Rapid API key QUOTA LIMIT REACHED")
                print(response.json())
                print(f"Trying to use {i+2}th Rapid API key")
                continue
            else:
                print(response.json())
                return response.json()
                break
        except:
            print(response.json())
            return response.json()
    print(response.json())
    
def get_message(message_id):
    url = "https://gmailnator.p.rapidapi.com/messageid"

    querystring = {"id":f"{message_id}"}

    def header_api_setter(rapid_api_key):
        headers = {
        	"x-rapidapi-key": f"{rapid_api_key}",
        	"x-rapidapi-host": "gmailnator.p.rapidapi.com"
        }

        return headers
    
    for i, rapid_api_key in enumerate(RAPID_API_KEYS):
        print(f"{i+1}th Rapid API key out of {len(RAPID_API_KEYS)} Keys is being used")
        response = requests.post(url, headers=header_api_setter(RAPID_API_KEYS[i]), params=querystring)

        try:
            if response.json()["error"]:
                print(f"{i+1}th Rapid API key QUOTA LIMIT REACHED")
                print(response.json())
                print(f"Trying to use {i+2}th Rapid API key")
                continue
            else:
                print(response.json())
                return response.json()
                break
        except:
            print(response.json())
            return response.json()
    print(response.json())


    print(response.json())
    return response.json()