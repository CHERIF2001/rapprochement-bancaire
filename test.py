import pandas as pd
import json
import os

# Chemin vers le fichier CSV résultant
results_file = 'resultats_comparaison.csv'

# Lire le fichier CSV résultant
results_df = pd.read_csv(results_file)

# Chemin vers le dossier contenant les fichiers JSON
json_folder = 'project/doc_json'

# Liste pour stocker les différences
differences = []

# Afficher les informations des lignes du CSV et des JSON associés
for _, result in results_df.iterrows():
    print(f"\nCSV File: {result['csv_file']}")
    print(f"Index: {result['index']}")
    print(f"Date: {result['date']}")
    print(f"Amount: {result['amount']}")
    print(f"Currency: {result['currency']}")
    print(f"Vendor: {result['vendor']}")
    print(f"Associated JSON File: {result['json_file']}")

    # Lire et afficher le contenu du JSON associé
    json_path = os.path.join(json_folder, result['json_file'] + '.json')
    if os.path.exists(json_path):
        with open(json_path, 'r') as file:
            json_content = json.load(file)
        
        print("JSON Content:")
        print(json.dumps(json_content, indent=4))
        
        # Comparaison des champs
        diff = {
            'csv_file': result['csv_file'],
            'index': result['index'],
            'json_file': result['json_file'],
            'fields': []
        }
        
        # Comparer date
        csv_date = str(result['date'])
        json_date = json_content.get('date', '')
        if csv_date != json_date:
            diff['fields'].append(('date', csv_date, json_date))
        
        # Comparer amount
        csv_amount = str(result['amount'])
        json_amount = str(json_content.get('amount', ''))
        if csv_amount != json_amount:
            diff['fields'].append(('amount', csv_amount, json_amount))
        
        # Comparer currency
        csv_currency = str(result['currency'])
        json_currency = json_content.get('currency', '')
        if csv_currency != json_currency:
            diff['fields'].append(('currency', csv_currency, json_currency))
        
        # Comparer vendor
        csv_vendor = str(result['vendor'])
        json_vendor = json_content.get('vendor', '')
        if csv_vendor != json_vendor:
            diff['fields'].append(('vendor', csv_vendor, json_vendor))
        
        if diff['fields']:
            differences.append(diff)
    else:
        print("JSON file not found.")
        differences.append({
            'csv_file': result['csv_file'],
            'index': result['index'],
            'json_file': result['json_file'],
            'error': 'JSON file not found'
        })
    
    print("\n" + "="*50)

# Afficher le résumé des différences
if differences:
    print("\n\nRÉSUMÉ DES DIFFÉRENCES:")
    print("="*50)
    for diff in differences:
        print(f"\nFichier CSV: {diff['csv_file']}")
        print(f"Index: {diff['index']}")
        print(f"Fichier JSON: {diff['json_file']}")
        
        if 'error' in diff:
            print(f"ERREUR: {diff['error']}")
        else:
            print("Champs différents:")
            for field, csv_val, json_val in diff['fields']:
                print(f"  {field}:")
                print(f"    CSV -> {csv_val}")
                print(f"    JSON -> {json_val}")
        print("-"*30)
else:
    print("\n\nAucune différence trouvée entre les fichiers CSV et JSON.")