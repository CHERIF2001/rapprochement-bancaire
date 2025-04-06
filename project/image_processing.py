import base64
from PIL import Image, ImageEnhance, ImageStat

def needs_enhancement(image_path, contrast_threshold=30, brightness_threshold=100):
    """Vérifie si l'image a besoin d'être améliorée en fonction du contraste et de la luminosité."""
    try:
        with Image.open(image_path) as img:
            grayscale_img = img.convert("L")
            stat = ImageStat.Stat(grayscale_img)
            contrast = stat.stddev[0]
            brightness = stat.mean[0]
            return contrast < contrast_threshold or brightness < brightness_threshold
    except Exception as e:
        print(f"Erreur lors de la vérification de l'image : {e}")
        return False

def enhance_image(image_path, output_path):
    """Améliore le contraste de l'image."""
    try:
        with Image.open(image_path) as img:
            enhancer = ImageEnhance.Contrast(img)
            enhanced_img = enhancer.enhance(2)
            enhanced_img.save(output_path)
            print(f"Image améliorée sauvegardée à {output_path}")
    except Exception as e:
        print(f"Erreur lors de l'amélioration de l'image : {e}")

def encode_image(image_path):
    """Encode l'image en base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Erreur : Le fichier {image_path} est introuvable.")
        return None
    except Exception as e:
        print(f"Erreur : {e}")
        return None
