// Données des clubs
const clubs = [
    'Man City', 'Real Madrid', 'Inter', 'Arsenal', 'Leverkusen', 'Bayern', 
    'Barcelona', 'Liverpool', 'Paris SG', 'Dortmund', 'Atalanta', 'RB Leipzig', 
    'Atletico', 'Sporting', 'Juventus', 'Milan', 'Stuttgart', 'PSV', 
    'Girona', 'Aston Villa', 'Monaco', 'Bologna', 'Benfica', 'Lille', 
    'Feyenoord', 'Sparta Praha', 'Brugge', 'Brest', 'Salzburg', 'Celtic', 
    'Sturm Graz', 'Shakhtar', 'Dinamo Zagreb', 'Crvena Zvezda', 'Young Boys', 
    'Slovan Bratislava'
];

// Données simulées (à remplacer par vos données réelles)
let donneesSimulees = {
    classementJ5: [],
    classementJ6: [],
    classementJ7: [],
    classementFinal: [],
    distributions: {},
    probabilitesQualif: {},
    enjeux: {}
};

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    initialiserSelects();
    chargerDonnees();
    configurerEvenements();
});

function initialiserSelects() {
    const clubSelect = document.getElementById('club-select');
    const club1Select = document.getElementById('club1-select');
    const club2Select = document.getElementById('club2-select');
    
    clubs.forEach(club => {
        const option = document.createElement('option');
        option.value = club;
        option.textContent = club;
        
        clubSelect.appendChild(option.cloneNode(true));
        club1Select.appendChild(option.cloneNode(true));
        club2Select.appendChild(option.cloneNode(true));
    });
}

async function chargerDonnees() {
    // Simulation du chargement des données
    // En production, vous chargeriez ces données depuis votre backend
    
    // Générer des données simulées pour la démonstration
    genererDonneesSimulees();
    
    // Mettre à jour l'interface
    mettreAJourClassement();
    mettreAJourDistributions();
    mettreAJourProbabilites();
}

function genererDonneesSimulees() {
    // Générer des classements simulés
    donneesSimulees.classementJ5 = genererClassementAleatoire();
    donneesSimulees.classementJ6 = genererClassementAleatoire();
    donneesSimulees.classementJ7 = genererClassementAleatoire();
    donneesSimulees.classementFinal = genererClassementAleatoire();
    
    // Générer des distributions simulées
    clubs.forEach(club => {
        donneesSimulees.distributions[club] = {
            position: genererDistributionPosition(),
            points: genererDistributionPoints()
        };
        
        donneesSimulees.probabilitesQualif[club] = {
            top8: Math.random() * 100,
            qualif: Math.random() * 100
        };
    });
    
    // Générer des enjeux simulés
    donneesSimulees.enjeux = genererEnjeuxSimules();
}

function genererClassementAleatoire() {
    const classement = [...clubs];
    
    // Mélanger le tableau
    for (let i = classement.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [classement[i], classement[j]] = [classement[j], classement[i]];
    }
    
    return classement.map((club, index) => ({
        position: index + 1,
        club: club,
        points: Math.floor(Math.random() * 25),
        diffButs: Math.floor(Math.random() * 30) - 10,
        buts: Math.floor(Math.random() * 20),
        butsExterieur: Math.floor(Math.random() * 10)
    }));
}

function genererDistributionPosition() {
    const distribution = {};
    for (let i = 1; i <= 36; i++) {
        distribution[i] = Math.random() * 0.1;
    }
    
    // Normaliser
    const total = Object.values(distribution).reduce((a, b) => a + b, 0);
    for (let i = 1; i <= 36; i++) {
        distribution[i] = (distribution[i] / total * 100).toFixed(2);
    }
    
    return distribution;
}

function genererDistributionPoints() {
    const distribution = {};
    for (let i = 0; i <= 24; i++) {
        distribution[i] = Math.random() * 0.1;
    }
    
    // Normaliser
    const total = Object.values(distribution).reduce((a, b) => a + b, 0);
    for (let i = 0; i <= 24; i++) {
        distribution[i] = (distribution[i] / total * 100).toFixed(2);
    }
    
    return distribution;
}

function genererEnjeuxSimules() {
    const enjeux = {};
    clubs.forEach(club => {
        enjeux[club] = {};
        clubs.forEach(autreClub => {
            if (club !== autreClub) {
                enjeux[club][autreClub] = Math.random() * 10;
            }
        });
    });
    return enjeux;
}

function configurerEvenements() {
    document.getElementById('update-classement').addEventListener('click', mettreAJourClassement);
    document.getElementById('update-distribution').addEventListener('click', mettreAJourDistributions);
    document.getElementById('simuler-match').addEventListener('click', simulerMatch);
    document.getElementById('calculer-enjeux').addEventListener('click', afficherEnjeux);
    document.getElementById('seuil-select').addEventListener('change', mettreAJourProbabilites);
}

function mettreAJourClassement() {
    const journee = document.getElementById('journee-select').value;
    let classement;
    
    switch(journee) {
        case 'J5': classement = donneesSimulees.classementJ5; break;
        case 'J6': classement = donneesSimulees.classementJ6; break;
        case 'J7': classement = donneesSimulees.classementJ7; break;
        case 'final': classement = donneesSimulees.classementFinal; break;
        default: classement = donneesSimulees.classementJ7;
    }
    
    const table = document.getElementById('classement-table');
    table.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Position</th>
                    <th>Club</th>
                    <th>Points</th>
                    <th>Diff. Buts</th>
                    <th>Buts</th>
                    <th>Buts Ext.</th>
                </tr>
            </thead>
            <tbody>
                ${classement.map(equipe => `
                    <tr>
                        <td>${equipe.position}</td>
                        <td>${equipe.club}</td>
                        <td>${equipe.points}</td>
                        <td>${equipe.diffButs}</td>
                        <td>${equipe.buts}</td>
                        <td>${equipe.butsExterieur}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function mettreAJourDistributions() {
    const club = document.getElementById('club-select').value;
    const type = document.getElementById('type-distribution').value;
    
    if (!club) return;
    
    const distribution = donneesSimulees.distributions[club][type];
    const ctx = document.getElementById('distribution-chart').getContext('2d');
    
    // Détruire le graphique existant
    if (window.distributionChart) {
        window.distributionChart.destroy();
    }
    
    const labels = Object.keys(distribution);
    const data = Object.values(distribution);
    
    window.distributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `Distribution ${type} - ${club}`,
                data: data,
                backgroundColor: 'rgba(0, 85, 164, 0.7)',
                borderColor: 'rgba(0, 85, 164, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Probabilité (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: type === 'position' ? 'Position au classement' : 'Nombre de points'
                    }
                }
            }
        }
    });
}

function mettreAJourProbabilites() {
    const seuil = document.getElementById('seuil-select').value;
    const ctx = document.getElementById('qualif-chart').getContext('2d');
    
    // Détruire le graphique existant
    if (window.qualifChart) {
        window.qualifChart.destroy();
    }
    
    const clubsTries = Object.keys(donneesSimulees.probabilitesQualif)
        .sort((a, b) => donneesSimulees.probabilitesQualif[b][seuil] - donneesSimulees.probabilitesQualif[a][seuil]);
    
    const labels = clubsTries;
    const data = clubsTries.map(club => donneesSimulees.probabilitesQualif[club][seuil]);
    
    window.qualifChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `Probabilité de ${seuil === 'top8' ? 'Top 8' : 'qualification'} (%)`,
                data: data,
                backgroundColor: clubsTries.map((_, index) => 
                    index < 8 ? 'rgba(239, 65, 53, 0.7)' : 'rgba(0, 85, 164, 0.7)'
                ),
                borderColor: clubsTries.map((_, index) => 
                    index < 8 ? 'rgba(239, 65, 53, 1)' : 'rgba(0, 85, 164, 1)'
                ),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Probabilité (%)'
                    }
                }
            }
        }
    });
}

function simulerMatch() {
    const club1 = document.getElementById('club1-select').value;
    const club2 = document.getElementById('club2-select').value;
    
    if (!club1 || !club2 || club1 === club2) {
        alert('Veuillez sélectionner deux clubs différents');
        return;
    }
    
    // Simulation simple du score
    const score1 = Math.floor(Math.random() * 5);
    const score2 = Math.floor(Math.random() * 5);
    
    document.getElementById('score-simulation').innerHTML = `
        <h4>${club1} ${score1} - ${score2} ${club2}</h4>
    `;
    
    document.getElementById('stats-match').innerHTML = `
        <p>Probabilité de victoire ${club1}: ${(Math.random() * 100).toFixed(1)}%</p>
        <p>Probabilité de match nul: ${(Math.random() * 30).toFixed(1)}%</p>
        <p>Probabilité de victoire ${club2}: ${(Math.random() * 100).toFixed(1)}%</p>
    `;
}

function afficherEnjeux() {
    const journee = document.getElementById('journee-enjeux').value;
    const enjeux = donneesSimulees.enjeux;
    
    let html = '<h3>Enjeux des matchs - Journée ' + journee + '</h3>';
    
    // Prendre un échantillon de clubs pour l'affichage
    const clubsEchantillon = clubs.slice(0, 5);
    
    clubsEchantillon.forEach(club => {
        html += `<h4>${club}</h4>`;
        html += '<table><thead><tr><th>Match</th><th>Impact</th></tr></thead><tbody>';
        
        // Trier les enjeux par impact décroissant
        const matches = Object.keys(enjeux[club])
            .map(autreClub => ({
                match: `${club} - ${autreClub}`,
                impact: enjeux[club][autreClub]
            }))
            .sort((a, b) => b.impact - a.impact)
            .slice(0, 5);
        
        matches.forEach(match => {
            html += `<tr><td>${match.match}</td><td>${match.impact.toFixed(2)}</td></tr>`;
        });
        
        html += '</tbody></table>';
    });
    
    document.getElementById('tableau-enjeux').innerHTML = html;
}