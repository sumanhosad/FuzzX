import os
import requests
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from PIL import Image
import signal
# Configure WebDriver options
#test
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

def load_wordlist(file_path):
    """Loads fuzz payloads from a wordlist file."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def take_screenshot(url, response, save_path):
    """Takes a screenshot of the URL using Selenium and saves it."""
    driver = webdriver.Firefox(service=FirefoxService(), options=options)
    driver.get(url)
    time.sleep(2)  # Wait for the page to load completely
    
    # Take screenshot
    screenshot = driver.get_screenshot_as_png()
    driver.quit()
    
    # Save the screenshot with the URL and response status code in the filename
    filename = os.path.join(save_path, f"screenshot_{url.replace('http://', '').replace('https://', '').replace('/', '_')}_{response.status_code}.png")
    with open(filename, 'wb') as file:
        file.write(screenshot)

def ensure_url_scheme(url):
    """Ensures the URL has a scheme (http or https)."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url

def fuzz_url(base_url, payloads):
    """Fuzzes the given URL and takes screenshots of appropriate responses."""
    base_url = ensure_url_scheme(base_url)
    
    # Create a directory based on the base URL
    domain_name = base_url.replace('http://', '').replace('https://', '').split('/')[0]
    save_path = os.path.join(os.getcwd(), domain_name)
    os.makedirs(save_path, exist_ok=True)

    try:
        for payload in payloads:
            if "FUZZ" in base_url:
                fuzzed_url = base_url.replace("FUZZ", payload)
            else:
                fuzzed_url = base_url.rstrip('/') + '/' + payload

            try:
                response = requests.get(fuzzed_url)
                print(f"Fuzzing {fuzzed_url} - Status code: {response.status_code}")
                if response.status_code == 200:  # Adjust based on what you consider appropriate
                    take_screenshot(fuzzed_url, response, save_path)
            except requests.RequestException as e:
                print(f"Error accessing {fuzzed_url}: {e}")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")

if __name__ == "__main__":
    base_url = input("Enter the URL with optional 'FUZZ' placeholder (e.g., example.com/FUZZ or example.com): ")
    wordlist_path = 'wordlist.txt'
    payloads = load_wordlist(wordlist_path)
    fuzz_url(base_url, payloads)

