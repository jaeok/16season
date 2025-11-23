from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time

def get_three_core_items_selenium():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    url = "https://lolchess.gg/champions/set15/three-cores"
    driver.get(url)
    time.sleep(5)  # 충분히 렌더링 시간을 줍니다

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    champion_data = {}
    
    for champ_block in soup.select("div.css-15za34x"):
        name_tag = champ_block.select_one(".champion-wrapper p")
        if not name_tag:
            continue
        name = name_tag.get_text(strip=True)

        sets = []
        item_table = champ_block.select_one("table.css-1522ukb")
        if not item_table:
            continue

        for row in item_table.select("tbody tr"):
            items = [img["src"].split("/")[-1].split("_")[0] for img in row.select("td:nth-of-type(1) img")]
            
            # 평균 등수와 픽률 요소가 있는지 먼저 확인합니다.
            avg_rank_tag = row.select_one("td:nth-of-type(2)")
            pick_rate_tag = row.select_one("td:nth-of-type(3)")
            
            avg_rank = avg_rank_tag.get_text(strip=True) if avg_rank_tag else "N/A"
            pick_rate = pick_rate_tag.get_text(strip=True) if pick_rate_tag else "N/A"
            
            sets.append({
                "items": items,
                "avg_rank": avg_rank,
                "pick_rate": pick_rate
            })
        champion_data[name] = sets

    return champion_data

if __name__ == "__main__":
    data = get_three_core_items_selenium()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    with open("three_core_items.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)