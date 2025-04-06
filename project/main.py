import os
import pandas as pd
from dotenv import load_dotenv
from image_processing import needs_enhancement, enhance_image
from receipt_extraction import extract_receipt_data
from bank_statement_processing import load_bank_statements_from_files
from comparaison_data import compare_uploaded_data

def process_uploads(receipts_dir, statements_dir, output_csv):
    """Traite les fichiers uploadés pour le rapprochement"""
    load_dotenv()
    api_key = os.getenv("mistral_key")

    # Préparation des dossiers
    enhanced_dir = os.path.join(os.path.dirname(receipts_dir), "enhanced")
    output_json = os.path.join(os.path.dirname(receipts_dir), "doc_json")
    
    os.makedirs(enhanced_dir, exist_ok=True)
    os.makedirs(output_json, exist_ok=True)

    # Traitement des factures
    for filename in os.listdir(receipts_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(receipts_dir, filename)
            enhanced_path = os.path.join(enhanced_dir, f"enhanced_{filename}")
            
            if needs_enhancement(img_path):
                enhance_image(img_path, enhanced_path)
                img_path = enhanced_path
            
            extract_receipt_data(api_key, img_path, output_json)

    # Traitement des relevés et comparaison
    compare_uploaded_data(statements_dir, output_json, output_csv, receipts_dir)

def search_receipts_from_uploads(csv_path, images_dir):
    """Recherche des images de factures correspondantes à partir des uploads"""
    results = []
    
    try:
        df = pd.read_csv(csv_path)
        
        # Créer un mapping des noms de fichiers sans extension
        image_files = {
            os.path.splitext(f)[0].lower(): os.path.join(images_dir, f)
            for f in os.listdir(images_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        }
        
        for _, row in df.iterrows():
            if pd.notna(row.get('json_file')):
                base_name = os.path.splitext(row['json_file'])[0].lower()
                
                # Chercher l'image correspondante
                img_path = image_files.get(base_name)
                if img_path and os.path.exists(img_path):
                    results.append({
                        **row.to_dict(),
                        'image_path': os.path.basename(img_path)  # Stocker seulement le nom du fichier
                    })
                    
    except Exception as e:
        print(f"Erreur de recherche: {str(e)}")
    
    return results

if __name__ == "__main__":
    # Pour le mode local (test)
    process_uploads("project/images/receipts", "project/bank_statements", 
                   "rapprochement_results.csv")