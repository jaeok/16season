// --- UI Module: Team List ---

import { state } from '../state.js';
import { selectTeam } from '../main.js';

let domCache;

export function initializeTeamList(cache) {
    domCache = cache;
}

export function displayTeams(teamsToDisplay, append = false) {
    const teamList = domCache.teamList;
    if (!teamList) return;
    if (!append) teamList.innerHTML = '';

    const fragment = document.createDocumentFragment();
    teamsToDisplay.forEach(team => {
        const card = document.createElement('div');
        card.className = 'team-card';
        const sortedChamps = [...team.champions].sort((a, b) => (state.championData.get(a)?.cost || 0) - (state.championData.get(b)?.cost || 0));
        card.innerHTML = `
            <div class="team-champions">${sortedChamps.map(c => `<span class="champion-tag${state.selectedChampions.has(c) ? ' active' : ''}">${c}</span>`).join('')}</div>
            <div class="synergies"><div class="synergy-item">${team.synergies.join(' / ')}</div></div>`;
        card.onclick = () => selectTeam(team.champions);
        fragment.appendChild(card);
    });
    teamList.appendChild(fragment);
}
