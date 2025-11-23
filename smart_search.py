import json
from itertools import combinations
from collections import Counter, defaultdict
import time

def load_data():
    """Loads champion and synergy data from JSON files."""
    with open('tft_champion_traits.json', 'r', encoding='utf-8') as f:
        champions_data = json.load(f)["champions_and_traits"]
    with open('synergy_counts.json', 'r', encoding='utf-8') as f:
        synergy_counts = json.load(f)
    return champions_data, synergy_counts

def prepare_data(champions_data, synergy_counts):
    """Prepares data structures for efficient search."""
    # 챔피언별 특성 맵
    champ_to_traits = {champ['name']: champ['traits'] for champ in champions_data if champ.get('name')}

    # 특성별 챔피언 맵
    trait_to_champs = defaultdict(list)
    for champ_name, traits in champ_to_traits.items():
        for trait in traits:
            trait_to_champs[trait].append(champ_name)

    # 목표 시너지와 필요 카운트 맵
    target_synergies = {}
    for syn in synergy_counts:
        if syn.get("targetSynergy"):
            name = syn["synergy_name"]
            count = syn["count"]
            if name not in target_synergies or count > target_synergies[name]:
                target_synergies[name] = count

    return champ_to_traits, trait_to_champs, target_synergies

def solve_backtracking(team, requirements, available_champs, champ_to_traits, trait_to_champs, solutions):
    """
    Recursively finds combinations using a backtracking algorithm.
    """
    # 가지치기: 팀 크기가 9를 초과하면 더 이상 탐색하지 않음
    if len(team) > 9:
        return

    # 목표 달성: 모든 요구사항을 만족시킨 경우
    if not requirements:
        if 7 <= len(team) <= 9:
            # 중복된 조합 방지를 위해 정렬된 튜플을 사용
            solution_tuple = tuple(sorted(team))
            if solution_tuple not in solutions:
                solutions.add(solution_tuple)
                print(f"Found a valid team of size {len(team)}: {solution_tuple}")
        return

    # 가장 제약이 심한 요구사항부터 처리 (남은 챔피언으로 채우기 가장 어려운 시너지)
    # 휴리스틱: 남은 요구 카운트 대비 해당 특성을 가진 챔피언 수가 가장 적은 시너지
    most_constrained_req = min(requirements.items(),
                               key=lambda req: len([c for c in trait_to_champs[req[0]] if c in available_champs]) / req[1])

    req_name, req_count = most_constrained_req

    # 이 요구사항을 만족시킬 수 있는 후보 챔피언 목록
    candidate_champs = [c for c in trait_to_champs[req_name] if c in available_champs]

    # 후보 챔피언들을 하나씩 팀에 추가하며 탐색
    for champ_to_add in candidate_champs:
        new_team = team + [champ_to_add]
        new_available = available_champs - {champ_to_add}

        # 새로 추가된 챔피언의 특성을 반영하여 요구사항 업데이트
        new_requirements = requirements.copy()
        for trait in champ_to_traits[champ_to_add]:
            if trait in new_requirements:
                new_requirements[trait] -= 1
                if new_requirements[trait] <= 0:
                    del new_requirements[trait]

        solve_backtracking(new_team, new_requirements, new_available, champ_to_traits, trait_to_champs, solutions)


def main():
    start_time = time.time()

    champions_data, synergy_counts_data = load_data()
    champ_to_traits, trait_to_champs, target_synergies = prepare_data(champions_data, synergy_counts_data)

    all_champion_names = set(champ_to_traits.keys())

    golem_emblems_list = [
        "격투가 상징", "책략가 상징", "봉쇄자 상징", "저격수 상징", "프로레슬러 상징",
        "전투사관학교 상징", "처형자 상징", "악령 상징", "신동 상징", "헤비급 상징",
        "요새 상징", "별 수호자 상징", "소울 파이터 상징", "전쟁기계 상징", "이단아 상징",
        "슈프림 셀 상징", "마법사 상징", "수정 갬빗 상징"
    ]
    golem_synergies = [emblem.replace(" 상징", "") for emblem in golem_emblems_list]
    golem_emblem_combinations = list(combinations(golem_synergies, 3))

    print("Target Synergies to achieve:")
    print(target_synergies)

    all_solutions = set()
    total_golem_combos = len(golem_emblem_combinations)

    for i, golem_combo in enumerate(golem_emblem_combinations):
        print(f"\n[{i+1}/{total_golem_combos}] Testing Golem Emblems: {golem_combo}")

        # 골렘 시너지를 반영한 초기 요구사항 설정
        initial_requirements = target_synergies.copy()
        golem_contribution = Counter(golem_combo)

        for trait, count in golem_contribution.items():
            if trait in initial_requirements:
                initial_requirements[trait] -= count
                if initial_requirements[trait] <= 0:
                    del initial_requirements[trait]

        if not initial_requirements:
            print("Golem emblems alone satisfy all requirements. No champions needed (not a valid team).")
            continue

        found_solutions_for_golem_combo = set()
        solve_backtracking([], initial_requirements, all_champion_names, champ_to_traits, trait_to_champs, found_solutions_for_golem_combo)

        if found_solutions_for_golem_combo:
            all_solutions.update(found_solutions_for_golem_combo)

    # 결과 저장
    output_filename = "smart_search_results.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(f"Found {len(all_solutions)} unique team combinations.\n")
        f.write(f"Target Synergies: {target_synergies}\n\n")

        # 크기별로 정렬
        sorted_solutions = sorted(list(all_solutions), key=len)

        for solution in sorted_solutions:
            f.write(f"Team Size: {len(solution)}\n")
            f.write(f"  Champions: {', '.join(solution)}\n\n")

    end_time = time.time()
    print(f"\n--- Search complete in {end_time - start_time:.2f} seconds ---")
    print(f"Found {len(all_solutions)} unique combinations. Results saved to {output_filename}")

if __name__ == "__main__":
    main()
