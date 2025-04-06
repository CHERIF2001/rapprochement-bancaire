from mistralai import Mistral
import os
import json
from image_processing import encode_image

def read_context():
    """Lit le contenu du fichier context.txt et retourne le texte."""
    try:
        with open("./context.txt", "r", encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Erreur lors de la lecture de context.txt : {e}")
        return None

def extract_receipt_data(api_key, image_path, output_dir="project/doc_json"):
    """Extrait les données d'une facture à partir d'une image."""
    model = "pixtral-large-2411"
    client = Mistral(api_key=api_key)
    
    # Création du dossier de sortie si inexistant
    os.makedirs(output_dir, exist_ok=True)
    
    # Gestion du nom de fichier (supprime 'enhanced_' si présent)
    original_filename = os.path.basename(image_path)
    if original_filename.startswith('enhanced_'):
        json_basename = original_filename.replace('enhanced_', '', 1)
    else:
        json_basename = original_filename
    
    json_filename = f"{os.path.splitext(json_basename)[0]}.json"
    json_path = os.path.join(output_dir, json_filename)

    base64_image = encode_image(image_path)
    if not base64_image:
        return None

    context_text = read_context()
    if not context_text:
        return None

    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": context_text + "\n\nImportant : Retourne uniquement le JSON formaté exactement comme dans l'exemple, sans commentaires ni texte supplémentaire."
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }
            ]
        }
    ]

    try:
        chat_response = client.chat.complete(
            model=model,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        # Récupération et traitement de la réponse
        receipt_data_str = chat_response.choices[0].message.content
        
        # Nettoyage des éventuels caractères d'échappement
        if receipt_data_str.startswith('"') and receipt_data_str.endswith('"'):
            receipt_data_str = receipt_data_str[1:-1].replace('\\"', '"')
        
        # Conversion en dict Python
        receipt_data = json.loads(receipt_data_str)
        
        # Formatage final selon la structure attendue
        formatted_data = {
            "date": receipt_data.get("date", ""),
            "time": receipt_data.get("time", ""),
            "currency": receipt_data.get("currency", ""),
            "vendor": receipt_data.get("vendor", ""),
            "amount": receipt_data.get("amount", ""),
            "adresse": receipt_data.get("adresse", "")
        }
        
        # Sauvegarde dans un fichier JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, indent=4, ensure_ascii=False)
        
        print(f"Données sauvegardées dans {json_path}")
        return formatted_data
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des données de la facture : {e}")
        return None
    """Extrait les données d'une facture à partir d'une image."""
    model = "pixtral-large-2411"
    client = Mistral(api_key=api_key)
    
    # Création du dossier de sortie si inexistant
    os.makedirs(output_dir, exist_ok=True)
    
    json_filename = f"{os.path.splitext(os.path.basename(image_path))[0]}.json"
    json_path = os.path.join(output_dir, json_filename)

    base64_image = encode_image(image_path)
    if not base64_image:
        return None

    context_text = read_context()
    if not context_text:
        return None

    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": context_text + "\n\nImportant : Retourne uniquement le JSON formaté exactement comme dans l'exemple, sans commentaires ni texte supplémentaire."
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }
            ]
        }
    ]

    try:
        chat_response = client.chat.complete(
            model=model,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        # Récupération et traitement de la réponse
        receipt_data_str = chat_response.choices[0].message.content
        
        # Nettoyage des éventuels caractères d'échappement
        if receipt_data_str.startswith('"') and receipt_data_str.endswith('"'):
            receipt_data_str = receipt_data_str[1:-1].replace('\\"', '"')
        
        # Conversion en dict Python
        receipt_data = json.loads(receipt_data_str)
        
        # Formatage final selon la structure attendue
        formatted_data = {
            "date": receipt_data.get("date", ""),
            "time": receipt_data.get("time", ""),
            "currency": receipt_data.get("currency", ""),
            "vendor": receipt_data.get("vendor", ""),
            "amount": receipt_data.get("amount", ""),
            "adresse": receipt_data.get("adresse", "")
        }
        
        # Sauvegarde dans un fichier JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, indent=4, ensure_ascii=False)
        
        print(f"Données sauvegardées dans {json_path}")
        
    except Exception as e:
        print(f"Erreur lors de l'extraction des données de la facture : {e}")
        return None
