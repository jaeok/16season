import os
import requests 
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def download_all_item_images_selenium(url, save_path):
    """
    lolchess.gg 페이지에서 모든 아이템의 이미지를 찾아 지정된 경로에 저장합니다.
    파일명은 '_숫자' 같은 부분을 제거하고 저장합니다.
    """
    print("lolchess.gg 모든 아이템 이미지 스크래핑 및 다운로드 시작...")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu') 
    chrome_options.add_argument('--disable-dev-shm-usage') 
    chrome_options.add_argument('--ignore-certificate-errors') 
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(url)
        print(f"'{url}' 페이지 로딩 중...")
        
        wait = WebDriverWait(driver, 20) 
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.css-1vrtnye tbody')))
        print("페이지 로딩 완료. HTML 파싱 시작...")

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        item_rows = soup.select('table.css-1vrtnye tbody tr')
        
        if not item_rows:
            print("오류: 페이지에서 아이템 목록을 찾을 수 없습니다. HTML 구조가 다시 변경되었을 수 있습니다.")
            return

        print(f"총 {len(item_rows)}개의 아이템을 발견했습니다. 다운로드를 시작합니다.")
        
        os.makedirs(save_path, exist_ok=True)

        for index, row in enumerate(item_rows):
            img_tag = row.select_one('img.ItemPortrait')
            
            if not img_tag:
                print(f"{index+1}번째 아이템에서 이미지 태그를 찾을 수 없습니다. 건너뜁니다.")
                continue

            img_src = img_tag.get('src')
            if not img_src:
                print(f"{index+1}번째 아이템의 src 속성을 찾을 수 없습니다. 건너뜁니다.")
                continue

            full_img_url = urljoin(url, img_src)
            
            # 파일명 추출 및 저장 경로 설정
            # 1. URL에서 파일명만 가져오고, 쿼리 파라미터는 제거합니다.
            raw_file_name = full_img_url.split('/')[-1].split('?')[0]
            
            # 2. 파일명에서 확장자를 분리합니다.
            base_name, file_extension = os.path.splitext(raw_file_name)
            
            # 3. 파일명에 '_'가 있으면 첫 번째 '_'까지만 사용합니다.
            if '_' in base_name:
                cleaned_name = base_name.split('_')[0]
            else:
                cleaned_name = base_name
            
            # 4. 정리된 파일명과 확장자를 다시 결합합니다.
            file_name = f"{cleaned_name}{file_extension}"
            
            full_save_path = os.path.join(save_path, file_name)

            # 이미지 다운로드
            try:
                img_response = requests.get(full_img_url, stream=True)
                img_response.raise_for_status()
                with open(full_save_path, 'wb') as f:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"{index+1}/{len(item_rows)} 다운로드 완료: {file_name}")
            except Exception as e:
                print(f"{index+1}번째 이미지 다운로드 실패 ({full_img_url}): {e}")

    except Exception as e:
        print(f"Selenium 작업 중 오류가 발생했습니다: {e}")
    finally:
        if driver:
            driver.quit() 

    print("\n모든 아이템 다운로드가 완료되었습니다.")

# 실행 설정
url = "https://lolchess.gg/items/set16"
from config import PROJECT_ROOT, ITEM_ICON_DIR

save_directory = ITEM_ICON_DIR

if __name__ == "__main__":
    download_all_item_images_selenium(url, save_directory)