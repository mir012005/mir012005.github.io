// =============================================================================
// 1. GESTION GLOBALE & NAVIGATION
// =============================================================================

// Stockage des instances de graphiques pour pouvoir les détruire avant redessin
let charts = {};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    chargerListeClubs();      // Remplit la grille d'accueil
    remplirTousLesMenus();      // Remplit les sélecteurs des clubs
    remplirDataListClubs();   // Remplit l'autocomplétion pour la recherche de match

    showPage('home');
});

// Navigation entre les pages (Sections)
function showPage(pageId) {
    // Masquer toutes les sections
    document.querySelectorAll('.page').forEach(page => page.style.display = 'none');
    // Afficher la section demandée
    const target = document.getElementById(pageId);
    if (target) target.style.display = 'block';
}

// =============================================================================
// 2. ACCUEIL & DONNÉES CLUBS
// =============================================================================

async function chargerListeClubs() {
    const grid = document.getElementById('clubsGrid');
    try {
        const response = await fetch('/api/clubs');
        const clubs = await response.json();
        
        grid.innerHTML = ''; // Nettoyer le loader
        clubs.forEach(club => {
            const card = document.createElement('div');
            card.className = 'club-card';
            card.innerHTML = `
                <div class="club-logo-wrapper">
                    <img src="logos/${club}.png" onerror="this.src='logos/default.png'">
                </div>
                <span class="club-name">${club}</span>
            `;
            // Clic sur une carte -> Lance le simulateur pour ce club
            card.onclick = () => {
                const input = document.getElementById('club');
                if (input) input.value = club;
                showPage('simulate');
                simulate();
            };
            grid.appendChild(card);
        });
    } catch (e) {
        grid.innerHTML = '<div class="error-msg">Erreur de chargement des clubs.</div>';
    }
}

// Remplit la datalist pour l'input de recherche de match (Ancien onglet impact)
async function remplirDataListClubs() {
    try {
        const res = await fetch('/api/clubs');
        const clubs = await res.json();
        const dl = document.getElementById('clubsList');
        if(dl) {
            dl.innerHTML = clubs.map(c => `<option value="${c}">`).join('');
        }
    } catch(e) {}
}

// =============================================================================
// 3. SIMULATEUR INDIVIDUEL (MONTE CARLO)
// =============================================================================

// Variable globale pour le graphique
let evolutionChartInstance = null;

// 1. FONCTION PRINCIPALE DE SIMULATION
// =============================================================================
// FONCTION PRINCIPALE DE SIMULATION (STATS + GRAPHIQUE)
// =============================================================================
// =============================================================================
// FONCTION PRINCIPALE DE SIMULATION (VOTRE VERSION + EVOLUTION)
// =============================================================================
async function simulate() {
    // 1. On récupère le club (Input ou Placeholder si clic depuis l'accueil)
    const clubInput = document.getElementById('club');
    const club = clubInput.value.trim() || clubInput.placeholder;

    // 2. On récupère la journée choisie (J0 par défaut)
    const daySelect = document.getElementById('simDaySelect');
    const selectedDay = daySelect ? parseInt(daySelect.value) : 0;
    
    const container = document.getElementById('resultsContainer');
    
    if (!club) return alert("Veuillez entrer un nom de club.");
    
    showPage('results');
    // On affiche quelle journée est simulée dans le loader
    container.innerHTML = `<div class="loader"></div><p style="text-align:center">Simulation depuis J${selectedDay}...</p>`;
    
    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            // ICI : On envoie la journée choisie au lieu de 6
            body: JSON.stringify({ club: club, day: selectedDay }) 
        });
        const data = await response.json();

        if (data.error) {
            container.innerHTML = `<div class="error-msg">❌ ${data.error}</div>`;
            return;
        }

        // 3. VOTRE HTML PRÉSERVÉ (Header + Stats Grid + Charts Column)
        // J'ai juste ajouté le bloc "Evolution" tout en bas
        container.innerHTML = `
            <div class="club-header">
                <div class="club-logo-wrapper" style="width:80px; height:80px;">
                    <img src="logos/${data.club}.png" onerror="this.src='logos/default.png'" alt="${data.club}" style="max-width:100%; max-height:100%;">
                </div>
                <div>
                    <h3>${data.club}</h3>
                    <p>Points Moyens prédits : <strong>${data.points_moyens}</strong> <span style="font-size:0.8em; color:#666;">(Base J${selectedDay})</span></p>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-box green">
                    <h4>Top 8</h4>
                    <span class="percentage">${data.proba_top_8}%</span>
                    <span class="sub-label">Qualif Directe</span>
                </div>
                <div class="stat-box yellow">
                    <h4>Barrage</h4>
                    <span class="percentage">${data.proba_barrage}%</span>
                    <span class="sub-label">9ème - 24ème</span>
                </div>
                <div class="stat-box red">
                    <h4>Éliminé</h4>
                    <span class="percentage">${data.proba_elimine}%</span>
                    <span class="sub-label">> 24ème</span>
                </div>
            </div>

            <div class="charts-column">
                <div class="chart-box">
                    <h4>Distribution des Points</h4>
                    <div class="chart-area"><canvas id="pointsChart"></canvas></div>
                </div>
                <div class="chart-box">
                    <h4>Distribution du Classement</h4>
                    <div class="chart-area"><canvas id="rankChart"></canvas></div>
                </div>
            </div>

            <div class="chart-wrapper" style="margin-top: 30px;">
                <h3 style="text-align:center; color:#002f5f;">📈 Historique & Trajectoire</h3>
                <p style="text-align:center; color:#666; font-size:0.9rem;">
                    Évolution des chances (J0 à J${selectedDay})
                </p>
                <div class="chart-area">
                    <canvas id="chartEvolution"></canvas>
                </div>
            </div>
        `;
        
        // 4. LANCEMENT DES GRAPHIQUES
        // Vos graphiques existants
        creerGraphique('pointsChart', data.distribution_points, 'Probabilité', '#007bff');
        creerGraphique('rankChart', data.distribution_rangs, 'Probabilité', '#6f42c1');

        // Le nouveau graphique d'évolution
        if (typeof chargerGraphiqueEvolution === "function") {
            chargerGraphiqueEvolution(club, selectedDay);
        }

    } catch (e) {
        console.error(e);
        container.innerHTML = `<div class="error-msg">❌ Erreur serveur</div>`;
    }
}

// 2. FONCTION DU GRAPHIQUE
async function chargerGraphiqueEvolution(club, maxDay) {
    try {
        // On demande l'historique arrêté à maxDay
        const res = await fetch('/api/evolution', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ club: club, day: maxDay })
        });
        const historyData = await res.json();

        const ctx = document.getElementById('chartEvolution').getContext('2d');

        // Reset du graph précédent
        if (evolutionChartInstance) {
            evolutionChartInstance.destroy();
        }

        // Création du nouveau graph
        evolutionChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: historyData.map(d => d.journee), // J0, J1...
                datasets: [
                    {
                        label: 'Chance Qualification (Top 24)',
                        data: historyData.map(d => d.qualif),
                        borderColor: '#0066cc', // Bleu UEFA
                        backgroundColor: 'rgba(0, 102, 204, 0.1)',
                        borderWidth: 3,
                        pointRadius: 5,
                        pointBackgroundColor: 'white',
                        pointBorderColor: '#0066cc',
                        pointBorderWidth: 2,
                        tension: 0.3, // Courbe lisse
                        fill: true
                    },
                    {
                        label: 'Chance Top 8 (Direct)',
                        data: historyData.map(d => d.top8),
                        borderColor: '#28a745', // Vert
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        borderDash: [5, 5], // Pointillés pour le Top 8
                        pointRadius: 0, // Pas de points pour alléger
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        top: 50,    // Marge en haut pour ne pas couper le point 100%
                        bottom: 10,
                        left: 10,
                        right: 10
                    }
                },
                scales: {
                    y: { 
                        beginAtZero: true, 
                        max: 100,
                        suggestedMax: 105,
                        title: { display: true, text: '% de Chances' }
                    }
                },
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: { mode: 'index', intersect: false }
                }
            }
        });

    } catch (e) {
        console.error("Erreur graph:", e);
    }
}

// =============================================================================
// 4. DUEL (PRÉDICTEUR MATCH UNIQUE)
// =============================================================================

async function remplirTousLesMenus() {
    try {
        const res = await fetch('/api/clubs');
        const clubs = await res.json();
        
        // Cibles : Duel (Home/Away) et Scénario (Club)
        const selHome = document.getElementById('selHome');
        const selAway = document.getElementById('selAway');
        const selScenario = document.getElementById('scenarioClub');

        // On remplit tout d'un coup
        clubs.forEach(c => {
            // Pour le Duel
            if (selHome) selHome.add(new Option(c, c));
            if (selAway) selAway.add(new Option(c, c));
            
            // Pour le Scénario (NOUVEAU)
            if (selScenario) selScenario.add(new Option(c, c));
        });

        // Petite astuce : sélectionner un club différent par défaut pour le Duel Away
        if (selAway) selAway.selectedIndex = 1; 

    } catch (e) {
        console.error("Erreur remplissage menus", e);
    }
}

async function lancerDuel() {
    const h = document.getElementById('selHome').value;
    const a = document.getElementById('selAway').value;
    
    if (h === a) return alert("Veuillez sélectionner deux équipes différentes.");
    
    const resBox = document.getElementById('duelResult');
    resBox.style.display = 'none';

    try {
        const response = await fetch('/api/predict-match', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ home: h, away: a })
        });
        const data = await response.json();

        // Mise à jour Score Moyen
        document.getElementById('resHomeName').innerText = data.home_team;
        document.getElementById('resAwayName').innerText = data.away_team;
        document.getElementById('resHomeScore').innerText = data.score_avg_home;
        document.getElementById('resAwayScore').innerText = data.score_avg_away;

        // Mise à jour Barres de Proba
        const barWin = document.getElementById('barWin');
        const barDraw = document.getElementById('barDraw');
        const barLoss = document.getElementById('barLoss');

        barWin.style.width = data.proba_win + '%';
        barWin.innerText = data.proba_win > 10 ? data.proba_win + '%' : '';
        
        barDraw.style.width = data.proba_draw + '%';
        barDraw.innerText = data.proba_draw > 10 ? data.proba_draw + '%' : '';
        
        barLoss.style.width = data.proba_loss + '%';
        barLoss.innerText = data.proba_loss > 10 ? data.proba_loss + '%' : '';

        resBox.style.display = 'block';
    } catch (e) {
        alert("Erreur lors de la simulation du duel.");
    }
}

// =============================================================================
// 5. CLASSEMENT PROJETÉ
// =============================================================================

async function chargerClassement() {
    const tbody = document.getElementById('rankingBody');
    const start = document.getElementById('startDay').value;
    const end = document.getElementById('endDay').value;
    
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center"><div class="loader"></div> Calcul...</td></tr>';
    
    try {
        const response = await fetch('/api/rankings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start: start, end: end })
        });
        const data = await response.json();
        
        tbody.innerHTML = '';
        data.forEach(r => {
            let cssClass = '';
            if (r.rank <= 8) cssClass = 'qualif-direct';
            else if (r.rank <= 24) cssClass = 'barrage';
            else cssClass = 'elimine';
            
            tbody.innerHTML += `
                <tr class="${cssClass}">
                    <td><strong>${r.rank}</strong></td>
                    <td style="text-align:left">
                        <img src="logos/${r.club}.png" class="mini-logo" onerror="this.src='logos/default.png'"> 
                        ${r.club}
                    </td>
                    <td><strong>${r.points}</strong></td>
                    <td>${r.diff > 0 ? '+'+r.diff : r.diff}</td>
                    <td>${r.buts}</td>
                    <td class="secondary-stat">${r.buts_ext}</td>
                    <td>${r.victoires}</td>
                    <td class="secondary-stat">${r.victoires_ext}</td>
                </tr>`;
        });
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="8">Erreur serveur</td></tr>';
    }
}

// =============================================================================
// 6. ANALYSES GLOBALES & PROBABILITÉS
// =============================================================================

async function chargerAnalysesGlobales() {
    // 1. Récupération de la journée choisie
    const select = document.getElementById('analysesStartDay');
    // Si le select n'existe pas encore (premier chargement), on prend 0 par défaut
    const day = select ? parseInt(select.value) : 0;

    // 2. Appel API pour les SEUILS (Graphiques)
    try {
        const response = await fetch('/api/seuils', {
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ day: day })
        });
        const data = await response.json();
        
        if (data.error) {
            console.error(data.error);
            return;
        }

        // 3. Mise à jour des graphiques
        creerGraphique('chartTop8', data.seuil_top8, `Points du 8ème (Base J${data.journee_utilisee})`, '#4bc0c0');
        creerGraphique('chartBarrage', data.seuil_barrage, `Points du 24ème (Base J${data.journee_utilisee})`, '#ffcd56');
    } catch (e) {
        console.error("Erreur seuils", e);
    }
}

async function chargerProbas() {
    const day = document.getElementById('probaStartDay').value;
    const t8 = document.getElementById('tbodyTop8');
    const tq = document.getElementById('tbodyQualif');
    
    t8.innerHTML = '<tr><td colspan="3" style="text-align:center"><div class="loader"></div></td></tr>';
    tq.innerHTML = '<tr><td colspan="3" style="text-align:center"><div class="loader"></div></td></tr>';
    
    try {
        const res = await fetch('/api/probas', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({day: day})
        });
        const data = await res.json();
        
        function fillTable(tbody, list, color) {
            if(!list || list.length === 0) tbody.innerHTML = '<tr><td colspan="3">Aucune donnée</td></tr>';
            else tbody.innerHTML = list.map((item, i) => `
                <tr>
                    <td>${i+1}</td>
                    <td style="text-align:left"><img src="logos/${item.club}.png" class="mini-logo"> ${item.club}</td>
                    <td><span class="score-badge" style="background:${color}">${item.proba}%</span></td>
                </tr>
            `).join('');
        }
        
        fillTable(t8, data.ranking_top8, '#28a745');
        fillTable(tq, data.ranking_qualif, '#fd7e14');
        
    } catch(e) {
        t8.innerHTML = '<tr><td colspan="3">Erreur</td></tr>';
        tq.innerHTML = '<tr><td colspan="3">Erreur</td></tr>';
    }
}

// =============================================================================
// 7. SECTION : IMPACT DES MATCHS (ANCIENNE / DÉTAILLÉE)
// =============================================================================

function switchImpactTab(tabName) {
    // Masquer les contenus
    document.querySelectorAll('#match-impact .impact-tab-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('#match-impact .tab-btn').forEach(btn => btn.classList.remove('active'));
    
    // Afficher le bon
    document.getElementById('impact-' + tabName).style.display = 'block';
    
    // Activer le bon bouton (Astuce basée sur l'ordre)
    const btns = document.querySelectorAll('#match-impact .tab-btn');
    if (tabName === 'specific') btns[0].classList.add('active');
    if (tabName === 'qualif') btns[1].classList.add('active');
    if (tabName === 'top8') btns[2].classList.add('active');
}

async function analyserImpactMatch() {
    const club = document.getElementById('impactClub').value;
    const journee = document.getElementById('impactJournee').value;
    const container = document.getElementById('impactResults');
    
    if(!club) return alert("Entrez un club");
    container.innerHTML = '<div class="loader"></div> Calcul...';
    
    try {
        const res = await fetch('/api/match-impact', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({club: club, journee: journee})
        });
        const data = await res.json();
        
        if(data.error) { container.innerHTML = `<div class="error-msg">${data.error}</div>`; return; }
        
        container.innerHTML = `
            <div class="impact-card">
                <h3>${data.club} ${data.domicile ? '🏠' : '✈️'} vs ${data.adversaire}</h3>
                <div class="scenarios-grid">
                    <div class="scenario-box victoire">
                        <h4>Victoire</h4>
                        <div>Qualif: <strong>${data.impact_victoire.proba_qualif}%</strong></div>
                        <div>Top 8: <strong>${data.impact_victoire.proba_top8}%</strong></div>
                    </div>
                    <div class="scenario-box nul">
                        <h4>Nul</h4>
                        <div>Qualif: <strong>${data.impact_nul.proba_qualif}%</strong></div>
                        <div>Top 8: <strong>${data.impact_nul.proba_top8}%</strong></div>
                    </div>
                    <div class="scenario-box defaite">
                        <h4>Défaite</h4>
                        <div>Qualif: <strong>${data.impact_defaite.proba_qualif}%</strong></div>
                        <div>Top 8: <strong>${data.impact_defaite.proba_top8}%</strong></div>
                    </div>
                </div>
                <div class="gains-box">
                    <p>Enjeu Victoire vs Défaite (Qualif) : <strong style="color:blue">+${(data.impact_victoire.proba_qualif - data.impact_defaite.proba_qualif).toFixed(1)}%</strong></p>
                </div>
            </div>
        `;
    } catch(e) { container.innerHTML = "Erreur serveur"; }
}

async function chargerMatchsImportants(type) {
    const container = document.getElementById(type === 'qualif' ? 'tableQualif' : 'tableTop8');
    container.innerHTML = '<div class="loader"></div>';
    
    try {
        const res = await fetch('/api/all-matches-impact', {
            method: 'POST', headers: {'Content-Type':'application/json'},
            body: JSON.stringify({journee: 7}) // Par défaut J7 pour l'instant
        });
        const data = await res.json();
        const list = type === 'qualif' ? data.par_qualif : data.par_top8;
        
        container.innerHTML = list.map((m, i) => `
            <div class="match-card" style="margin-bottom:10px; display:flex; justify-content:space-between;">
                <span><strong>#${i+1}</strong> ${m.match}</span>
                <span class="score-badge high">Impact: ${type === 'qualif' ? m.impact_qualif.global : m.impact_top8.global}</span>
            </div>
        `).join('');
    } catch(e) { container.innerHTML = "Erreur"; }
}

// =============================================================================
// 8. SECTION : SCÉNARIOS & HYPE (NOUVELLE / RAPIDE)
// =============================================================================

function switchScenarioTab(tabName) {
    document.getElementById('scenario-tab').style.display = 'none';
    document.getElementById('hype-tab').style.display = 'none';
    
    // Reset boutons
    const btns = document.querySelectorAll('#impact-zone .tab-btn');
    btns.forEach(b => b.classList.remove('active'));
    
    if (tabName === 'scenario') {
        document.getElementById('scenario-tab').style.display = 'block';
        btns[0].classList.add('active');
    } else {
        document.getElementById('hype-tab').style.display = 'block';
        btns[1].classList.add('active');
    }
}

async function lancerScenario() {
    const club = document.getElementById('scenarioClub').value;
    const start = document.getElementById('scenarioStartDay').value;
    const target = document.getElementById('scenarioTargetDay').value;
    const resVal = document.getElementById('scenarioResult').value; // V, N ou D
    const box = document.getElementById('scenarioResultBox');

    if(!club) return alert("Veuillez choisir un club dans la liste.");
    
    // Affichage temporaire (Loader)
    box.style.display = 'block';
    box.style.opacity = '0.5'; // Effet de chargement

    try {
        const res = await fetch('/api/scenario', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({club: club, start_day: start, day: target, result: resVal})
        });
        const data = await res.json();
        
        if(data.error) {
            alert(data.error);
            box.style.display = 'none';
            return;
        }

        box.style.opacity = '1';

        // 1. Mise à jour du Badge Central (Si Victoire...)
        const badge = document.getElementById('resBadge');
        let txtRes = resVal === 'V' ? 'Victoire' : (resVal === 'N' ? 'Nul' : 'Défaite');
        badge.innerText = "Si " + txtRes;
        badge.className = 'result-badge ' + (resVal === 'V' ? 'win' : (resVal === 'N' ? 'draw' : 'loss'));

        // 2. Remplir la colonne AVANT
        document.getElementById('beforeQualif').innerText = data.avant.qualif + '%';
        document.getElementById('beforeTop8').innerText = data.avant.top8 + '%';

        // 3. Remplir la colonne APRÈS
        document.getElementById('afterQualif').innerText = data.apres.qualif + '%';
        document.getElementById('afterTop8').innerText = data.apres.top8 + '%';

        // 4. Gérer les badges de DIFFÉRENCE (+10%, -5%...)
        updateDiffBadge('diffQualif', data.delta.qualif);
        updateDiffBadge('diffTop8', data.delta.top8);

        // 5. Verdict textuel en bas
        const vb = document.getElementById('scenarioVerdict');
        let vText = "Pas de changement majeur";
        let vColor = "#ccc";

        // Logique simple pour le verdict
        if (data.apres.qualif >= 99) { vText = "✅ Qualification quasi-assurée !"; vColor = "#28a745"; }
        else if (data.apres.qualif <= 5) { vText = "❌ Élimination très probable"; vColor = "#dc3545"; }
        else if (data.delta.qualif >= 15) { vText = "🚀 Bond énorme au classement !"; vColor = "#28a745"; }
        else if (data.delta.qualif <= -15) { vText = "⚠️ Chute dangereuse"; vColor = "#dc3545"; }
        else { vText = "Situation en évolution..."; vColor = "#ffc107"; }

        vb.innerText = vText;
        vb.style.borderLeftColor = vColor;

    } catch(e) { 
        console.error(e);
        alert("Erreur serveur lors de la simulation");
        box.style.display = 'none';
    }
}

// Fonction utilitaire pour colorer les + et -
function updateDiffBadge(elementId, value) {
    const el = document.getElementById(elementId);
    if (value > 0) {
        el.innerText = "+" + value + "%";
        el.className = "diff-badge positive";
    } else if (value < 0) {
        el.innerText = value + "%"; // Le moins est déjà dans la valeur
        el.className = "diff-badge negative";
    } else {
        el.innerText = "=";
        el.className = "diff-badge neutral";
    }
}

async function chargerImportance() {
    const start = document.getElementById('impStartDay').value;
    const target = document.getElementById('impTargetDay').value;
    const list = document.getElementById('importanceList');
    
    list.innerHTML = '<div style="text-align:center; padding:20px"><div class="loader"></div> Calcul des enjeux...</div>';
    
    try {
        const res = await fetch('/api/importance', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({start: start, target: target})
        });
        const data = await res.json();
        
        list.innerHTML = "";
        if(data.length === 0) { list.innerHTML = "Aucun match trouvé."; return; }
        
        data.forEach((m, i) => {
            let cls = m.score > 50 ? 'high' : (m.score > 20 ? 'medium' : 'low');
            list.innerHTML += `
                <div class="match-card">
                    <div class="match-info">
                        <span class="rank">#${i+1}</span>
                        <div class="teams">
                            <img src="logos/${m.dom}.png" class="mini-logo"> ${m.dom} 
                            <span class="vs">vs</span> 
                            ${m.ext} <img src="logos/${m.ext}.png" class="mini-logo">
                        </div>
                        <div class="score-badge ${cls}">${m.score}</div>
                    </div>
                    <div class="hype-bar-bg">
                        <div class="hype-bar-fill ${cls}" style="width:${Math.min(m.score, 100)}%"></div>
                    </div>
                    <div class="match-details-text">
                        Intérêt ${m.dom}: <strong>${m.details.dom_val}</strong> | 
                        Intérêt ${m.ext}: <strong>${m.details.ext_val}</strong>
                    </div>
                </div>`;
        });
    } catch(e) { list.innerHTML = "Erreur serveur"; }
}

// =============================================================================
// 9. UTILITAIRES GRAPHIQUES (CHART.JS)
// =============================================================================

function creerGraphique(canvasId, distributionData, label, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Détruire l'ancien graphique s'il existe pour éviter le scintillement
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    
    // Trier les clés (x-axis) numériquement
    const labels = Object.keys(distributionData).sort((a, b) => parseFloat(a) - parseFloat(b));
    const values = labels.map(k => distributionData[k] * 100); // Conversion en %

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                backgroundColor: color,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, title: { display: true, text: '%' } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}