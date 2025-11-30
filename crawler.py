import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('https://mobalytics.gg/tft/new-set-release')

        await page.wait_for_selector('h2:has-text("New Game Mechanic: Unlockables")')

        html = await page.content()
        await browser.close()

        soup = BeautifulSoup(html, 'html.parser')
        data = {}

        # --- New Game Mechanic: Unlockables ---
        unlockables_section = soup.find('h2', string='New Game Mechanic: Unlockables')
        if unlockables_section:
            data['unlockables'] = []
            table = unlockables_section.find_next('div', class_='m-1wr8x8q')
            if table:
                rows = table.find_all('div', class_='m-p2fgxx')
                for row in rows:
                    champion_name_tag = row.find('span', class_='m-12wal98')
                    cost_tag = row.find('span', class_='m-7wdacc')
                    unlock_condition_tag = row.find('div', class_='m-ro9z7e')

                    if champion_name_tag and cost_tag and unlock_condition_tag:
                        data['unlockables'].append({
                            'champion_name': champion_name_tag.text.strip(),
                            'cost': cost_tag.text.strip(),
                            'unlock_condition': unlock_condition_tag.text.strip()
                        })

        # --- New Set 16 Augments ---
        augments_section = soup.find('h2', string='New Set 16 Augments')
        if augments_section:
            data['augments'] = []
            table = augments_section.find_next('div', class_='m-101th0h')
            if table:
                rows = table.find_all('div', class_='m-1uum3g8')
                for row in rows:
                    augment_name_tag = row.find('span', class_='m-25fahk')
                    tier_tag = row.find('span', class_='m-15cwj9k')
                    augment_bonus_tag = row.find('p', class_='m-1vrrnd3')

                    if augment_name_tag and tier_tag and augment_bonus_tag:
                        data['augments'].append({
                            'augment_name': augment_name_tag.text.strip(),
                            'tier': tier_tag.text.strip(),
                            'augment_bonus': augment_bonus_tag.text.strip()
                        })

        # --- New Set 16 Traits ---
        traits_section = soup.find('h2', string='New Set 16 Traits')
        if traits_section:
            data['traits'] = []
            # Find all trait cards that follow the "Traits" header
            trait_cards = traits_section.find_all_next('div', class_='m-j93hpe')
            for card in trait_cards:
                # This is a bit tricky as Champions and Team Comps also use this class.
                # We'll check for a trait-specific element to ensure we are in the right section.
                trait_name_tag = card.find('p', class_='ehr3ysz0')
                if not trait_name_tag:
                    # If this card doesn't have a trait name, it's probably from another section, so we stop.
                    break

                trait_name = trait_name_tag.find('span').text.strip()
                description_tag = card.find('div', class_='m-2ma9g8')
                description = description_tag.text.strip() if description_tag else ""

                bonuses = []
                bonus_section = card.find('div', class_='m-41gsnl')
                if bonus_section:
                    for bonus in bonus_section.find_all('div', class_='m-yeouz0'):
                        needed_tag = bonus.find('p', class_='m-24mlye')
                        effect_tag = bonus.find('p', class_='m-1be4f1o')
                        if needed_tag and effect_tag:
                            bonuses.append({'needed': needed_tag.text.strip(), 'effect': effect_tag.text.strip()})

                champions = []
                champion_section = card.find('div', class_='m-1szfm7t')
                if champion_section:
                    for champion in champion_section.find_all('a', class_='m-1mnuv8o'):
                        champ_name_tag = champion.find('div', class_='m-fdk2wo')
                        if champ_name_tag:
                            champions.append(champ_name_tag.text.strip())

                data['traits'].append({
                    'trait_name': trait_name,
                    'description': description,
                    'bonuses': bonuses,
                    'champions': champions
                })

        # --- New Set 16 Champions ---
        champions_section_header = soup.find('h2', string='New Set 16 Champions')
        if champions_section_header:
            data['champions'] = []
            champions_grid = champions_section_header.find_next('div', class_='m-m03a3y')
            if champions_grid:
                champion_cards = champions_grid.find_all('a', class_='m-1s3cvie')
                for card in champion_cards:
                    name_tag = card.find('span', class_='m-1xvjosc')
                    cost_tag = card.find('div', class_='m-s5xdrg')
                    ability_name_tag = card.find('p', class_='m-1rhbarm')
                    ability_desc_tag = card.find('div', class_='m-2ma9g8')

                    name = name_tag.text.strip() if name_tag else "Unknown"
                    cost = cost_tag.text.strip() if cost_tag else "Unknown"
                    ability_name = ability_name_tag.text.strip() if ability_name_tag else "Unknown"
                    ability_desc = ability_desc_tag.text.strip() if ability_desc_tag else "Unknown"

                    stats = []
                    stats_section = card.find_all('div', class_='m-bcffy2')
                    for stat in stats_section:
                        stat_name_tag = stat.find('p', class_='m-u8mwkb')
                        stat_value_tag = stat.find('p', class_='m-vgzzr8')
                        if stat_name_tag and stat_value_tag:
                            stats.append({stat_name_tag.text.strip(): stat_value_tag.text.strip()})

                    data['champions'].append({
                        'name': name,
                        'cost': cost,
                        'ability_name': ability_name,
                        'ability_description': ability_desc,
                        'ability_stats': stats
                    })

        # --- New Set 16 Team Comps ---
        team_comps_section = soup.find('h2', string='New Set 16 Team Comps')
        if team_comps_section:
            data['team_comps'] = []
            comp_cards = team_comps_section.find_all_next('div', class_='m-1hi5yi4')
            for card in comp_cards:
                name_tag = card.find('a', class_='m-vt6jeq')
                if not name_tag or not name_tag.find('span'): continue

                name = name_tag.find('span').text.strip()
                playstyle_tags = card.find_all('div', class_='m-ttncf1')
                playstyle = [p.text.strip() for p in playstyle_tags]
                difficulty_tag = card.find('div', class_='m-1mzrjt7')
                difficulty = difficulty_tag.text.strip() if difficulty_tag else ""

                champions = []
                champion_section = card.find('div', class_='m-1n86dvu')
                if not champion_section:
                    champion_section = card.find('div', class_='m-j4g3c0')

                if champion_section:
                    for champion in champion_section.find_all('a', class_='m-1pjvpo5'):
                        champ_name_tag = champion.find('div', class_='m-fdk2wo')
                        if champ_name_tag:
                            champions.append(champ_name_tag.text.strip())

                if name and champions: # Only add if we have a name and some champions
                    data['team_comps'].append({
                        'name': name,
                        'playstyle': playstyle,
                        'difficulty': difficulty,
                        'champions': champions
                    })

        with open('final_json_data.txt', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    asyncio.run(main())
