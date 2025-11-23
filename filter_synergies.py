import json

def get_target_synergies(synergy_counts_file):
    """
    Reads the synergy_counts.json file and returns a list of target synergy dictionaries.
    """
    with open(synergy_counts_file, 'r', encoding='utf-8') as f:
        synergy_counts = json.load(f)

    target_synergies_list = []
    for synergy in synergy_counts:
        if synergy.get('targetSynergy'):
            # Create a dictionary for each target synergy combination
            target_synergies_list.append({synergy['synergy_name']: synergy['count']})

    # The above is not quite right. A team can have multiple synergies.
    # The problem is to find a team that has ALL the target synergies.
    # Let's rebuild the target synergy dictionary correctly.

    target_synergies = {}
    for synergy in synergy_counts:
        if synergy.get('targetSynergy'):
            name = synergy['synergy_name']
            count = synergy['count']
            if name not in target_synergies or count > target_synergies[name]:
                target_synergies[name] = count

    # The user request is to find teams that match the synergy and count.
    # It does not say that a team should have ALL target synergies.
    # It says "check if its synergies match the target synergies and their counts."
    # Let's assume this means that any team that has *any* of the target synergies with the correct count is a match.
    # This is a bit ambiguous. Let's try a different interpretation.
    # "synergy_counts.json 파일의 targetSynerge true 인 시너지와 카운트가 일치하는 팀을 찾아서 파일로 저장해줘"
    # This means "Find teams where the synergy and count match a synergy with targetSynergy:true in the synergy_counts.json file and save it to a file."

    # This implies that if a team has a synergy "별 수호자: 8" and this exists in the synergy_counts.json with targetSynergy: true, then it's a match.
    # The logic in the previous script was too strict. Let's create a set of tuples for faster lookup.

    targets = set()
    for synergy in synergy_counts:
        if synergy.get('targetSynergy'):
            targets.add((synergy['synergy_name'], synergy['count']))
    return targets


def filter_compositions_by_synergy(input_file, output_file, target_synergies):
    """
    Filters team compositions from an input file based on synergy match and saves them to an output file.
    """
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'a', encoding='utf-8') as outfile:
        for line in infile:
            try:
                composition = json.loads(line.strip())
                synergies = composition.get("synergies", {})

                # Check if any of the team's synergies match any of the target synergies
                for synergy_name, synergy_count in synergies.items():
                    if (synergy_name, synergy_count) in target_synergies:
                        outfile.write(line.strip() + '\n')
                        break # Move to the next composition once a match is found
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line in {input_file}: {line.strip()}")

def main():
    """
    Main function to execute the filtering process.
    """
    synergy_counts_file = "synergy_counts.json"
    target_synergies = get_target_synergies(synergy_counts_file)

    input_files = [
        "ai_team_compositions_size_6.jsonl",
        "ai_team_compositions_size_7.jsonl",
        "ai_team_compositions_size_8.jsonl",
        "ai_team_compositions_size_9.jsonl"
    ]

    output_file = "filtered_compositions_by_synergy.jsonl"

    # Clear the output file before starting
    with open(output_file, 'w', encoding='utf-8') as f:
        pass

    for input_file in input_files:
        print(f"Processing {input_file} -> {output_file}")
        filter_compositions_by_synergy(input_file, output_file, target_synergies)
        print(f"Finished processing {input_file}")

if __name__ == "__main__":
    main()
