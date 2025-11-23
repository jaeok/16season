import json
import re

def parse_team_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    teams = {}
    # Split the content by "--- 조합" to process each team block
    team_blocks = re.split(r'--- 조합 \d+ ---', content)

    for i, block in enumerate(team_blocks):
        if not block.strip():
            continue

        champions = []
        synergies = []

        # Extract champions
        champ_match = re.search(r'🏆 챔피언: (.*)', block)
        if champ_match:
            champions = [name.strip() for name in champ_match.group(1).split(',')]

        # Extract synergies
        synergy_section_match = re.search(r'✨ 활성 시너지:\n((?:  - .*\n?)*)', block)
        if synergy_section_match:
            synergy_lines = synergy_section_match.group(1).strip().split('\n')
            for line in synergy_lines:
                synergy_match = re.search(r'- ([\w\s]+) \(\d+\)', line)
                if synergy_match:
                    synergies.append(synergy_match.group(1).strip())

        if champions and synergies:
            team_name = f"AI 추천 팀 {i}"
            teams[team_name] = {
                "champions": sorted(champions),
                "synergies": sorted(synergies)
            }

    return teams

def main():
    teams_data = parse_team_data('result.txt')

    if teams_data:
        # The server expects a list of objects, not a dictionary.
        # Let's reformat.
        formatted_teams = []
        for team_name, details in teams_data.items():
             # The server code seems to expect a list of champion names, not objects
            formatted_teams.append({
                "name": team_name,
                "champions": details["champions"],
                "synergies": details["synergies"]
            })

        with open('final_team_compositions.json', 'w', encoding='utf-8') as f:
            json.dump(formatted_teams, f, ensure_ascii=False, indent=4)

        print(f"Successfully parsed {len(formatted_teams)} teams and saved to final_team_compositions.json")
    else:
        print("No teams were parsed from result.txt")

if __name__ == '__main__':
    main()
