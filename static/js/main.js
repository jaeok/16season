import { state } from './state.js';
import * as api from './api.js';
import { initializeBoard, updateBoard } from './ui/board.js';
import { initializeChampionList, renderChampionList } from './ui/championList.js';
import { initializeTeamList, displayTeams } from './ui/teamList.js';
import { initializeSynergyList, updateActiveSynergies } from './ui/synergy.js';

const domCache = {};

function debounce(func, wait) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function showLoader() { if (domCache.loaderOverlay) domCache.loaderOverlay.style.display = 'flex'; }
function hideLoader() { if (domCache.loaderOverlay) domCache.loaderOverlay.style.display = 'none'; }

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    initializeDOMCache();
    window.addEventListener('scroll', handleScroll);
    domCache.championSearch.addEventListener('input', debounce(renderChampionList, 300));
    domCache.clearSelectionButton.addEventListener('click', clearSelection);

    // Initialize recommendation mode buttons
    domCache.modeButtons.forEach(button => {
        button.addEventListener('click', () => changeRecommendationMode(button.dataset.mode));
    });
});

window.addEventListener('load', async () => {
    showLoader();
    try {
        const [champions, attackRanges, itemIcons, initialSelection] = await Promise.all([
            api.fetchChampions(),
            api.fetchAttackRanges(),
            api.fetchItemIcons(),
            api.syncSelectionWithServer()
        ]);

        state.championData = champions;
        window.allChampions = Array.from(champions.keys());
        state.attackRangeData = attackRanges;
        state.itemIcons = itemIcons;
        state.selectedChampions = initialSelection;

        await updateAll();
    } catch (error) {
        console.error('Error on window load:', error);
    } finally {
        hideLoader();
    }
});

function initializeDOMCache() {
    domCache.championList = document.getElementById('championList');
    domCache.teamList = document.getElementById('teamList');
    domCache.board = document.getElementById('board');
    domCache.championSearch = document.getElementById('championSearch');
    domCache.loaderOverlay = document.getElementById('loader-overlay');
    domCache.activeSynergies = document.getElementById('activeSynergies');
    domCache.clearSelectionButton = document.querySelector('.clear-selection');
    domCache.modeButtons = document.querySelectorAll('.mode-button');

    initializeBoard(domCache);
    initializeChampionList(domCache);
    initializeTeamList(domCache);
    initializeSynergyList(domCache);
}

// --- Core Application Logic ---
async function updateAll() {
    if (state.isApplyingSelection) return;
    state.isApplyingSelection = true;
    showLoader();

    try {
        await api.updateSelectionOnServer(Array.from(state.selectedChampions));
        state.currentPage = 0;
        state.allTeamsLoaded = false;
        domCache.teamList.innerHTML = '';
        state.deactivationCounts.clear();

        const dataFetchPromises = [
            api.fetchTeams(0).then(teams => {
                if (teams.length > 0) {
                    displayTeams(teams, true);
                } else {
                    state.allTeamsLoaded = true;
                }
            }),
            api.fetchSuggestedChampions().then(champs => state.suggestedChampions = champs),
            api.fetchBulkRecommendationCounts().then(counts => state.recommendationCounts = counts)
        ];

        if (state.selectedChampions.size > 0) {
            const deactivationPromises = Array.from(state.selectedChampions).map(async (champion) => {
                const count = await api.fetchDeactivationCount(champion);
                if (count > 0) {
                    state.deactivationCounts.set(champion, count);
                }
            });
            dataFetchPromises.push(...deactivationPromises);
        }

        await Promise.all(dataFetchPromises);

        renderChampionList();
        updateBoard();
        updateActiveSynergies();
    } catch(error) {
        console.error("Error during updateAll:", error);
    } finally {
        state.isApplyingSelection = false;
        hideLoader();
    }
}

// --- Event Handlers ---
export function toggleChampion(championName) {
    const newSelection = new Set(state.selectedChampions);
    if (newSelection.has(championName)) newSelection.delete(championName);
    else newSelection.add(championName);
    state.selectedChampions = newSelection;
    updateAll();
}

export function selectTeam(teamChampions) {
    state.selectedChampions = new Set(teamChampions);
    updateAll();
}

function clearSelection() {
    state.selectedChampions.clear();
    updateAll();
}

async function changeRecommendationMode(mode) {
    if (mode === state.currentRecommendationMode) return;
    domCache.modeButtons.forEach(b => b.classList.remove('active'));
    document.querySelector(`.mode-button[data-mode="${mode}"]`).classList.add('active');
    state.currentRecommendationMode = mode;
    await updateAll();
}

function handleScroll() {
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100) {
        if (!state.isLoading && !state.allTeamsLoaded) {
            loadMoreTeams();
        }
    }
}

async function loadMoreTeams() {
    state.isLoading = true;
    showLoader();
    try {
        state.currentPage++;
        const teams = await api.fetchTeams(state.currentPage);
        if (teams.length > 0) {
            displayTeams(teams, true);
        } else {
            state.allTeamsLoaded = true;
        }
    } catch (e) {
        console.error('Error loading more teams:', e);
        state.currentPage--; // Rollback page count on error
    } finally {
        state.isLoading = false;
        hideLoader();
    }
}
