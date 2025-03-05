import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import urllib3
from webdriver_manager.chrome import ChromeDriverManager

from gmail_generator import get_inbox, get_message

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_driver():
    """Initialize Selenium WebDriver with Chrome options."""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('--disable-extensions')
    # Add realistic browser characteristics
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    # Remove automation flags
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # Execute CDP commands to modify browser characteristics
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        })
        driver.set_page_load_timeout(60)  # Increased timeout
        return driver
    except Exception as e:
        print(f"Driver creation error: {str(e)}")
        raise Exception(f"Failed to create driver: {str(e)}")


def get_verification_link(message_content):
    """Extract verification link from email content by finding the anchor tag with specific text."""
    try:
        # If message_content is a dict, extract the 'content' field
        if isinstance(message_content, dict) and 'content' in message_content:
            message_content = message_content['content']
        
        # Parse the HTML content
        soup = BeautifulSoup(message_content, 'html.parser')
        
        # Define a function to find the <a> tag containing "Confirm Email Address"
        def contains_verification_text(tag):
            return tag.name == 'a' and 'Confirm Email Address' in tag.text
        
        # Find the tag
        verification_tag = soup.find(contains_verification_text)
        
        # Check if the tag exists and has an href attribute
        if verification_tag and 'href' in verification_tag.attrs:
            return verification_tag['href']
        
        raise Exception("Verification link not found in email content")
    except Exception as e:
        print(f"Error parsing verification email: {str(e)}")
        raise Exception(f"Failed to extract verification link: {str(e)}")

def register_zebracat(email):
    """Register a new account on zebracat.ai."""
    driver = None
    try:
        driver = create_driver()
        print(f"Trying to register with Email: {email} on zebracat.ai")
        
        driver.get("https://studio.zebracat.ai/login/")

        email_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(email)

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
        ).click()

        fullname_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "fullname"))
        )
        fullname_input.send_keys("King Sam")

        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys("Study@123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(30)
        
        for _ in range(20):
            all_messages = get_inbox(email)
            try:
                for mail in all_messages:
                    print(mail)
                    if "hello@zebracat.ai" in str(mail["from"]):
                        message_id = mail["id"]
                        message_content = get_message(message_id)
                        verification_link = get_verification_link(message_content)
                        driver.get(verification_link)
                        time.sleep(10)
                        print("Registration successful")
                        time.sleep(10)
                        return True
            except Exception as e:
                print(f"Error getting verification message content: {str(e)}")
                print(f"Waiting for verification email:")
                time.sleep(30)
                all_messages = get_inbox(email)
        
        
    except Exception as e:
        print(f"Error during registration of account {email} on zebracat.ai: {e}")
        return False
    finally:
        if driver:
            driver.quit()

def initial_setup_zebracat(email):
    """Perform initial setup for a zebracat.ai account."""
    driver = None
    try:
        driver = create_driver()
        print(f"Trying to perform initial setup for Email: {email} on zebracat.ai")
        
        driver.get("https://studio.zebracat.ai/login/")
        
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(email)

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
        ).click()

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys("Study@123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(10)
        driver.get("https://studio.zebracat.ai/")

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'option') and contains(text(), 'Content Creator')]"))
        ).click()

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
        ).click()

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'option') and contains(text(), 'YouTube Shorts')]"))
        ).click()

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit')]"))
        ).click()

        time.sleep(10)
        print(f"Initial setup successful for account {email} on zebracat.ai")
        return True

    except Exception as e:
        print(f"Error during initial setup of account {email} on zebracat.ai: {e}")
        return False
    finally:
        if driver:
            driver.quit()

def login_zebracat(email):
    """Log in to a zebracat.ai account."""
    driver = None
    try:
        driver = create_driver()
        print(f"Trying to login with Email: {email} on zebracat.ai")
        
        driver.get("https://studio.zebracat.ai/login/")

        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(email)

        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
        ).click()

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys("Study@123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(10)
        driver.get("https://studio.zebracat.ai/")
        time.sleep(10)
        
        print("Login successful")
        return True

    except Exception as e:
        print(f"Error during login of account {email} on zebracat.ai: {e}")
        return False
    finally:
        if driver:
            driver.quit()

def get_email():
    """Read email list from gmails.txt."""
    try:
        with open("gmails.txt", "r") as file:
            emails = file.read().splitlines()
        return emails
    except Exception as e:
        print(f"Error reading email file: {e}")
        return []

def main():
    """Main function to automate account registration and setup."""
    email_list = get_email()

    if not email_list:
        print("No emails found. Please check input files.")
        return

    accounts_data = {}
    i = 0

    try:
        while i <= min(59, len(email_list)-1):
            email = email_list[i]
            print(f"\nProcessing account {i+1}/60")
            print(f"Email: {email}")

            try:
                if register_zebracat(email):
                    time.sleep(5)
                    if initial_setup_zebracat(email):
                        time.sleep(5)
                        if login_zebracat(email):
                            accounts_data[email] = "Study@123"
                            with open("accounts_data.json", "w") as json_file:
                                json.dump(accounts_data, json_file, indent=4)
                            print(f"Account {email} successfully set up and saved")
                        else:
                            print(f"Login failed for account {email}")
                    else:
                        print(f"Initial setup failed for account {email}")
                else:
                    print(f"Registration failed for account {email}")

            except Exception as e:
                print(f"Error processing account {email}: {e}")
                continue

            i += 1
            time.sleep(5)

    except Exception as e:
        print(f"Critical error in main process: {e}")
    finally:
        print("\nProcess completed")
        print(f"Successfully processed {len(accounts_data)} accounts")

if __name__ == "__main__":
    main()