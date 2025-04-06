import pandas as pd
import os
import glob
import json
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(text1, text2):
    if pd.isna(text1) or pd.isna(text2):
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer().fit_transform([str(text1), str(text2)])
        vectors = vectorizer.toarray()
        return cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    except:
        return 0.0

def compare_uploaded_data(csv_folder, json_folder, output_file, img_folder):
    results = []
    
    # Charger tous les relevés bancaires
    bank_df = pd.DataFrame()
    for csv_file in glob.glob(os.path.join(csv_folder, "*.csv")):
        try:
            df = pd.read_csv(csv_file)
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            bank_df = pd.concat([bank_df, df], ignore_index=True)
        except Exception as e:
            print(f"Erreur avec le fichier {csv_file}: {e}")
            continue
    
    if bank_df.empty:
        print("Aucune donnée bancaire valide trouvée")
        return False
    
    # Convertir les colonnes essentielles
    bank_df['date'] = pd.to_datetime(bank_df['date'], errors='coerce')
    bank_df['amount'] = pd.to_numeric(bank_df['amount'], errors='coerce')
    
    # Créer un mapping des images disponibles
    image_files = {
        os.path.splitext(f)[0].lower(): os.path.join(img_folder, f)
        for f in os.listdir(img_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    }
    
    # Traiter chaque fichier JSON de facture
    for json_file in glob.glob(os.path.join(json_folder, "*.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            if not all(k in json_data for k in ['amount', 'date']):
                continue
                
            json_amount = float(json_data['amount'])
            json_date = datetime.strptime(json_data['date'], '%m/%d/%Y')
            
            # Rechercher dans les relevés bancaires
            for _, csv_row in bank_df.iterrows():
                if pd.isna(csv_row['amount']) or pd.isna(csv_row['date']):
                    continue
                    
                if abs(float(csv_row['amount']) - json_amount) < 0.01:
                    date_diff = abs((csv_row['date'] - json_date).days)
                    vendor_sim = calculate_similarity(
                        csv_row.get('vendor', ''),
                        json_data.get('vendor', '')
                    )
                    
                    # Chercher l'image correspondante
                    base_name = os.path.splitext(os.path.basename(json_file))[0].lower()
                    img_path = image_files.get(base_name)
                    
                    # Construction du résultat
                    result = {
                        'json_file': os.path.basename(json_file),
                        'similarity_score': vendor_sim,
                        'date_difference': date_diff,
                        'amount': json_amount,
                        'date': csv_row['date'].strftime('%Y-%m-%d'),
                        'vendor': str(csv_row.get('vendor', ''))
                    }
                    
                    if img_path:
                        result['image_path'] = os.path.basename(img_path)
                    
                    # Ajout des autres colonnes
                    for col in csv_row.index:
                        if col not in result:
                            result[col] = csv_row[col]
                    
                    results.append(result)
                    
        except Exception as e:
            print(f"Erreur avec le fichier {json_file}: {e}")
            continue
    
    # Sauvegarde des résultats
    if results:
        result_df = pd.DataFrame(results)
        result_df.to_csv(output_file, index=False)
        return True
    
    return False