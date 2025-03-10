import json
from gmail_generator import generate_gmail
from zebracat_functions import account_maker_zebracat, login_zebracat, create_video_zebracat
import time
import os
import pickle
from title_generator import main_title_generator

import os
import pickle
import datetime
import pytz
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload


def upload_to_youtube(video_file, title, description="Don't forget to like and subscribe", tags=None):
    """
    Uploads the given video file to YouTube and schedules it for the next day at 2:00 PM IST
    after the last uploaded or scheduled video on the channel.
    Requires a client_secrets.json file in your working directory.
    """
    try:
        # Define OAuth scope for YouTube API
        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        credentials = None

        # Load existing credentials if available
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                credentials = pickle.load(token)
            print("Token loaded. Valid:", credentials.valid, "Expired:", credentials.expired)

        # Refresh or obtain new credentials if necessary
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
                credentials = flow.run_local_server(port=0)
            # Save credentials for future use
            with open("token.pickle", "wb") as token:
                pickle.dump(credentials, token)
        
        # Build the YouTube API client
        youtube = build("youtube", "v3", credentials=credentials)
        
        # Define IST timezone (UTC+5:30)
        ist = pytz.timezone('Asia/Kolkata')

        # Step 1: Get the uploads playlist ID for the authenticated user's channel
        channels_response = youtube.channels().list(part="contentDetails", mine=True).execute()
        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Step 2: Fetch all video IDs from the uploads playlist with pagination
        video_ids = []
        page_token = None
        while True:
            playlist_items_response = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=page_token
            ).execute()
            for item in playlist_items_response['items']:
                video_ids.append(item['snippet']['resourceId']['videoId'])
            page_token = playlist_items_response.get('nextPageToken')
            if not page_token:
                break

        # Step 3: Fetch video details in batches (max 50 IDs per request)
        all_videos = []
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i + 50]
            videos_response = youtube.videos().list(
                part="snippet,status",
                id=','.join(chunk)
            ).execute()
            all_videos.extend(videos_response['items'])

        # Step 4: Extract publish dates in IST
        publish_dates_ist = []
        for video in all_videos:
            if video['status']['privacyStatus'] == "public" and 'publishedAt' in video['snippet']:
                # Public video: use snippet.publishedAt
                publish_time_utc = datetime.datetime.fromisoformat(video['snippet']['publishedAt'].replace('Z', '+00:00'))
                publish_time_ist = publish_time_utc.astimezone(ist)
                publish_dates_ist.append(publish_time_ist.date())
            elif 'publishAt' in video['status']:
                # Scheduled video: use status.publishAt
                publish_time_utc = datetime.datetime.fromisoformat(video['status']['publishAt'].replace('Z', '+00:00'))
                publish_time_ist = publish_time_utc.astimezone(ist)
                publish_dates_ist.append(publish_time_ist.date())

        # Step 5: Determine the next publish date
        if not publish_dates_ist:
            # If no videos exist, schedule for tomorrow
            today_ist = datetime.datetime.now(ist).date()
            next_date_ist = today_ist + datetime.timedelta(days=1)
        else:
            # Otherwise, use the day after the latest publish date
            latest_date_ist = max(publish_dates_ist)
            next_date_ist = latest_date_ist + datetime.timedelta(days=1)
        
        # Set the schedule time to 2:00 PM IST on the next day
        desired_time_ist = datetime.datetime.combine(next_date_ist, datetime.time(14, 0), tzinfo=ist)
        desired_time_utc = desired_time_ist.astimezone(pytz.utc)
        publish_at = desired_time_utc.isoformat().replace('+00:00', 'Z')

        # Step 6: Define video metadata
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": "28"  # Science & Technology
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_at
            }
        }
        
        # Step 7: Prepare and upload the video
        media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        # Upload with progress feedback
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploading... {int(status.progress() * 100)}% complete")
        
        print("Upload Complete!")
        return response
    
    except HttpError as e:
        print(f"An HTTP error occurred during upload: {e}")
        print(f"Video upload failed. Local video file ({video_file}) retained.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during upload: {e}")
        print(f"Video upload failed. Local video file ({video_file}) retained.")
        return None


def main():
    # Check if running in GitHub Actions environment
    is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
    if is_github_actions:
        print("Running in GitHub Actions environment")

    video_title = main_title_generator()
    print(f"Generated video title: {video_title}")
    
    accounts_data = {}

    # Setting up zebracat.ai and downloading the video.
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
            create_video_zebracat(email, video_title)
        except Exception as e:
            print(f"Error in creating video for {email} on zebracat.ai: {e}")

    except Exception as e:
        print(f"Critical error in main process: {e}")
    finally:
        print("\nProcess completed")
        print(f"Successfully processed {len(accounts_data)} accounts")
    
        
    # Uploading the video to YouTube
    print("Uploading video to YouTube...")
    response = upload_to_youtube(video_file = "downloaded_video.mp4", title= video_title)
    if response:
        print("Video uploaded successfully!")
        print("Response snippet:", response.get("snippet", {}))
        print("Deleting the local video files")
        try:
            os.remove("downloaded_video.mp4")
            print("Local video file (downloaded_video.mp4) deleted.")
        except Exception as e:
            print("Failed to delete local video file (downloaded_video.mp4):", e)
    else:
        print("Video upload failed. Local video file (downloaded_video.mp4) retained.")
        # In GitHub Actions, we want to make sure the workflow fails if upload fails
        if is_github_actions:
            print("GitHub Actions detected - marking workflow as failed due to upload failure")
            import sys
            sys.exit(1)

if __name__ == "__main__":
    main()
