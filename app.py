from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('propulse.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS entrepreneurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        age INTEGER,
        pays TEXT,
        secteur TEXT,
        activite TEXT,
        capital REAL,
        chiffre_affaires REAL,
        anciennete INTEGER,
        difficultes TEXT,
        date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def generer_conseils(difficultes, capital, chiffre_affaires):
    conseils = []
    taux_amelioration = 0

    if 'Financement' in difficultes or 'Manque de financement' in difficultes:
        conseils.append({
            'probleme': 'Manque de financement',
            'conseil': 'Renseignez-vous sur les microcrédits et fonds d\'appui aux jeunes entrepreneurs. Des coopératives locales ou ONG offrent des prêts sans garantie.',
            'impact': 20
        })
        taux_amelioration += 20

    if 'Clients' in difficultes:
        conseils.append({
            'probleme': 'Manque de clients',
            'conseil': 'Utilisez WhatsApp et Facebook pour promouvoir votre activité gratuitement. Offrez une réduction à vos premiers clients pour créer du bouche-à-oreille.',
            'impact': 15
        })
        taux_amelioration += 15

    if 'Visibilité' in difficultes:
        conseils.append({
            'probleme': 'Manque de visibilité',
            'conseil': 'Créez une page Facebook ou Instagram pour votre activité. Publiez des photos régulièrement et inscrivez-vous sur les marchés locaux.',
            'impact': 15
        })
        taux_amelioration += 15

    if 'Concurrence' in difficultes:
        conseils.append({
            'probleme': 'Concurrence difficile',
            'conseil': 'Différenciez-vous avec un service personnalisé ou un programme de fidélité. Misez sur la qualité plutôt que le prix.',
            'impact': 10
        })
        taux_amelioration += 10

    if 'Transport/Livraison' in difficultes:
        conseils.append({
            'probleme': 'Transport et livraison',
            'conseil': 'Proposez la livraison via des moto-taxis locaux. Regroupez vos livraisons par zone pour réduire les coûts.',
            'impact': 10
        })
        taux_amelioration += 10

    if not conseils:
        conseils.append({
            'probleme': 'Optimisation générale',
            'conseil': 'Tenez un carnet de comptes quotidien. Fixez-vous un objectif mensuel et évaluez vos progrès chaque semaine.',
            'impact': 10
        })
        taux_amelioration = 10

    benefice_actuel = chiffre_affaires - capital
    ca_estime = chiffre_affaires * (1 + taux_amelioration / 100)
    benefice_estime = ca_estime - capital
    gain_estime = ca_estime - chiffre_affaires

    return {
        'conseils': conseils,
        'taux_amelioration': taux_amelioration,
        'benefice_actuel': round(benefice_actuel, 0),
        'ca_estime': round(ca_estime, 0),
        'benefice_estime': round(benefice_estime, 0),
        'gain_estime': round(gain_estime, 0)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/soumettre', methods=['POST'])
def soumettre():
    data = request.form
    nom = data['nom']
    age = data['age']
    pays = data['pays']
    secteur = data['secteur']
    activite = data.get('activite', '')
    capital = float(data['capital'])
    chiffre_affaires = float(data['chiffre_affaires'])
    anciennete = data['anciennete']
    difficultes = data.get('difficultes', '')

    conn = sqlite3.connect('propulse.db')
    c = conn.cursor()
    c.execute('''INSERT INTO entrepreneurs
        (nom, age, pays, secteur, activite, capital, chiffre_affaires, anciennete, difficultes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (nom, age, pays, secteur, activite, capital, chiffre_affaires, anciennete, difficultes))
    conn.commit()
    conn.close()

    diagnostic = generer_conseils(difficultes, capital, chiffre_affaires)

    return render_template('resultat.html',
        nom=nom,
        secteur=secteur,
        capital=capital,
        chiffre_affaires=chiffre_affaires,
        difficultes=difficultes,
        diagnostic=diagnostic
    )

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('propulse.db')
    df = pd.read_sql_query("SELECT * FROM entrepreneurs", conn)
    conn.close()
    return render_template('dashboard.html', data=df.to_dict('records'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)