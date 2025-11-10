# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from Modele_elo_rating import simulation_pour_enjeux, distribution_par_position, classement_par_adversaires
from results import convert_txt_to_csv

app = Flask(__name__)
CORS(app)

# --- Chargement des données ---
DATA_FILE = "data/csv-cl-2024-2025.csv"
donnees = pd.read_csv(DATA_FILE).to_dict(orient="list")  # adapter selon format attendu

# --- Endpoints ---

@app.route("/simulate", methods=["POST"])
def simulate():
    """
    Body JSON attendu:
    {
        "club": "Paris SG",
        "journee": 7,
        "N": 1000
    }
    """
    data = request.json
    club = data.get("club")
    journee = int(data.get("journee", 1))
    N = int(data.get("N", 1000))

    try:
        enjeux_ = simulation_pour_enjeux(journee=journee, données=donnees, debut=1, demi=True, N=N)
        distribution = distribution_par_position(N=N, données=donnees, debut=1, demi=False)
        return jsonify({
            "success": True,
            "club": club,
            "enjeux": enjeux_.get(club, {}),
            "distribution": distribution.get(club, {})
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/adversaires/<club>", methods=["GET"])
def adversaires(club):
    """
    Retourne les stats cumulées des adversaires pour un club donné
    """
    try:
        df = classement_par_adversaires(données=donnees)
        if club not in df["Clubs"].values:
            return jsonify({"success": False, "error": "Club introuvable"}), 404
        stats = df[df["Clubs"]==club].to_dict(orient="records")[0]
        return jsonify({"success": True, "club": club, "adversaires": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/matchs", methods=["GET"])
def matchs():
    from Modele_elo_rating import calendrier
    return jsonify({"success": True, "calendrier": calendrier})

@app.route("/convert", methods=["POST"])
def convert():
    """
    Convertit un fichier texte en CSV via results.py
    Body JSON attendu:
    {
        "input_file": "path/to/file.txt",
        "output_file": "path/to/output.csv"
    }
    """
    data = request.json
    input_file = data.get("input_file")
    output_file = data.get("output_file")
    try:
        convert_txt_to_csv(input_file=input_file, output_file=output_file)
        return jsonify({"success": True, "message": f"{input_file} converti en {output_file}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- Run Flask ---
if __name__ == "__main__":
    app.run(debug=True)
