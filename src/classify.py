# src/classify.py

import requests
from .utils import log_to_file, sanitize_filename
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def classify_content(content, policies, api_base_url, headers, url):
    matches = {}
    matches_dir = Path(__file__).parent.parent / "matches"
    matches_dir.mkdir(exist_ok=True)

    sanitized_url = sanitize_filename(url)
    matches_filepath = matches_dir / "match_log.txt"  # Changed file name

    def classify_and_log(policy):
        result, status_code = classify_text(content, policy, api_base_url, url)
        total_matches = result.get('totalMatches', 0)
        log_to_file(f"Classification attempt for URL: {url} with Policy: {policy['name']}. Total Matches: {total_matches}, Status Code: {status_code}")
        if total_matches > 0:
            with open(matches_filepath, 'a', encoding='utf-8') as f:
                f.write(f"Url: {url}, Policy: {policy['name']}, Matches: {total_matches}\n")
            return policy['name'], result
        else:
            log_to_file(f"No matches or error for URL: {url} with Policy: {policy['name']}.")
        return None, None

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(classify_and_log, policy) for policy in policies]
        for future in as_completed(futures):
            future.result()

    return matches

def classify_text(content, policy, api_base_url, url):
    files = {
        'Text': (None, content),
        'PolicyId': (None, policy["id"])
    }
    try:
        response = requests.post(api_base_url, files=files, timeout=10)
        log_to_file(f"API Request sent for URL: {url} with Policy: {policy['name']}. Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            log_to_file(f"API Response for URL: {url} with Policy: {policy['name']}: {result}")
            return result, response.status_code
        else:
            log_to_file(f"API call failed for URL: {url} with Policy: {policy['name']}. Status Code: {response.status_code}, Response: {response.text}")
            return {'totalMatches': 0}, response.status_code
    except Exception as e:
        log_to_file(f"Error in classification for URL: {url} with Policy: {policy['name']}: {e}", is_error=True)
        return {'totalMatches': 0}, 0


