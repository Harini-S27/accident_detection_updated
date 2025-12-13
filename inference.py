"""
YOLOv11 Accident Severity Detection - Inference Script
Handles both image and video input for real-time detection
"""

from ultralytics import YOLO
import cv2
import os
import argparse
from pathlib import Path

class AccidentSeverityDetector:
    """Accident Severity Detector using YOLOv11"""
    
    def __init__(self, model_path='runs/train/accident_severity_yolov11/weights/best.pt'):
        """
        Initialize the detector
        
        Args:
            model_path: Path to trained model weights
        """
        self.model = YOLO(model_path)
        self.classes = ['fire', 'moderate', 'severe']
        self.colors = {
            'fire': (0, 0, 255),      # Red
            'moderate': (0, 165, 255), # Orange
            'severe': (0, 255, 255)    # Yellow
        }
        
    def predict_image(self, image_path, conf_threshold=0.5, save=True, output_dir='runs/detect'):
        """
        Detect accidents in a single image
        
        Args:
            image_path: Path to input image
            conf_threshold: Confidence threshold for detections
            save: Whether to save annotated image
            output_dir: Directory to save results
        """
        print(f"\nProcessing image: {image_path}")
        
        # Run inference
        results = self.model.predict(
            source=image_path,
            conf=conf_threshold,
            save=save,
            project=output_dir,
            name='image_results',
            exist_ok=True
        )
        
        # Display results
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.classes[cls]
                print(f"  Detected: {class_name} (confidence: {conf:.2%})")
        
        return results
    
    def predict_video(self, video_path, conf_threshold=0.5, save=True, output_dir='runs/detect'):
        """
        Detect accidents in a video
        
        Args:
            video_path: Path to input video
            conf_threshold: Confidence threshold for detections
            save: Whether to save annotated video
            output_dir: Directory to save results
        """
        print(f"\nProcessing video: {video_path}")
        
        # Run inference on video
        results = self.model.predict(
            source=video_path,
            conf=conf_threshold,
            save=save,
            project=output_dir,
            name='video_results',
            exist_ok=True,
            stream=True  # Stream for efficient processing
        )
        
        # Process results
        frame_count = 0
        detections = []
        
        for r in results:
            frame_count += 1
            boxes = r.boxes
            
            if len(boxes) > 0:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = self.classes[cls]
                    detections.append({
                        'frame': frame_count,
                        'class': class_name,
                        'confidence': conf
                    })
                    
            if frame_count % 30 == 0:  # Print every 30 frames
                print(f"  Processed {frame_count} frames...")
        
        print(f"\nTotal frames processed: {frame_count}")
        print(f"Total detections: {len(detections)}")
        
        # Summary of detections
        if detections:
            print("\nDetection Summary:")
            for cls in self.classes:
                count = sum(1 for d in detections if d['class'] == cls)
                if count > 0:
                    avg_conf = sum(d['confidence'] for d in detections if d['class'] == cls) / count
                    print(f"  {cls}: {count} detections (avg confidence: {avg_conf:.2%})")
        
        return detections
    
    def predict_realtime(self, source=0, conf_threshold=0.5):
        """
        Real-time detection from webcam or video stream
        
        Args:
            source: Video source (0 for webcam, or video path)
            conf_threshold: Confidence threshold for detections
        """
        print(f"\nStarting real-time detection...")
        print("Press 'q' to quit")
        
        cap = cv2.VideoCapture(source)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Run inference
            results = self.model.predict(frame, conf=conf_threshold, verbose=False)
            
            # Visualize results
            annotated_frame = results[0].plot()
            
            # Display
            cv2.imshow('Accident Severity Detection', annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("Real-time detection stopped.")
    
    def batch_predict(self, input_dir, conf_threshold=0.5, save=True, output_dir='runs/detect'):
        """
        Batch prediction on multiple images/videos
        
        Args:
            input_dir: Directory containing images/videos
            conf_threshold: Confidence threshold
            save: Whether to save results
            output_dir: Output directory
        """
        input_path = Path(input_dir)
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
        # Process images
        images = [f for f in input_path.glob('*') if f.suffix.lower() in image_extensions]
        if images:
            print(f"\nProcessing {len(images)} images...")
            for img in images:
                self.predict_image(str(img), conf_threshold, save, output_dir)
        
        # Process videos
        videos = [f for f in input_path.glob('*') if f.suffix.lower() in video_extensions]
        if videos:
            print(f"\nProcessing {len(videos)} videos...")
            for vid in videos:
                self.predict_video(str(vid), conf_threshold, save, output_dir)

def main():
    parser = argparse.ArgumentParser(description='YOLOv11 Accident Severity Detection')
    parser.add_argument('--model', type=str, 
                       default='runs/train/accident_severity_yolov11/weights/best.pt',
                       help='Path to trained model')
    parser.add_argument('--source', type=str, required=True,
                       help='Path to image/video file, directory, or webcam (0)')
    parser.add_argument('--conf', type=float, default=0.5,
                       help='Confidence threshold')
    parser.add_argument('--save', action='store_true',
                       help='Save results')
    parser.add_argument('--output', type=str, default='runs/detect',
                       help='Output directory')
    parser.add_argument('--realtime', action='store_true',
                       help='Real-time detection mode')
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = AccidentSeverityDetector(args.model)
    
    # Determine input type and process
    if args.realtime:
        source = 0 if args.source == '0' else args.source
        detector.predict_realtime(source, args.conf)
    elif os.path.isfile(args.source):
        # Single file
        ext = os.path.splitext(args.source)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
            detector.predict_image(args.source, args.conf, args.save, args.output)
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            detector.predict_video(args.source, args.conf, args.save, args.output)
        else:
            print(f"Unsupported file format: {ext}")
    elif os.path.isdir(args.source):
        # Directory
        detector.batch_predict(args.source, args.conf, args.save, args.output)
    else:
        print(f"Invalid source: {args.source}")

if __name__ == "__main__":
    main()
