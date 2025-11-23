// --- API Communication ---

import { state } from './state.js';

export async function fetchChampions() {
    const response = await fetch('/api/all_champion_data');
    return new Map(Object.entries(await response.json()));
}

export async function fetchAttackRanges() {
    const response = await fetch('/api/attack_ranges');
    return new Map(Object.entries(await response.json()));
}

export async function fetchItemIcons() {
    return await (await fetch('/api/item_icons')).json();
}

export async function fetchTeams(page = 0) {
    const response = await fetch(`/api/teams?mode=${state.currentRecommendationMode}&page=${page}`);
    return await response.json();
}

export async function fetchSuggestedChampions() {
    if (state.selectedChampions.size === 0) return new Set();
    const response = await fetch(`/api/all_recommended_champions?mode=${state.currentRecommendationMode}`);
    const champs = await response.json();
    return new Set(champs);
}

export async function fetchBulkRecommendationCounts() {
    const response = await fetch(`/api/bulk_recommendation_counts?mode=${state.currentRecommendationMode}`);
    const counts = await response.json();
    return new Map(Object.entries(counts));
}

export async function fetchDeactivationCount(championName) {
    if (!championName) return 0;
    try {
        const response = await fetch(`/api/deactivation_recommendation_count/${encodeURIComponent(championName)}?mode=${state.currentRecommendationMode}`);
        if (!response.ok) return 0;
        const data = await response.json();
        return data.count || 0;
    } catch (error) {
        console.error(`Error fetching deactivation count for ${championName}:`, error);
        return 0;
    }
}

export async function fetchItemRecommendations(championName) {
    const response = await fetch(`/api/item_recommendations/${encodeURIComponent(championName)}`);
    return await response.json();
}

export async function syncSelectionWithServer() {
    const response = await fetch('/api/get_selection_status');
    const data = await response.json();
    if (data.selected) return new Set(data.selected);
    return new Set();
}

export async function updateSelectionOnServer(champions) {
    try {
        const response = await fetch('/api/set_selection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ champions: champions })
        });
        return (await response.json()).success;
    } catch (error) {
        console.error('Selection update error:', error);
        return false;
    }
}
