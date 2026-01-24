
import torch
import sys

MODEL_PATH = r'c:\Users\abhis\tutorials\emotions\models\model.pth'

def inspect_checkpoint():
    print(f"Inspecting model at: {MODEL_PATH}")
    try:
        checkpoint = torch.load(MODEL_PATH, map_location='cpu')
        
        if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
            print("Checkpoint is a dict with 'state_dict' key.")
            keys = list(checkpoint['state_dict'].keys())
        elif isinstance(checkpoint, dict):
            print("Checkpoint is a dict (likely state_dict itself).")
            keys = list(checkpoint.keys())
        else:
            print("Checkpoint is not a dict.")
            return

        print(f"Total keys: {len(keys)}")
        print("First 20 keys:")
        for key in keys[:20]:
            print(f"  {key}")
            
        print("\nChecking for 'conv1' related keys:")
        for key in keys:
            if 'conv1' in key:
                print(f"  {key}")
                
    except Exception as e:
        print(f"Error loading checkpoint: {e}")

if __name__ == "__main__":
    inspect_checkpoint()
