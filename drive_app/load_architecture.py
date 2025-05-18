# Import Data Science Libraries
import pandas as pd
import numpy as np
import torch
import open_clip
import albumentations as A
from PIL import Image
import joblib
import os

def load_architecture():
    # Define device
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    
    # Load CLIP model
    model, _, preprocess = open_clip.create_model_and_transforms(
        model_name="ViT-L-14",
        pretrained="laion2b_s32b_b82k",  # OpenCLIP weights
        device=device
    )

    # Define augmentation pipeline
    augment = A.Compose([
        A.RandomRotate90(),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.3),
        A.RandomBrightnessContrast(p=0.3),
        A.GaussianBlur(p=0.2),
        A.ColorJitter(p=0.2),
    ])

    # Get the absolute path to the models directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, 'models')
    
    # Load the trained classifier and label encoder with absolute paths
    classifier_path = os.path.join(models_dir, 'waste_label_classifier.pkl')
    encoder_path = os.path.join(models_dir, 'waste_label_encoder.pkl')
    
    try:
        classifier = joblib.load(classifier_path)
        label_encoder = joblib.load(encoder_path)
    except Exception as e:
        print(f"Error loading models: {str(e)}")
        print(f"Looking for models in: {models_dir}")
        raise

    # Create a wrapper class to maintain compatibility with existing code
    class CLIPWrapper:
        def __init__(self, clip_model, preprocess_fn, classifier, label_encoder, augment, device):
            self.model = clip_model
            self.preprocess = preprocess_fn
            self.classifier = classifier
            self.label_encoder = label_encoder
            self.augment = augment
            self.device = device

        def predict(self, image, n_aug=5, candidate_labels=None):
            try:
                if isinstance(image, str):
                    image = Image.open(image).convert("RGB")
                elif isinstance(image, np.ndarray):
                    image = Image.fromarray(image).convert("RGB")
                
                scores = []
                for _ in range(n_aug):
                    augmented = self.augment(image=np.array(image))["image"]
                    pil_image = Image.fromarray(augmented)
                    
                    preprocessed = self.preprocess(pil_image).unsqueeze(0).to(self.device)
                    with torch.no_grad():
                        features = self.model.encode_image(preprocessed).cpu().numpy()
                    
                    proba = self.classifier.predict_proba(features)
                    scores.append(proba)
                
                avg_proba = np.mean(scores, axis=0)
                predicted_idx = np.argmax(avg_proba)
                predicted_class = self.label_encoder.inverse_transform([predicted_idx])[0]
                
                return predicted_class
            except Exception as e:
                print(f"Error in prediction: {str(e)}")
                return 'failure'

    # Create and return the wrapped model
    wrapped_model = CLIPWrapper(
        clip_model=model,
        preprocess_fn=preprocess,
        classifier=classifier,
        label_encoder=label_encoder,
        augment=augment,
        device=device
    )

    print('CLIP model loaded')
    return wrapped_model