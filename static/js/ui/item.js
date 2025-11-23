// --- UI Module: Items ---

import { state } from '../state.js';
import { fetchItemRecommendations } from '../api.js';

export async function displayItemRecommendations(championName, container, max_sets = 3) {
    if (state.itemRecsCache.has(championName)) {
        renderItemIcons(state.itemRecsCache.get(championName), container, max_sets);
        return;
    }
    try {
        const recs = await fetchItemRecommendations(championName);
        state.itemRecsCache.set(championName, recs);
        renderItemIcons(recs, container, max_sets);
    } catch (e) {
        state.itemRecsCache.set(championName, null);
    }
}

function findBestIconMatch(itemName) {
    if (!itemName || !state.itemIcons) return null;
    const normalize = (str) => str.toLowerCase().replace(/[^a-z0-9]/g, '');
    const normalizedItemName = normalize(itemName);
    return state.itemIcons.find(iconFile => normalize(iconFile.split('.')[0]) === normalizedItemName) || null;
}

function renderItemIcons(allRecs, container, max_sets) {
    const masterContainer = document.createElement('div');
    masterContainer.className = 'recommended-items-container';
    (allRecs || []).filter(rec => rec.items?.length > 0).slice(0, max_sets).forEach(rec => {
        const itemsContainer = document.createElement('div');
        itemsContainer.className = 'recommended-items';
        rec.items.forEach(itemName => {
            const iconFile = findBestIconMatch(itemName);
            if (iconFile) {
                const img = document.createElement('img');
                img.src = `/static/tft_item_icons/${iconFile}`;
                img.alt = itemName;
                img.title = itemName;
                itemsContainer.appendChild(img);
            }
        });
        if (itemsContainer.hasChildNodes()) masterContainer.appendChild(itemsContainer);
    });
    if (masterContainer.hasChildNodes()) container.appendChild(masterContainer);
}
