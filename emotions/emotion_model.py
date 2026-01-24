
import torch
import torch.nn as nn
import torch.nn.functional as F
import os

def conv3x3(in_planes, out_planes, stride=1):
    """3x3 convolution with padding"""
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=1, bias=False)

class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = nn.BatchNorm2d(planes)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = nn.BatchNorm2d(planes)
        self.shortcut = downsample  # Renamed from 'downsample' to 'shortcut' to match keys
        self.stride = stride

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.shortcut is not None:
            residual = self.shortcut(x)

        out += residual
        out = self.relu(out)

        return out

class FaceEmotionModel(nn.Module):
    def __init__(self, num_classes=7):
        super(FaceEmotionModel, self).__init__()
        self.inplanes = 64
        
        # Input: 1 channel (Grayscale), 64 filters, 3x3 kernel
        self.conv1 = nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        # No MaxPool
        
        # Layers - Single BasicBlock each (based on keys.txt showing layer1.conv1 not layer1.0.conv1)
        self.layer1 = self._make_layer(BasicBlock, 64, stride=1)
        self.layer2 = self._make_layer(BasicBlock, 128, stride=2)
        self.layer3 = self._make_layer(BasicBlock, 256, stride=2)
        self.layer4 = self._make_layer(BasicBlock, 512, stride=2)
        
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512 * BasicBlock.expansion, num_classes)

    def _make_layer(self, block, planes, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        # IMPORTANT: Only ONE block per layer group
        # This matches keys like 'layer1.conv1' instead of 'layer1.0.conv1'
        layer = block(self.inplanes, planes, stride, downsample)
        self.inplanes = planes * block.expansion
        return layer

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)

        return x

def get_model(num_classes=7):
    return FaceEmotionModel(num_classes=num_classes)

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
            print(f"Strict load failed: {e}. Retrying soft load...")
            model.load_state_dict(state_dict, strict=False)
        
        model.to(device)
        model.eval()
        
        print("✓ Model loaded successfully")
        return model
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None
