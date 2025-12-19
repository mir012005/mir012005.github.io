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