from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import Modele_elo_rating as model
import json
import os

app = Flask(__name__)
CORS(app)  # Autoriser les requêtes cross-origin

# Servir les fichiers statiques
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

# Routes API
@app.route('/api/clubs')
def get_clubs():
    return jsonify(model.clubs_en_ldc)

@app.route('/api/classement/<journee>')
def get_classement(journee):
    # Adapter selon votre modèle
    if journee == 'J7':
        classement = model.générer_classement(données=model.données_J7, debut=8, fin=8)
    elif journee == 'J6':
        classement = model.générer_classement(données=model.données_J6, debut=7, fin=8)
    else:
        classement = model.générer_classement()
    
    return classement.to_json()

@app.route('/api/distribution/<club>/<type_dist>')
def get_distribution(club, type_dist):
    if type_dist == 'position':
        distribution = model.distribution_position_par_club(N=10000)
    else:
        distribution = model.distribution_points_par_club(N=10000)
    
    return jsonify(distribution.get(club, {}))

@app.route('/api/probabilites/<seuil>')
def get_probabilites(seuil):
    distribution = model.distribution_position_par_club(N=10000)
    probas = {}
    
    for club in model.clubs_en_ldc:
        if seuil == 'top8':
            probas[club] = model.proba_top_8(club, distribution)
        else:
            probas[club] = model.proba_qualification(club, distribution)
    
    return jsonify(probas)

@app.route('/api/simuler-match', methods=['POST'])
def simuler_match():
    data = request.json
    club1 = data.get('club1')
    club2 = data.get('club2')
    
    score_moyen = model.score_moyen(club1, club2)
    proba_victoire = model.win_expectation(club1, club2)
    
    return jsonify({
        'score_moyen': score_moyen,
        'proba_victoire1': proba_victoire,
        'proba_victoire2': 1 - proba_victoire,
        'proba_nul': 0.2  # À calculer selon votre modèle
    })

@app.route('/api/enjeux/<journee>')
def get_enjeux(journee):
    j = int(journee)
    enjeux = model.simulation_pour_enjeux(journee=j, données=model.données_J6, debut=7, N=1000)
    return jsonify(enjeux)

if __name__ == '__main__':
    app.run(debug=True, port=5000)