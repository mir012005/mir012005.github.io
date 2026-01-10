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
        
        // Cibles : Duel, Scénario ET Hypo-mètre (Nouveau)
        const selHome = document.getElementById('selHome');
        const selAway = document.getElementById('selAway');
        const selScenario = document.getElementById('scenarioClub');
        const selHypo = document.getElementById('hypo-club-select'); // <--- AJOUT IMPORTANT

        clubs.forEach(c => {
            if (selHome) selHome.add(new Option(c, c));
            if (selAway) selAway.add(new Option(c, c));
            if (selScenario) selScenario.add(new Option(c, c));
            if (selHypo) selHypo.add(new Option(c, c)); // <--- AJOUT IMPORTANT
        });

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
// 8. SECTION : LABO & HYPE (SCÉNARIOS + HYPO-MÈTRE)
// =============================================================================

// Gestion des onglets internes
function switchScenarioTab(tabName) {
    // Masquer les contenus
    document.getElementById('tab-scenario').style.display = 'none';
    document.getElementById('tab-hypo').style.display = 'none';

    // Désactiver les boutons
    const btnScen = document.getElementById('btn-tab-scenario');
    const btnHypo = document.getElementById('btn-tab-hypo');
    if(btnScen) btnScen.classList.remove('active');
    if(btnHypo) btnHypo.classList.remove('active');

    // Activer le bon onglet
    if (tabName === 'scenario') {
        document.getElementById('tab-scenario').style.display = 'block';
        if(btnScen) btnScen.classList.add('active');
    } else {
        document.getElementById('tab-hypo').style.display = 'block';
        if(btnHypo) btnHypo.classList.add('active');
    }
}

// --- PARTIE A : SCÉNARIO (WHAT-IF) ---

async function lancerScenario() {
    const club = document.getElementById('scenarioClub').value;
    const start = document.getElementById('scenarioStartDay').value;
    const target = document.getElementById('scenarioTargetDay').value;
    const resVal = document.getElementById('scenarioResult').value;
    const box = document.getElementById('scenarioResultBox');

    if(!club) return alert("Veuillez choisir un club.");
    
    box.style.display = 'block';
    box.style.opacity = '0.5'; // Effet chargement

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

        // Mise à jour de l'affichage
        const badge = document.getElementById('resBadge');
        let txtRes = resVal === 'V' ? 'Victoire' : (resVal === 'N' ? 'Nul' : 'Défaite');
        badge.innerText = "Si " + txtRes;
        badge.className = 'result-badge ' + (resVal === 'V' ? 'win' : (resVal === 'N' ? 'draw' : 'loss'));

        document.getElementById('beforeQualif').innerText = data.avant.qualif + '%';
        document.getElementById('beforeTop8').innerText = data.avant.top8 + '%';
        
        document.getElementById('afterQualif').innerText = data.apres.qualif + '%';
        document.getElementById('afterTop8').innerText = data.apres.top8 + '%';

        updateDiffBadge('diffQualif', data.delta.qualif);
        updateDiffBadge('diffTop8', data.delta.top8);

    } catch(e) { 
        console.error(e);
        box.style.display = 'none';
    }
}

function updateDiffBadge(elementId, value) {
    const el = document.getElementById(elementId);
    if (value > 0) {
        el.innerText = "+" + value + "%";
        el.className = "diff-badge positive";
    } else if (value < 0) {
        el.innerText = value + "%";
        el.className = "diff-badge negative";
    } else {
        el.innerText = "=";
        el.className = "diff-badge neutral";
    }
}

// --- PARTIE B : HYPO-MÈTRE (NOUVELLE VERSION) ---

async function lancerHypometre() {
    const club = document.getElementById('hypo-club-select').value;
    const day = document.getElementById('hypo-day-select').value;
    const container = document.getElementById('hypo-resultats');
    const loader = document.getElementById('hypo-loading');
    
    container.innerHTML = '';
    loader.style.display = 'block';

    if(!club) {
        alert("Veuillez choisir votre équipe.");
        loader.style.display = 'none';
        return;
    }

    try {
        // C'est ici qu'on appelle la nouvelle route Python
        const res = await fetch('/api/hypometre', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({club: club, day: day})
        });
        const data = await res.json();

        loader.style.display = 'none';

        if (data.error) {
            container.innerHTML = `<div class="error-msg">${data.error}</div>`;
            return;
        }

        if (!data.liste || data.liste.length === 0) {
            container.innerHTML = `<div class="placeholder-text">Aucun match de la prochaine journée n'a d'impact significatif.</div>`;
            return;
        }

        // Création des cartes de matchs
        data.liste.forEach(item => {
            let isOwn = item.is_my_match;
            let borderStyle = isOwn ? "border-left: 6px solid #00d2be;" : "border-left: 6px solid #555;";
            let bgStyle = isOwn ? "background: rgba(0, 210, 190, 0.08);" : "background: rgba(255, 255, 255, 0.05);";
            
            let badge = isOwn 
                ? `<span style="background:#00d2be; color:#000; padding:2px 6px; border-radius:4px; font-size:0.7em; font-weight:bold; margin-left:8px;">VOTRE MATCH</span>` 
                : `<span style="background:#555; color:#fff; padding:2px 6px; border-radius:4px; font-size:0.7em; margin-left:8px;">RIVAL</span>`;

            let barColor = item.score > 20 ? "#e74c3c" : (item.score > 10 ? "#f1c40f" : "#3498db");
            let barWidth = Math.min(100, item.score * 3); 

            let html = `
            <div class="match-card" style="${borderStyle} ${bgStyle} padding:15px; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:600; font-size:1.05rem;">${item.match} ${badge}</div>
                    <div style="font-size:1.2rem; font-weight:800; color:${barColor};">${item.score}%</div>
                </div>
                <div style="font-size:0.85rem; color:#888; margin:5px 0;">Impact sur votre qualification</div>
                <div style="width:100%; height:6px; background:rgba(0,0,0,0.2); border-radius:3px; overflow:hidden;">
                    <div style="width:${barWidth}%; height:100%; background:${barColor}; transition: width 0.5s ease;"></div>
                </div>
            </div>`;
            
            container.innerHTML += html;
        });

    } catch (e) {
        loader.style.display = 'none';
        container.innerHTML = `<div class="error-msg">Erreur serveur : ${e}</div>`;
    }
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