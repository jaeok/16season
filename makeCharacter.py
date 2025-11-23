import json

def transform_and_save_champion_data(input_file_path, output_file_path):
    """
    TFT 챔피언 JSON 파일에서 이름과 특성 정보만 추출하여 새로운 형식으로 변환하고,
    지정된 파일에 저장합니다.

    Args:
        input_file_path (str): 읽어올 JSON 파일의 경로.
        output_file_path (str): 변환된 데이터를 저장할 JSON 파일의 경로.
    """
    try:
        # 입력 파일 읽기
        with open(input_file_path, 'r', encoding='utf-8') as f:
            champion_data = json.load(f)
    except FileNotFoundError:
        print(f"오류: 입력 파일을 찾을 수 없습니다 - {input_file_path}")
        return
    except json.JSONDecodeError:
        print(f"오류: 입력 JSON 파일의 형식이 올바르지 않습니다. - {input_file_path}")
        return
    
    # 데이터 변환
    transformed_data = []
    for champion in champion_data:
        extracted_info = {
            "name": champion.get("name"),
            "traits": champion.get("traits", [])
        }
        transformed_data.append(extracted_info)
        
    output_dict = {"champions_and_traits": transformed_data}
    
    try:
        # 변환된 데이터를 출력 파일에 저장
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(output_dict, f, ensure_ascii=False, indent=2)
        print(f"성공적으로 데이터를 {output_file_path}에 저장했습니다.")
    except IOError:
        print(f"오류: 출력 파일을 쓰는 중 오류가 발생했습니다 - {output_file_path}")

# --- 사용 예시 ---
if __name__ == "__main__":
    # 이 스크립트를 실행하기 전에 'tft_all_champions_set15.txt' 파일에
    # JSON 데이터가 저장되어 있어야 합니다.
    input_file = "tft_all_champions_set15.txt"
    output_file = "tft_champion_traits.json"

    transform_and_save_champion_data(input_file, output_file)