// --- UI Module: Synergy List ---

import { state } from '../state.js';
// This module would need access to the synergy calculation API
// For now, let's assume it's a simple render function.

let domCache;

export function initializeSynergyList(cache) {
    domCache = cache;
}

export async function updateActiveSynergies() {
    const container = domCache.activeSynergies;
    if (!container) return;
    try {
        // This API call is not in api.js, let's assume it exists for now
        const response = await fetch('/api/calculate_synergies');
        const synergies = await response.json();
        if (synergies.error) return;

        container.innerHTML = synergies.map(s => `
            <div class="synergy-tag ${s.current_level > 0 ? 'active' : ''}">
                <span class="name">${s.name}</span>
                <span class="count">${s.count}/${s.next_level || s.max_level}</span>
            </div>`).join('');
    } catch (e) {
        console.error('시너지 업데이트 오류:', e);
    }
}
