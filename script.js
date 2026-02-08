// SYSTÈME DE TRADUCTION FR/EN (Incomplète par manque de temps)
const TRANSLATIONS = {
    fr: {
        // Accueil
        welcome: "Bienvenue sur le Simulateur LDC",
        description: "Ce projet utilise la méthode de Monte Carlo et les lois de Poisson pour prédire la fin de la saison.",
        choose_team: "Choisissez une équipe :",
        
        // Navigation
        nav_home: "Accueil",
        nav_analyses: "Seuils qualif",
        nav_duel: "Duel",
        nav_ranking: "Classement",
        nav_probas: "Probabilités",
        nav_labo: "Scénarios",
        nav_about: "A propos",
        
        // Duel
        duel_title: "🔮 Prédicteur de Match",
        duel_desc: "Simulez une rencontre spécifique en utilisant le modèle Elo + Poisson.",
        home: "Domicile 🏠",
        away: "Extérieur ✈️",
        simulate_match: "Simuler le match",
        
        // Classement
        ranking_title: "🏆 Classement Projeté (Moyenne)",
        ranking_desc: "Simulez le classement sur une période précise.",
        start_situation: "Situation de départ (Après) :",
        simulate_until: "Simuler jusqu'à la :",
        calculate: "🔄 Calculer",
        
        // Résultats
        results_title: "Résultats de la simulation",
        back_btn: "← Choisir un autre club",
        avg_points: "Points Moyens prédits :",
        top8: "Top 8",
        playoff: "Barrage",
        eliminated: "Éliminé",
        direct_qualif: "Qualif Directe",
        
        // Labo
        labo_title: "💥 Scénarios & Enjeux",
        labo_desc: "Simulez des scénarios ou analysez les matchs cruciaux pour votre équipe.",
        scenario_tab: "🔮 Scénario (What-If)",
        hypo_tab: "🎯 Importance",
        start_day: "Départ :",
        match_day: "Match en :",
        hypothesis: "Hypothèse :",
        simulate: "Simuler",
        victory: "Victoire",
        draw: "Nul",
        defeat: "Défaite",
        before: "Avant",
        after: "Après",
        qualif: "Qualif",
        
        // Analyses
        analyses_title: "Analyses Globales (Monte Carlo)",
        
        // Probabilités
        probas_title: "📊 Probabilités de Qualification",
        probas_desc: "Estimation des chances de chaque club selon la journée de départ (Simulé 1 000 000 fois).",
        
        // Footer
        theme_night: " Mode Nuit",
        theme_day: " Mode Jour"
    },
    en: {
        // Home
        welcome: "Welcome to the UCL Simulator",
        description: "This project uses Monte Carlo method and Poisson distributions to predict the end of the season.",
        choose_team: "Choose a team:",
        
        // Navigation
        nav_home: "Home",
        nav_analyses: "Analysis",
        nav_duel: "Duel",
        nav_ranking: "Ranking",
        nav_probas: "Probabilities",
        nav_labo: "Scenarios",
        nav_about: "About",
        
        // Duel
        duel_title: "🔮 Match Predictor",
        duel_desc: "Simulate a specific match using the Elo + Poisson model.",
        home: "Home 🏠",
        away: "Away ✈️",
        simulate_match: "Simulate match",
        
        // Ranking
        ranking_title: "🏆 Projected Ranking (Average)",
        ranking_desc: "Simulate the ranking over a specific period.",
        start_situation: "Starting situation (After):",
        simulate_until: "Simulate until:",
        calculate: "🔄 Calculate",
        
        // Results
        results_title: "Simulation Results",
        back_btn: "← Choose another club",
        avg_points: "Predicted Average Points:",
        top8: "Top 8",
        playoff: "Playoff",
        eliminated: "Eliminated",
        direct_qualif: "Direct Qualification",
        
        // Lab
        labo_title: "💥 Scenarios & Stakes",
        labo_desc: "Simulate scenarios or analyze crucial matches for your team.",
        scenario_tab: "🔮 Scenario (What-If)",
        hypo_tab: "🎯 Importance",
        start_day: "Start:",
        match_day: "Match on:",
        hypothesis: "Hypothesis:",
        simulate: "Simulate",
        victory: "Victory",
        draw: "Draw",
        defeat: "Defeat",
        before: "Before",
        after: "After",
        qualif: "Qualif",
        
        // Analysis
        analyses_title: "Global Analysis (Monte Carlo)",
        
        // Probabilities
        probas_title: "📊 Qualification Probabilities",
        probas_desc: "Estimated chances for each club based on the starting matchday (Simulated 1 000 000 times).",
        
        // Footer
        theme_night: " Night Mode",
        theme_day: " Day Mode"
    }
};

let currentLang = localStorage.getItem('lang') || 'fr';

function toggleLanguage() {
    currentLang = currentLang === 'fr' ? 'en' : 'fr';
    localStorage.setItem('lang', currentLang);
    applyLanguage();
    updateLangButton();
}

function applyLanguage() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (TRANSLATIONS[currentLang][key]) {
            el.textContent = TRANSLATIONS[currentLang][key];
        }
    });
}

function updateLangButton() {
    const btn = document.getElementById('lang-toggle');
    if (btn) {
        btn.innerHTML = `<i class="fa-solid fa-globe"></i> ${currentLang === 'fr' ? 'EN' : 'FR'}`;
    }
}


// Stockage des instances de graphiques pour pouvoir les détruire avant redessin
let charts = {};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    chargerListeClubs();      // Remplit la grille d'accueil
    remplirTousLesMenus();      // Remplit les sélecteurs des clubs
    remplirDataListClubs();   // Remplit l'autocomplétion pour la recherche de match
    filtrerJourneesDisponibles();

    showPage('home');
    
    // Appliquer la langue sauvegardée
    applyLanguage();
    updateLangButton();
});

async function filtrerJourneesDisponibles() {
    try {
        const response = await fetch('/api/max-journee');
        const data = await response.json();
        const maxJ = data.max_journee;
        
        const dropdowns = ['startDay', 'simDaySelect', 'analysesStartDay', 
                          'probaStartDay', 'scenarioStartDay', 'hypo-day-select'];
        
        dropdowns.forEach(id => {
            const select = document.getElementById(id);
            if (select) {
                Array.from(select.options).forEach(option => {
                    if (parseInt(option.value) > maxJ) {
                        option.disabled = true;
                        option.style.color = '#ccc';
                    }
                });
                if (parseInt(select.value) > maxJ) select.value = maxJ.toString();
            }
        });
    } catch (error) {
        console.error('Erreur filtrage journées:', error);
    }
}

// Navigation entre les pages (Sections)
function showPage(pageId) {
    // Masquer toutes les sections
    document.querySelectorAll('.page').forEach(page => page.style.display = 'none');
    // Afficher la section demandée
    const target = document.getElementById(pageId);
    if (target) target.style.display = 'block';
}


// ACCUEIL & DONNÉES CLUBS
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


// 3. SIMULATEUR INDIVIDUEL (MONTE CARLO)

// Variable globale pour le graphique
let evolutionChartInstance = null;

// 1. FONCTION PRINCIPALE DE SIMULATION
async function simulate() {
    // On récupère le club (Input ou Placeholder si clic depuis l'accueil)
    const clubInput = document.getElementById('club');
    const club = clubInput.value.trim() || clubInput.placeholder;

    // On récupère la journée choisie (J0 par défaut)
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
            // On envoie la journée choisie au lieu de 6
            body: JSON.stringify({ club: club, day: selectedDay }) 
        });
        const data = await response.json();

        if (data.error) {
            container.innerHTML = `<div class="error-msg">❌ ${data.error}</div>`;
            return;
        }

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
                <h3 style="text-align:center; color:#002f5f;">📈 Historique</h3>
                <p style="text-align:center; color:#666; font-size:0.9rem;">
                    
                </p>
                <div class="chart-area">
                    <canvas id="chartEvolution"></canvas>
                </div>
            </div>
        `;
        
        // LANCEMENT DES GRAPHIQUES
        creerGraphique('pointsChart', data.distribution_points, 'Probabilité', '#007bff');
        creerGraphique('rankChart', data.distribution_rangs, 'Probabilité', '#6f42c1');

        // Le graphique d'évolution
        if (typeof chargerGraphiqueEvolution === "function") {
            chargerGraphiqueEvolution(club, selectedDay);
        }

    } catch (e) {
        console.error(e);
        container.innerHTML = `<div class="error-msg">❌ Erreur serveur</div>`;
    }
}

// ONCTION DU GRAPHIQUE
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
                        borderColor: '#28a745',
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
                        top: 50,
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

// DUEL (PRÉDICTEUR MATCH UNIQUE)
async function remplirTousLesMenus() {
    try {
        const res = await fetch('/api/clubs');
        const clubs = await res.json();
        
        const selHome = document.getElementById('selHome');
        const selAway = document.getElementById('selAway');
        const selScenario = document.getElementById('scenarioClub');
        const selHypo = document.getElementById('hypo-club-select');

        clubs.forEach(c => {
            if (selHome) selHome.add(new Option(c, c));
            if (selAway) selAway.add(new Option(c, c));
            if (selScenario) selScenario.add(new Option(c, c));
            if (selHypo) selHypo.add(new Option(c, c));
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

// CLASSEMENT PROJETÉ
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

// ANALYSES GLOBALES & PROBABILITÉS
async function chargerAnalysesGlobales() {
    // Récupération de la journée choisie
    const select = document.getElementById('analysesStartDay');
    // Si le select n'existe pas encore (premier chargement), on prend 0 par défaut
    const day = select ? parseInt(select.value) : 0;

    // Appel API pour les SEUILS (Graphiques)
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

        // Mise à jour des graphiques
        creerGraphique('chartTop8', data.seuil_top8, `Points du 8ème (Base J${data.journee_utilisee})`, '#4bc0c0');
        creerGraphique('chart9eme', data.seuil_9eme, `Points du 9ème (Base J${data.journee_utilisee})`, '#b19cd9');
        creerGraphique('chartBarrage', data.seuil_barrage, `Points du 24ème (Base J${data.journee_utilisee})`, '#ffcd56');
        creerGraphique('chart25eme', data.seuil_25eme, `Points du 25ème (Base J${data.journee_utilisee})`, '#e74c3c');
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

// LABO & HYPE (SCÉNARIOS + HYPO-MÈTRE)
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

// PARTIE A : SCÉNARIO
async function lancerScenario() {
    const club = document.getElementById('scenarioClub').value;
    const start = document.getElementById('scenarioStartDay').value;
    const target = document.getElementById('scenarioTargetDay').value;
    const resVal = document.getElementById('scenarioResult').value;
    const box = document.getElementById('scenarioResultBox');

    if(!club) return alert("Veuillez choisir un club.");
    if(parseInt(start) >= parseInt(target)) return alert("La journée de départ doit être avant la journée du match.");
    
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

// HYPO-MÈTRE
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
            
            // Crée le badge J7, J8, etc. si l'info est dispo
            let dayBadge = item.journee ? `<span class="day-badge">J${item.journee}</span>` : '';
            // Couleurs basées sur le score cumulé
            let scoreCumule = item.score_cumule || item.score || 0;
            let scoreQualif = item.score_qualif || item.score || 0;
            let scoreTop8 = item.score_top8 || 0;
            
            let barColorQualif = scoreQualif > 20 ? "#e74c3c" : (scoreQualif > 10 ? "#f1c40f" : "#3498db");
            let barColorTop8 = scoreTop8 > 20 ? "#e74c3c" : (scoreTop8 > 10 ? "#f1c40f" : "#9b59b6");
            
            let barWidthQualif = Math.min(100, Math.abs(scoreQualif) * 3);
            let barWidthTop8 = Math.min(100, Math.abs(scoreTop8) * 3);

            let html = `
            <div class="match-card" style="${borderStyle} ${bgStyle} padding:15px; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <div style="font-weight:600; font-size:1.05rem;">
                        ${dayBadge} ${item.match} ${badge}
                    </div>
                </div>
                
                <div style="display:flex; gap:15px;">
                    <div style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size:0.8rem; color:#888;">Top 24</span>
                            <span style="font-size:1rem; font-weight:700; color:${barColorQualif};">
                                ${item.score_qualif > 0 ? '+' : ''}${item.score_qualif}%
                            </span>
                        </div>
                        <div style="width:100%; height:5px; background:rgba(0,0,0,0.2); border-radius:3px; overflow:hidden; margin-top:3px;">
                            <div style="width:${barWidthQualif}%; height:100%; background:${barColorQualif}; transition: width 0.5s ease;"></div>
                        </div>
                    </div>
                    
                    <div style="flex:1;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-size:0.8rem; color:#888;">Top 8</span>
                            <span style="font-size:1rem; font-weight:700; color:${barColorTop8};">
                                ${item.score_top8 > 0 ? '+' : ''}${item.score_top8}%
                            </span>
                        </div>
                        <div style="width:100%; height:5px; background:rgba(0,0,0,0.2); border-radius:3px; overflow:hidden; margin-top:3px;">
                            <div style="width:${barWidthTop8}%; height:100%; background:${barColorTop8}; transition: width 0.5s ease;"></div>
                        </div>
                    </div>
                </div>
            </div>`;
            
            container.innerHTML += html;
        });

    } catch (e) {
        loader.style.display = 'none';
        container.innerHTML = `<div class="error-msg">Erreur serveur : ${e}</div>`;
    }
}

// UTILITAIRES GRAPHIQUES (CHART.JS)
function creerGraphique(canvasId, distributionData, label, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Détruire l'ancien graphique s'il existe pour éviter le scintillement
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    // Créer un range continu du min au max (même si certaines valeurs ont proba=0)
    const keys = Object.keys(distributionData).map(k => parseInt(k));
    const minVal = Math.min(...keys);
    const maxVal = Math.max(...keys);
    
    const labels = [];
    const values = [];
    for (let i = minVal; i <= maxVal; i++) {
        labels.push(i.toString());
        values.push((distributionData[i] || distributionData[i.toString()] || 0) * 100);
    }

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