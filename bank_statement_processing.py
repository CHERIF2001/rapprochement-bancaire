import pandas as pd
import os

def load_bank_statements_from_files(folder_path):
    """Charge les relevés bancaires à partir d'un dossier temporaire d'uploads"""
    combined_df = pd.DataFrame()
    all_statements = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            try:
                df = pd.read_csv(file_path)
                # Standardisation des noms de colonnes
                df.columns = df.columns.str.lower().str.replace(' ', '_')
                all_statements.append(df)
            except Exception as e:
                print(f"Erreur lors de la lecture de {filename}: {e}")
    
    if all_statements:
        combined_df = pd.concat(all_statements, ignore_index=True)
    
    return combined_df