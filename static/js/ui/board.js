// --- UI Module: Board ---

import { state } from '../state.js';
import { toggleChampion } from '../main.js';
import { displayItemRecommendations } from './item.js';

let domCache;

export function initializeBoard(cache) {
    domCache = cache;
    const board = domCache.board;
    board.innerHTML = '';
    for (let i = 0; i < 28; i++) {
        const cell = document.createElement('div');
        cell.className = 'board-cell';
        board.appendChild(cell);
    }
}

export function updateBoard() {
    if (!state.attackRangeData || state.attackRangeData.size === 0) {
        console.warn("Attack range data not loaded, skipping board update.");
        return;
    }

    const cells = domCache.board.querySelectorAll('.board-cell');
    cells.forEach(c => {
        c.innerHTML = '';
        c.className = 'board-cell';
        c.onclick = null; // Clear previous event listeners
    });

    let rowCounters = [0, 0, 0, 0];
    for (const championName of state.selectedChampions) {
        const attackRange = state.attackRangeData.get(championName) || 1;
        const rowIndex = Math.min(attackRange - 1, 3);
        if (rowCounters[rowIndex] >= 7) continue;

        const cellIndex = rowIndex * 7 + rowCounters[rowIndex];
        const cell = cells[cellIndex];
        if (!cell) continue;

        cell.classList.add('filled');
        cell.onclick = () => toggleChampion(championName);

        const contentWrapper = document.createElement('div');
        contentWrapper.className = 'board-cell-content-wrapper';
        contentWrapper.innerHTML = `<span class="champion-name-on-board">${championName}</span>`;
        cell.appendChild(contentWrapper);

        displayItemRecommendations(championName, contentWrapper, 1);

        const deactivationCount = state.deactivationCounts.get(championName);
        if (deactivationCount > 0) {
            const countSpan = document.createElement('span');
            countSpan.className = 'deactivation-count';
            countSpan.textContent = `-${deactivationCount}`;
            contentWrapper.appendChild(countSpan);
        }

        rowCounters[rowIndex]++;
    }
}
