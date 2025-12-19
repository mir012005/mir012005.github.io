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
