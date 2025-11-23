import requests
import json
from bs4 import BeautifulSoup
import re

URL = "https://lolchess.gg/champions/set15/three-cores"
OUTPUT_FILE = "three_core_items.json"

def parse_item_name(img_tag):
    """Parses the item name from an image tag's alt text or src."""
    if not img_tag:
        return "Unknown Item"

    item_name = img_tag.get('alt', '').strip()
    if item_name:
        # Remove spaces for consistency
        return item_name.replace(' ', '')

    # Fallback to parsing src if alt is not available
    src = img_tag.get('src', '')
    try:
        filename = src.split('/')[-1]
        # Clean up the filename to get a clean item id
        item_id = re.sub(r'(_\d+|\.png|\.jpg|\.jpeg|\.webp|TFT_Item_)', '', filename, flags=re.IGNORECASE)
        return item_id.replace('_', '')
    except Exception:
        return "Unknown Item"

def scrape_three_core_data():
    """
    Scrapes the three-core item data for all champions from the main page.
    """
    try:
        print(f"Fetching data from {URL}...")
        response = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        print("Successfully fetched page content.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    all_champion_data = {}

    # Find all champion data blocks. The provided class seems to be the container for each champ row.
    # The structure is a bit complex, with champions listed inside different tier articles.
    champion_blocks = soup.select('div.css-15za34x')

    print(f"Found {len(champion_blocks)} potential champion blocks. Parsing now...")

    for block in champion_blocks:
        # Find the champion name within the block
        champion_name_tag = block.find('p', class_=re.compile(r'text-\[11px\]'))
        if not champion_name_tag:
            continue

        champion_name_kr = champion_name_tag.text.strip()
        if not champion_name_kr:
            continue

        print(f"Processing champion: {champion_name_kr}")
        all_champion_data[champion_name_kr] = []

        # Find the nested table with item builds for this champion
        build_table = block.find('table', class_=re.compile(r'css-1522ukb'))
        if not build_table or not build_table.find('tbody'):
            print(f"  - No item build table found for {champion_name_kr}.")
            continue

        for row in build_table.find('tbody').find_all('tr'):
            columns = row.find_all('td')
            if len(columns) < 3:
                continue

            # Extract items, avg_rank, and pick_rate
            items_tags = columns[0].find_all('img')
            items = [parse_item_name(tag) for tag in items_tags]
            avg_rank = columns[1].text.strip()
            pick_rate = columns[2].text.strip()

            all_champion_data[champion_name_kr].append({
                "items": items,
                "avg_rank": avg_rank,
                "pick_rate": pick_rate
            })
        print(f"  - Found {len(all_champion_data[champion_name_kr])} item sets.")

    return all_champion_data

if __name__ == "__main__":
    champion_data = scrape_three_core_data()

    if champion_data:
        # Filter out champions with no data found
        champion_data = {k: v for k, v in champion_data.items() if v}

        print(f"\nSuccessfully parsed data for {len(champion_data)} champions.")

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(champion_data, f, ensure_ascii=False, indent=2)

        print(f"Data successfully saved to {OUTPUT_FILE}")
    else:
        print("Scraping failed or no data was found.")
