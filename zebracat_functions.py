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


def get_verification_link_zebracat(message_content):
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
                        verification_link = get_verification_link_zebracat(message_content)
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


def account_maker_zebracat(email):
    print(f"\nProcessing account {email}")

    print(f"Trying to register the account: {email} on zebracat.ai")
    register_zebracat(email)
    print(f"Registration successful for the account: {email} on zebracat.ai")
    
    print(f"Trying to perform initial setup for the account: {email} on zebracat.ai")
    initial_setup_zebracat(email)
    print(f"Initial setup successful for the account: {email} on zebracat.ai")

    print(f"\nProcess completed for the account: {email}")
    print(f"Successfully Set Up the account: {email} on zebracat.ai")


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

def create_video_zebracat(email, video_title):

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
        
        print(f"Login successful with account {email} on zebracat.ai")


        print(f"Trying to create video with Email: {email} on zebracat.ai on the topic: {video_title}")

        # Step 2: Navigate to the Zebracat Website
        driver.get("https://studio.zebracat.ai/")

        # Step 3: Click on "Create Video" Button
        create_video_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Video')]"))
        )
        create_video_button.click()

        # Step 4: Wait for and Select "Hyperrealism"
        hyperrealism_div = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'sc-iA-DsXs') and contains(., 'Hyperrealism')]"))
        )
        hyperrealism_div.click()

        # Step 5: Wait 2 Seconds and Click "Next Step"
        time.sleep(2)
        next_step_button = driver.find_element(By.ID, ":r0:")
        next_step_button.click()

        # Step 6: Select "Fun Facts" from Dropdown
        time.sleep(1)
        story_style_combobox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'sc-JrDLc') and contains(., 'Select your story style')]"))
        )
        time.sleep(1)
        story_style_combobox.click()
        fun_facts_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-value='funfacts']"))
        )
        fun_facts_option.click()

        # Step 7: Enter Text into Textarea
        time.sleep(1)
        textarea = driver.find_element(By.XPATH, "//textarea[@placeholder='Example: motivational video encouraging a more healthy and active lifestyle.']")
        textarea.clear()
        textarea.send_keys(f"Create a youtube shorts on the topic: {video_title}. Make sure that first 5 seconds are very very engaging.")

        # Step 8: Click the Checkbox
        time.sleep(1)
        checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox']")
        checkbox.click()

        # Step 9: Select 9:16 Aspect Ratio
        time.sleep(1)
        aspect_ratio_div = driver.find_element(By.XPATH, "//div[contains(@class, 'sc-dOvA-dm') and contains(., '9:16')]")
        aspect_ratio_div.click()

        # Step 10: Click on the Slider Mark
        time.sleep(1)
        slider_mark = driver.find_element(By.XPATH, "//span[contains(@class, 'MuiSlider-mark') and contains(@style, 'left: 6.89655%')]")
        slider_mark.click()

        # Step 11: Click "Change" Button
        time.sleep(1)
        change_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Change')]")
        change_button.click()

        # Step 13: Select "Hindi" Language
        time.sleep(60)
        language_combobox = driver.find_element(By.XPATH, "//div[contains(@class, 'sc-JrDLc') and contains(., 'English')]")
        language_combobox.click()
        hindi_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-value='hindi']"))
        )
        hindi_option.click()

        # Step 14: Select "Male" Voice Gender
        time.sleep(5)
        voice_gender_combobox = driver.find_element(By.XPATH, "//div[contains(@class, 'sc-JrDLc') and contains(., 'All')]")
        voice_gender_combobox.click()
        male_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-value='male']"))
        )
        male_option.click()

        # Step 15: Select "Raju - Relatable Hindi Voice"
        time.sleep(10)
        voice_div = driver.find_element(By.XPATH, "//div[contains(@class, 'py6 main') and contains(., 'Raju - Relatable Hindi Voice')]")
        voice_div.click()

        # Step 16: Click "Select" Button
        time.sleep(5)
        select_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Select')]")
        select_button.click()

        # Change Video Mood to Energetic
        time.sleep(10)
        combobox = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='combobox' and contains(text(), 'Happy')]"))
        )
        combobox.click()
        time.sleep(5)
        energetic_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-value='Energetic']"))
        )
        energetic_option.click()

        # Step 17: Click "Next Step" After 1 Second
        time.sleep(5)

        next_step_button_2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next Step')]"))
        )
        next_step_button_2.click()

        # Step 18: Wait 20 Seconds and Click "Generate Video"
        time.sleep(20)
        generate_video_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate Video')]"))
        )
        generate_video_button.click()

        # Step 19: Check for Checkbox and Handle
        time.sleep(10)
        try:
            checkbox_2 = driver.find_element(By.XPATH, "//input[@type='checkbox' and @class='sc-dChVcU cwixky PrivateSwitchBase-input']")
            checkbox_2.click()
            generate_video_button.click()
        except:
            pass  # Checkbox not found, proceed without action

        # Step 20: Wait 10 minutes and Click "Export"
        time.sleep(600)
        export_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Export')]")
        export_button.click()

        # Step 21: Click "Prepare Video"
        prepare_video_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Prepare Video')]")
        prepare_video_button.click()

        # Step 22: Wait 10 Minutes for Video Processing
        time.sleep(600)

        # Step 23: Click "More" and Select "Download"
        more_icon = driver.find_element(By.XPATH, "//div[contains(@class, 'sc-fPgHrj')]")
        more_icon.click()
        download_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(., 'Download')]"))
        )
        download_option.click()

        # Step 24: Wait 15 Minutes for Download Preparation
        time.sleep(900)

        # Step 25: Close the Browser
        driver.quit()
    
    except Exception as e:
        print(f"Error creating video with account {email} on zebracat.ai on the topic {video_title}: {e}")
        return False
    finally:
        if driver:
            driver.quit()