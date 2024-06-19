# src\scraper.py

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from .utils import log_to_file, sanitize_filename
from pathlib import Path
import traceback
import time

def indicator_hit(content):
    indicators = [
        "is parked free", "domain for sale", "courtesy of GoDaddy.com",
        "buy this domain", "parked domain", "domain is for sale",
        "domain has expired", "renew this domain", 
        "error 404", "error 403", "503 service unavailable", "empty OK", "nginx", "403 Forbidden",
        "this site can’t be reached", "this page isn’t working", "Suspicious Site Blocked",
        "404 Page not found", "empty OK", "HTTP Status: 404 (not found)", "ERROR: The request could not be satisfied",

    ]
    for indicator in indicators:
        if indicator in content.lower():
            return True, indicator
    return False, None

def file_exists_for_url(filename):
    scraped_content_path = Path("/Users/andrewlazare/Projects/python script/scraped_content").joinpath(f"{filename}_scraped_content.txt")
    throw_path = Path("/Users/andrewlazare/Projects/python script/throw").joinpath(f"{filename}_not_suitable.txt")
    return scraped_content_path.exists() or throw_path.exists()

def scrape_webpage_with_selenium(original_url):
    log_to_file(f"Initiating scraping process for {original_url}")

    if not original_url.startswith(('http://', 'https://')):
        original_url = 'http://' + original_url

    filename = sanitize_filename(original_url)
    if file_exists_for_url(filename):
        log_to_file(f"Skipping {original_url} as content has already been processed.")
        return True

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--enable-automation")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.cookies": 1,
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.javascript": 1
    })

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(original_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)

        content = driver.page_source
        sale_or_error, indicator = indicator_hit(content)
        if sale_or_error:
            reason = f"Domain appears to be parked, in error, or not suitable for processing. Indicator Hit: {indicator}"
            log_reason_and_return_false(reason, original_url, filename)
        elif not content.strip():
            reason = "Content is blank or not meaningful."
            log_reason_and_return_false(reason, original_url, filename)
        else:
            soup = BeautifulSoup(content, 'html.parser')
            texts = soup.stripped_strings
            clean_text = "\n".join(texts)
            if clean_text.strip():
                with open(Path("/Users/andrewlazare/Projects/python script/scraped_content").joinpath(f"{filename}_scraped_content.txt"), 'w', encoding='utf-8') as f:
                    f.write(clean_text)
                log_to_file(f"Content parsed and written to {filename}_scraped_content.txt")
                return True
            else:
                reason = "Content is blank or not meaningful after parsing."
                log_reason_and_return_false(reason, original_url, filename)
    except Exception as e:
        log_to_file(f"Exception encountered while processing {original_url}: {str(e)}", is_error=True)
        log_to_file(traceback.format_exc(), is_error=True)
        log_to_file(f"Logging error for unreachable URL: {original_url}")  # Log error for unreachable URL
        with open(Path("/Users/andrewlazare/Projects/python script/throw").joinpath("throw_log.txt"), 'a', encoding='utf-8') as f:
            f.write(f"URL: {original_url}, Error message: {str(e).splitlines()[0]}\n")  # Log shorter error message
    finally:
        if driver:
            driver.quit()
    return False

def log_reason_and_return_false(reason, original_url, filename):
    log_to_file(f"Logged issue for {original_url}: {reason}")
    with open(Path("/Users/andrewlazare/Projects/python script/throw").joinpath("throw_log.txt"), 'a', encoding='utf-8') as f:
        f.write(f"URL: {original_url}, Reason: {reason}\n")
    return False
