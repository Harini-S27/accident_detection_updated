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
# Import Twilio SMS (optional - UI will work without it)
try:
    from twilio_sms import TwilioSMSAlert
    TWILIO_AVAILABLE = True
except Exception as e:
    print(f"[Warning] Twilio SMS not available: {e}")
    TWILIO_AVAILABLE = False
    TwilioSMSAlert = None

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
        
        # Initialize Twilio SMS alert system
        self.sms_alert = None
        if TWILIO_AVAILABLE and TwilioSMSAlert:
            try:
                self.sms_alert = TwilioSMSAlert('twilio_config.json')
            except Exception as e:
                print(f"[SMS] Failed to initialize SMS alerts: {e}")
                self.sms_alert = None
        
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
            # Load model with error handling for version compatibility
            self.update_status("Loading model...")
            try:
                model = YOLO(self.model_path)
            except (AttributeError, RuntimeError, Exception) as model_error:
                error_str = str(model_error)
                # Check if it's a version compatibility issue
                if 'C3k2' in error_str or 'Can\'t get attribute' in error_str:
                    self.update_status("Model version mismatch - using default model...")
                    # Fallback to pretrained model
                    fallback_model = 'yolo11n.pt'
                    if os.path.exists(fallback_model):
                        model = YOLO(fallback_model)
                        self.root.after(0, lambda: messagebox.showwarning(
                            "Model Compatibility Warning",
                            f"Your trained model requires a different Ultralytics version.\n"
                            f"Using default model ({fallback_model}) for now.\n\n"
                            f"To fix: Update ultralytics to match training version:\n"
                            f"pip install --upgrade ultralytics"
                        ))
                    else:
                        raise Exception("Could not load model and fallback not available")
                else:
                    raise model_error
            
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
            
            # Build results text with accident alert
            results_text = (
                f"✅ Processing complete!\n"
                f"📊 Frames processed: {frame_count}\n"
                f"🔍 Total detections: {len(detections)}\n"
                f"🔥 Fire: {fire_count} | ⚠️ Moderate: {moderate_count} | 🚨 Severe: {severe_count}"
            )
            
            # Pass all parameters to processing_complete
            video_name = Path(self.video_path).name if self.video_path else "Unknown"
            self.root.after(0, self.processing_complete, results_text, severe_count, 
                          fire_count, moderate_count, frame_count, video_name)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.processing_error, error_msg)
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def processing_complete(self, results_text, severe_count=0, 
                          fire_count=0, moderate_count=0, frame_count=0, video_name="Unknown"):
        self.progress.stop()
        self.status_label.config(text="✅ Success!", fg='#4CAF50')
        
        # Check if severe accident detected (severe_count >= 1)
        if severe_count >= 1:
            # Display ACCIDENT DETECTED prominently in bold
            accident_alert = "⚠️ ACCIDENT DETECTED ⚠️"
            full_results = f"{accident_alert}\n\n{results_text}"
            
            # Configure results label with bold red styling
            self.results_label.config(
                text=full_results,
                fg='#FF0000',
                font=("Arial", 12, "bold"),
                justify=tk.LEFT
            )
        else:
            # Normal results display
            self.results_label.config(
                text=results_text,
                fg='#333333',
                font=("Arial", 9),
                justify=tk.LEFT
            )
        
        self.upload_btn.config(state=tk.NORMAL)
        self.process_btn.config(state=tk.NORMAL)
        
        if self.output_path:
            self.open_btn.pack(pady=10)
        
        # Handle SMS alerts when severe accident detected
        if severe_count >= 1:
            if self.sms_alert and self.sms_alert.enabled:
                # SMS is enabled - send alert
                try:
                    # Send SMS alert in background thread to avoid blocking UI
                    import threading
                    def send_sms():
                        print("\n[SMS] Severe accident detected - Sending SMS alerts...")
                        sms_results = self.sms_alert.send_accident_alert(
                            video_name=video_name,
                            frame_count=frame_count,
                            fire_count=fire_count,
                            moderate_count=moderate_count,
                            severe_count=severe_count
                        )
                        
                        # Update UI with SMS status
                        if sms_results:
                            success_count = sum(1 for r in sms_results if r['status'] == 'success')
                            failed_count = sum(1 for r in sms_results if r['status'] == 'failed')
                            
                            if success_count > 0:
                                sms_message = f"✅ Success! SMS sent to {success_count} contact(s)"
                                if failed_count > 0:
                                    sms_message += f" (Failed: {failed_count})"
                                
                                # Get contact names
                                contact_phones = [r['phone'] for r in sms_results if r['status'] == 'success']
                                if contact_phones:
                                    sms_message += f"\n📱 Sent to: {', '.join(contact_phones)}"
                                
                                self.root.after(0, lambda msg=sms_message: self.status_label.config(
                                    text=msg,
                                    fg='#4CAF50',
                                    font=("Arial", 10, "bold")
                                ))
                            elif failed_count > 0:
                                # All failed
                                self.root.after(0, lambda: self.status_label.config(
                                    text=f"❌ SMS failed to send to {failed_count} contact(s). Check Twilio credentials.",
                                    fg='#FF0000',
                                    font=("Arial", 10, "bold")
                                ))
                    
                    sms_thread = threading.Thread(target=send_sms)
                    sms_thread.daemon = True
                    sms_thread.start()
                except Exception as e:
                    print(f"[SMS] Error sending SMS: {e}")
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"❌ SMS Error: {str(e)[:50]}",
                        fg='#FF0000'
                    ))
            else:
                # SMS is disabled - show warning in UI
                sms_status = "⚠️ SMS Alerts Disabled - Twilio not configured"
                if self.sms_alert:
                    sms_status += f"\n📱 Contact: +918248450441 (configure in twilio_config.json)"
                
                # Update status label
                current_status = self.status_label.cget('text')
                if current_status and current_status != "✅ Success!":
                    new_status = f"{current_status}\n{sms_status}"
                else:
                    new_status = sms_status
                
                self.status_label.config(
                    text=new_status,
                    fg='#FF8800',
                    font=("Arial", 9, "bold")
                )
                
                print(f"[SMS] Severe accident detected but SMS alerts are disabled")
                print(f"[SMS] Please configure twilio_config.json with your Twilio credentials")
        
        # Show warning dialog if severe accident detected
        if severe_count >= 1:
            messagebox.showwarning(
                "⚠️ ACCIDENT DETECTED ⚠️",
                "SEVERE ACCIDENT DETECTED IN VIDEO!\n\n" + results_text
            )
        else:
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
    try:
        print("=" * 70)
        print("Starting Accident Detection UI...")
        print("=" * 70)
        print()
        
        root = tk.Tk()
        print("✓ Tkinter window created")
        
        # Set window properties
        root.title("Accident Severity Detection - Video Tester")
        root.geometry("700x500")
        
        # Center window on screen
        root.update_idletasks()
        width = 700
        height = 500
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Bring window to front
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
        
        print("✓ Window positioned and brought to front")
        print()
        print("Creating UI components...")
        try:
            app = AccidentDetectionUI(root)
            print("✓ UI components created")
        except Exception as e:
            print(f"❌ ERROR creating UI components: {e}")
            import traceback
            traceback.print_exc()
            input("\nPress Enter to exit...")
            return
        print()
        print("=" * 70)
        print("UI WINDOW SHOULD BE VISIBLE NOW!")
        print("If you don't see it, check:")
        print("  - Taskbar for minimized window")
        print("  - Press Alt+Tab to switch windows")
        print("=" * 70)
        print()
        
        root.mainloop()
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to start UI")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
