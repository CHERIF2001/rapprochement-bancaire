import os
import pandas as pd
from dotenv import load_dotenv
from image_processing import needs_enhancement, enhance_image
from receipt_extraction import extract_receipt_data
from bank_statement_processing import load_bank_statements
from comparaison_data import comparer_csv_json

def main(receipts_path, statements_path, output_json, output_csv):
    """Fonction principale de rapprochement"""
    load_dotenv()
    api_key = os.getenv("mistral_key")

    # Préparation des dossiers
    enhanced_dir = os.path.join(os.path.dirname(receipts_path), "enhanced")
    os.makedirs(enhanced_dir, exist_ok=True)
    os.makedirs(output_json, exist_ok=True)

    # Traitement des factures
    for filename in os.listdir(receipts_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(receipts_path, filename)
            enhanced_path = os.path.join(enhanced_dir, f"enhanced_{filename}")
            
            if needs_enhancement(img_path):
                enhance_image(img_path, enhanced_path)
                img_path = enhanced_path
            
            extract_receipt_data(api_key, img_path, output_json)

    # Traitement des relevés
    bank_data = load_bank_statements(statements_path)
    comparer_csv_json(statements_path, output_json, output_csv, receipts_path)

def search_receipts(csv_path, images_dir):
    """Recherche des images de factures correspondantes"""
    results = []
    
    try:
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            if pd.notna(row.get('json_file')):
                base_name = os.path.splitext(row['json_file'])[0]
                for ext in ['.jpg', '.jpeg', '.png']:
                    img_path = os.path.join(images_dir, base_name + ext)
                    if os.path.exists(img_path):
                        results.append({
                            **row.to_dict(),
                            'image_path': img_path
                        })
                        break
    except Exception as e:
        print(f"Erreur de recherche: {str(e)}")
    
    return results

if __name__ == "__main__":
    main("project/images/receipts", "project/bank_statements", 
         "project/doc_json", "rapprochement_results.csv")