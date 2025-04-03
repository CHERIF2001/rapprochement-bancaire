import os
import json
from dotenv import load_dotenv
from image_processing import needs_enhancement, enhance_image, encode_image
from receipt_extraction import extract_receipt_data
from bank_statement_processing import load_bank_statements
from comparaison_data import comparer_csv_json

def main():
    load_dotenv()
    api_key = os.environ["mistral_key"]
    folder_path = "project/images"
    bank_folder_path = "project/bank_statements"
    output_json_path = "project/doc_json"
    output_csv_path = "resultats_comparaison.csv"

    receipts_folder = os.path.join(folder_path, "receipts")
    enhanced_folder = os.path.join(folder_path, "enhanced-receipts")
    os.makedirs(receipts_folder, exist_ok=True)
    os.makedirs(enhanced_folder, exist_ok=True)

    
    # for filename in os.listdir(receipts_folder):
    #     if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
    #         image_path = os.path.join(receipts_folder, filename)
    #         output_path = os.path.join(enhanced_folder, f"enhanced_{filename}")

    #         if needs_enhancement(image_path):
    #             enhance_image(image_path, output_path)
    #             image_to_process = output_path
    #         else:
    #             image_to_process = image_path

    #         extract_receipt_data(api_key, image_to_process)
    bank_df = load_bank_statements(bank_folder_path)
    comparer_csv_json(bank_folder_path, output_json_path,output_csv_path)

if __name__ == "__main__":
    main()
