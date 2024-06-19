# main.py

from pathlib import Path
from src.utils import ensure_directories_exist, log_to_file, sanitize_filename, file_exists_for_url
from src.scraper import scrape_webpage_with_selenium
from src.classify import classify_content
from src.policies import load_policies

def main():
    ensure_directories_exist()
    log_to_file("Main process initiated.")

    policies_filepath = Path(__file__).resolve().parent / 'resources' / 'response_1708232219067.json'
    policies = load_policies(policies_filepath)
    if not policies:
        log_to_file("Failed to load policies, process terminated.", is_error=True)
        return

    api_base_url = 'https://classiapi.data443.com/api/classification/text'
    headers = {'accept': 'text/plain', 'Content-Type': 'multipart/form-data'}
    urls_file_path = Path(__file__).resolve().parent / 'resources' / 'unknown domains.txt'

    if urls_file_path.is_file():
        with open(urls_file_path, 'r', encoding='utf-8') as file:
            urls = file.read().splitlines()

        for url in urls:
            filename = sanitize_filename(url)
            # Skip if content is already scraped or flagged as not suitable.
            if file_exists_for_url(filename):
                log_to_file(f"Skipping processing for {url} as it has already been processed.")
                continue

            scraping_result = scrape_webpage_with_selenium(url)
            if not scraping_result:
                log_to_file(f"Skipping classification for {url} as scraping was not successful or not required.")
                continue

            # The script only reaches this part if the scraping was successful
            content_path = Path("/Users/andrewlazare/Projects/python script/scraped_content").joinpath(f"{filename}_scraped_content.txt")
            with open(content_path, 'r', encoding='utf-8') as content_file:
                content = content_file.read()
            
            if content.strip():
                matches = classify_content(content, policies, api_base_url, headers, url)
                if matches:
                    for policy_name, match in matches.items():
                        matches_filename = Path("/Users/andrewlazare/Projects/python script/matches").joinpath(f"{filename}_matches.txt")
                        with open(matches_filename, 'w', encoding='utf-8') as f:
                            f.write(f"{policy_name}: {match['totalMatches']} matches\n")
                        log_to_file(f"Classification matches written to: {matches_filename}")
                else:
                    log_to_file(f"No classification matches found for URL: {url}.")
            else:
                log_to_file(f"Skipped classification due to empty content for URL: {url}.")
    else:
        log_to_file("URLs file not found.")

    log_to_file("Main process completed.")

if __name__ == "__main__":
    main()
