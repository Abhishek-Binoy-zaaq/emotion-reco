
import torch
import sys

MODEL_PATH = r'c:\Users\abhis\tutorials\emotions\models\model.pth'

def dump_keys():
    try:
        checkpoint = torch.load(MODEL_PATH, map_location='cpu')
        
        if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
            keys = list(checkpoint['state_dict'].keys())
        elif isinstance(checkpoint, dict):
            keys = list(checkpoint.keys())
        else:
            with open('keys.txt', 'w') as f:
                f.write("Checkpoint is not a dict")
            return

        with open('keys.txt', 'w') as f:
            for key in keys:
                f.write(f"{key}\n")
        
        print("Keys dumped to keys.txt")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_keys()
