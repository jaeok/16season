import json
import requests
from bs4 import BeautifulSoup
import re
import time

def get_champion_names():
    """Reads champion names from the JSON file."""
    try:
        with open('tft_all_champions_set15.json', 'r', encoding='utf-8') as f:
            champions = json.load(f)
        return [champion['champion_name'] for champion in champions]
    except FileNotFoundError:
        print("Error: tft_all_champions_set15.json not found.")
        return []

def parse_item_name_from_src(img_tag):
    """Parses the item name from the image tag's alt text or src URL."""
    if not img_tag:
        return "unknown_item"

    # Prioritize alt text as it's often cleaner
    item_name = img_tag.get('alt')
    if item_name:
        return item_name.replace(' ', '')

    # Fallback to parsing the src attribute
    src = img_tag.get('src', '')
    try:
        filename = src.split('/')[-1]
        # Extracts name, ignoring version numbers or hashes
        match = re.match(r"([a-zA-Z0-9\-\_]+?)(?:_?\d+)?\.(?:png|jpg|jpeg|webp)", filename)
        if match:
            # Clean up common naming conventions like 'TFT_Item_InfinityEdge'
            return match.group(1).replace('TFT_Item_', '').replace('_', '')
        return filename.split('.')[0] # fallback
    except Exception:
        return "unknown_item"

def scrape_champion_data(champion_name):
    """Scrapes comprehensive item data for a single champion."""
    url = f"https://lolchess.gg/champions/set15/{champion_name}?statistics=three-cores"
    print(f"Scraping {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch data for {champion_name}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # New, more robust method to find the table
    table = None
    all_tables = soup.find_all('table')
    for t in all_tables:
        headers = [th.text.strip() for th in t.select('thead th')]
        if 'Avg.Rank' in headers and 'Pick Rate' in headers and 'Win Rate' in headers:
            table = t
            break

    if not table:
        print(f"Could not find item statistics table for {champion_name}")
        return []

    item_sets = []
    tbody = table.find('tbody')
    if not tbody:
        return []

    for row in tbody.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) < 7:
            continue

        item_images = columns[1].find_all('img')
        items = [parse_item_name_from_src(img) for img in item_images]

        avg_rank_text = columns[2].text.strip()
        pick_rate_text = columns[3].text.strip()
        win_rate_text = columns[5].text.strip()

        try:
            win_rate = float(win_rate_text.replace('%', ''))
        except (ValueError, TypeError):
            win_rate = 0.0

        item_sets.append({
            'items': items,
            'avg_rank': avg_rank_text,
            'pick_rate': pick_rate_text,
            'win_rate': win_rate
        })

    return item_sets

def main():
    """Main function to scrape data and save to JSON."""
    champion_names = get_champion_names()
    if not champion_names:
        return

    all_champion_data = {}

    for i, name in enumerate(champion_names):
        if not name:
            continue

        item_data = scrape_champion_data(name)
        if item_data is not None:
            all_champion_data[name] = item_data
        else:
            all_champion_data[name] = []

        # Add a small delay to avoid overwhelming the server
        if i < len(champion_names) - 1:
            time.sleep(1)

    with open('full_champion_stats.json', 'w', encoding='utf-8') as f:
        json.dump(all_champion_data, f, ensure_ascii=False, indent=2)

    print("\nScraping complete. Data saved to full_champion_stats.json")

if __name__ == '__main__':
    main()
