// --- Application State ---
// This module holds the shared state of the application.

export const state = {
    selectedChampions: new Set(),
    suggestedChampions: new Set(),
    recommendationCounts: new Map(),
    deactivationCounts: new Map(),
    championData: new Map(),
    attackRangeData: new Map(),
    itemIcons: [],
    itemRecsCache: new Map(),
    currentRecommendationMode: 'ai',
    currentPage: 0,
    isLoading: false,
    allTeamsLoaded: false,
    isApplyingSelection: false,
};

// Functions to modify state could be added here if needed,
// but for now we will modify it directly from main.js for simplicity.
