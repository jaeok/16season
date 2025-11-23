import asyncio
import json
import re
from bs4 import BeautifulSoup

# 사용자님의 지시에 따라 from crawl4ai import * 만 사용합니다.
from crawl4ai import *

# 시즌 설정 (변수로 쉽게 수정 가능)
SEASON = "set15"  # set14, set13, set12 등으로 변경 가능

async def get_champion_names_from_season(season):
    """
    lolchess.gg에서 특정 시즌의 모든 챔피언 이름을 가져옵니다.
    
    Args:
        season (str): 시즌 번호 (예: "set15", "set14", "set13")
    
    Returns:
        list: 챔피언 이름 리스트 (소문자)
    """
    url = f"https://lolchess.gg/champions/{season}/"
    print(f"시즌 {season} 챔피언 목록 크롤링 시작: {url}")
    
    async with AsyncWebCrawler(headless=False) as crawler:
        try:
            # 페이지 크롤링
            result = await crawler.arun(url=url)
            
            if not result.html:
                print(f"오류: {season} 페이지에서 HTML을 가져올 수 없습니다.")
                return []
            
            # HTML 파싱
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # 챔피언 링크 찾기
            champion_links = []
            
            # 여러 가지 방법으로 챔피언 링크 찾기
            link_patterns = [
                "a[href*='/champions/']",
                ".champion-list a",
                ".guide-champion-list a",
                "a[href*='champions']"
            ]
            
            for pattern in link_patterns:
                links = soup.select(pattern)
                if links:
                    print(f"패턴 '{pattern}'으로 {len(links)}개의 링크를 찾았습니다.")
                    champion_links = links
                    break
            
            if not champion_links:
                # 모든 링크에서 champions 관련 링크 필터링
                all_links = soup.find_all('a', href=True)
                champion_links = [link for link in all_links if '/champions/' in link.get('href')]
                print(f"href 필터링으로 {len(champion_links)}개의 링크를 찾았습니다.")
            
            # 챔피언 이름 추출
            champion_names = []
            for link in champion_links:
                href = link.get('href', '')
                
                # href에서 챔피언 이름 추출
                # 예: /champions/set15/garen -> garen
                parts = href.split('/')
                if len(parts) >= 3:
                    champion_name = parts[-1]
                    
                    # 유효한 챔피언 이름인지 확인
                    if champion_name and champion_name != season and champion_name not in ['champions', 'set15', 'set14', 'set13', 'stats', 'three-cores', 'meta', 'tier-list', 'synergies', 'items', 'augments', 'power-ups', 'overlay', 'tools', 'guides', 'boards', 'duo-finder']:
                        # 소문자로 변환하고 중복 제거
                        champion_name_lower = champion_name.lower()
                        if champion_name_lower not in champion_names:
                            champion_names.append(champion_name_lower)
            
            print(f"총 {len(champion_names)}개의 고유한 챔피언을 찾았습니다.")
            
            # 디버깅: 처음 10개 챔피언 출력
            if champion_names:
                print("찾은 챔피언들 (처음 10개):")
                for i, name in enumerate(champion_names[:10]):
                    print(f"  {i+1}. {name}")
            
            return champion_names
            
        except Exception as e:
            print(f"오류: {season} 시즌 크롤링 중 오류 발생: {str(e)}")
            return []

async def get_champion_data(season, champion_name):
    """
    개별 챔피언 페이지에서 상세 데이터를 가져옵니다.
    
    Args:
        season (str): 시즌 번호
        champion_name (str): 챔피언 이름 (소문자)
    
    Returns:
        dict: 챔피언 상세 데이터
    """
    url = f"https://lolchess.gg/champions/{season}/{champion_name}"
    print(f"챔피언 '{champion_name}' 데이터 크롤링 시작: {url}")
    
    async with AsyncWebCrawler(headless=False) as crawler:
        try:
            # 페이지 크롤링 (로딩 대기)
            result = await crawler.arun(url=url, wait_for=".champion-info-wrapper", timeout=10000)
            
            if not result.html:
                print(f"오류: {champion_name} 페이지에서 HTML을 가져올 수 없습니다.")
                return None
            
            # HTML 파싱
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # 챔피언 데이터 초기화
            champion_data = {
                "name": "",
                "cost": 0,
                "traits": [],
                "role": "",
                "health": "",
                "attack_damage": "",
                "dps": "",
                "attack_range": "",
                "attack_speed": "",
                "armor": "",
                "magic_resistance": "",
                "skill_name": "",
                "skill_description": ""
            }
            
            # champion-info-wrapper 찾기
            champion_info_wrapper = soup.find('div', class_='champion-info-wrapper')
            if not champion_info_wrapper:
                print("경고: champion-info-wrapper를 찾을 수 없습니다.")
                return None
            
            print("champion-info-wrapper를 찾았습니다.")
            
            # 1. 챔피언 이름 추출 (h3 태그)
            name_tag = champion_info_wrapper.find('h3')
            if name_tag:
                champion_data["name"] = name_tag.get_text(strip=True)
                print(f"이름: {champion_data['name']}")
            else:
                print("경고: h3 태그를 찾을 수 없습니다.")
            
            # 2. 기본 정보 추출 (비용, 특성, 역할군)
            primary_info = champion_info_wrapper.find('div', class_='primary-ifno')
            if primary_info:
                print("primary-ifno 컨테이너를 찾았습니다.")
                
                # 비용 추출
                cost_label = primary_info.find('div', class_='label', string='비용')
                if cost_label:
                    cost_value = cost_label.find_next_sibling('div', class_='value')
                    if cost_value and cost_value.find('span'):
                        cost_text = cost_value.find('span').get_text(strip=True)
                        try:
                            champion_data["cost"] = int(cost_text)
                            print(f"비용: {champion_data['cost']}")
                        except ValueError:
                            print(f"비용 변환 실패: '{cost_text}'")
                
                # 특성 추출
                traits_label = primary_info.find('div', class_='label', string='특성')
                if traits_label:
                    traits_value_div = traits_label.find_next_sibling('div', class_='value')
                    if traits_value_div:
                        traits = [span.get_text(strip=True) for span in traits_value_div.find_all('span')]
                        champion_data["traits"] = traits
                        print(f"특성: {champion_data['traits']}")
                
                # 역할군 추출
                role_label = primary_info.find('div', class_='label', string='역할군')
                if role_label:
                    role_value = role_label.find_next_sibling('div', class_='value')
                    if role_value and role_value.find('span'):
                        champion_data["role"] = role_value.find('span').get_text(strip=True)
                        print(f"역할군: {champion_data['role']}")
            else:
                print("경고: primary-ifno 클래스를 찾을 수 없습니다.")
            
            # 3. 스탯 정보 추출
            stats_div = champion_info_wrapper.find('div', class_='css-ykyr23')
            if stats_div:
                print("css-ykyr23 스탯 컨테이너를 찾았습니다.")
                
                stats_map = {
                    '체력': 'health',
                    '공격력': 'attack_damage',
                    'DPS': 'dps',
                    '공격 사거리': 'attack_range',
                    '공격속도': 'attack_speed',
                    '방어력': 'armor',
                    '마법 저항력': 'magic_resistance'
                }
                
                for stat_div in stats_div.find_all('div', class_='css-2da5ti'):
                    label_tag = stat_div.find('div', class_='label')
                    value_tag = stat_div.find('div', class_='value')
                    
                    if label_tag and value_tag:
                        label = label_tag.get_text(strip=True)
                        if label in stats_map:
                            value = value_tag.get_text(strip=True)
                            
                            if label == '공격 사거리':
                                # 공격 사거리는 이미지이므로 특별 처리
                                img_tag = value_tag.find('img')
                                if img_tag and img_tag.has_attr('src'):
                                    src = img_tag['src']
                                    # src에서 숫자 추출 (예: ...attack_distance305.png → 5)
                                    import re
                                    match = re.search(r'attack_distance(\d+)\.png', src)
                                    if match:
                                        full_number = int(match.group(1))
                                        # 마지막 자리만 추출 (301→1, 305→5)
                                        last_digit = full_number % 10
                                        champion_data[stats_map[label]] = last_digit
                                    else:
                                        champion_data[stats_map[label]] = ''
                                else:
                                    champion_data[stats_map[label]] = value
                            
                            else:
                                champion_data[stats_map[label]] = value
                            
                            print(f"{label}: {champion_data[stats_map[label]]}")
            else:
                print("경고: css-ykyr23 클래스를 찾을 수 없습니다.")
            
            # 4. 스킬 정보 추출
            skill_figcaption = champion_info_wrapper.find('figcaption', class_='css-luahd8')
            if skill_figcaption:
                print("css-luahd8 스킬 figcaption을 찾았습니다.")
                
                # 스킬 이름 추출
                skill_name_tag = skill_figcaption.find('strong')
                if skill_name_tag:
                    champion_data["skill_name"] = skill_name_tag.get_text(strip=True)
                    print(f"스킬 이름: {champion_data['skill_name']}")
                
                # 스킬 설명 추출
                skill_description_tag = skill_figcaption.find('p', class_='skill-description')
                if skill_description_tag:
                    # <br> 태그를 줄 바꿈으로 변환하고 텍스트 추출
                    description = str(skill_description_tag).replace('<br/>', '\n').replace('<br>', '\n')
                    soup_desc = BeautifulSoup(description, 'html.parser')
                    champion_data["skill_description"] = soup_desc.get_text(strip=True)
                    print(f"스킬 설명 길이: {len(champion_data['skill_description'])}")
            else:
                print("경고: css-luahd8 클래스를 찾을 수 없습니다.")
            
            # 5. 페이지가 올바른 챔피언 페이지인지 확인
            if champion_data["name"] == "" or champion_data["name"] == "시즌 15 챔피언":
                print("경고: 올바른 챔피언 페이지가 아닙니다.")
                return None
            
            print(f"\n=== 최종 결과 ===")
            for key, value in champion_data.items():
                print(f"{key}: {value}")
            
            return champion_data
            
        except Exception as e:
            print(f"오류: {champion_name} 데이터 크롤링 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

async def main():
    """
    시즌별 챔피언 이름을 크롤링하고 모든 챔피언의 상세 데이터를 JSON 파일로 저장합니다.
    """
    print(f"=== TFT 시즌 {SEASON} 챔피언 목록 크롤러 ===")
    
    # 챔피언 이름 가져오기
    champion_names = await get_champion_names_from_season(SEASON)
    
    if champion_names:
        print(f"\n크롤링 완료!")
        print(f"총 {len(champion_names)}개의 챔피언을 찾았습니다.")
        
        # Python 리스트 형태로 출력 (코드에 바로 복사 가능)
        print(f"\nPython 리스트 형태:")
        print(f"champion_names = {champion_names}")
        
        # 모든 챔피언의 상세 데이터 가져오기
        all_champions_data = []
        
        for i, champion_name in enumerate(champion_names):
            print(f"\n=== {i+1}/{len(champion_names)}: {champion_name} 상세 데이터 크롤링 ===")
            
            # 챔피언 데이터 가져오기
            champion_data = await get_champion_data(SEASON, champion_name)
            
            if champion_data:
                # 챔피언 이름 추가
                champion_data["champion_name"] = champion_name
                champion_data["season"] = SEASON
                champion_data["url"] = f"https://lolchess.gg/champions/{SEASON}/{champion_name}"
                
                all_champions_data.append(champion_data)
                print(f"✅ {champion_name} 데이터 성공적으로 추출")
            else:
                print(f"❌ {champion_name} 데이터 추출 실패")
        
        # 전체 결과를 JSON 파일로 저장
        if all_champions_data:
            output_filename = f"tft_all_champions_{SEASON}.json"
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(all_champions_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n=== 크롤링 완료 ===")
            print(f"성공적으로 추출된 챔피언 수: {len(all_champions_data)}/{len(champion_names)}")
            print(f"결과가 '{output_filename}' 파일에 저장되었습니다.")
        else:
            print("추출된 데이터가 없습니다.")
        
        return champion_names
        
    else:
        print("챔피언을 찾을 수 없습니다.")
        return []

if __name__ == "__main__":
    # 챔피언 목록을 배열로 받기
    champion_names = asyncio.run(main())
    
    # 전체 챔피언 목록도 JSON 파일로 저장
    if champion_names:
        print(f"\n=== 테스트 설정 ===")
        print(f"시즌: {SEASON}")
        print(f"전체 챔피언 수: {len(champion_names)}")
        
        # 전체 챔피언 목록도 JSON 파일로 저장
        champion_list_filename = f"tft_champions_list_{SEASON}.json"
        champion_list_data = {
            "season": SEASON,
            "total_champions": len(champion_names),
            "champion_names": champion_names,
            "crawl_url": f"https://lolchess.gg/champions/{SEASON}/"
        }
        
        with open(champion_list_filename, 'w', encoding='utf-8') as f:
            json.dump(champion_list_data, f, ensure_ascii=False, indent=2)
        
        print(f"챔피언 목록이 '{champion_list_filename}' 파일에 저장되었습니다.")
        
    else:
        print("챔피언 목록을 가져올 수 없습니다.")