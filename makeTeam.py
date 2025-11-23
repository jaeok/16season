import json
import itertools
from collections import defaultdict
import time
import math
import multiprocessing
import sys
# TQDM 라이브러리를 시도하고, 없으면 플래그를 설정
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# --------------------------------------------------------------------------
# 1. 일꾼(Worker) 프로세스를 위한 초기화 함수 및 작업 함수 정의
# --------------------------------------------------------------------------

def init_worker(champ_data_arg, synergy_tiers_arg):
    """
    각 일꾼 프로세스가 생성될 때 한 번만 실행되는 초기화 함수.
    메인 프로세스로부터 받은 데이터를 각 일꾼의 전역 변수로 설정합니다.
    """
    global champion_data, synergy_tiers
    champion_data = champ_data_arg
    synergy_tiers = synergy_tiers_arg

def check_team_validity(team):
    """
    팀의 모든 시너지가 '낭비 없이' 활성화 상태인지 검사하는 함수.
    하나라도 비활성/낭비되는 시너지가 있으면 None을 반환하고,
    모두 완벽하게 활성화 상태면 (팀, 시너지 정보)를 반환합니다.
    """
    current_synergy_counts = defaultdict(int)
    for champion in team:
        for trait in champion_data[champion]:
            current_synergy_counts[trait] += 1
    
    # 팀에 포함된 모든 시너지가 활성화 조건에 정확히 맞는지 확인
    for synergy_name, count in current_synergy_counts.items():
        # 해당 시너지의 활성화 단계 목록(Set)을 가져옴
        activation_levels = synergy_tiers.get(synergy_name)
        
        # 활성화 단계 목록이 없거나, 현재 인원수가 활성화 단계 목록에 포함되지 않으면 무효 조합
        if not activation_levels or count not in activation_levels:
            return None  # 비활성/낭비 시너지가 있으므로 이 조합은 탈락

    # 모든 검사를 통과했다면 유효한 조합이므로 결과 반환
    return team, current_synergy_counts

# --------------------------------------------------------------------------
# 2. 메인 로직 함수 정의
# --------------------------------------------------------------------------

def find_fully_activated_teams(champions, synergies, team_size):
    """
    비활성/낭비되는 시너지가 없는 모든 팀 조합 목록을 찾습니다.
    """
    # 메인 프로세스에서만 데이터를 지역 변수로 로드합니다.
    local_champion_data = {champ['name']: champ['traits'] for champ in champions if 'name' in champ and 'traits' in champ}
    
    # 시너지 티어를 Set으로 저장하여 'in' 연산 속도를 높입니다.
    local_synergy_tiers = defaultdict(set)
    for synergy in synergies:
        if 'synergy_name' in synergy and 'count' in synergy:
            local_synergy_tiers[synergy['synergy_name']].add(synergy['count'])

    all_champions = list(local_champion_data.keys())

    # 조합 수 계산
    try:
        total_combinations = math.comb(len(all_champions), team_size)
    except ValueError:
        print(f"오류: 팀 크기({team_size})가 전체 챔피언 수({len(all_champions)})보다 클 수 없습니다.")
        return

    # --- 기본 정보 출력 ---
    num_cores = multiprocessing.cpu_count()
    print(f"총 {len(all_champions)}명의 챔피언, {team_size}인 팀 조합: {total_combinations:,}개")
    print(f"컴퓨터의 {num_cores}개 코어를 모두 사용하여 '낭비 없는 시너지 조합'을 탐색합니다.")
    if team_size > 6:
        print("경고: 팀 규모가 7 이상이면 계산에 매우 오랜 시간이 소요될 수 있습니다.")

    # --- 파일 설정 및 멀티프로세싱 시작 ---
    start_time = time.time()
    valid_team_count = 0
    output_filename = f'ai_team_compositions_size_{team_size}.jsonl'
    print(f"\n결과를 '{output_filename}' 파일에 실시간으로 저장합니다.")

    try:
        with open(output_filename, 'w', encoding='utf-8') as f_out:
            with multiprocessing.Pool(processes=num_cores, initializer=init_worker, initargs=(local_champion_data, local_synergy_tiers)) as pool:
                # --- Chunksize 설정 ---
                # 작업을 적절한 크기의 묶음으로 보내 통신 오버헤드를 줄입니다.
                # 매우 큰 작업량의 경우 동적 계산이 오히려 메인 프로세스를 정지시킬 수 있으므로 고정값을 사용합니다.
                chunksize = 10000
                print(f"병렬 처리 효율을 위해 작업을 {chunksize:,}개씩 묶어서 처리합니다.")

                results_iterator = pool.imap_unordered(check_team_validity, itertools.combinations(all_champions, team_size), chunksize=chunksize)

                # --- tqdm 라이브러리 유무에 따른 메인 루프 분기 ---
                if TQDM_AVAILABLE:
                    print("tqdm 라이브러리를 사용하여 진행률을 표시합니다.")
                    pbar = tqdm(results_iterator, total=total_combinations, desc="조합 탐색 중")
                    for result in pbar:
                        if result:
                            valid_team_count += 1
                            team, synergies_dict = result
                            output_dict = {
                                "champions": sorted(list(team)),
                                "synergies": {s: c for s, c in sorted(synergies_dict.items())}
                            }
                            f_out.write(json.dumps(output_dict, ensure_ascii=False) + '\n')
                else:
                    print("tqdm 라이브러리를 찾을 수 없습니다. 진행 상황을 maketeam_progress.log 파일에 기록합니다.")
                    processed_count = 0
                    with open('maketeam_progress.log', 'a', encoding='utf-8') as log_file:
                        log_file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 탐색 시작. 총 조합 수: {total_combinations:,}\n")
                        for result in results_iterator:
                            processed_count += 1
                            # 1억개 마다 로그 기록
                            if processed_count > 0 and processed_count % 100000000 == 0:
                                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                                percentage = processed_count / total_combinations
                                log_message = f"[{timestamp}] {processed_count:,} / {total_combinations:,} 조합 확인됨 ({percentage:.2%})\n"
                                log_file.write(log_message)
                                log_file.flush()

                            if result:
                                valid_team_count += 1
                                team, synergies_dict = result
                                output_dict = {
                                    "champions": sorted(list(team)),
                                    "synergies": {s: c for s, c in sorted(synergies_dict.items())}
                                }
                                f_out.write(json.dumps(output_dict, ensure_ascii=False) + '\n')

    except Exception as e:
        print(f"\n오류 발생: 처리 중 예외가 발생했습니다 - {e}")
        return

    end_time = time.time()

    # --- 최종 결과 출력 ---
    print("\n" + "="*50)
    print("탐색 완료!")
    print(f"총 탐색 시간: {end_time - start_time:.2f}초")
    print(f"총 {valid_team_count:,}개의 '낭비 없는 시너지 조합'을 찾았습니다.")
    print(f"결과는 '{output_filename}'에 안전하게 저장되었습니다.")
    print("="*50)

# --------------------------------------------------------------------------
# 4. 스크립트 실행 지점
# --------------------------------------------------------------------------

def main():
    """
    메인 실행 함수: 데이터 로드, 사용자 입력 처리 및 조합 탐색 실행
    """
    # --- 데이터 파일 경로 설정 ---
    CHAMPIONS_FILE = 'tft_all_champions_set15.json'
    SYNERGIES_FILE = 'synergy_counts.json'

    # --- 데이터 로드 ---
    try:
        with open(CHAMPIONS_FILE, 'r', encoding='utf-8') as f:
            champions_data = json.load(f)

        with open(SYNERGIES_FILE, 'r', encoding='utf-8') as f:
            synergies_data = json.load(f)

    except FileNotFoundError as e:
        print(f"오류: 데이터 파일을 찾을 수 없습니다. '{e.filename}'")
        print("스크립트를 실행하기 전에 필요한 데이터 파일이 모두 있는지 확인하세요.")
        return
    except json.JSONDecodeError as e:
        print(f"오류: JSON 데이터 파일을 파싱하는 중 오류가 발생했습니다 - {e}")
        return

    # --- 팀 규모 설정 ---
    if len(sys.argv) > 1:
        try:
            team_size = int(sys.argv[1])
            if team_size <= 0:
                raise ValueError
        except ValueError:
            print("오류: 팀 규모는 0보다 큰 정수여야 합니다.")
            print("사용법: python makeTeam.py [팀 규모]")
            return
    else:
        team_size = 8
        print("정보: 팀 규모가 지정되지 않았습니다. 기본값인 8로 설정합니다.")
        print("      이 작업은 매우 오래 걸릴 수 있습니다. 다른 숫자를 지정하려면,")
        print("      'python makeTeam.py 6'과 같이 실행하세요.")

    find_fully_activated_teams(champions_data, synergies_data, team_size)


# 스크립트가 직접 실행될 때만 아래 코드가 동작하도록 보장합니다.
# 멀티프로세싱을 위해 반드시 필요한 구조입니다.
if __name__ == '__main__':
    # 멀티프로세싱 시작 방식을 'fork'로 설정 (macOS 및 Linux에서 안정적)
    # 'spawn'이 기본값인 OS(Windows, macOS 최신 버전)에서 발생할 수 있는 문제를 예방합니다.
    if sys.platform.startswith('darwin') or sys.platform.startswith('win32'):
         multiprocessing.set_start_method('spawn', force=True)
    main()