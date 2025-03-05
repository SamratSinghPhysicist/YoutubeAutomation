import json
from gmail_generator import generate_gmail
from zebracat_functions import account_maker_zebracat, login_zebracat, create_video_zebracat
import time


def upload_to_youtube(video_file, title, description="Don't forget to like and subscribe", tags=None, privacyStatus="public"):
    """
    Uploads the given video file to YouTube.
    Requires a client_secrets.json file in your working directory.
    """
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request

        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        credentials = None

        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                credentials = pickle.load(token)
            print("Token loaded. Valid:", credentials.valid, "Expired:", credentials.expired)

        # If credentials are not valid, initiate the OAuth flow.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
                credentials = flow.run_local_server(port=0)
            # Save the credentials for future use.
            with open("token.pickle", "wb") as token:
                pickle.dump(credentials, token)
        
        youtube = build("youtube", "v3", credentials=credentials)
        
        # Provide additional metadata: description, tags, and categoryId.
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": "28"  # For example, "28" is often used for Science & Technology.
            },
            "status": {
                "privacyStatus": privacyStatus
            }
        }
        
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploading... {int(status.progress() * 100)}% complete")
        
        print("Upload Complete!")
        return response
    
    except Exception as e:
        print("An error occurred during upload:", e)
        return None



def main(video_title):

    accounts_data = {}

    #Seting up zebracat.ai and downloading the video.
    try:  
        email = generate_gmail()
        print(f"\nProcessing account: {email}")
        try:
            if account_maker_zebracat(email):
                time.sleep(5)
                if login_zebracat(email):
                    accounts_data[f"{email}"] = "Study@123"
                    with open("zebracat_accounts_data.json", "w") as json_file:
                        json.dump(accounts_data, json_file, indent=4)
                    print(f"Account {email} successfully set up and saved")
                else:
                    print(f"Login failed for account {email}")
            else:
                print(f"Account creation Failed on zebracat.ai for account {email}")
        except Exception as e:
            print(f"Error in account creation for {email} on zebracat.ai: {e}")
        
        try:
            create_video_zebracat(email, video_title=video_title)
        except Exception as e:
            print(f"Error in creating video for {email} on zebracat.ai: {e}")

    except Exception as e:
        print(f"Critical error in main process: {e}")
    finally:
        print("\nProcess completed")
        print(f"Successfully processed {len(accounts_data)} accounts")

    #Uploading the video to youtube.
    try:
        upload_to_youtube("downloaded_video.mp4", video_title)
    except Exception as e:
        print(f"Error in uploading video to youtube: {e}")

if __name__ == "__main__":
    video_title = "Space mei diamond rain!"
    main(video_title)
