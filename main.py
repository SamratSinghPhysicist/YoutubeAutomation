import json
from gmail_generator import generate_gmail
from zebracat_functions import account_maker_zebracat, login_zebracat, create_video_zebracat
import time

def main():

    accounts_data = {}
    i = 0

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
            create_video_zebracat(email, video_title="Why do owl wake up at night?")
        except Exception as e:
            print(f"Error in creating video for {email} on zebracat.ai: {e}")

    except Exception as e:
        print(f"Critical error in main process: {e}")
    finally:
        print("\nProcess completed")
        print(f"Successfully processed {len(accounts_data)} accounts")

if __name__ == "__main__":
    main()
