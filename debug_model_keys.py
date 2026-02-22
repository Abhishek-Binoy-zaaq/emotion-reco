
import sys
import os
import torch
import numpy as np

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') 
import django
django.setup()

from emotions.emotion_model import load_trained_model

def verify_fix():
    model_path = r'c:\Users\abhis\tutorials\emotions\models\affectnet_mobilenet_v2_best.pth'
    
    print(f"Testing load_trained_model with: {model_path}")
    
    model = load_trained_model(model_path)
    
    if model:
        print("\nModel returned successfully.")
        
        # Test inference
        model.eval()
        dummy_input = torch.randn(1, 3, 224, 224)
        if torch.cuda.is_available():
            dummy_input = dummy_input.cuda()
            
        with torch.no_grad():
            output = model(dummy_input)
            probs = torch.nn.functional.softmax(output, dim=1)
            conf, idx = torch.max(probs, 1)
            
        print(f"Inference successful.")
        print(f"Max Prob: {conf.item()}")
        print(f"Class Idx: {idx.item()}")
        
        if conf.item() > 0.15: # Random for 8 classes is 0.125. 0.15 is slightly better but noise input is unpredictable.
             print("Confidence seems reasonable for noise (not uniform 0.125)")
    else:
        print("Model failed to load.")

if __name__ == "__main__":
    verify_fix()


if __name__ == "__main__":
    verify_fix()
