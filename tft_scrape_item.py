import json
import requests
from bs4 import BeautifulSoup
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_champion_names():
    """Reads champion names from the JSON file."""
    try:
        with open('tft_all_champions_set15.json', 'r', encoding='utf-8') as f:
            champions = json.load(f)
        return [champion['champion_name'] for champion in champions]
    except FileNotFoundError:
        print("Error: tft_all_champions_set15.json not found.")
        return []

def parse_item_name_from_src(src):
    """Parses the item name from the image src URL."""
    if not src:
        return "unknown_item"
    try:
        filename = src.split('/')[-1]
        match = re.match(r"([a-zA-Z0-9]+)", filename)
        if match:
            return match.group(1)
        return filename.split('.')[0]
    except Exception:
        return "unknown_item"

def scrape_champion_data(champion_name, driver):
    """Scrapes item data for a single champion using Selenium."""
    url = f"https://lolchess.gg/champions/set15/{champion_name}?statistics=three-cores"
    print(f"Scraping {url}")
    
    try:
        driver.get(url)
        
        # 테이블이 나타날 때까지 최대 10초간 기다립니다.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "css-18jn4bq"))
        )
        
        # 페이지 소스를 가져와 BeautifulSoup으로 파싱합니다.
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
    except Exception as e:
        print(f"Could not fetch data for {champion_name} with Selenium: {e}")
        return []

    table = soup.find('table', class_='css-18jn4bq')
    if not table:
        print(f"Could not find item table for {champion_name}")
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
        items = [parse_item_name_from_src(img.get('src')) for img in item_images]

        win_rate_text = columns[5].text.strip()
        try:
            win_rate = float(win_rate_text.replace('%', ''))
        except ValueError:
            win_rate = 0.0

        item_sets.append({'items': items, 'win_rate': win_rate})

    return item_sets

def main():
    """Main function to scrape data and save to JSON."""
    champion_names = get_champion_names()
    if not champion_names:
        return

    all_champion_data = {}
    
    # Chrome 드라이버를 설정하고 실행합니다.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # ✨ 이 줄을 추가하여 SSL/TLS 인증서 오류를 무시하도록 설정합니다.
    chrome_options.add_argument('--ignore-certificate-errors')
    # ✨ 이 옵션을 추가하여 로그 메시지를 숨깁니다.
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"Failed to initialize WebDriver: {e}")
        return

    for i, name in enumerate(champion_names):
        item_data = scrape_champion_data(name, driver)
        if item_data is not None:
            sorted_items = sorted(item_data, key=lambda x: x['win_rate'], reverse=True)
            all_champion_data[name] = sorted_items[:3]
        else:
            all_champion_data[name] = []
        
        if i < len(champion_names) - 1:
            time.sleep(1)
            
    driver.quit() # 작업 완료 후 드라이버를 종료합니다.

    with open('champion_item_stats.json', 'w', encoding='utf-8') as f:
        json.dump(all_champion_data, f, ensure_ascii=False, indent=2)

    print("\nScraping complete. Data saved to champion_item_stats.json")

if __name__ == '__main__':
    main()