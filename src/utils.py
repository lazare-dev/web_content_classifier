# # src\utils.py

# from pathlib import Path

# def ensure_directories_exist():
#     Path("scraped_content").mkdir(exist_ok=True)
#     Path("matches").mkdir(exist_ok=True)
#     Path("throw").mkdir(exist_ok=True)  # Ensure the throw directory exists

# def log_to_file(message, is_error=False):
#     filename = "log_error.txt" if is_error else "log_trace.txt"
#     with open(filename, 'a', encoding='utf-8') as log_file:
#         log_file.write(f"{message}\n")

# def sanitize_filename(url):
#     # Remove http:// or https:// from the URL to avoid 'http___' in filenames
#     clean_url = url.replace('http://', '').replace('https://', '')
#     return "".join(c if c.isalnum() or c in '_.' else '_' for c in clean_url)

# def file_exists_for_url(filename):
#     scraped_content_path = Path("/Users/andrewlazare/Projects/python script/scraped_content").joinpath(f"{filename}_scraped_content.txt")
#     throw_path = Path("/Users/andrewlazare/Projects/python script/throw").joinpath(f"{filename}_not_suitable.txt")
#     return scraped_content_path.exists() or throw_path.exists()


# src\utils.py

from pathlib import Path

def ensure_directories_exist():
    Path("scraped_content").mkdir(exist_ok=True)
    Path("matches").mkdir(exist_ok=True)
    Path("throw").mkdir(exist_ok=True)  # Ensure the throw directory exists

def log_to_file(message, is_error=False):
    filename = "log_error.txt" if is_error else "log_trace.txt"
    with open(filename, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{message}\n")

def sanitize_filename(url):
    # Remove http:// or https:// from the URL to avoid 'http___' in filenames
    clean_url = url.replace('http://', '').replace('https://', '')
    return "".join(c if c.isalnum() or c in '_.' else '_' for c in clean_url)

def file_exists_for_url(filename):
    scraped_content_path = Path("/Users/andrewlazare/Projects/python script/scraped_content").joinpath(f"{filename}_scraped_content.txt")
    throw_path = Path("/Users/andrewlazare/Projects/python script/throw").joinpath(f"{filename}_not_suitable.txt")
    return scraped_content_path.exists() or throw_path.exists()