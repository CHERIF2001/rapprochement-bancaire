import pandas as pd
import os
import glob
import json
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(text1, text2):
    """Calcule la similarité cosinus entre deux textes"""
    if pd.isna(text1) or pd.isna(text2):
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer().fit_transform([str(text1), str(text2)])
        vectors = vectorizer.toarray()
        return cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    except:
        return 0.0

def comparer_csv_json(csv_folder, json_folder, output_file, img_folder):
    """Compare les transactions bancaires avec les données extraites des factures"""
    results = []
    
    for csv_file in glob.glob(os.path.join(csv_folder, "*.csv")):
        try:
            df_csv = pd.read_csv(csv_file)
            if df_csv.empty:
                continue
                
            # Conversion des colonnes essentielles
            df_csv['date'] = pd.to_datetime(df_csv['date'], errors='coerce')
            df_csv['amount'] = pd.to_numeric(df_csv['amount'], errors='coerce')
            
            # Vérification des colonnes requises
            if 'vendor' not in df_csv.columns:
                df_csv['vendor'] = ''
            
            for json_file in glob.glob(os.path.join(json_folder, "*.json")):
                with open(json_file, 'r', encoding='utf-8') as f:
                    try:
                        json_data = json.load(f)
                    except json.JSONDecodeError:
                        continue
                
                try:
                    # Vérification des champs requis dans le JSON
                    if not all(k in json_data for k in ['amount', 'date']):
                        continue
                    
                    json_amount = float(json_data['amount'])
                    json_date = datetime.strptime(json_data['date'], '%m/%d/%Y')
                    
                    for _, csv_row in df_csv.iterrows():
                        if pd.isna(csv_row['amount']) or pd.isna(csv_row['date']):
                            continue
                            
                        if abs(float(csv_row['amount']) - json_amount) < 0.01:
                            # Calcul des métriques
                            date_diff = abs((csv_row['date'] - json_date).days)
                            vendor_sim = calculate_similarity(
                                csv_row.get('vendor', ''),
                                json_data.get('vendor', '')
                            )
                            
                            # Recherche de l'image
                            base_name = os.path.splitext(os.path.basename(json_file))[0]
                            img_path = None
                            for ext in ['.jpg', '.jpeg', '.png']:
                                test_path = os.path.join(img_folder, base_name + ext)
                                if os.path.exists(test_path):
                                    img_path = test_path
                                    break
                            
                            # Construction du résultat
                            result = {
                                'csv_file': os.path.basename(csv_file),
                                'json_file': os.path.basename(json_file),
                                'similarity_score': vendor_sim,
                                'date_difference': date_diff,
                                'amount': json_amount,
                                'date': csv_row['date'].strftime('%Y-%m-%d'),
                                'vendor': str(csv_row.get('vendor', ''))
                            }
                            
                            # Ajout du chemin de l'image si trouvée
                            if img_path:
                                result['image_path'] = img_path
                            
                            # Ajout des autres colonnes du CSV
                            for col in csv_row.index:
                                if col not in result:
                                    result[col] = csv_row[col]
                            
                            results.append(result)
                except (ValueError, TypeError, KeyError) as e:
                    continue
        except Exception as e:
            continue
    
    # Sauvegarde des résultats
    if results:
        result_df = pd.DataFrame(results)
        
        # Assure que les colonnes essentielles existent
        if 'similarity_score' not in result_df.columns:
            result_df['similarity_score'] = 0.0
        
        result_df.to_csv(output_file, index=False)
        return True
    return False