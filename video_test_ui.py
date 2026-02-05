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
        self.live_detection_active = False
        self.live_detection_thread = None
        
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
        self.upload_btn.pack(side=tk.LEFT, padx=10)
        
        # Live Detection button
        self.live_detection_btn = tk.Button(
            file_frame,
            text="🔴 Live Detection",
            command=self.start_live_detection,
            font=("Arial", 12, "bold"),
            bg='#FF5722',
            fg='white',
            padx=30,
            pady=15,
            cursor='hand2',
            relief=tk.RAISED,
            borderwidth=3
        )
        self.live_detection_btn.pack(side=tk.LEFT, padx=10)
        
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
    
    def start_live_detection(self):
        """Start live camera detection"""
        if self.live_detection_active:
            messagebox.showinfo("Already Running", "Live detection is already active!")
            return
        
        # Confirm camera access
        response = messagebox.askyesno(
            "Live Detection",
            "This will open your camera for real-time accident detection.\n\n"
            "Continue?"
        )
        if not response:
            return
        
        # Disable buttons
        self.upload_btn.config(state=tk.DISABLED)
        self.live_detection_btn.config(state=tk.DISABLED, text="🔴 Live Detection (Running...)")
        self.process_btn.config(state=tk.DISABLED)
        
        # Update status
        self.status_label.config(text="🔴 Live Detection Active - Camera opening...", fg='#FF5722')
        self.results_label.config(text="", fg='#333333')
        self.progress.start(10)
        
        # Start live detection in separate thread
        self.live_detection_active = True
        self.live_detection_thread = threading.Thread(target=self.run_live_detection)
        self.live_detection_thread.daemon = True
        self.live_detection_thread.start()
    
    def run_live_detection(self):
        """Run live detection from camera"""
        cap = None
        model = None
        
        try:
            # Load model
            self.update_status("Loading model for live detection...")
            try:
                model = YOLO(self.model_path)
            except (AttributeError, RuntimeError, Exception) as model_error:
                error_str = str(model_error)
                if 'C3k2' in error_str or 'Can\'t get attribute' in error_str:
                    fallback_model = 'yolo11n.pt'
                    if os.path.exists(fallback_model):
                        model = YOLO(fallback_model)
                    else:
                        raise Exception("Could not load model")
                else:
                    raise model_error
            
            # Open camera (front camera - index 0)
            self.update_status("Opening front camera...")
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                raise Exception("Could not open camera. Make sure camera is connected and not used by another application.")
            
            # Set camera properties for better quality
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.update_status("🔴 Live Detection Active - Camera window opening...")
            conf_threshold = self.conf_var.get()
            
            # Create named window and set properties
            window_name = 'Accident Detection - Live Camera Feed'
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 800, 600)
            cv2.moveWindow(window_name, 100, 100)  # Position window
            
            frame_count = 0
            detections = []
            severe_detected = False
            sms_sent = False
            
            # Process frames
            while self.live_detection_active:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Run inference on frame
                results = model.predict(
                    source=frame,
                    conf=conf_threshold,
                    verbose=False
                )
                
                # Process detections
                for r in results:
                    boxes = r.boxes
                    frame_severe = False
                    
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
                        
                        if class_name == 'severe':
                            frame_severe = True
                            severe_detected = True
                    
                    # Draw detections on frame
                    annotated_frame = r.plot()
                    
                    # Add status text overlay on video
                    status_text = "LIVE DETECTION - Press 'Q' to stop"
                    text_color = (0, 255, 0)  # Green for normal
                    if frame_severe:
                        status_text = "SEVERE ACCIDENT DETECTED!"
                        text_color = (0, 0, 255)  # Red for severe
                    
                    # Add text background for better visibility
                    (text_width, text_height), baseline = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                    cv2.rectangle(annotated_frame, (5, 5), (text_width + 15, text_height + 20), (0, 0, 0), -1)
                    cv2.putText(annotated_frame, status_text, (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
                    
                    # Add frame count and detection info
                    info_text = f"Frame: {frame_count} | Detections: {len(boxes)}"
                    cv2.putText(annotated_frame, info_text, (10, annotated_frame.shape[0] - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Display frame in the named window
                    cv2.imshow(window_name, annotated_frame)
                    
                    # Bring window to front (Windows specific)
                    try:
                        import win32gui
                        import win32con
                        hwnd = win32gui.FindWindow(None, window_name)
                        if hwnd:
                            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                                 win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, 
                                                 win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                            win32gui.BringWindowToTop(hwnd)
                    except:
                        pass  # If win32gui not available, continue without it
                    
                    # Check for severe accident and send SMS (once)
                    if severe_detected and not sms_sent:
                        # Calculate counts
                        fire_count = sum(1 for d in detections if d['class'] == 'fire')
                        moderate_count = sum(1 for d in detections if d['class'] == 'moderate')
                        severe_count = sum(1 for d in detections if d['class'] == 'severe')
                        
                        # Update UI with accident alert
                        self.root.after(0, self.update_live_accident_detected, 
                                      frame_count, fire_count, moderate_count, severe_count)
                        
                        # Send SMS alert
                        if self.sms_alert and self.sms_alert.enabled:
                            try:
                                self.sms_alert.send_accident_alert(
                                    video_name="Live Camera Feed",
                                    frame_count=frame_count,
                                    fire_count=fire_count,
                                    moderate_count=moderate_count,
                                    severe_count=severe_count
                                )
                                sms_sent = True
                            except Exception as e:
                                print(f"[SMS] Error sending SMS: {e}")
                
                # Check for 'q' or ESC key to stop (waitKey is needed to update window)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC to stop
                    break
                
                # Check if window was closed by user
                try:
                    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                        break
                except:
                    # Window might have been closed
                    break
                
                # Update UI with current stats every 30 frames
                if frame_count % 30 == 0:
                    fire_count = sum(1 for d in detections if d['class'] == 'fire')
                    moderate_count = sum(1 for d in detections if d['class'] == 'moderate')
                    severe_count = sum(1 for d in detections if d['class'] == 'severe')
                    
                    self.root.after(0, self.update_live_status, 
                                  frame_count, fire_count, moderate_count, severe_count)
            
            # Cleanup
            cv2.destroyAllWindows()
            
            # Final update
            fire_count = sum(1 for d in detections if d['class'] == 'fire')
            moderate_count = sum(1 for d in detections if d['class'] == 'moderate')
            severe_count = sum(1 for d in detections if d['class'] == 'severe')
            
            self.root.after(0, self.live_detection_complete, 
                          frame_count, fire_count, moderate_count, severe_count)
            
        except Exception as e:
            error_msg = f"Live detection error: {str(e)}"
            print(f"[Live Detection] {error_msg}")
            self.root.after(0, self.live_detection_error, error_msg)
        finally:
            if cap is not None:
                cap.release()
            cv2.destroyAllWindows()
            self.live_detection_active = False
    
    def update_live_status(self, frame_count, fire_count, moderate_count, severe_count):
        """Update UI with live detection status"""
        status_text = f"🔴 Live: {frame_count} frames | Fire: {fire_count} | Moderate: {moderate_count} | Severe: {severe_count}"
        self.status_label.config(text=status_text, fg='#FF5722')
    
    def update_live_accident_detected(self, frame_count, fire_count, moderate_count, severe_count):
        """Update UI when severe accident detected in live feed"""
        # Display ACCIDENT DETECTED prominently
        accident_alert = "⚠️ ACCIDENT DETECTED ⚠️"
        results_text = (
            f"{accident_alert}\n\n"
            f"🔴 LIVE DETECTION\n"
            f"📊 Frames processed: {frame_count}\n"
            f"🔍 Total detections: {fire_count + moderate_count + severe_count}\n"
            f"🔥 Fire: {fire_count} | ⚠️ Moderate: {moderate_count} | 🚨 Severe: {severe_count}"
        )
        
        self.results_label.config(
            text=results_text,
            fg='#FF0000',
            font=("Arial", 12, "bold"),
            justify=tk.LEFT
        )
        
        self.status_label.config(
            text="⚠️ SEVERE ACCIDENT DETECTED IN LIVE FEED! ⚠️",
            fg='#FF0000',
            font=("Arial", 11, "bold")
        )
        
        # Show warning dialog
        messagebox.showwarning(
            "⚠️ ACCIDENT DETECTED ⚠️",
            f"SEVERE ACCIDENT DETECTED IN LIVE CAMERA FEED!\n\n"
            f"Frames: {frame_count}\n"
            f"Severe: {severe_count}\n"
            f"Moderate: {moderate_count}\n"
            f"Fire: {fire_count}\n\n"
            f"SMS alert has been sent!"
        )
    
    def live_detection_complete(self, frame_count, fire_count, moderate_count, severe_count):
        """Called when live detection stops"""
        self.progress.stop()
        self.live_detection_active = False
        
        # Re-enable buttons
        self.upload_btn.config(state=tk.NORMAL)
        self.live_detection_btn.config(state=tk.NORMAL, text="🔴 Live Detection")
        self.process_btn.config(state=tk.NORMAL)
        
        # Final status
        if severe_count >= 1:
            self.status_label.config(
                text=f"✅ Live detection stopped. Severe accidents detected: {severe_count}",
                fg='#FF0000'
            )
        else:
            self.status_label.config(
                text=f"✅ Live detection stopped. Frames processed: {frame_count}",
                fg='#4CAF50'
            )
        
        messagebox.showinfo(
            "Live Detection Complete",
            f"Live detection stopped.\n\n"
            f"Frames processed: {frame_count}\n"
            f"Fire: {fire_count} | Moderate: {moderate_count} | Severe: {severe_count}"
        )
    
    def live_detection_error(self, error_msg):
        """Handle live detection errors"""
        self.progress.stop()
        self.live_detection_active = False
        
        # Re-enable buttons
        self.upload_btn.config(state=tk.NORMAL)
        self.live_detection_btn.config(state=tk.NORMAL, text="🔴 Live Detection")
        self.process_btn.config(state=tk.NORMAL)
        
        self.status_label.config(text=f"❌ Error: {error_msg[:50]}", fg='#f44336')
        messagebox.showerror("Live Detection Error", error_msg)
        
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
