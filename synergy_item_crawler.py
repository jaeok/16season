import asyncio
import json
from bs4 import BeautifulSoup
from crawl4ai import *

# 시즌 설정 (변수로 쉽게 수정 가능)
SEASON = "set15"  # set14, set13, set12 등으로 변경 가능

async def get_synergy_data(season):
    """
    lolchess.gg에서 특정 시즌의 시너지 데이터를 가져옵니다.
    
    Args:
        season (str): 시즌 번호 (예: "set15", "set14", "set13")
    
    Returns:
        list: 시너지 데이터 리스트
    """
    url = f"https://lolchess.gg/synergies/{season}"
    print(f"시즌 {season} 시너지 데이터 크롤링 시작: {url}")
    
    async with AsyncWebCrawler(headless=False) as crawler:
        try:
            # 페이지 크롤링 (로딩 대기)
            result = await crawler.arun(url=url, wait_for="table", timeout=15000)
            
            if not result.html:
                print(f"오류: {season} 시너지 페이지에서 HTML을 가져올 수 없습니다.")
                return []
            
            # HTML 파싱
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # 시너지 데이터 추출
            synergies_data = []
            
            # 테이블에서 시너지 데이터 찾기
            tables = soup.find_all('table')
            print(f"테이블 수: {len(tables)}")
            
            for table in tables:
                rows = table.find_all('tr')
                print(f"테이블 행 수: {len(rows)}")
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 7:  # 시너지, 평균 등수, TOP4, 승률, 픽률, 게임 수, 챔피언 TOP3
                        synergy_data = {}
                        
                        # 각 셀의 데이터 추출
                        for i, cell in enumerate(cells):
                            cell_text = cell.get_text(strip=True)
                            
                            if i == 0:  # 시너지 이름
                                synergy_data["synergy_name"] = cell_text
                            elif i == 1:  # 평균 등수
                                try:
                                    synergy_data["average_rank"] = float(cell_text)
                                except ValueError:
                                    synergy_data["average_rank"] = cell_text
                            elif i == 2:  # TOP4
                                try:
                                    synergy_data["top4_rate"] = float(cell_text.replace('%', ''))
                                except ValueError:
                                    synergy_data["top4_rate"] = cell_text
                            elif i == 3:  # 승률
                                try:
                                    synergy_data["win_rate"] = float(cell_text.replace('%', ''))
                                except ValueError:
                                    synergy_data["win_rate"] = cell_text
                            elif i == 4:  # 픽률
                                try:
                                    synergy_data["pick_rate"] = float(cell_text.replace('%', ''))
                                except ValueError:
                                    synergy_data["pick_rate"] = cell_text
                            elif i == 5:  # 게임 수
                                try:
                                    synergy_data["games_played"] = int(cell_text.replace(',', ''))
                                except ValueError:
                                    synergy_data["games_played"] = cell_text
                            elif i == 6:  # 챔피언 TOP3
                                synergy_data["top_champions"] = cell_text
                        
                        # 유효한 시너지 데이터인지 확인
                        if synergy_data.get("synergy_name") and synergy_data["synergy_name"] not in ['시너지', 'Synergy', '']:
                            synergies_data.append(synergy_data)
                            print(f"시너지 추가: {synergy_data['synergy_name']}")
            
            print(f"총 {len(synergies_data)}개의 시너지 데이터를 찾았습니다.")
            
            # 디버깅: 처음 5개 시너지 출력
            if synergies_data:
                print("찾은 시너지들 (처음 5개):")
                for i, synergy in enumerate(synergies_data[:5]):
                    print(f"  {i+1}. {synergy}")
            
            return synergies_data
            
        except Exception as e:
            print(f"오류: {season} 시즌 시너지 크롤링 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

async def get_item_data(season):
    """
    lolchess.gg에서 특정 시즌의 아이템 목록 및 효과 데이터를 가져옵니다.
    제공된 HTML 구조에 맞춰 수정되었습니다.
    
    Args:
        season (str): 시즌 번호 (예: "set15", "set14", "set13")
    
    Returns:
        list: 아이템 데이터 리스트 (이름, 이미지, 효과)
    """
    url = f"https://lolchess.gg/items/{season}/guide"
    print(f"시즌 {season} 아이템 데이터 크롤링 시작: {url}")
    
    async with AsyncWebCrawler(headless=True) as crawler: # headless를 True로 변경하여 백그라운드 실행 (필요 시 False)
        try:
            # wait_for 조건을 더 구체적으로 변경합니다.
            # 이 페이지에서는 item 목록이 들어있는 테이블 자체가 로딩되면 됩니다.
            result = await crawler.arun(url=url, wait_for="table.css-s97u20", timeout=15000)
            
            if not result.html:
                print(f"오류: {season} 아이템 페이지에서 HTML을 가져올 수 없습니다.")
                return []
            
            soup = BeautifulSoup(result.html, 'html.parser')
            items_data = []
            
            # 아이템 목록을 포함하는 특정 테이블을 찾습니다.
            # 제공된 HTML의 테이블 클래스를 사용합니다.
            item_table = soup.find('table', class_='css-s97u20')
            
            if not item_table:
                print(f"오류: 아이템 테이블 (class='css-s97u20')을 찾을 수 없습니다.")
                return []

            # 테이블의 각 행(<tr>)을 순회합니다.
            rows = item_table.find_all('tr')
            print(f"아이템 테이블 행 수: {len(rows)}")

            # 첫 번째 행은 헤더이므로 스킵합니다.
            for row in rows[1:]:
                item_data = {}
                
                # 첫 번째 td는 아이템 정보 (이름, 이미지, 조합 재료)
                item_info_cell = row.find('td')
                if not item_info_cell:
                    continue

                # 아이템 이름 추출
                item_name_tag = item_info_cell.find('div', class_='css-1vrsxza')
                item_data["item_name"] = item_name_tag.get_text(strip=True) if item_name_tag else None
                
                # 아이템 이미지 URL 추출
                item_img_tag = item_info_cell.find('div', class_='css-ok8zxw').find('img')
                item_data["item_image_url"] = item_img_tag['src'] if item_img_tag else None

                # 아이템 효과 추출 (css-xrzf54 또는 css-uh2eun 클래스 사용)
                # 제공된 HTML에서는 두 번째 td (class="css-uh2eun e14r4a8l13")에 깔끔하게 효과만 있습니다.
                effect_cell = row.find_all('td')
                if len(effect_cell) > 1:
                    # <br> 태그를 줄 바꿈으로 변환하여 텍스트 추출
                    effect_html = str(effect_cell[1])
                    effect_text_soup = BeautifulSoup(effect_html, 'html.parser')
                    effect_text = effect_text_soup.get_text(separator='\n', strip=True)
                    item_data["item_effect"] = effect_text
                else:
                    # 첫 번째 td 내에도 효과가 있을 수 있으므로 폴백 처리
                    effect_div = item_info_cell.find('div', class_='css-xrzf54')
                    if effect_div:
                        effect_html = str(effect_div)
                        effect_text_soup = BeautifulSoup(effect_html, 'html.parser')
                        item_data["item_effect"] = effect_text_soup.get_text(separator='\n', strip=True)
                    else:
                        item_data["item_effect"] = None


                # 조합 아이템 재료 추출 (조합 아이템인 경우에만 해당)
                ingredient_div = item_info_cell.find('div', class_='css-fmsyuf')
                if ingredient_div:
                    ingredients = []
                    # 재료 이미지 태그 찾기
                    ingredient_imgs = ingredient_div.find_all('img')
                    for img in ingredient_imgs:
                        ingredients.append(img['src'])
                    item_data["ingredients_image_urls"] = ingredients
                else:
                    item_data["ingredients_image_urls"] = [] # 기본 아이템은 재료가 없음

                if item_data.get("item_name"):
                    items_data.append(item_data)
                    print(f"아이템 추가: {item_data['item_name']}")
            
            print(f"총 {len(items_data)}개의 아이템 데이터를 찾았습니다.")
            
            if items_data:
                print("찾은 아이템들 (처음 5개):")
                for i, item in enumerate(items_data[:5]):
                    print(f"  {i+1}. {item}")
            
            return items_data
            
        except Exception as e:
            print(f"오류: {season} 시즌 아이템 크롤링 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

async def get_augment_data(season):
    """
    lolchess.gg에서 특정 시즌의 증강체 데이터를 가져옵니다.

    Args:
        season (str): 시즌 번호 (예: "set15", "set14", "set13")

    Returns:
        list: 증강체 데이터 리스트
    """
    url = f"https://lolchess.gg/augments/{season}"
    print(f"시즌 {season} 증강체 데이터 크롤링 시작: {url}")

    async with AsyncWebCrawler(headless=False) as crawler:
        try:
            # 페이지 크롤링 (로딩 대기)
            result = await crawler.arun(url=url, wait_for="table", timeout=15000)

            if not result.html:
                print(f"오류: {season} 증강체 페이지에서 HTML을 가져올 수 없습니다.")
                return []

            # HTML 파싱
            soup = BeautifulSoup(result.html, 'html.parser')

            # 증강체 데이터 추출
            augments_data = []

            # 증강체 테이블 찾기 (사용자가 제공한 HTML 구조 기반)
            augment_table = soup.find('table', class_='css-1qp7y41 e110kr665')

            if not augment_table:
                print(f"오류: {season} 증강체 테이블을 찾을 수 없습니다.")
                return []

            for row in augment_table.select('tbody tr'):
                # 증강체 이름: div.css-1eu4zav.e110kr667 span
                name_span = row.select_one('div.css-1eu4zav.e110kr667 span')
                # 증강체 효과: div.css-xrzf54.e110kr666
                effect_div = row.select_one('div.css-xrzf54.e110kr666')

                if name_span and effect_div:
                    augment_name = name_span.get_text(strip=True)
                    augment_effect = effect_div.get_text(strip=True)
                    augments_data.append({"name": augment_name, "effect": augment_effect})

            print(f"증강체 데이터 {len(augments_data)}개 추출 완료.")
            return augments_data

        except Exception as e:
            print(f"증강체 데이터 크롤링 중 오류 발생: {e}")
            return []

async def get_power_up_data(season):
    """
    lolchess.gg에서 특정 시즌의 파워업 데이터를 가져옵니다.
    
    Args:
        season (str): 시즌 번호 (예: "set15")
    
    Returns:
        list: 파워업 데이터 리스트
    """
    url = f"https://lolchess.gg/rewards/{season}/power-ups"
    print(f"시즌 {season} 파워업 데이터 크롤링 시작: {url}")
    
    async with AsyncWebCrawler(headless=False) as crawler:
        try:
            # 페이지 크롤링 (로딩 대기)
            # 파워업 목록이 로딩될 때까지 기다립니다.
            result = await crawler.arun(url=url, wait_for="div.css-1y29jp8.efk5oo90 ul li", timeout=15000)
            
            if not result.html:
                print(f"오류: {season} 파워업 페이지에서 HTML을 가져올 수 없습니다.")
                return []
            
            # HTML 파싱
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # 파워업 데이터 추출
            power_ups_data = []
            
            # 파워업 리스트 컨테이너
            power_up_list_container = soup.find('div', class_='css-1y29jp8 efk5oo90')
            
            if not power_up_list_container:
                print(f"오류: {season} 파워업 리스트 컨테이너를 찾을 수 없습니다.")
                return []

            # 각 파워업 항목 순회
            for li in power_up_list_container.select('ul li'):
                power_up_item_div = li.select_one('div.css-f0uu6s.ewd7isn0')
                if not power_up_item_div:
                    continue

                # 파워업 이름
                name_span = power_up_item_div.select_one('div.power-up-name span')
                power_up_name = name_span.get_text(strip=True) if name_span else "이름 없음"

                # 파워업 효과 (stats)
                effect_p = power_up_item_div.select_one('div.stats p')
                power_up_effect = effect_p.get_text(strip=True) if effect_p else "효과 없음"

                # 태그 (가중치, 최대 스테이지 등)
                tags = []
                for tag_div in power_up_item_div.select('div.power-up-tags div.tag'):
                    tags.append(tag_div.get_text(strip=True))
                

                power_ups_data.append({
                    "name": power_up_name,
                    "effect": power_up_effect,
                    "tags": tags
                })

            print(f"파워업 데이터 {len(power_ups_data)}개 추출 완료.")
            return power_ups_data

        except Exception as e:
            print(f"파워업 데이터 크롤링 중 오류 발생: {e}")
            return []


async def main():
    """
    시즌별 시너지와 아이템 데이터를 크롤링하고 JSON 파일로 저장합니다.
    """
    print(f"=== TFT 시즌 {SEASON} 시너지 & 아이템 크롤러 ===")
    
    # 시너지 데이터 가져오기
    print("\n=== 시너지 데이터 크롤링 ===")
    synergies_data = await get_synergy_data(SEASON)
    
    # 아이템 데이터 가져오기
    print("\n=== 아이템 데이터 크롤링 ===")
    items_data = await get_item_data(SEASON)
    
    # 증강체 데이터 가져오기
    print("\n=== 증강체 데이터 크롤링 ===")
    augments_data = await get_augment_data(SEASON)
    
    # 파워업 데이터 가져오기
    print("\n=== 파워업 데이터 크롤링 ===")
    power_ups_data = await get_power_up_data(SEASON)
    
    # 전체 결과를 하나의 JSON 파일로 저장
    all_data = {
        "season": SEASON,
        "synergies": synergies_data,
        "items": items_data,
        "total_synergies": len(synergies_data),
        "total_items": len(items_data),
        "augments": augments_data,
        "total_augments": len(augments_data),
        "power_ups": power_ups_data,
        "total_power_ups": len(power_ups_data),
        "crawl_urls": {
            "synergies": f"https://lolchess.gg/synergies/{SEASON}",
            "items": f"https://lolchess.gg/items/{SEASON}/guide",
            "augments": f"https://lolchess.gg/augments/{SEASON}",
            "power_ups": f"https://lolchess.gg/rewards/{SEASON}/power-ups"
        }
    }
    
    if synergies_data or items_data or augments_data or power_ups_data:
        print(f"\n=== 크롤링 완료 ===")
        print(f"성공적으로 추출된 시너지 수: {len(synergies_data)}")
        print(f"성공적으로 추출된 아이템 수: {len(items_data)}")
        print(f"성공적으로 추출된 증강체 수: {len(augments_data)}")
        print(f"성공적으로 추출된 파워업 수: {len(power_ups_data)}")
        # 전체 결과를 JSON 파일로 저장
        output_filename = f"tft_synergies_items_augments_power_ups_{SEASON}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"결과가 '{output_filename}' 파일에 저장되었습니다.")
        
        
        return all_data
        
    else:
        print("데이터를 찾을 수 없습니다.")
        return {}

if __name__ == "__main__":
    # 시너지와 아이템 데이터 크롤링 실행
    all_data = asyncio.run(main())
    
    if all_data:
        print(f"\n=== 크롤링 결과 요약 ===")
        print(f"시즌: {SEASON}")
        print(f"총 시너지 수: {all_data['total_synergies']}")
        print(f"총 아이템 수: {all_data['total_items']}")
        print(f"총 증강체 수: {all_data['total_augments']}")
        print(f"총 파워업 수: {all_data['total_power_ups']}")
    else:
        print("데이터를 가져올 수 없습니다.") 