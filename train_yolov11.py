"""
YOLOv11 Accident Severity Detection - Training Script
Handles both image and video input for accident severity classification
Classes: fire, moderate, severe
"""

from ultralytics import YOLO
import torch
import os

def train_model():
    """Train YOLOv11 model on accident severity detection dataset"""
    
    print("=" * 60)
    print("YOLOv11 Accident Severity Detection - Training")
    print("=" * 60)
    
    # Check for GPU availability
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\nUsing device: {device}")
    if device == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA Version: {torch.version.cuda}")
    
    # Initialize YOLOv11 model
    print("\nInitializing YOLOv11n (nano) model...")
    model = YOLO('yolo11n.pt')  # Start with pretrained YOLOv11 nano model
    
    # Training parameters
    print("\nTraining Configuration:")
    config = {
        'data': 'data.yaml',           # Path to dataset config
        'epochs': 100,                  # Number of training epochs
        'imgsz': 640,                   # Image size (as per preprocessing)
        'batch': 16,                    # Batch size (adjust based on GPU memory)
        'device': device,               # Training device
        'patience': 20,                 # Early stopping patience
        'save': True,                   # Save checkpoints
        'project': 'runs/train',        # Project directory
        'name': 'accident_severity_yolov11',  # Experiment name
        'exist_ok': True,               # Overwrite existing project
        'pretrained': True,             # Use pretrained weights
        'optimizer': 'auto',            # Optimizer (auto, SGD, Adam, AdamW)
        'verbose': True,                # Verbose output
        'seed': 42,                     # Random seed for reproducibility
        'deterministic': True,          # Deterministic mode
        'single_cls': False,            # Multi-class detection
        'rect': False,                  # Rectangular training
        'cos_lr': True,                 # Cosine learning rate scheduler
        'close_mosaic': 10,             # Disable mosaic augmentation for last N epochs
        'resume': False,                # Resume from last checkpoint
        'amp': True,                    # Automatic Mixed Precision training
        'fraction': 1.0,                # Dataset fraction to use
        'profile': False,               # Profile ONNX and TensorRT speeds
        'freeze': None,                 # Freeze layers (None or list of layer indices)
        'lr0': 0.01,                    # Initial learning rate
        'lrf': 0.01,                    # Final learning rate (lr0 * lrf)
        'momentum': 0.937,              # SGD momentum/Adam beta1
        'weight_decay': 0.0005,         # Optimizer weight decay
        'warmup_epochs': 3.0,           # Warmup epochs
        'warmup_momentum': 0.8,         # Warmup initial momentum
        'warmup_bias_lr': 0.1,          # Warmup initial bias lr
        'box': 7.5,                     # Box loss gain
        'cls': 0.5,                     # Class loss gain
        'dfl': 1.5,                     # DFL loss gain
        'pose': 12.0,                   # Pose loss gain
        'kobj': 2.0,                    # Keypoint obj loss gain
        'label_smoothing': 0.0,         # Label smoothing
        'nbs': 64,                      # Nominal batch size
        'hsv_h': 0.015,                 # HSV-Hue augmentation
        'hsv_s': 0.7,                   # HSV-Saturation augmentation
        'hsv_v': 0.4,                   # HSV-Value augmentation
        'degrees': 0.0,                 # Rotation augmentation
        'translate': 0.1,               # Translation augmentation
        'scale': 0.5,                   # Scale augmentation
        'shear': 0.0,                   # Shear augmentation
        'perspective': 0.0,             # Perspective augmentation
        'flipud': 0.0,                  # Flip up-down augmentation
        'fliplr': 0.5,                  # Flip left-right augmentation
        'mosaic': 1.0,                  # Mosaic augmentation
        'mixup': 0.0,                   # Mixup augmentation
        'copy_paste': 0.0,              # Copy-paste augmentation
    }
    
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Start training
    print("\n" + "=" * 60)
    print("Starting Training...")
    print("=" * 60 + "\n")
    
    results = model.train(**config)
    
    # Training complete
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    
    # Validate the model
    print("\nValidating model on test set...")
    metrics = model.val(data='data.yaml', split='test')
    
    print("\n" + "=" * 60)
    print("Test Set Metrics:")
    print("=" * 60)
    print(f"mAP@50: {metrics.box.map50:.4f}")
    print(f"mAP@50-95: {metrics.box.map:.4f}")
    print(f"Precision: {metrics.box.mp:.4f}")
    print(f"Recall: {metrics.box.mr:.4f}")
    
    # Export model to different formats
    print("\n" + "=" * 60)
    print("Exporting Model...")
    print("=" * 60)
    
    # Export to ONNX for deployment
    print("\nExporting to ONNX format...")
    model.export(format='onnx')
    
    print("\n" + "=" * 60)
    print("All Done!")
    print("=" * 60)
    print(f"\nBest model saved at: runs/train/accident_severity_yolov11/weights/best.pt")
    print(f"Last model saved at: runs/train/accident_severity_yolov11/weights/last.pt")
    
    return model

if __name__ == "__main__":
    model = train_model()
