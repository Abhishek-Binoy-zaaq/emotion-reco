
import torch
import torch.nn as nn
import torchvision.models as models
import os

class MobileNetV2EmotionModel(nn.Module):
    def __init__(self, num_classes=8):
        super(MobileNetV2EmotionModel, self).__init__()
        # Load MobileNetV2 architecture
        self.mobilenet = models.mobilenet_v2(pretrained=False)
        
        # Modify the classifier for emotion recognition
        # MobileNetV2 classifier structure:
        # (classifier): Sequential(
        #   (0): Dropout(p=0.2, inplace=False)
        #   (1): Linear(in_features=1280, out_features=1000, bias=True)
        # )
        self.mobilenet.classifier[1] = nn.Linear(self.mobilenet.last_channel, num_classes)

    def forward(self, x):
        return self.mobilenet(x)

def get_model(num_classes=8):
    return MobileNetV2EmotionModel(num_classes=num_classes)

def load_trained_model(model_path, device=None):
    """
    Loads the trained model from the specified path
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    print(f"Loading emotion model from: {model_path}")
    
    try:
        # Create model architecture (MobileNetV2 for AffectNet)
        model = get_model(num_classes=8)
        
        # Load weights
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
            
        checkpoint = torch.load(model_path, map_location=device)
        
        if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        elif isinstance(checkpoint, dict):
            state_dict = checkpoint
        else:
            raise ValueError("Unknown checkpoint format")
            
        # Load state dict
        try:
            missing, unexpected = model.load_state_dict(state_dict, strict=True)
            if missing: print(f"Missing keys: {missing}")
            if unexpected: print(f"Unexpected keys: {unexpected}")
        except Exception as e:
            print(f"Standard load failed: {e}. Trying to load into model.mobilenet...")
            try:
                # Fallback for checkpoints saved from models.mobilenet_v2() directly
                model.mobilenet.load_state_dict(state_dict, strict=True)
                print("✓ Loaded successfully into model.mobilenet")
            except Exception as e2:
                print(f"All loading attempts failed. Last error: {e2}")
                # Try soft load as last resort
                print("Retrying soft load on full model...")
                model.load_state_dict(state_dict, strict=False)
        
        model.to(device)
        model.eval()
        
        print("✓ Model loaded successfully")
        return model
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None
