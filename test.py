import json
import glob

synergy_counts_path = "synergy_counts.json"
input_files = [
    "ai_team_compositions_size_6.jsonl",
    "ai_team_compositions_size_7.jsonl",
    "ai_team_compositions_size_8.jsonl",
    "ai_team_compositions_size_9.jsonl",
]
output_path = "filtered_compositions_all.jsonl"

# targetSynergy=True인 시너지 (이름, count) 세트
with open(synergy_counts_path, "r", encoding="utf-8") as f:
    synergy_data = json.load(f)
target_synergies = {(s["synergy_name"], s["count"]) for s in synergy_data if s["targetSynergy"]}

filtered_compositions = []

# 여러 파일에서 읽기
for file in input_files:
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            comp = json.loads(line)
            comp_synergies = {(name, count) for name, count in comp.get("synergies", {}).items()}
            if target_synergies & comp_synergies:  # 교집합 있으면 추가
                comp["source_file"] = file  # 원본 파일 정보 추가 (선택)
                filtered_compositions.append(comp)

# 결과 저장
with open(output_path, "w", encoding="utf-8") as f:
    for comp in filtered_compositions:
        f.write(json.dumps(comp, ensure_ascii=False) + "\n")

print(f"필터링된 조합 저장 완료: {output_path}")
