import json
import glob

def load_synergy_levels(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_synergy(synergy_name, synergy_level, required_synergies):
    if synergy_name in required_synergies:
        required_level = required_synergies[synergy_name]
        if isinstance(required_level, list):
            return synergy_level in required_level
        else:
            return synergy_level == required_level
    return False

def process_composition_files(synergy_levels):
    files_to_process = glob.glob('ai_team_compositions_size_*.jsonl')

    gold_synergies = synergy_levels.get('골드', {})
    prism_synergies = synergy_levels.get('프리즘', {})

    for input_filepath in files_to_process:
        output_filepath = f"filtered_{input_filepath}"
        print(f"Processing {input_filepath} -> {output_filepath}")

        with open(input_filepath, 'r', encoding='utf-8') as infile, \
             open(output_filepath, 'w', encoding='utf-8') as outfile:

            for line in infile:
                try:
                    composition = json.loads(line)
                    synergies = composition.get('synergies', {})

                    is_synergy_met = False
                    for name, level in synergies.items():
                        if check_synergy(name, level, gold_synergies) or \
                           check_synergy(name, level, prism_synergies):
                            is_synergy_met = True
                            break

                    if is_synergy_met:
                        outfile.write(line)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line in {input_filepath}: {line.strip()}")

def main():
    synergy_levels = load_synergy_levels('synergy_level.json')
    process_composition_files(synergy_levels)
    print("File processing complete.")

if __name__ == "__main__":
    main()
