import json

# 1. Ouvrir et lire le fichier JSON
with open("project/images/all_receipts_data.json", "r", encoding='utf-8') as f:
    data = json.load(f)  # Notez json.load() (pour les fichiers) et non json.loads() (pour les strings)

# 2. Afficher avec indentation
print(json.dumps(data, indent=2, ensure_ascii=False))  # ensure_ascii=False pour les caractères spéciaux