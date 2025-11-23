import json
import re

def get_champion_name_map():
    """Creates a mapping from Korean to English champion names."""
    try:
        with open('tft_all_champions_set15.json', 'r', encoding='utf-8') as f:
            champions = json.load(f)
        name_map = {champion['name']: champion['champion_name'] for champion in champions}
        return name_map
    except FileNotFoundError:
        print("Error: tft_all_champions_set15.json not found.")
        return {}

def parse_rank(rank_str):
    """Parses the numeric value from an avg_rank string like '#3.65'."""
    match = re.search(r'\d+\.\d+', rank_str)
    if match:
        return float(match.group())
    return float('inf') # Return infinity if parsing fails, so it won't be chosen as the best rank

def main():
    # Load all necessary data
    try:
        with open('champion_item_stats.json', 'r', encoding='utf-8') as f:
            top2_data = json.load(f)
        with open('three_core_items.json', 'r', encoding='utf-8') as f:
            best_rank_data_kr = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Could not open a required data file: {e}")
        return

    name_map = get_champion_name_map()
    if not name_map:
        return

    final_data = {}

    # Iterate through champions in the base file (champion_item_stats.json)
    for eng_name, builds in top2_data.items():
        if not eng_name:
            continue

        # 1. Get the top 2 builds
        final_builds = builds[:2]

        # Find the corresponding Korean name to look up in the other file
        kor_name = next((k for k, v in name_map.items() if v == eng_name), None)

        if kor_name and kor_name in best_rank_data_kr:
            best_rank_builds = best_rank_data_kr[kor_name]

            if best_rank_builds:
                # 2. Find the build with the best (lowest) avg_rank
                best_build = min(best_rank_builds, key=lambda x: parse_rank(x.get('avg_rank', '#inf')))

                # 3. Add it to our list with win_rate = 100
                best_build_formatted = {
                    "items": best_build.get("items", []),
                    "win_rate": 100
                }

                # Avoid adding a duplicate build
                is_duplicate = False
                for existing_build in final_builds:
                    if set(existing_build.get("items", [])) == set(best_build_formatted["items"]):
                        is_duplicate = True
                        break

                if not is_duplicate:
                    final_builds.append(best_build_formatted)

        final_data[eng_name] = final_builds

    # Save the final combined data
    with open('champion_item_stat2.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print("Processing complete. champion_item_stat2.json has been created.")

if __name__ == '__main__':
    main()
