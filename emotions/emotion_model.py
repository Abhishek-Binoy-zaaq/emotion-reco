
import torch
import torch.nn as nn
from torchvision import models
import os

def get_model(num_classes=7):
    """
    Creates the ResNet18 model architecture
    """
    # Load ResNet18 structure
    # We use weights=None because we will load our own trained weights
    model = models.resnet18(weights=None)
    
    # Modify the final fully connected layer to match our number of classes
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    
    return model

def load_trained_model(model_path, device=None):
    """
    Loads the trained model from the specified path
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    print(f"Loading emotion model from: {model_path}")
    
    try:
        # Create model architecture
        model = get_model(num_classes=7)
        
        # Load weights
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
            
        checkpoint = torch.load(model_path, map_location=device)
        
        # Handle different checkpoint formats (state_dict vs full checkpoint)
        if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        elif isinstance(checkpoint, dict):
            state_dict = checkpoint
        else:
            raise ValueError("Unknown checkpoint format")
            
        # Load state dict
        model.load_state_dict(state_dict)
        
        # Move to device and set to eval mode
        model.to(device)
        model.eval()
        
        print("✓ Model loaded successfully")
        return model
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None
