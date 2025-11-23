# -*- coding: utf-8 -*-
import json
from collections import defaultdict
import sys

# --- 데이터 로딩 ---

def load_data_from_json():
    """
    JSON 파일에서 챔피언 및 특성 데이터를 로드합니다.
    """
    try:
        with open('synergy_counts.json', 'r', encoding='utf-8') as f:
            synergy_data = json.load(f)

        with open('tft_champion_traits.json', 'r', encoding='utf-8') as f:
            champion_data = json.load(f)

    except FileNotFoundError as e:
        print(f"오류: 데이터 파일 '{e.filename}'을 찾을 수 없습니다. 스크립트와 같은 디렉토리에 있는지 확인하세요.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("오류: JSON 파일의 형식이 잘못되었습니다. 파일 내용을 확인하세요.")
        sys.exit(1)

    # TRAIT_THRESHOLDS 생성
    trait_thresholds_builder = defaultdict(list)
    for synergy in synergy_data:
        trait_thresholds_builder[synergy['synergy_name']].append(synergy['count'])

    trait_thresholds = {name: sorted(counts) for name, counts in trait_thresholds_builder.items()}

    # CHAMPIONS 생성
    champions = {item['name']: item['traits'] for item in champion_data['champions_and_traits']}

    return champions, trait_thresholds

# 데이터 로드 실행
CHAMPIONS, TRAIT_THRESHOLDS = load_data_from_json()
ALL_CHAMPION_NAMES = sorted(list(CHAMPIONS.keys()))
UNIQUE_TRAITS = {trait for trait, thresholds in TRAIT_THRESHOLDS.items() if thresholds == [1]}


# --- 알고리즘 (재귀 + 최적화) ---

def find_optimal_compositions_recursive(team, start_index, emblems, team_size, results):
    """
    재귀적으로 팀 조합을 탐색하는 함수
    """
    # 최적화(Pruning)
    remaining_slots = team_size - len(team)

    current_traits = defaultdict(int)
    for champ in team:
        for trait in CHAMPIONS[champ]:
            current_traits[trait] += 1

    wasted_traits_count = 0
    for trait, count in current_traits.items():
        if trait in UNIQUE_TRAITS or trait in emblems:
            continue
        if trait in TRAIT_THRESHOLDS:
            min_req = TRAIT_THRESHOLDS[trait][0]
            if 0 < count < min_req:
                # 낭비 특성을 완성하려면 최소 (min_req - count)명의 챔피언이 더 필요함
                # 여기서는 간단히 1로 계산하여, 낭비 특성 수만 카운트
                wasted_traits_count += 1

    if wasted_traits_count > remaining_slots:
        return

    # Base Case: 팀 구성 완료
    if len(team) == team_size:
        trait_counts = defaultdict(int)
        for champ_name in team:
            for trait in CHAMPIONS[champ_name]:
                trait_counts[trait] += 1

        for emblem in emblems:
            trait_counts[emblem] += 1

        is_wasted = False
        for trait, count in trait_counts.items():
            if trait in UNIQUE_TRAITS:
                continue
            if trait in TRAIT_THRESHOLDS:
                min_req = TRAIT_THRESHOLDS[trait][0]
                if 0 < count < min_req:
                    is_wasted = True
                    break

        if not is_wasted:
            results.append({'team': sorted(team), 'traits': dict(trait_counts)})
            print(f"\r조합 발견! 현재까지 {len(results)}개. 계속 탐색 중...", end="")
        return

    # Recursive Step
    if len(team) < team_size:
        for i in range(start_index, len(ALL_CHAMPION_NAMES)):
            team.append(ALL_CHAMPION_NAMES[i])
            find_optimal_compositions_recursive(team, i + 1, emblems, team_size, results)
            team.pop() # Backtrack

def print_results(results):
    print("\n" + "="*40)
    if not results:
        print("조건을 만족하는 조합을 찾지 못했습니다.")
        print("팁: 챔피언 목록이나 징표를 변경해보세요.")
        return

    print(f"탐색 완료! 총 {len(results)}개의 시너지 낭비 없는 조합을 찾았습니다:\n")

    for i, comp in enumerate(results, 1):
        print(f"--- 조합 {i} ---")
        print(f"챔피언: {', '.join(comp['team'])}")

        active_synergies = []
        for trait, count in sorted(comp['traits'].items()):
            if trait not in TRAIT_THRESHOLDS: continue

            active_level = 0
            for threshold in TRAIT_THRESHOLDS[trait]:
                if count >= threshold:
                    active_level = threshold

            if active_level > 0:
                active_synergies.append(f"{trait}({active_level})")

        print(f"활성 시너지: {', '.join(active_synergies)}")
        print("-" * (13 + len(str(i))))
        print()

# --- 실행 ---
if __name__ == "__main__":
    # 사용자 요청에 따라 징표 목록을 한국어 특성 이름으로 설정
    my_emblems = ['슈프림 셀', '마법사', '수정 갬빗']
    team_size = 8

    print("최적의 조합 탐색을 시작합니다 (JSON 데이터 로드)...")
    print(f"조건: 챔피언 {team_size}명, 징표: {', '.join(my_emblems)}, 시너지 낭비 없음")
    print("-" * 30)

    found_compositions = []
    try:
        find_optimal_compositions_recursive([], 0, my_emblems, team_size, found_compositions)
    except KeyboardInterrupt:
        print("\n사용자에 의해 탐색이 중단되었습니다.")

    print_results(found_compositions)
