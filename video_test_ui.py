"""
Accident Severity Detection - Video Testing UI
Upload and test videos with a simple GUI interface
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
from ultralytics import YOLO
import cv2
import os

class AccidentDetectionUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Accident Severity Detection - Video Tester")
        self.root.geometry("700x500")
        self.root.configure(bg='#f0f0f0')
        
        # Model path
        self.model_path = "runs/train/accident_severity_yolov11/weights/best.pt"
        self.video_path = None
        self.output_path = None
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title = tk.Label(
            self.root,
            text="🚗 Accident Severity Detection",
            font=("Arial", 20, "bold"),
            bg='#f0f0f0',
            fg='#333333'
        )
        title.pack(pady=20)
        
        # Subtitle
        subtitle = tk.Label(
            self.root,
            text="Upload a video to detect and classify accidents",
            font=("Arial", 11),
            bg='#f0f0f0',
            fg='#666666'
        )
        subtitle.pack(pady=5)
        
        # Frame for file selection
        file_frame = tk.Frame(self.root, bg='#f0f0f0')
        file_frame.pack(pady=30)
        
        # Upload button
        self.upload_btn = tk.Button(
            file_frame,
            text="📁 Select Video File",
            command=self.select_video,
            font=("Arial", 12, "bold"),
            bg='#4CAF50',
            fg='white',
            padx=30,
            pady=15,
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=3
        )
        self.upload_btn.pack()
        
        # Selected file label
        self.file_label = tk.Label(
            self.root,
            text="No file selected",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#888888',
            wraplength=600
        )
        self.file_label.pack(pady=10)
        
        # Confidence threshold
        conf_frame = tk.Frame(self.root, bg='#f0f0f0')
        conf_frame.pack(pady=15)
        
        tk.Label(
            conf_frame,
            text="Confidence Threshold:",
            font=("Arial", 10),
            bg='#f0f0f0'
        ).pack(side=tk.LEFT, padx=5)
        
        self.conf_var = tk.DoubleVar(value=0.5)
        self.conf_scale = tk.Scale(
            conf_frame,
            from_=0.1,
            to=0.9,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.conf_var,
            length=200,
            bg='#f0f0f0'
        )
        self.conf_scale.pack(side=tk.LEFT, padx=5)
        
        self.conf_value = tk.Label(
            conf_frame,
            text="0.5",
            font=("Arial", 10, "bold"),
            bg='#f0f0f0'
        )
        self.conf_value.pack(side=tk.LEFT, padx=5)
        
        self.conf_var.trace('w', self.update_conf_label)
        
        # Process button
        self.process_btn = tk.Button(
            self.root,
            text="🔍 Detect Accidents",
            command=self.process_video,
            font=("Arial", 12, "bold"),
            bg='#2196F3',
            fg='white',
            padx=40,
            pady=15,
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=3,
            state=tk.DISABLED
        )
        self.process_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            orient=tk.HORIZONTAL,
            length=500,
            mode='indeterminate'
        )
        self.progress.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#333333'
        )
        self.status_label.pack(pady=10)
        
        # Results label
        self.results_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 9),
            bg='#f0f0f0',
            fg='#666666',
            justify=tk.LEFT
        )
        self.results_label.pack(pady=5)
        
        # Open output button (hidden initially)
        self.open_btn = tk.Button(
            self.root,
            text="📂 Open Output Video",
            command=self.open_output,
            font=("Arial", 10, "bold"),
            bg='#FF9800',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2'
        )
        
    def update_conf_label(self, *args):
        self.conf_value.config(text=f"{self.conf_var.get():.1f}")
        
    def select_video(self):
        filetypes = (
            ('Video files', '*.mp4 *.avi *.mov *.mkv *.webm'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Select a video file',
            filetypes=filetypes
        )
        
        if filename:
            self.video_path = filename
            self.file_label.config(
                text=f"Selected: {Path(filename).name}",
                fg='#4CAF50'
            )
            self.process_btn.config(state=tk.NORMAL)
            self.status_label.config(text="")
            self.results_label.config(text="")
            if hasattr(self, 'open_btn'):
                self.open_btn.pack_forget()
    
    def process_video(self):
        if not self.video_path:
            messagebox.showwarning("No File", "Please select a video file first!")
            return
        
        # Disable buttons during processing
        self.upload_btn.config(state=tk.DISABLED)
        self.process_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Processing video... Please wait", fg='#2196F3')
        self.progress.start(10)
        
        # Run in thread to keep UI responsive
        thread = threading.Thread(target=self.run_inference)
        thread.daemon = True
        thread.start()
    
    def run_inference(self):
        try:
            # Load model
            self.update_status("Loading model...")
            model = YOLO(self.model_path)
            
            # Run inference
            self.update_status("Detecting accidents in video...")
            conf_threshold = self.conf_var.get()
            
            results = model.predict(
                source=self.video_path,
                conf=conf_threshold,
                save=True,
                project='runs/detect',
                name='video_results',
                exist_ok=True,
                stream=True
            )
            
            # Process results
            frame_count = 0
            detections = []
            
            for r in results:
                frame_count += 1
                boxes = r.boxes
                
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_names = ['fire', 'moderate', 'severe']
                    class_name = class_names[cls]
                    detections.append({
                        'frame': frame_count,
                        'class': class_name,
                        'confidence': conf
                    })
            
            # Find output video
            output_dir = Path('runs/detect/video_results')
            video_files = list(output_dir.glob('*.mp4')) + list(output_dir.glob('*.avi'))
            if video_files:
                self.output_path = str(video_files[0])
            
            # Calculate statistics
            fire_count = sum(1 for d in detections if d['class'] == 'fire')
            moderate_count = sum(1 for d in detections if d['class'] == 'moderate')
            severe_count = sum(1 for d in detections if d['class'] == 'severe')
            
            results_text = (
                f"✅ Processing complete!\n"
                f"📊 Frames processed: {frame_count}\n"
                f"🔍 Total detections: {len(detections)}\n"
                f"🔥 Fire: {fire_count} | ⚠️ Moderate: {moderate_count} | 🚨 Severe: {severe_count}"
            )
            
            self.root.after(0, self.processing_complete, results_text)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.processing_error, error_msg)
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def processing_complete(self, results_text):
        self.progress.stop()
        self.status_label.config(text="✅ Success!", fg='#4CAF50')
        self.results_label.config(text=results_text, fg='#333333')
        self.upload_btn.config(state=tk.NORMAL)
        self.process_btn.config(state=tk.NORMAL)
        
        if self.output_path:
            self.open_btn.pack(pady=10)
        
        messagebox.showinfo(
            "Success",
            "Video processing complete!\n\n" + results_text
        )
    
    def processing_error(self, error_msg):
        self.progress.stop()
        self.status_label.config(text="❌ Error occurred", fg='#f44336')
        self.upload_btn.config(state=tk.NORMAL)
        self.process_btn.config(state=tk.NORMAL)
        messagebox.showerror("Error", error_msg)
    
    def open_output(self):
        if self.output_path and os.path.exists(self.output_path):
            os.startfile(self.output_path)
        else:
            messagebox.showwarning("File Not Found", "Output video file not found!")

def main():
    root = tk.Tk()
    app = AccidentDetectionUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
