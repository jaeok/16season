import requests
from bs4 import BeautifulSoup
import re

URL = "https://lolchess.gg/champions/set15/three-cores"

def run_debug():
    try:
        response = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    print("Page fetched successfully. Parsing with BeautifulSoup...")
    soup = BeautifulSoup(response.content, 'html.parser')

    # --- Debugging Starts ---

    # 1. Check for the specific container the user mentioned.
    # The class name from the user is "css-6ztpii e1b28sf30". We search for the first part.
    container = soup.find('div', class_='css-6ztpii')
    if container:
        print("[SUCCESS] Found the main container: <div class='css-6ztpii...'>")

        # 2. Check for champion rows inside this container.
        # The user's HTML shows these are inside a div with class 'css-15za34x'.
        champion_blocks_in_container = container.select('div.css-15za34x')
        print(f"  - Found {len(champion_blocks_in_container)} champion blocks (.css-15za34x) inside this container.")

    else:
        print("[FAILURE] Could not find the main container: <div class='css-6ztpii...'>")

    # 3. As a fallback, check for the champion blocks anywhere in the document.
    all_champion_blocks = soup.select('div.css-15za34x')
    print(f"\nFor reference, found {len(all_champion_blocks)} champion blocks (.css-15za34x) in the *entire* document.")

    # 4. Let's also check for the articles that group the tiers.
    articles = soup.find_all('article', class_=re.compile(r'css-'))
    print(f"Found {len(articles)} <article> tags with 'css-' classes.")

if __name__ == "__main__":
    run_debug()
