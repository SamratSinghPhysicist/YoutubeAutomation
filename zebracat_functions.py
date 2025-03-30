from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from bs4 import BeautifulSoup
import urllib3
from webdriver_manager.chrome import ChromeDriverManager
from gmail_generator import get_inbox, get_message

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_driver(download_dir=None):
    """Initialize Selenium WebDriver with Chrome options.
    Optimized for both local and CI/CD environments (GitHub Actions).
    """
    chrome_options = Options()
    # chrome_options.add_argument('--headless')   # Headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Set download directory if provided
    if download_dir:
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })

    try:
        # Check if running in GitHub Actions
        is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
        
        if is_github_actions:
            # GitHub Actions specific setup
            print("Running in GitHub Actions environment")
            
            # Set up virtual display for headless browser in Linux environment
            try:
                from pyvirtualdisplay import Display
                display = Display(visible=0, size=(1920, 1080))
                display.start()
                print("Virtual display started for GitHub Actions")
            except Exception as display_error:
                print(f"Note: Virtual display setup failed, continuing anyway: {display_error}")
            
            # In GitHub Actions, Chrome is installed via workflow
            try:
                import chromedriver_autoinstaller
                chromedriver_autoinstaller.install()
                print("ChromeDriver auto-installed for GitHub Actions")
            except Exception as auto_install_error:
                print(f"ChromeDriver auto-install failed: {auto_install_error}")
            
            driver = webdriver.Chrome(options=chrome_options)
            print("Driver created for GitHub Actions")
        else:
            # Local environment setup with ChromeDriverManager
            try:
                print("Installing ChromeDriver...")
                driver_path = ChromeDriverManager().install()
                print(f"ChromeDriver installed at: {driver_path}")
                service = Service(driver_path)
                print("Service created")
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print("Driver created")
            except Exception as local_error:
                print(f"Error with ChromeDriverManager: {local_error}")
                # Fallback to system Chrome if available
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                    print("Driver created using system Chrome")
                except Exception as system_error:
                    print(f"Error with system Chrome: {system_error}")
                    raise Exception("Failed to create driver with both ChromeDriverManager and system Chrome")
        
        # Common setup for both environments
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        })
        driver.set_page_load_timeout(60)
        return driver

    except Exception as e:
        print(f"Driver creation error: {str(e)}")
        raise Exception(f"Failed to create driver: {str(e)}")

def get_verification_link_zebracat(message_content):
    """Extract verification link from email content by finding the anchor tag with specific text."""
    try:
        if isinstance(message_content, dict) and 'content' in message_content:
            message_content = message_content['content']
        
        soup = BeautifulSoup(message_content, 'html.parser')
        
        def contains_verification_text(tag):
            return tag.name == 'a' and 'Confirm Email Address' in tag.text
        
        verification_tag = soup.find(contains_verification_text)
        
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

        email_input = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(email)

        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
        ).click()

        fullname_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "fullname"))
        )
        fullname_input.send_keys("King Sam")

        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys("Study@123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(60)
        
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
                        time.sleep(7)
                        print("Registration successful")
                        return True
            except Exception as e:
                print(f"Error getting verification message content: {str(e)}")
                print(f"Waiting for verification email:")
                time.sleep(60)
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
        
        email_input = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(email)

        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
        ).click()

        password_input = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys("Study@123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(10)
        driver.get("https://studio.zebracat.ai/")

        time.sleep(10)
        print("Clicking on option 'Content Creator'")
        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'option') and contains(text(), 'Content Creator')]"))
        ).click()

        time.sleep(10)
        print("Clicking on 'Continue' Button")
        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
        ).click()

        time.sleep(10)
        print("Clicking on option 'Youtube Shorts'")
        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'option') and contains(text(), 'YouTube Shorts')]"))
        ).click()

        time.sleep(10)
        print("Clicking on 'Submit' Button")
        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit')]"))
        ).click()

        time.sleep(7)
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
    if register_zebracat(email):
        print(f"Registration successful for the account: {email} on zebracat.ai")
    
    print(f"Trying to perform initial setup for the account: {email} on zebracat.ai")
    if initial_setup_zebracat(email):
                              
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

        email_input = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(email)

        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
        ).click()

        password_input = WebDriverWait(driver, 120).until(
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

def rename_downloaded_file(download_dir, new_name="downloaded_video.mp4"):
    """Rename the most recently downloaded .mp4 file."""
    files = os.listdir(download_dir)
    video_files = [f for f in files if f.endswith(".mp4")]
    
    if not video_files:
        raise FileNotFoundError("No .mp4 file found in the download directory!")
    elif len(video_files) > 1:
        print("Warning: Multiple .mp4 files found. Renaming the latest one.")
        video_files.sort(key=lambda x: os.path.getmtime(os.path.join(download_dir, x)), reverse=True)
    
    original_file = video_files[0]
    original_path = os.path.join(download_dir, original_file)
    new_path = os.path.join(download_dir, new_name)
    
    if os.path.exists(new_path):
        os.remove(new_path)  # Remove existing file with the same name
    os.rename(original_path, new_path)
    print(f"Renamed '{original_file}' to '{new_name}'")
    return new_path

def create_video_zebracat(email, video_title):
    def sanitize_text(text):
        # Remove or replace problematic characters
        return ''.join(char for char in text if ord(char) < 65536)
    driver = None
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of this script
    try:
        # Create driver with custom download directory
        driver = create_driver(download_dir=script_dir)

        # Logging in on zebracat.ai
        print(f"Trying to login with Email: {email} on zebracat.ai")
        
        driver.get("https://studio.zebracat.ai/login/")

        email_input = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(email)

        WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
        ).click()

        password_input = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys("Study@123")

        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        time.sleep(10)
        driver.get("https://studio.zebracat.ai/")
        
        print(f"Login successful with account {email} on zebracat.ai")
        
        # Generate sample video first
        print("Starting the process to generate sample video...")
        
        # Try to click on Black Holes & Supernovas option with retry logic
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                print(f"Attempt {attempt+1}: Trying to click on 'Black Holes & Supernovas' option")
                black_holes_option = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//p[contains(@class, 'sc-iapWAC') and contains(text(), 'Black Holes & Supernovas')]"))
                )
                black_holes_option.click()
                print("Successfully clicked on 'Black Holes & Supernovas' option")
                break
            except Exception as e:
                print(f"Failed to find 'Black Holes & Supernovas' option: {e}")
                if attempt < max_attempts - 1:
                    print("Clicking on Shuffle button and trying again")
                    try:
                        # Fixed XPath for the Shuffle button
                        shuffle_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'normal-text') and contains(text(), 'Shuffle')]"))
                        )
                        shuffle_button.click()
                        print("Clicked on Shuffle button")
                        time.sleep(2)  # Wait for new options to load
                    except Exception as shuffle_error:
                        print(f"Failed to click on Shuffle button: {shuffle_error}")
                        # Try alternative XPath if the first one fails
                        try:
                            shuffle_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//div[text()='Shuffle']"))
                            )
                            shuffle_button.click()
                            print("Clicked on Shuffle button (alternative selector)")
                            time.sleep(2)
                        except Exception as alt_error:
                            print(f"Failed to click on Shuffle button with alternative selector: {alt_error}")
                else:
                    print("Maximum attempts reached. Could not find 'Black Holes & Supernovas' option")
                    raise Exception("Failed to find 'Black Holes & Supernovas' option after multiple attempts")
        
        # Click Next Step
        time.sleep(2)
        print("Clicking Next Step button")
        next_step_button = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.ID, ":r0:"))
        )
        next_step_button.click()
        
        # Click on AI Image
        time.sleep(2)
        print("Clicking on AI Image option")
        ai_image_option = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//p[contains(@class, 'sc-iapWAC') and contains(text(), 'AI Image')]"))
        )
        ai_image_option.click()
        
        # Click Next Step again
        time.sleep(2)
        print("Clicking Next Step button again")
        next_step_button2 = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.ID, ":r1:"))
        )
        next_step_button2.click()
        
        # Click Generate Video
        time.sleep(5)
        print("Clicking Generate Video button")
        generate_video_button = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.ID, ":r2:"))
        )
        generate_video_button.click()
        
        time.sleep(10)
        
        # Navigate back to studio page to create the actual video
        print("Navigating back to studio page to create the actual video")
        driver.get("https://studio.zebracat.ai/")
        time.sleep(10)
        
        # Now proceed with creating the actual video
        print(f"Trying to create actual video with Email: {email} on zebracat.ai on the topic: {video_title}")

        # Navigate to the Zebracat studio page
        driver.get("https://studio.zebracat.ai/")
        time.sleep(10)

        # Click on "Create Video" Button
        create_video_button = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create Video')]"))
        )
        create_video_button.click()

        print("Adding video settings ...")
        
        # Select Realistic style 
        time.sleep(2)
        print("Clicking Realistic option")
        realistic_option = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//p[contains(@class, 'sc-iapWAC') and text()='Realistic']"))
        )
        realistic_option.click()

        # Wait 2 Seconds and Click "Next Step"
        time.sleep(2)
        print("Clicking Next Step")
        next_step_button = driver.find_element(By.ID, ":r0:")
        next_step_button.click()

        # Select "Fantasy" from Dropdown
        time.sleep(1)
        print("Opening Story Style Dropdown")
        story_style_combobox = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'sc-JrDLc') and contains(., 'Select your story style')]"))
        )
        time.sleep(2)
        story_style_combobox.click()

        print("Clicking Fantasy Option")
        fun_facts_option = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-value='fantasy']"))
        )
        fun_facts_option.click()

        # Enter Text into Textarea
        time.sleep(2)
        print("Describing the video title in textarea")
        textarea = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Example: motivational video encouraging a more healthy and active lifestyle.']"))
        )
        textarea.clear()
        sanitized_prompt = sanitize_text(f"Create a youtube shorts on the topic: {video_title}. Make sure that first 5 seconds are very very engaging.")
        driver.execute_script("arguments[0].value = arguments[1]", textarea, sanitized_prompt)
        textarea.send_keys(" ")

        # Select 9:16 Aspect Ratio
        time.sleep(1)
        print("Selecting Aspect Ratio -> 9:16")
        aspect_ratio = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'title')]//p[contains(text(), '9:16')]"))
        )
        aspect_ratio.click()

        # Click Change button
        time.sleep(1)
        print("Clicking Change Button for changing voice")
        change_button = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Change')]"))
        )
        change_button.click()

        # Select "Hindi" Language
        print("Opening Lanuguage Dropdown")
        time.sleep(60)
        language_combobox = driver.find_element(By.XPATH, "//div[contains(@class, 'sc-JrDLc') and contains(., 'English')]")
        language_combobox.click()

        time.sleep(10)
        print("Selecting Hindi from dropdown")
        hindi_option = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-value='hindi']"))
        )
        hindi_option.click()

        # Select "Male" Voice Gender
        print("Selecting Male voice")
        time.sleep(5)
        voice_gender_combobox = driver.find_element(By.XPATH, "//div[contains(@class, 'sc-JrDLc') and contains(., 'All')]")
        voice_gender_combobox.click()
        male_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-value='male']"))
        )
        male_option.click()

        # Select "Madhur's" Voice
        print("Selecting Madhur's Voice")
        time.sleep(10)
        voice_option = WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'py6 main') and contains(text(), 'Madhur')]"))
        )
        voice_option.click()

        # Click "Select" Button
        time.sleep(5)
        print("Clicking Select button (for confirming voice changes)")
        select_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Select')]")
        select_button.click()

        # Change Video Mood to Energetic
        print("Opening dropdown to change video mood to energetic")
        time.sleep(10)
        combobox = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='combobox' and contains(text(), 'Serious')]"))
        )
        combobox.click()
        time.sleep(2)
        print("Changing video mood to Suspenseful")
        energetic_option = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-value='Suspenseful']"))
        )
        energetic_option.click()

        # Click "Next Step" After 3 Second
        print("Clicking Next Step button")
        time.sleep(3)
        next_step_button_2 = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next Step')]"))
        )
        next_step_button_2.click()

        # Wait 20 Seconds and Click "Generate Video"
        time.sleep(20)
        print("Clicking Generate Video Button after confirming script")
        generate_video_button = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate Video')]"))
        )
        generate_video_button.click()

        # Check for Checkbox and Handle
        time.sleep(30)
        try:
            time.sleep(1)
            print("Clicking the checkbox")
            checkbox_2 = driver.find_element(By.XPATH, "//input[@class='sc-fyVfxW bZrHmF PrivateSwitchBase-input']")
            checkbox_2.click()            

            generate_video_button.click()
            
        except:
            print("Couldn't find script's language verification checkbox")
            print("Continuing ...")
            pass  # Checkbox not found, proceed without action

        # Wait 5 minutes and Click "Export"
        print("Video Generation started ...")
        time.sleep(300)
        print("Video generation done. \n Trying to export and process the video for download ...")
        print("Clicking on export button")
        
        # Using a more specific selector for the export button with SVG
        export_button = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, '_primary-btn') and .//p[contains(text(), 'Export')]]"))
        )
        export_button.click()
        
        # Click "Prepare Video" with the updated selector
        print("Clicking on Prepare video button")
        prepare_video_button = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sc-cHqXqK') and contains(text(), 'Prepare Video')]"))
        )
        prepare_video_button.click()

        # Wait 5 Minutes for Video Processing
        print("Video exporting and processing in 720p started ...")
        time.sleep(300)

        print("Video processing Done")

        # Click "More" and Select "Download" with updated selectors
        print("Downloading the video ...")
        
        # Click "More" and Select "Download" with updated selectors
        print("Downloading the video ...")
        
        # Try multiple approaches to find the correct more-icon
        try:
            # First try to find the more-icon near the download section
            # Wait for any loading to complete
            time.sleep(5)
            
            # Try to find the more icon by its position in the document
            # Look for the more icon that appears after the video is processed
            more_icons = driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-gppfCo')]//svg[contains(@class, 'more-icon')]")
            
            if len(more_icons) > 0:
                print(f"Found {len(more_icons)} more-icons, clicking on the first one")
                more_icons[0].click()
            else:
                # Try alternative selector
                print("Trying alternative selector for more-icon")
                more_icon = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'sc-gppfCo')]"))
                )
                more_icon.click()
            
            # Wait 2 seconds and click on Download option
            time.sleep(2)
            print("Clicking on download option")
            download_option = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'sc-dcJsrY')]//span[contains(text(), 'Download')]"))
            )
            download_option.click()
            
        except Exception as e:
            print(f"Error with first approach: {e}")
            # Try a different approach - JavaScript click
            try:
                print("Trying JavaScript approach to click more-icon")
                more_icons = driver.find_elements(By.XPATH, "//div[contains(@class, 'sc-gppfCo')]")
                if more_icons:
                    driver.execute_script("arguments[0].click();", more_icons[0])
                    time.sleep(2)
                    
                    # Try to find and click download option
                    download_options = driver.find_elements(By.XPATH, "//span[contains(text(), 'Download')]")
                    if download_options:
                        driver.execute_script("arguments[0].click();", download_options[0])
                    else:
                        raise Exception("Download option not found after clicking more-icon")
                else:
                    raise Exception("No more-icons found with JavaScript approach")
            except Exception as js_error:
                print(f"Error with JavaScript approach: {js_error}")
                # Final fallback - try to use direct URL for download if possible
                print("Attempting to use direct download URL if available")
                # This would depend on the site structure

        # Wait 5 Minutes for Download Preparation
        time.sleep(300)
        
        # Rename the downloaded file
        video_path = rename_downloaded_file(script_dir)
        print(f"Video created and downloaded as: {video_path}")
        return True

    except Exception as e:
        print(f"Error creating video with account {email} on zebracat.ai on the topic {video_title}: {e}")
        return False
    finally:
        if driver:
            driver.quit()
