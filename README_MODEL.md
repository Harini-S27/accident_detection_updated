# YOLOv11 Accident Severity Detection Model

## Overview
This project trains a YOLOv11 model to detect and classify accident severity levels from images and videos.

**Classes:**
- 🔥 **fire**: Fire-related accidents
- ⚠️ **moderate**: Moderate severity accidents  
- 🚨 **severe**: Severe accidents

**Dataset:**
- Total Images: 9,442
- Train: 6,327 images (67%)
- Valid: 1,892 images (20%)
- Test: 1,223 images (13%)

## Performance Metrics
- mAP@50: 96.8%
- Precision: 96.9%
- Recall: 93.7%

## Installation

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Install PyTorch with GPU Support (Optional but Recommended)
Visit [PyTorch website](https://pytorch.org/get-started/locally/) and install the appropriate version for your system.

For CUDA 11.8:
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

For CUDA 12.1:
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

For CPU only:
```powershell
pip install torch torchvision torchaudio
```

## Training

### Quick Start
```powershell
python train_yolov11.py
```

### Training Parameters
The training script uses the following configuration:
- Model: YOLOv11n (nano - fastest)
- Image Size: 640x640
- Epochs: 100
- Batch Size: 16
- Optimizer: Auto
- Learning Rate: 0.01 (initial) → 0.0001 (final)
- Augmentations: HSV, flip, mosaic, scale, translate

### Model Variants
You can modify the model size in `train_yolov11.py`:
```python
# Options: yolo11n.pt, yolo11s.pt, yolo11m.pt, yolo11l.pt, yolo11x.pt
model = YOLO('yolo11n.pt')  # Change to desired variant
```

| Model | Size | Speed | mAP |
|-------|------|-------|-----|
| YOLOv11n | Smallest | Fastest | Good |
| YOLOv11s | Small | Fast | Better |
| YOLOv11m | Medium | Medium | Great |
| YOLOv11l | Large | Slower | Excellent |
| YOLOv11x | Largest | Slowest | Best |

## Inference

### 1. Single Image
```powershell
python inference.py --source path/to/image.jpg --save
```

### 2. Video File
```powershell
python inference.py --source path/to/video.mp4 --save
```

### 3. Real-time Webcam
```powershell
python inference.py --source 0 --realtime
```

### 4. Batch Processing (Folder)
```powershell
python inference.py --source path/to/folder --save
```

### Advanced Options
```powershell
# Custom confidence threshold
python inference.py --source image.jpg --conf 0.7

# Custom model path
python inference.py --source image.jpg --model path/to/custom/model.pt

# Custom output directory
python inference.py --source image.jpg --save --output my_results
```

## Project Structure
```
Final Year Project/
├── data.yaml                  # Dataset configuration
├── train_yolov11.py          # Training script
├── inference.py              # Inference script
├── requirements.txt          # Dependencies
├── README_MODEL.md           # This file
├── train/                    # Training images & labels
├── valid/                    # Validation images & labels
├── test/                     # Test images & labels
└── runs/
    ├── train/                # Training results
    │   └── accident_severity_yolov11/
    │       ├── weights/
    │       │   ├── best.pt   # Best model checkpoint
    │       │   └── last.pt   # Last model checkpoint
    │       ├── results.png   # Training curves
    │       ├── confusion_matrix.png
    │       └── ...
    └── detect/               # Inference results
        ├── image_results/
        └── video_results/
```

## Usage Examples

### Python API
```python
from inference import AccidentSeverityDetector

# Initialize detector
detector = AccidentSeverityDetector('runs/train/accident_severity_yolov11/weights/best.pt')

# Predict on image
results = detector.predict_image('accident.jpg', conf_threshold=0.5, save=True)

# Predict on video
detections = detector.predict_video('dashcam.mp4', conf_threshold=0.5, save=True)

# Real-time detection
detector.predict_realtime(source=0, conf_threshold=0.5)
```

### Ultralytics CLI
```powershell
# Train
yolo task=detect mode=train model=yolo11n.pt data=data.yaml epochs=100 imgsz=640

# Predict
yolo task=detect mode=predict model=runs/train/accident_severity_yolov11/weights/best.pt source=image.jpg

# Validate
yolo task=detect mode=val model=runs/train/accident_severity_yolov11/weights/best.pt data=data.yaml
```

## Model Export

The training script automatically exports to ONNX format. For other formats:

```python
from ultralytics import YOLO

model = YOLO('runs/train/accident_severity_yolov11/weights/best.pt')

# Export to different formats
model.export(format='onnx')        # ONNX
model.export(format='torchscript') # TorchScript
model.export(format='tensorrt')    # TensorRT
model.export(format='coreml')      # CoreML (iOS)
model.export(format='tflite')      # TensorFlow Lite
```

## Tips for Better Results

1. **GPU Training**: Use a GPU for 10-20x faster training
2. **Data Augmentation**: Already configured in the training script
3. **Early Stopping**: Set with `patience=20` to prevent overfitting
4. **Batch Size**: Increase if you have more GPU memory (e.g., batch=32)
5. **Image Size**: Larger = more accurate but slower (try 1280)
6. **Epochs**: More epochs = better results (try 200-300)

## Troubleshooting

### CUDA Out of Memory
```python
# Reduce batch size in train_yolov11.py
'batch': 8,  # Instead of 16
```

### Slow Training
- Ensure GPU is being used (check output for "Using device: cuda")
- Reduce image size or batch size
- Use smaller model variant (yolo11n.pt)

### Poor Detection Results
- Lower confidence threshold: `--conf 0.3`
- Try different model sizes (m, l, x)
- Train for more epochs

## Performance Monitoring

Training progress can be monitored in real-time:
- Check `runs/train/accident_severity_yolov11/results.png` for training curves
- TensorBoard: `tensorboard --logdir runs/train`

## Citation

If you use this model, please cite:
```
@software{yolov11_ultralytics,
  author = {Glenn Jocher and Jing Qiu},
  title = {Ultralytics YOLOv11},
  year = {2024},
  url = {https://github.com/ultralytics/ultralytics}
}
```

## License
CC BY 4.0

## Contact
For issues or questions, please refer to the Ultralytics documentation: https://docs.ultralytics.com/
