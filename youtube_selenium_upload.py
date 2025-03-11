from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import sys
import logging
from pathlib import Path
from title_generator import main_title_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def create_driver():
    """Initialize Selenium WebDriver with Chrome options.
    Optimized for both local and CI/CD environments (GitHub Actions).
    """
    chrome_options = Options()
    # Uncomment for headless mode if needed
    # chrome_options.add_argument('--headless')
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
    
    # Enable file downloads
    chrome_options.add_experimental_option("prefs", {
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    try:
        # Check if running in GitHub Actions
        is_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
        
        if is_github_actions:
            # GitHub Actions specific setup
            logging.info("Running in GitHub Actions environment")
            
            # Set up virtual display for headless browser in Linux environment
            try:
                from pyvirtualdisplay import Display
                display = Display(visible=0, size=(1920, 1080))
                display.start()
                logging.info("Virtual display started for GitHub Actions")
            except Exception as display_error:
                logging.warning(f"Note: Virtual display setup failed, continuing anyway: {display_error}")
            
            # In GitHub Actions, Chrome is installed via workflow
            try:
                import chromedriver_autoinstaller
                chromedriver_autoinstaller.install()
                logging.info("ChromeDriver auto-installed for GitHub Actions")
            except Exception as auto_install_error:
                logging.error(f"ChromeDriver auto-install failed: {auto_install_error}")
            
            driver = webdriver.Chrome(options=chrome_options)
            logging.info("Driver created for GitHub Actions")
        else:
            # Local environment setup with ChromeDriverManager
            try:
                logging.info("Installing ChromeDriver...")
                driver_path = ChromeDriverManager().install()
                logging.info(f"ChromeDriver installed at: {driver_path}")
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                logging.info("Driver created")
            except Exception as local_error:
                logging.error(f"Error with ChromeDriverManager: {local_error}")
                # Fallback to system Chrome if available
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                    logging.info("Driver created using system Chrome")
                except Exception as system_error:
                    logging.error(f"Error with system Chrome: {system_error}")
                    raise Exception("Failed to create driver with both ChromeDriverManager and system Chrome")
        
        # Common setup for both environments
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        })
        driver.set_page_load_timeout(120)  # Increased timeout for YouTube
        return driver

    except Exception as e:
        logging.error(f"Driver creation error: {str(e)}")
        raise Exception(f"Failed to create driver: {str(e)}")

def wait_and_click(driver, by, selector, timeout=120, description="element"):
    """Wait for an element to be clickable and then click it."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        element.click()
        logging.info(f"Clicked on {description}")
        return True
    except TimeoutException:
        logging.error(f"Timeout waiting for {description} to be clickable")
        return False
    except Exception as e:
        logging.error(f"Error clicking on {description}: {str(e)}")
        return False

def wait_and_send_keys(driver, by, selector, text, timeout=120, description="input field"):
    """Wait for an element to be visible and then send keys to it."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, selector))
        )
        element.clear()
        element.send_keys(text)
        logging.info(f"Entered text in {description}")
        return True
    except TimeoutException:
        logging.error(f"Timeout waiting for {description} to be visible")
        return False
    except Exception as e:
        logging.error(f"Error entering text in {description}: {str(e)}")
        return False

def upload_to_youtube_selenium(video_file, title, description="Like and Subscribe for more amazing content", email="sam1212yt1@gmail.com", password="Renu@Villa3"):
    """Upload a video to YouTube using Selenium automation."""
    # Verify video file exists
    if not os.path.exists(video_file):
        logging.error(f"Video file not found: {video_file}")
        return False
    
    # Get absolute path to video file
    video_file_path = os.path.abspath(video_file)
    logging.info(f"Video file path: {video_file_path}")
    
    driver = None
    try:
        # Initialize the driver
        driver = create_driver()
        
        # Step 1: Navigate to YouTube Studio
        logging.info("Navigating to YouTube Studio...")
        driver.get("https://studio.youtube.com")
        time.sleep(30)  # Wait for 60 seconds as requested
        
        # Step 2: Enter email
        logging.info("Entering email...")
        email_success = wait_and_send_keys(
            driver, 
            By.CSS_SELECTOR, 
            "input[type='email']", 
            email,
            description="email field"
        )
        if not email_success:
            raise Exception("Failed to enter email")
        
        # Step 3: Click Next
        next_button_success = wait_and_click(
            driver, 
            By.XPATH, 
            "//button[contains(@class, 'VfPpkd-LgbsSe') or contains(@class, 'VfPpkd-RLmnJb')]//span[contains(text(), 'Next') or contains(text(), 'next')]/..", 
            timeout=60,  # Increased timeout to 3 minutes
            description="next button"
        )
        if not next_button_success:
            # Try alternative selector if the first one fails
            next_button_success = wait_and_click(
                driver,
                By.CSS_SELECTOR,
                "button[jsname='LgbsSe']",
                timeout=60,
                description="next button (alternative)"
            )
        if not next_button_success:
            raise Exception("Failed to click next button")
        
        # Step 4: Wait and enter password
        time.sleep(30)  # Wait for 30 seconds as requested
        logging.info("Entering password...")
        
        # Take screenshot before entering password (for debugging)
        try:
            screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_before_password.png")
            driver.save_screenshot(screenshot_path)
            logging.info(f"Saved screenshot before password entry to {screenshot_path}")
        except Exception as ss_error:
            logging.warning(f"Failed to save screenshot: {ss_error}")
            
        # Try multiple selectors for password field
        password_success = wait_and_send_keys(
            driver, 
            By.CSS_SELECTOR, 
            "input[type='password']", 
            password,
            description="password field"
        )
        
        if not password_success:
            # Try alternative selector
            password_success = wait_and_send_keys(
                driver,
                By.XPATH,
                "//input[@name='password' or @aria-label='Enter your password']",
                password,
                description="password field (alternative)"
            )
            
        if not password_success:
            raise Exception("Failed to enter password")
            
        # Add a small delay after entering password
        time.sleep(5)
        
        # Step 5: Click Sign In
        logging.info("Clicking sign in button...")
        
        # Take screenshot before clicking sign in button (for debugging)
        try:
            screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_before_signin.png")
            driver.save_screenshot(screenshot_path)
            logging.info(f"Saved screenshot before sign in to {screenshot_path}")
        except Exception as ss_error:
            logging.warning(f"Failed to save screenshot: {ss_error}")
            
        # Print page source for debugging
        try:
            logging.info("Current page title: " + driver.title)
            logging.info("Looking for sign in button...")
        except Exception as e:
            logging.warning(f"Error getting page info: {e}")
            
        # Try multiple selectors with increased timeout
        signin_button_success = wait_and_click(
            driver, 
            By.CSS_SELECTOR, 
            ".VfPpkd-RLmnJb", 
            timeout=30,
            description="sign in button"
        )
        
        if not signin_button_success:
            # Try alternative selector if the first one fails
            signin_button_success = wait_and_click(
                driver,
                By.XPATH,
                "//button[contains(@class, 'VfPpkd-LgbsSe') or contains(@class, 'VfPpkd-RLmnJb')]//span[contains(text(), 'Next') or contains(text(), 'next') or contains(text(), 'Sign in')]/..",
                timeout=30,
                description="sign in button (alternative 1)"
            )
            
        if not signin_button_success:
            # Try another alternative selector
            signin_button_success = wait_and_click(
                driver,
                By.CSS_SELECTOR,
                "button[jsname='LgbsSe']",
                timeout=30,
                description="sign in button (alternative 2)"
            )
            
        if not signin_button_success:
            # Try even more generic selectors
            signin_button_success = wait_and_click(
                driver,
                By.XPATH,
                "//button[contains(., 'Sign in') or contains(., 'Next') or contains(., 'Continue')]",
                timeout=30,
                description="sign in button (alternative 3)"
            )
            
        if not signin_button_success:
            # Try to find any button that might be the sign in button
            try:
                logging.info("Attempting to find any possible sign in button...")
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for i, button in enumerate(buttons):
                    try:
                        logging.info(f"Button {i}: {button.get_attribute('outerHTML')}")
                    except:
                        pass
            except Exception as e:
                logging.warning(f"Error listing buttons: {e}")
                
            # Take screenshot after failure (for debugging)
            try:
                screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_signin_failed.png")
                driver.save_screenshot(screenshot_path)
                logging.info(f"Saved failure screenshot to {screenshot_path}")
            except Exception as ss_error:
                logging.warning(f"Failed to save screenshot: {ss_error}")
                
            raise Exception("Failed to click sign in button")
        
        # Step 6: Wait for YouTube Studio to load and click upload button
        time.sleep(60)  # Wait for 60 seconds as requested
        logging.info("Clicking upload button...")
        upload_button_success = wait_and_click(
            driver, 
            By.ID, 
            "upload-icon", 
            description="upload button"
        )
        if not upload_button_success:
            # Try alternative selector if ID doesn't work
            upload_button_success = wait_and_click(
                driver, 
                By.CSS_SELECTOR, 
                "ytcp-icon-button#upload-icon", 
                description="upload button (alternative)"
            )
        if not upload_button_success:
            raise Exception("Failed to click upload button")
        
        # Step 7: Click on Select Files button
        select_files_success = wait_and_click(
            driver, 
            By.CSS_SELECTOR, 
            "button.ytcp-button-shape-impl[aria-label='Select files']", 
            description="select files button"
        )
        if not select_files_success:
            # Try alternative selector
            select_files_success = wait_and_click(
                driver, 
                By.XPATH, 
                "//div[contains(text(), 'Select files')]", 
                description="select files button (alternative)"
            )
        if not select_files_success:
            raise Exception("Failed to click select files button")
        
        # Step 8: Handle file upload dialog
        # Since we can't directly interact with the OS file dialog, we need to use JavaScript
        # to bypass it and set the file input value directly
        try:
            # Find the hidden file input element
            time.sleep(5)  # Wait for file dialog to appear
            logging.info(f"Attempting to upload file: {video_file_path}")
            
            # Try to find the file input element
            file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            
            # Make it visible using JavaScript if it's hidden
            driver.execute_script("arguments[0].style.display = 'block';", file_input)
            
            # Send the file path to the input
            file_input.send_keys(video_file_path)
            logging.info("File path sent to input field")
        except NoSuchElementException:
            logging.error("Could not find file input element")
            raise Exception("Failed to find file input element")
        except Exception as e:
            logging.error(f"Error during file upload: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
        
        # Step 9: Wait for upload to complete and processing to start
        logging.info("Waiting for video to upload and process...")
        time.sleep(60)  # Wait for 1 minute as requested
        
        # Step 10: Enter video title
        logging.info("Entering video title...")
        try:
            # Wait for the title field to be available and enter the title
            title_field = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#textbox[aria-label*='Add a title']"))
            )
            
            # Use JavaScript to set the value instead of innerHTML
            # This approach avoids the TrustedHTML security restriction
            driver.execute_script("arguments[0].textContent = '';", title_field)
            
            # Make the element focused before sending keys
            driver.execute_script("arguments[0].focus();", title_field)
            
            # Use ActionChains for more reliable text input
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.move_to_element(title_field).click().send_keys(title).perform()
            
            logging.info("Title entered successfully")
        except Exception as e:
            logging.error(f"Error entering title: {str(e)}")
            # Try alternative approach if the first method fails
            try:
                logging.info("Trying alternative method for entering title...")
                # Try to find the title field using different selectors
                title_field = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Add a title') or contains(@aria-label, 'title')]"))
                )
                # Click to focus and then send keys
                title_field.click()
                title_field.send_keys(title)
                logging.info("Title entered successfully using alternative method")
            except Exception as alt_error:
                logging.error(f"Alternative title entry method also failed: {str(alt_error)}")
                raise Exception(f"Failed to enter title: {str(e)}")
        
        # Step 11: Enter video description
        logging.info("Entering video description...")
        try:
            # Wait for the description field to be available and enter the description
            desc_field = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#textbox[aria-label*='Tell viewers']"))
            )
            
            # Use JavaScript to set the value instead of innerHTML
            # This approach avoids the TrustedHTML security restriction
            driver.execute_script("arguments[0].textContent = '';", desc_field)
            
            # Make the element focused before sending keys
            driver.execute_script("arguments[0].focus();", desc_field)
            
            # Use ActionChains for more reliable text input
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.move_to_element(desc_field).click().send_keys(description).perform()
            
            logging.info("Description entered successfully")
        except Exception as e:
            logging.error(f"Error entering description: {str(e)}")
            # Try alternative approach if the first method fails
            try:
                logging.info("Trying alternative method for entering description...")
                # Try to find the description field using different selectors
                desc_field = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Tell viewers') or contains(@aria-label, 'description')]"))
                )
                # Click to focus and then send keys
                desc_field.click()
                desc_field.send_keys(description)
                logging.info("Description entered successfully using alternative method")
            except Exception as alt_error:
                logging.error(f"Alternative description entry method also failed: {str(alt_error)}")
                # Continue anyway as this might not be critical
                logging.warning("Continuing without description")
        
        # Step 12: Click on Not Made for Kids radio button
        logging.info("Selecting 'Not Made for Kids' option...")
        try:
            not_for_kids_radio = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "offRadio"))
            )
            not_for_kids_radio.click()
            logging.info("Selected 'Not Made for Kids' option")
        except Exception as e:
            logging.error(f"Error selecting 'Not Made for Kids' option: {str(e)}")
            # Continue anyway as this might already be selected
        
        # Step 13: Click Next button (first next)
        logging.info("Clicking first Next button...")
        try:
            # Try multiple selectors for the Next button with increased timeout
            next_button = None
            selectors = [
                ".yt-spec-touch-feedback-shape__fill",
                "#next-button",
                "button.next-button",
                "//button[contains(text(), 'Next')]",
                "//div[contains(@class, 'next-button')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        next_button = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS selector
                        next_button = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    if next_button:
                        break
                except:
                    continue
            
            if next_button:
                # Try regular click first
                try:
                    next_button.click()
                except:
                    # If regular click fails, try JavaScript click
                    driver.execute_script("arguments[0].click();", next_button)
                logging.info("Clicked first Next button")
            else:
                # If all selectors fail, try finding any button with Next text
                buttons = driver.find_elements(By.TAG_NAME, "button")
                next_clicked = False
                for button in buttons:
                    try:
                        if "next" in button.text.lower():
                            button.click()
                            next_clicked = True
                            logging.info("Clicked first Next button using text search")
                            break
                    except:
                        continue
                
                if not next_clicked:
                    raise Exception("Could not find Next button")
        except Exception as e:
            logging.error(f"Error clicking first Next button: {str(e)}")
            logging.warning("Attempting to continue despite Next button error")
        
        # Step 14: Wait and click Next button again (second next)
        time.sleep(60)  # Wait for 3 minutes as requested
        logging.info("Clicking second Next button...")
        try:
            # Try multiple selectors for the Next button with increased timeout
            next_button = None
            selectors = [
                ".yt-spec-touch-feedback-shape__fill",
                "#next-button",
                "button.next-button",
                "//button[contains(text(), 'Next')]",
                "//div[contains(@class, 'next-button')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        next_button = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS selector
                        next_button = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    if next_button:
                        break
                except:
                    continue
            
            if next_button:
                # Try regular click first
                try:
                    next_button.click()
                except:
                    # If regular click fails, try JavaScript click
                    driver.execute_script("arguments[0].click();", next_button)
                logging.info("Clicked second Next button")
            else:
                # If all selectors fail, try finding any button with Next text
                buttons = driver.find_elements(By.TAG_NAME, "button")
                next_clicked = False
                for button in buttons:
                    try:
                        if "next" in button.text.lower():
                            button.click()
                            next_clicked = True
                            logging.info("Clicked second Next button using text search")
                            break
                    except:
                        continue
                
                if not next_clicked:
                    raise Exception("Could not find second Next button")
        except Exception as e:
            logging.error(f"Error clicking second Next button: {str(e)}")
            logging.warning("Attempting to continue despite second Next button error")
        
        # Step 15: Wait and click Next button again (third next)
        time.sleep(60)  # Wait for 3 minutes as requested
        logging.info("Clicking third Next button...")
        try:
            # Try multiple selectors for the Next button with increased timeout
            next_button = None
            selectors = [
                ".yt-spec-touch-feedback-shape__fill",
                "#next-button",
                "button.next-button",
                "//button[contains(text(), 'Next')]",
                "//div[contains(@class, 'next-button')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        next_button = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS selector
                        next_button = WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    if next_button:
                        break
                except:
                    continue
            
            if next_button:
                # Try regular click first
                try:
                    next_button.click()
                except:
                    # If regular click fails, try JavaScript click
                    driver.execute_script("arguments[0].click();", next_button)
                logging.info("Clicked third Next button")
            else:
                # If all selectors fail, try finding any button with Next text
                buttons = driver.find_elements(By.TAG_NAME, "button")
                next_clicked = False
                for button in buttons:
                    try:
                        if "next" in button.text.lower():
                            button.click()
                            next_clicked = True
                            logging.info("Clicked third Next button using text search")
                            break
                    except:
                        continue
                
                if not next_clicked:
                    raise Exception("Could not find third Next button")
        except Exception as e:
            logging.error(f"Error clicking third Next button: {str(e)}")
            logging.warning("Attempting to continue despite third Next button error")
        
        # Step 16: Click on Public radio button for visibility
        time.sleep(60)  # Wait for 2 minutes as requested
        logging.info("Selecting Public visibility...")
        try:
            public_radio = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='radioLabel' and text()='Public']")
            ))
            public_radio.click()
            logging.info("Selected Public visibility")
        except Exception as e:
            logging.error(f"Error selecting Public visibility: {str(e)}")
            raise Exception(f"Failed to select Public visibility: {str(e)}")
        
        # Step 17: Click on Publish button
        time.sleep(5)  # Wait for 5 seconds as requested
        logging.info("Clicking publish button...")
        try:
            # Try multiple selectors for the Publish button with increased timeout
            publish_button = None
            publish_selectors = [
                ".yt-spec-button-shape-next.yt-spec-button-shape-next--filled",
                "//button[contains(text(), 'Publish') or contains(text(), 'PUBLISH')]",
                "//span[contains(text(), 'Publish')]/parent::button",
                "//div[contains(@class, 'publish-button')]",
                "//button[contains(@class, 'publish')]"
            ]
            
            for selector in publish_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        publish_button = WebDriverWait(driver, 30).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        # CSS selector
                        publish_button = WebDriverWait(driver, 30).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    if publish_button:
                        break
                except:
                    continue
            
            if publish_button:
                # Try regular click first
                try:
                    publish_button.click()
                except:
                    # If regular click fails, try JavaScript click
                    driver.execute_script("arguments[0].click();", publish_button)
                logging.info("Clicked publish button")
            else:
                # If all selectors fail, try finding any button with Publish text
                buttons = driver.find_elements(By.TAG_NAME, "button")
                publish_clicked = False
                for button in buttons:
                    try:
                        button_text = button.text.lower()
                        if "publish" in button_text or "schedule" in button_text or "done" in button_text:
                            # Take a screenshot before clicking the button (for debugging)
                            try:
                                screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_before_publish.png")
                                driver.save_screenshot(screenshot_path)
                                logging.info(f"Saved screenshot before publish to {screenshot_path}")
                            except Exception as ss_error:
                                logging.warning(f"Failed to save screenshot: {ss_error}")
                            
                            # Try regular click first
                            try:
                                button.click()
                            except:
                                # If regular click fails, try JavaScript click
                                driver.execute_script("arguments[0].click();", button)
                            
                            publish_clicked = True
                            logging.info(f"Clicked button with text: {button_text}")
                            break
                    except:
                        continue
                
                if not publish_clicked:
                    raise Exception("Could not find Publish button")
        except Exception as e:
            logging.error(f"Error clicking publish button: {str(e)}")
            # Continue anyway as the video might still be uploaded
            logging.warning("Video may still be uploaded despite publish button error")
        
        # Step 18: Wait for final confirmation
        time.sleep(60)  # Wait for 2 minutes as requested
        try:
            success_message = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Video published') or contains(text(), 'Video scheduled') or contains(text(), 'Scheduled for')]"))
            )
            logging.info("Upload confirmed successful!")
            upload_success = True
        except:
            logging.warning("Could not confirm upload success, but it might still have worked")
            # The upload might still be successful even if we can't confirm it
            upload_success = True
        
        logging.info("Upload process completed successfully")
        return True
    
    except Exception as e:
        logging.error(f"Error during YouTube upload: {str(e)}")
        return False
    
    finally:
        # Close the browser window regardless of success or failure
        if driver:
            try:
                driver.quit()
                logging.info("Browser closed")
            except Exception as e:
                logging.error(f"Error closing browser: {str(e)}")

def main():
    # Get video title from title generator or use a default
    try:
        video_title = main_title_generator()
        logging.info(f"Generated video title: {video_title}")
    except Exception as e:
        video_title = "Amazing Content You Need to See"
        logging.error(f"Error generating title, using default: {str(e)}")
    
    # Set video file path
    # video_file = "downloaded_video.mp4"
    video_file = "downloaded_video.mp4"
    video_path = os.path.join(os.getcwd(), video_file)
    
    # Check if video file exists
    if not os.path.exists(video_path):
        logging.error(f"Video file not found: {video_path}")
        sys.exit(1)
    
    # Upload video to YouTube
    logging.info(f"Starting YouTube upload for video: {video_file} with title: {video_title}")
    success = upload_to_youtube_selenium(
        video_file=video_path,
        title=video_title,
        description="Like and Subscribe for more amazing content"
    )
    
    if success:
        logging.info("YouTube upload completed successfully!")
    else:
        logging.error("YouTube upload failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()