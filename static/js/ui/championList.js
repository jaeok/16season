// --- UI Module: Champion List ---

import { state } from '../state.js';
import { toggleChampion } from '../main.js';

let domCache;

export function initializeChampionList(cache) {
    domCache = cache;
}

export function renderChampionList() {
    const championList = domCache.championList;
    if (!championList || !window.allChampions) return;

    const searchTerm = domCache.championSearch.value.toLowerCase();
    championList.innerHTML = '';
    const fragment = document.createDocumentFragment();

    const sortedChampions = [...window.allChampions].sort((a, b) => {
        const aIsSelected = state.selectedChampions.has(a);
        const bIsSelected = state.selectedChampions.has(b);
        const aIsSuggested = state.suggestedChampions.has(a);
        const bIsSuggested = state.suggestedChampions.has(b);
        const costA = state.championData.get(a)?.cost || 0;
        const costB = state.championData.get(b)?.cost || 0;

        // 1. Selected champions first
        if (aIsSelected !== bIsSelected) {
            return bIsSelected - aIsSelected;
        }
        // 2. Suggested champions next
        if (aIsSuggested !== bIsSuggested) {
            return bIsSuggested - aIsSuggested;
        }
        // 3. Cost next
        if (costA !== costB) {
            return costA - costB;
        }
        // 4. Name last
        return a.localeCompare(b);
    });

    sortedChampions.forEach(champion => {
        if (searchTerm && !champion.toLowerCase().includes(searchTerm)) return;

        const championInfo = state.championData.get(champion) || { cost: 1 };
        const div = document.createElement('div');
        div.className = 'champion-item';

        if (state.selectedChampions.has(champion)) {
            div.classList.add('selected');
        } else if (state.suggestedChampions.has(champion)) {
            div.classList.add('suggested');
        }

        div.innerHTML = `<span class="champion-cost cost-${championInfo.cost}">${championInfo.cost}</span><span class="champion-name">${champion}</span>`;
        div.onclick = () => toggleChampion(champion);

        const count = state.recommendationCounts.get(champion);
        if (count > 0) {
            const countSpan = document.createElement('span');
            countSpan.className = 'recommended-count';
            countSpan.textContent = `+${count}`;
            div.appendChild(countSpan);
        }

        fragment.appendChild(div);
    });
    championList.appendChild(fragment);
}
