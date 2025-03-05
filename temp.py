import re

from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Selenium Wire proxy configuration
sw_options = {
    'proxy': {
        'http': f'http://8.219.229.53:8080',
        'https': f'http://8.219.229.53:8080',
    }
}

# Set up Chrome options (optional settings)
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start Chrome maximized
chrome_options.add_argument("--no-sandbox")       # Avoid sandboxing (useful in restricted environments)
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource issues

# Set up WebDriver using webdriver-manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, seleniumwire_options=sw_options, options=chrome_options)

# Access target website
driver.get('https://www.youtube.com/')
time.sleep(20)

# Example: Extract the IP from the response
response = driver.page_source

# using simple regex to parse origin ip
print("Response:", response)
print("Your IP is:", re.search("HTTP_X_FORWARDED_FOR = (\d+\.)+\d+", response).group().split("=")[-1])

# quit the browser instance
driver.quit()

