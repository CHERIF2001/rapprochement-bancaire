import pandas as pd
import os

def load_bank_statements(folder_path):
    """Charge les relevés bancaires à partir d'un dossier dans un DataFrame."""
    combined_df = pd.DataFrame()
    all_statements = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            all_statements.append(df)
    combined_df = pd.concat(all_statements, ignore_index=True)
    return combined_df
