import pandas as pd
import json
import os
import glob
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_cosine_similarity(text1, text2):
    """Calcule la similarité cosinus entre deux textes."""
    if pd.isna(text1) or pd.isna(text2):
        return 0.0
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity([vectors[0]], [vectors[1]])
    return cosine_sim[0][0]

def parse_json_date(date_str):
    """Convertit une chaîne de caractères en objet datetime."""
    for fmt in ('%m/%d/%Y', '%m/%d/%y'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Format de date inattendu : {date_str}")

def comparer_csv_json(csv_folder, json_folder, output_file):
    """Compare les fichiers CSV et JSON et enregistre les résultats dans un fichier CSV."""
    # Lister tous les fichiers CSV et JSON
    csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))
    json_files = glob.glob(os.path.join(json_folder, '*.json'))

    # Liste pour stocker les résultats
    all_results = []

    # Parcourir chaque fichier CSV
    for csv_file in csv_files:
        csv_data = pd.read_csv(csv_file)
        csv_data['amount'] = pd.to_numeric(csv_data['amount'], errors='coerce')
        csv_data['date'] = pd.to_datetime(csv_data['date'], errors='coerce')

        # Parcourir chaque ligne du CSV
        for index, row in csv_data.iterrows():
            if pd.notnull(row['date']) and pd.notnull(row['amount']):
                # Filtrer les fichiers JSON par montant
                matching_jsons = []
                for json_file in json_files:
                    with open(json_file, 'r') as file:
                        json_data = json.load(file)

                    try:
                        json_amount = float(json_data['amount'])
                        json_date = parse_json_date(json_data['date'])
                        json_name = os.path.splitext(os.path.basename(json_file))[0]
                    except (ValueError, KeyError, TypeError):
                        continue

                    if row['amount'] == json_amount:
                        matching_jsons.append((json_file, json_data, json_date, json_name))

                # Filtrer par devise
                # matching_jsons = [(jf, jd, jdt, jn) for jf, jd, jdt, jn in matching_jsons if row['currency'] == jd['currency']]

                # Trier par date et similarité de lieu
                best_match = None
                best_score = -1
                for json_file, json_data, json_date, json_name in matching_jsons:
                    date_difference = abs((row['date'] - json_date).days)
                    vendor_similarity = calculate_cosine_similarity(row['vendor'], json_data.get('vendor', ''))
                    address_similarity = calculate_cosine_similarity(row['vendor'], json_data.get('adresse', ''))

                    # Calculer un score combiné
                    similarity_score = max(vendor_similarity, address_similarity)
                    date_score = 1 / (date_difference + 1)
                    combined_score = (similarity_score + date_score) / 2

                    if combined_score > best_score:
                        best_score = combined_score
                        best_match = (json_file, json_name, index, combined_score, vendor_similarity, address_similarity, date_difference, row['date'], row['amount'], row['currency'], row['vendor'])

                if best_match:
                    all_results.append({
                        'csv_file': csv_file,
                        'json_file': best_match[1],
                        'index': best_match[2],
                        'combined_score': best_match[3],
                        'vendor_similarity': best_match[4],
                        'address_similarity': best_match[5],
                        'date_difference': best_match[6],
                        'date': best_match[7],
                        'amount': best_match[8],
                        'currency': best_match[9],
                        'vendor': best_match[10]
                    })

    # Convertir les résultats en DataFrame et éliminer les doublons
    results_df = pd.DataFrame(all_results).drop_duplicates(subset=['csv_file', 'json_file', 'index'])

    # Enregistrer les résultats dans un nouveau fichier CSV
    results_df.to_csv(output_file, index=False)
    print(f"Comparaison terminée et résultats enregistrés dans '{output_file}'.")
