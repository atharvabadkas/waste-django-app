import re
import requests
from io import BytesIO
from PIL import Image
import numpy as np
from .models import ImageClassificationResult

def extract_wt_from_filename(image_name):
    """
    Extract WT and number from the image filename.
    Example: DT20241115_TM170028_MC64E8337E7884_WT257_TC37_TX36_RN393
    Returns: (WT257, 257)
    """
    match = re.search(r'WT(-?\d+)', image_name)
    if match:
        return match.group(0), int(match.group(1))
    return None, None

def classify_image(image_path, model):
    """
    Classify an image using the provided CLIP model wrapper.
    """
    try:
        # If the path is a URL, download the image first
        if image_path.startswith('http'):
            response = requests.get(image_path)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                image = Image.open(image_data).convert('RGB')
            else:
                print(f"Failed to fetch image. HTTP Status: {response.status_code}")
                return 'failure'
        else:
            image = Image.open(image_path).convert('RGB')

        # Use the CLIP wrapper's predict method
        result = model.predict(image)
        return result
    except Exception as e:
        print(f"Error during classification: {e}")
        return 'failure'

def handle_classification_results(image, result):
    """
    Handle the classification results, flagging images as "SU" or "SK2" based on filename.
    """
    wt, wt_number = extract_wt_from_filename(image['name'])

    if wt_number == 65100001:
        image['classification_flag'] = "SU"  # Proxy image flag
    else:
        image['classification_flag'] = "SK2"  # Weight image flag
    
    # Store result in the database
    ImageClassificationResult.objects.create(
        image_name=image['name'],
        classification_flag=image['classification_flag'],
        classification_status=result
    )

def model_process_images(sets, model):
    """
    Process sets of images using the CLIP model.
    """
    for image_set in sets:
        for image in image_set:
            # Get the image URL from thumbnailLink
            image_url = image['thumbnailLink']
            
            # Classify the image
            classification_result = classify_image(image_url, model)
            
            # Store the classification result
            image['classification_result'] = classification_result

            # Handle classification results
            handle_classification_results(image, classification_result)

    return sets