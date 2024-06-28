
import os
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import signal
import sys
from urllib.parse import urlparse, unquote

# Configure WebDriver options
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

def load_wordlist(file_path):
    """Loads fuzz payloads from a wordlist file."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def take_screenshot(driver, url, response, save_path):
    """Takes a screenshot of the URL using Selenium and saves it."""
    driver.get(url)
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return
    
    # Extract domain name and path from URL
    parsed_url = urlparse(url)
    base_name = parsed_url.netloc.replace('www.', '')  # Extract domain name without 'www.'
    path = parsed_url.path.strip('/')
    path = unquote(path)  # Decode any URL encoding in the path
    
    # Create directory if it doesn't exist
    save_dir = os.path.join(save_path, base_name)
    os.makedirs(save_dir, exist_ok=True)
    
    # Clean up URL path for filename
    filename = os.path.join(save_dir, f"{path}.png")
    
    # Take screenshot and save
    screenshot = driver.get_screenshot_as_png()
    with open(filename, 'wb') as file:
        file.write(screenshot)

def ensure_url_scheme(url):
    """Ensures the URL has a scheme (http or https)."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url

def fuzz_url(base_url, payloads, driver):
    """Fuzzes the given URL and takes screenshots of appropriate responses."""
    base_url = ensure_url_scheme(base_url)
    
    # Create a directory to save screenshots
    save_path = os.path.join(os.getcwd(), 'screenshots')
    os.makedirs(save_path, exist_ok=True)

    def signal_handler(sig, frame):
        print("\nProcess interrupted by user.")
        driver.quit()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    for payload in payloads:
        fuzzed_url = base_url.replace("FUZZ", payload) if "FUZZ" in base_url else base_url.rstrip('/') + '/' + payload

        try:
            response = requests.get(fuzzed_url)
            print(f"Fuzzing {fuzzed_url} - Status code: {response.status_code}")
            if response.status_code == 200:  # Adjust based on what you consider appropriate
                take_screenshot(driver, fuzzed_url, response, save_path)
        except requests.RequestException as e:
            print(f"Error accessing {fuzzed_url}: {e}")

if __name__ == "__main__":
    base_url = input("Enter the URL with optional 'FUZZ' placeholder (e.g., example.com/FUZZ or example.com): ")
    wordlist_path = 'wordlist.txt'
    payloads = load_wordlist(wordlist_path)

    driver = webdriver.Firefox(service=FirefoxService(), options=options)
    try:
        fuzz_url(base_url, payloads, driver)
    finally:
        driver.quit()

