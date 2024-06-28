import requests
import itertools
import string
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from PIL import Image
from io import BytesIO

# Configure WebDriver options
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

def generate_fuzz_payloads():
    """Generates payloads to fuzz the URL."""
    payloads = []
    characters = string.ascii_lowercase + string.digits
    for length in range(1, 4):  # You can adjust the range for more extensive fuzzing
        for payload in itertools.product(characters, repeat=length):
            payloads.append(''.join(payload))
    return payloads

def take_screenshot(url, response):
    """Takes a screenshot of the URL using Selenium and saves it."""
    driver = webdriver.Chrome(service=ChromeService(), options=options)
    driver.get(url)
    time.sleep(2)  # Wait for the page to load completely
    
    # Take screenshot
    screenshot = driver.get_screenshot_as_png()
    driver.quit()
    
    # Save the screenshot with the URL and response status code in the filename
    filename = f"screenshot_{url.replace('http://', '').replace('https://', '').replace('/', '_')}_{response.status_code}.png"
    with open(filename, 'wb') as file:
        file.write(screenshot)

def fuzz_url(base_url):
    """Fuzzes the given URL and takes screenshots of appropriate responses."""
    fuzz_payloads = generate_fuzz_payloads()
    for payload in fuzz_payloads:
        fuzzed_url = base_url.replace("FUZZ", payload)
        try:
            response = requests.get(fuzzed_url)
            print(f"Fuzzing {fuzzed_url} - Status code: {response.status_code}")
            if response.status_code == 200:  # Adjust based on what you consider appropriate
                take_screenshot(fuzzed_url, response)
        except requests.RequestException as e:
            print(f"Error accessing {fuzzed_url}: {e}")

if __name__ == "__main__":
    base_url = "http://example.com/FUZZ"
    fuzz_url(base_url)

