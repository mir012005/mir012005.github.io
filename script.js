// Variable globale pour stocker les instances de graphiques et éviter les bugs de superposition
let charts = {};

function showPage(pageId) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.style.display = 'none');
    document.getElementById(pageId).style.display = 'block';
}

// ==========================================
// 1. SIMULATION INDIVIDUELLE
// ==========================================
/*
//je step un peu sur houssam
async function simulate() {
    const clubInput = document.getElementById('club');
    const club = clubInput.value.trim();
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (club === "") {
        alert("Veuillez entrer un nom de club !");
        return;
    }

    showPage('results');
    resultsContainer.innerHTML = `
        <div class="loading-container">
            <div class="loader"></div>
            <p>Simulation de 1000 saisons pour ${club}...</p>
        </div>`;

    try {
        // Appel à l'API Python
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ club: club })
        });

        const data = await response.json();

        if (data.error) {
            resultsContainer.innerHTML = `<div class="error-msg">❌ Erreur : ${data.error} <br> Vérifiez l'orthographe (ex: "Paris SG", "Man City").</div>`;
            return;
        }

        // Construction de l'affichage
        resultsContainer.innerHTML = `
            <div class="club-header">
                <h3>${data.club}</h3>
                <span class="avg-points">Points moyens estimés : <strong>${data.points_moyens}</strong></span>
            </div>

            <div class="stats-grid">
                <div class="stat-box green">
                    <h4>Top 8 (Direct)</h4>
                    <span class="percentage">${data.proba_top_8}%</span>
                </div>
                <div class="stat-box yellow">
                    <h4>Barrages</h4>
                    <span class="percentage">${data.proba_barrage}%</span>
                </div>
                <div class="stat-box red">
                    <h4>Éliminé</h4>
                    <span class="percentage">${data.proba_elimine}%</span>
                </div>
            </div>

            <div class="main-chart-container">
                <canvas id="probaChart"></canvas>
            </div>
        `;

        // Dessiner le graphique
        creerGraphique('probaChart', data.distribution, `Distribution des points - ${data.club}`, '#0066cc');

    } catch (error) {
        console.error(error);
        resultsContainer.innerHTML = `<div class="error-msg">❌ Impossible de contacter le serveur Python. Vérifiez qu'il est lancé.</div>`;
    }
}

*/
// ==========================================
// 1. SIMULATION INDIVIDUELLE (MISE A JOUR)
// ==========================================
// ==========================================
// 1. SIMULATION INDIVIDUELLE (MISE A JOUR)
// ==========================================
async function simulate() {
    const clubInput = document.getElementById('club');
    const club = clubInput.value.trim();
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (club === "") {
        alert("Veuillez entrer un nom de club !");
        return;
    }

    showPage('results');
    resultsContainer.innerHTML = `
        <div class="loading-container">
            <div class="loader"></div>
            <p>Simulation de 1000 saisons pour ${club}...</p>
        </div>`;

    try {
        // Appel API
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ club: club })
        });

        const data = await response.json();

        if (data.error) {
            resultsContainer.innerHTML = `<div class="error-msg">❌ Erreur : ${data.error}</div>`;
            return;
        }

        // Construction de l'affichage
        // Notez la nouvelle div "charts-column" pour empiler les graphes
        resultsContainer.innerHTML = `
            <div class="club-header">
                <h3>${data.club}</h3>
                <span class="avg-points">Points moyens estimés : <strong>${data.points_moyens}</strong></span>
            </div>

            <div class="stats-grid">
                <div class="stat-box green">
                    <h4>Top 8 (Direct)</h4>
                    <span class="percentage">${data.proba_top_8}%</span>
                </div>
                <div class="stat-box yellow">
                    <h4>Barrages</h4>
                    <span class="percentage">${data.proba_barrage}%</span>
                </div>
                <div class="stat-box red">
                    <h4>Éliminé</h4>
                    <span class="percentage">${data.proba_elimine}%</span>
                </div>
            </div>

            <div class="charts-column">
                
                <div class="chart-box">
                    <h4>📊 Distribution des Points Finaux</h4>
                    <div class="chart-area">
                        <canvas id="pointsChart"></canvas>
                    </div>
                </div>

                <div class="chart-box">
                    <h4>🏆 Distribution du Classement Final</h4>
                    <div class="chart-area">
                        <canvas id="rankChart"></canvas>
                    </div>
                </div>

            </div>
        `;

        // Génération des graphiques
        // Graphe Points (Bleu)
        creerGraphique('pointsChart', data.distribution_points, 'Probabilité (%)', '#0066cc');
        
        // Graphe Classement (Violet pour différencier)
        creerGraphique('rankChart', data.distribution_rangs, 'Probabilité (%)', '#9b59b6');

    } catch (error) {
        console.error(error);
        resultsContainer.innerHTML = `<div class="error-msg">❌ Erreur de communication avec le serveur.</div>`;
    }
}

// ==========================================
// 2. ANALYSES GLOBALES
// ==========================================
async function chargerAnalysesGlobales() {
    // On charge les seuils
    try {
        const response = await fetch('/api/seuils');
        const data = await response.json();
        
        creerGraphique('chartTop8', data.seuil_top8, 'Points du 8ème', '#4bc0c0');
        creerGraphique('chartBarrage', data.seuil_barrage, 'Points du 24ème', '#ffcd56');
    } catch (e) {
        console.error("Erreur seuils", e);
    }

    // On charge l'importance des matchs
    try {
        const list = document.getElementById('listeImportance');
        list.innerHTML = '<div class="loader small"></div> Calcul des impacts...';
        
        const response2 = await fetch('/api/importance');
        const data2 = await response2.json();

        list.innerHTML = "";
        data2.forEach((item, index) => {
            list.innerHTML += `
                <li>
                    <span class="rank">#${index + 1}</span>
                    <span class="match-name">${item.match}</span>
                    <span class="score">Impact: <strong>${item.score}</strong></span>
                </li>`;
        });
    } catch (e) {
        console.error("Erreur importance", e);
    }
}

// ==========================================
// 3. FONCTION UTILITAIRE GRAPHIQUE
// ==========================================
function creerGraphique(canvasId, distribution, label, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Si un graphique existe déjà sur ce canvas, on le détruit proprement
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    // Trier les clés (points) par ordre croissant
    const labels = Object.keys(distribution).sort((a, b) => parseInt(a) - parseInt(b));
    // Récupérer les valeurs correspondantes et convertir en pourcentage si nécessaire
    const dataValues = labels.map(k => distribution[k] * 100); 

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels, // ex: ["10 pts", "11 pts"...]
            datasets: [{
                label: label + ' (%)',
                data: dataValues,
                backgroundColor: color,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: (context) => context.raw.toFixed(1) + '%' } }
            },
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Probabilité (%)' } }
            }
        }
    });
}

// =========== 19/12/2025 16:42 début MIR ===============================
// 4. GESTION DES LOGOS ET DE LA GRILLE
// ==========================================

// Lancer le chargement dès que la page s'ouvre
document.addEventListener('DOMContentLoaded', () => {
    chargerListeClubs();
    // Si vous aviez d'autres inits, gardez-les
});

async function chargerListeClubs() {
    const grid = document.getElementById('clubsGrid');
    
    try {
        const response = await fetch('/api/clubs');
        const clubs = await response.json();
        
        // Si erreur
        if (clubs.error) {
            grid.innerHTML = `<p style="color:red">Erreur: ${clubs.error}</p>`;
            return;
        }

        // On vide le "Chargement..."
        grid.innerHTML = ''; 

        clubs.forEach(club => {
            // Création de la carte (div)
            const card = document.createElement('div');
            card.className = 'club-card';
            
            // Chemin de l'image : on suppose que c'est le nom exact + .png
            // On ajoute un timestamp ?v=1 pour éviter les soucis de cache si vous changez l'image
            const logoPath = `logos/${club}.png`; 
            
            // On construit le HTML de la carte
            // onerror : si l'image n'existe pas, on met une image par défaut
            card.innerHTML = `
                <div class="club-logo-wrapper">
                    <img src="${logoPath}" 
                         alt="${club}" 
                         onerror="this.onerror=null; this.src='logos/default.png';">
                </div>
                <span class="club-name">${club}</span>
            `;

            // RENDRE CLIQUABLE
            // Quand on clique, ça remplit le champ caché et ça lance la simulation
            card.onclick = () => {
                // 1. Remplir l'input (même s'il est caché ou sur l'autre page)
                const input = document.getElementById('club');
                if(input) input.value = club;

                // 2. Changer de page
                showPage('simulate');

                // 3. Lancer la fonction existante simulate()
                simulate();
            };

            grid.appendChild(card);
        });

    } catch (error) {
        console.error("Erreur JS:", error);
        grid.innerHTML = '<p>Impossible de charger les équipes.</p>';
    }
}
// =========== 19/12/2025 16:42 fin MIR ===============================

// ==========================================
// 5. GESTION DU DUEL (MATCH PREDICTOR)
// ==========================================

// A. AU CHARGEMENT DE LA PAGE
// On écoute l'événement "DOMContentLoaded" (quand la page est prête)
document.addEventListener('DOMContentLoaded', () => {
    // On lance la fonction qui remplit les listes
    remplirListesDuel();
});

// Fonction pour récupérer les clubs et remplir les <select>
async function remplirListesDuel() {
    try {
        // 1. On demande la liste des clubs à Python
        const res = await fetch('/api/clubs');
        const clubs = await res.json();
        
        // 2. On cible les deux menus déroulants HTML par leur ID
        const selHome = document.getElementById('selHome');
        const selAway = document.getElementById('selAway');
        
        // 3. Pour chaque club, on crée une option
        clubs.forEach(clubName => {
            // new Option(texte_visible, valeur_interne)
            selHome.add(new Option(clubName, clubName));
            selAway.add(new Option(clubName, clubName));
        });
        
        // Petite astuce : on sélectionne par défaut le 2ème club pour l'équipe extérieure
        // pour ne pas avoir "Arsenal vs Arsenal" au début.
        selAway.selectedIndex = 1; 

    } catch (err) {
        console.error("Erreur chargement liste duel:", err);
    }
}

// B. QUAND ON CLIQUE SUR "SIMULER LE MATCH"
async function lancerDuel() {
    // 1. Récupérer les valeurs choisies par l'utilisateur
    const homeTeam = document.getElementById('selHome').value;
    const awayTeam = document.getElementById('selAway').value;
    
    // 2. Vérification de sécurité
    if(homeTeam === awayTeam) {
        alert("Une équipe ne peut pas jouer contre elle-même !");
        return; // On arrête tout ici
    }

    // 3. On cache le résultat précédent (si existant) pour faire propre
    const resultBox = document.getElementById('duelResult');
    resultBox.style.display = 'none';

    try {
        // 4. On appelle le serveur Python (C'est le coup de téléphone)
        const response = await fetch('/api/predict-match', {
            method: 'POST', // On envoie des données
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ home: homeTeam, away: awayTeam })
        });
        
        // 5. On récupère la réponse de Python (le dictionnaire JSON)
        const data = await response.json();
        
        // Si Python renvoie une erreur, on l'affiche
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // 6. MISE A JOUR DE L'INTERFACE (On remplit les trous du HTML)
        
        // Noms des équipes
        document.getElementById('resHomeName').innerText = data.home_team;
        document.getElementById('resAwayName').innerText = data.away_team;
        
        // Scores prédits (moyennes)
        document.getElementById('resHomeScore').innerText = data.score_avg_home;
        document.getElementById('resAwayScore').innerText = data.score_avg_away;

        // Barres de probabilités (Largeur en % + Texte)
        // Victoire Domicile
        const bWin = document.getElementById('barWin');
        bWin.style.width = data.proba_win + '%';
        bWin.innerText = data.proba_win + '%';
        
        // Match Nul
        const bDraw = document.getElementById('barDraw');
        bDraw.style.width = data.proba_draw + '%';
        bDraw.innerText = data.proba_draw + '%';
        
        // Victoire Extérieur
        const bLoss = document.getElementById('barLoss');
        bLoss.style.width = data.proba_loss + '%';
        bLoss.innerText = data.proba_loss + '%';

        // 7. Tout est prêt, on affiche la boite de résultat !
        resultBox.style.display = 'block';

    } catch (err) {
        console.error("Erreur duel:", err);
        alert("Erreur lors de la simulation du match.");
    }
}

// =========== 20/12/2025 MIR ===============================

// ==========================================
// 6. CLASSEMENT
// ==========================================
/*
async function chargerClassement() {
    const tbody = document.getElementById('rankingBody');
    const startSelect = document.getElementById('startDay');
    const endSelect = document.getElementById('endDay');
    
    const startVal = startSelect ? startSelect.value : 1;
    const endVal = endSelect ? endSelect.value : 8;

    if (parseInt(startVal) > parseInt(endVal)) {
        alert("La journée de début doit être <= à la fin !"); return;
    }

    tbody.innerHTML = '<tr><td colspan="8" class="loading-cell">Calcul en cours...</td></tr>';

    try {
        const response = await fetch('/api/ranking', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start: startVal, end: endVal })
        });
        const data = await response.json();

        if (data.error) {
            tbody.innerHTML = `<tr><td colspan="8" style="color:red">Erreur: ${data.error}</td></tr>`; return;
        }

        tbody.innerHTML = ''; 

        data.forEach(row => {
            const tr = document.createElement('tr');
            
            // Définition de la couleur de la ligne (Zone)
            let rowClass = '';
            if (row.rank <= 8) rowClass = 'zone-top8';
            else if (row.rank <= 24) rowClass = 'zone-barrage';
            else rowClass = 'zone-elim';

            tr.className = rowClass;
            
            // Injection des 8 colonnes (Pas de colonne Zone texte, pas d'Elo)
            tr.innerHTML = `
                <td class="rank-cell"><b>${row.rank}</b></td>
                <td class="club-cell" style="text-align:left;">
                    <div class="club-flex">
                        <img src="logos/${row.club}.png" onerror="this.src='logos/default.png'" class="mini-logo">
                        <span>${row.club}</span>
                    </div>
                </td>
                <td class="points-cell"><b>${row.points}</b></td>
                <td>${row.diff > 0 ? '+' : ''}${row.diff}</td>
                <td>${row.buts}</td>
                <td class="secondary-stat">${row.buts_ext}</td>
                <td>${row.victoires}</td>
                <td class="secondary-stat">${row.victoires_ext}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="8">Erreur connexion.</td></tr>';
    }
}
*/
async function chargerClassement() {
    const tbody = document.getElementById('rankingBody');
    
    // 1. Récupération des valeurs
    const startSelect = document.getElementById('startDay');
    const endSelect = document.getElementById('endDay');
    
    const startVal = parseInt(startSelect.value);
    const endVal = parseInt(endSelect.value);

    // 2. Sécurité : Vérifier l'ordre chronologique
    if (startVal >= endVal) {
        alert(`Impossible de simuler : La journée de fin (J${endVal}) doit être après le départ (J${startVal}).`);
        return;
    }

    tbody.innerHTML = '<tr><td colspan="8" class="loading"><div class="loader small"></div> Calcul en cours...</td></tr>';

    try {
        // 3. Appel API avec les DEUX paramètres
        const response = await fetch('/api/rankings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                start: startVal, 
                end: endVal 
            }) 
        });

        const data = await response.json();
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8">Aucune donnée disponible.</td></tr>';
            return;
        }

        // 4. Affichage du tableau
        data.forEach(row => {
            let rowClass = "";
            if (row.rank <= 8) rowClass = "qualif-direct";
            else if (row.rank <= 24) rowClass = "barrage";
            else rowClass = "elimine";

            tbody.innerHTML += `
                <tr class="${rowClass}">
                    <td>${row.rank}</td>
                    <td class="club-cell">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <img src="logos/${row.club}.png" class="mini-logo" onerror="this.src='logos/default.png'">
                            <strong>${row.club}</strong>
                        </div>
                    </td>
                    <td><strong>${row.points}</strong></td>
                    <td>${row.diff}</td>
                    <td>${row.buts}</td>
                    <td class="secondary-stat">${row.buts_ext}</td>
                    <td>${row.victoires}</td>
                    <td class="secondary-stat">${row.victoires_ext}</td>
                </tr>
            `;
        });
    } catch (error) {
        console.error('Erreur:', error);
        tbody.innerHTML = '<tr><td colspan="8" style="color:red; text-align:center;">Erreur serveur</td></tr>';
    }
}

// ==========================================
// ANALYSE D'IMPACT DES MATCHS
// ==========================================

function switchImpactTab(tabName) {
    // Cacher tous les onglets
    document.querySelectorAll('.impact-tab-content').forEach(tab => tab.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    // Afficher le bon onglet
    if (tabName === 'specific') {
        document.getElementById('impact-specific').style.display = 'block';
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
    } else if (tabName === 'qualif') {
        document.getElementById('impact-qualif').style.display = 'block';
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
    } else if (tabName === 'top8') {
        document.getElementById('impact-top8').style.display = 'block';
        document.querySelectorAll('.tab-btn')[2].classList.add('active');
    }
}
async function analyserImpactMatch() {
    const club = document.getElementById('impactClub').value.trim();
    const journee = parseInt(document.getElementById('impactJournee').value);
    const container = document.getElementById('impactResults');
    
    if (!club) {
        alert('Entrez un nom de club');
        return;
    }
    
    container.innerHTML = '<div class="loading-container"><div class="loader"></div><p>Analyse en cours...</p></div>';
    
    try {
        const response = await fetch('/api/match-impact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ club, journee, journee_donnees: 6 })
        });
        
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<div class="error-msg">❌ ${data.error}</div>`;
            return;
        }
        
        const domicileText = data.domicile ? '🏠 Domicile' : '✈️ Extérieur';
        
        container.innerHTML = `
            <div class="impact-card">
                <h3>${club} vs ${data.adversaire}</h3>
                <p class="match-info">${domicileText} - Journée ${journee}</p>
                
                <div class="scenarios-grid">
                    <div class="scenario-box victoire">
                        <h4>✅ Victoire</h4>
                        <div class="stat-line">
                            <span>Qualification :</span>
                            <strong>${data.impact_victoire.proba_qualif}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Top 8 :</span>
                            <strong>${data.impact_victoire.proba_top8}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Classement moyen :</span>
                            <strong>${data.impact_victoire.classement_moyen}</strong>
                        </div>
                    </div>
                    
                    <div class="scenario-box nul">
                        <h4>⚖️ Match Nul</h4>
                        <div class="stat-line">
                            <span>Qualification :</span>
                            <strong>${data.impact_nul.proba_qualif}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Top 8 :</span>
                            <strong>${data.impact_nul.proba_top8}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Classement moyen :</span>
                            <strong>${data.impact_nul.classement_moyen}</strong>
                        </div>
                    </div>
                    
                    <div class="scenario-box defaite">
                        <h4>❌ Défaite</h4>
                        <div class="stat-line">
                            <span>Qualification :</span>
                            <strong>${data.impact_defaite.proba_qualif}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Top 8 :</span>
                            <strong>${data.impact_defaite.proba_top8}%</strong>
                        </div>
                        <div class="stat-line">
                            <span>Classement moyen :</span>
                            <strong>${data.impact_defaite.classement_moyen}</strong>
                        </div>
                    </div>
                </div>
                
                <div class="gains-box">
                    <h4>📊 Enjeux</h4>
                    <p><strong>Victoire vs Nul :</strong> +${data.gain_victoire_vs_nul.qualif}% qualif, +${data.gain_victoire_vs_nul.top8}% top8</p>
                    <p><strong>Nul vs Défaite :</strong> +${data.gain_nul_vs_defaite.qualif}% qualif, +${data.gain_nul_vs_defaite.top8}% top8</p>
                    <p><strong>Places gagnées (victoire) :</strong> ${data.gain_victoire_vs_nul.classement} places en moyenne</p>
                </div>
            </div>
        `;
        
    } catch (error) {
        container.innerHTML = '<div class="error-msg">❌ Erreur serveur</div>';
    }
}

async function chargerMatchsImportants(type) {
    const container = type === 'qualif' 
        ? document.getElementById('tableQualif') 
        : document.getElementById('tableTop8');
    
    container.innerHTML = '<div class="loading-container"><div class="loader"></div><p>Calcul en cours...</p></div>';
    
    try {
        const response = await fetch('/api/all-matches-impact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ journee: 7, journee_donnees: 6 })
        });
        
        const data = await response.json();
        
        if (data.error) {
            container.innerHTML = `<div class="error-msg">❌ ${data.error}</div>`;
            return;
        }
        
        // Choisir le bon classement
        const matchs = type === 'qualif' ? data.par_qualif : data.par_top8;
        const metrique = type === 'qualif' ? 'impact_qualif' : 'impact_top8';
        const titre = type === 'qualif' ? 'Qualification' : 'Top 8';
        
        let html = `
            <table class="ranking-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Match</th>
                        <th>Impact Global ${titre}</th>
                        <th>Club le + Impacté</th>
                        <th>Impact Max</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        matchs.forEach((match, idx) => {
            html += `
                <tr>
                    <td>${idx + 1}</td>
                    <td style="text-align:left;">${match.match}</td>
                    <td>${match[metrique].global}</td>
                    <td>${match[metrique].club_max}</td>
                    <td>${match[metrique].max}</td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        container.innerHTML = html;
        
    } catch (error) {
        container.innerHTML = '<div class="error-msg">❌ Erreur serveur</div>';
    }
}

// --- FONCTION POUR CHARGER LES PROBAS ---
async function chargerProbas() {
    const day = document.getElementById('probaStartDay').value;
    const tbodyTop8 = document.getElementById('tbodyTop8');
    const tbodyQualif = document.getElementById('tbodyQualif');

    // Afficher le chargement
    const loadingRow = '<tr><td colspan="3" style="text-align:center;"><div class="loader"></div> Calcul...</td></tr>';
    tbodyTop8.innerHTML = loadingRow;
    tbodyQualif.innerHTML = loadingRow;

    try {
        const response = await fetch('/api/probas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ day: parseInt(day) })
        });

        const data = await response.json();

        if (data.error) {
            tbodyTop8.innerHTML = `<tr><td colspan="3" style="color:red">${data.error}</td></tr>`;
            tbodyQualif.innerHTML = `<tr><td colspan="3" style="color:red">${data.error}</td></tr>`;
            return;
        }

        // Fonction utilitaire pour générer les lignes
        const generateRows = (list, colorClass) => {
            if (list.length === 0) return '<tr><td colspan="3">Aucune donnée</td></tr>';
            
            return list.map((item, index) => `
                <tr>
                    <td>${index + 1}</td>
                    <td style="text-align:left; display:flex; align-items:center; gap:10px;">
                        <img src="logos/${item.club}.png" class="mini-logo" onerror="this.src='logos/default.png'">
                        ${item.club}
                    </td>
                    <td>
                        <span class="score-badge ${colorClass}" style="width:50px; display:inline-block;">
                            ${item.proba}%
                        </span>
                    </td>
                </tr>
            `).join('');
        };

        // Remplissage des tableaux
        tbodyTop8.innerHTML = generateRows(data.ranking_top8, 'green-bg');
        tbodyQualif.innerHTML = generateRows(data.ranking_qualif, 'orange-bg');

    } catch (error) {
        console.error(error);
        tbodyTop8.innerHTML = '<tr><td colspan="3">Erreur serveur</td></tr>';
        tbodyQualif.innerHTML = '<tr><td colspan="3">Erreur serveur</td></tr>';
    }
}

//c'est moi ca
// --- FONCTION SCENARIO (DASHBOARD) ---
// GESTION DES ONGLETS
function switchImpactTab(tabName) {
    document.getElementById('impact-specific').style.display = 'none';
    document.getElementById('impact-ranking').style.display = 'none';
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

    if (tabName === 'specific') {
        document.getElementById('impact-specific').style.display = 'block';
        document.querySelector("button[onclick*='specific']").classList.add('active');
    } else {
        document.getElementById('impact-ranking').style.display = 'block';
        document.querySelector("button[onclick*='ranking']").classList.add('active');
    }
}

// FONCTION SCENARIO
async function lancerScenario() {
    const club = document.getElementById('scenarioClub').value;
    const start = document.getElementById('scenarioStartDay').value;
    const target = document.getElementById('scenarioTargetDay').value;
    const res = document.getElementById('scenarioResult').value;
    const box = document.getElementById('scenarioResultBox');

    if(!club) return alert("Club?");
    box.style.display = 'block';
    document.getElementById('scenarioVerdict').innerText = "Simulation...";

    try {
        const rep = await fetch('/api/scenario', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({club:club, start_day:start, day:target, result:res})
        });
        const data = await rep.json();
        if(data.error) return alert(data.error);

        // Mise à jour UI
        document.getElementById('scenarioTitle').innerHTML = `Si <strong>${data.club}</strong> fait <strong>${res}</strong>`;
        document.getElementById('dispTop8').innerText = data.proba_top8+"%";
        document.getElementById('barTop8').style.width = data.proba_top8+"%";
        document.getElementById('dispQualif').innerText = data.proba_qualif+"%";
        document.getElementById('barQualif').style.width = data.proba_qualif+"%";
        
        let v = "❌ Éliminé"; let c = "red";
        if(data.proba_qualif > 99) { v="✅ Qualifié"; c="green"; }
        else if(data.proba_qualif > 50) { v="⚖️ Incertain"; c="orange"; }
        
        const vb = document.getElementById('scenarioVerdict');
        vb.innerText = v; vb.style.borderLeftColor = c;

    } catch(e) { alert(e); }
}

// FONCTION IMPORTANCE
async function chargerImportance() {
    const start = document.getElementById('impStartDay').value;
    const target = document.getElementById('impTargetDay').value;
    const list = document.getElementById('importanceList');
    
    list.innerHTML = "Calcul...";
    try {
        const rep = await fetch('/api/importance', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({start:start, target:target})
        });
        const data = await rep.json();
        list.innerHTML = "";
        
        data.forEach((m, i) => {
            let cls = m.score > 50 ? 'high' : (m.score > 20 ? 'medium' : 'low');
            list.innerHTML += `
                <div class="match-card">
                    <div class="match-info"><strong>#${i+1}</strong> ${m.match} <span class="score-badge ${cls}">${m.score}</span></div>
                    <div class="hype-bar-bg"><div class="hype-bar-fill ${cls}" style="width:${Math.min(m.score,100)}%"></div></div>
                </div>`;
        });
    } catch(e) { list.innerHTML = "Erreur"; }
}

