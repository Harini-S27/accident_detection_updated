# 🚀 How to Run the Accident Detection Project

## Quick Start (Easiest Method)

### Option 1: Double-Click Batch File ⭐ RECOMMENDED
1. Navigate to your project folder: `Accident-Detection`
2. Double-click **`RUN_UI.bat`**
3. The UI window will open automatically

### Option 2: Command Line
1. Open **Command Prompt** or **PowerShell**
2. Navigate to project folder:
   ```bash
   cd C:\Users\27har\cursor_clg_project\Accident-Detection
   ```
3. Run the application:
   ```bash
   python video_test_ui.py
   ```

### Option 3: Debug Mode (If having issues)
1. Double-click **`START_UI_DEBUG.bat`**
2. This shows detailed startup information
3. Helps identify any errors

---

## What You'll See

When the application starts, you'll see:

**UI Window:**
- Title: "Accident Severity Detection - Video Tester"
- Two buttons at the top:
  - 🟢 **"📁 Select Video File"** - Upload and process videos
  - 🔴 **"🔴 Live Detection"** - Real-time detection (coming soon)
- Confidence threshold slider
- Blue "🔍 Detect Accidents" button
- Results display area

---

## Using the Application

### Step 1: Select a Video
- Click **"📁 Select Video File"**
- Choose a video file (.mp4, .avi, .mov, etc.)
- File name will appear below the button

### Step 2: Adjust Settings (Optional)
- Move the **Confidence Threshold** slider
- Default: 0.5 (50%)
- Higher = fewer but more confident detections
- Lower = more detections but may include false positives

### Step 3: Detect Accidents
- Click **"🔍 Detect Accidents"**
- Wait for processing (progress bar will show)
- Results will appear when complete

### Step 4: View Results
- If severe accident detected: **"⚠️ ACCIDENT DETECTED ⚠️"** in bold red
- Statistics shown: frames, detections, severity counts
- SMS alert automatically sent to +918248450441 (if configured)
- Click **"📂 Open Output Video"** to see annotated video

---

## Requirements

Before running, make sure you have:

✅ **Python 3.8+** installed
- Check: `python --version`

✅ **Required packages** installed:
```bash
pip install -r requirements.txt
```

✅ **Trained model** available:
- Location: `runs/train/accident_severity_yolov11/weights/best.pt`
- If missing, the app will use default model

✅ **Twilio configured** (optional, for SMS alerts):
- File: `twilio_config.json`
- See `TWILIO_SETUP.md` for setup instructions

---

## Troubleshooting

### ❌ Window doesn't appear?
1. Check taskbar for minimized window
2. Press **Alt+Tab** to switch windows
3. Check console for error messages
4. Try `START_UI_DEBUG.bat` for detailed info

### ❌ Import errors?
```bash
pip install -r requirements.txt
```

### ❌ Model not found?
- App will use default YOLO model
- To train your own: `python train_yolov11.py`

### ❌ SMS not working?
- Check `twilio_config.json` is configured
- See `TWILIO_SETUP.md` for setup
- SMS is optional - app works without it

---

## Project Structure

```
Accident-Detection/
├── video_test_ui.py          # Main UI application ⭐
├── RUN_UI.bat                # Quick launcher ⭐
├── inference.py              # Command-line inference
├── train_yolov11.py          # Training script
├── twilio_sms.py             # SMS alert system
├── requirements.txt          # Dependencies
└── runs/train/.../best.pt    # Trained model
```

---

## Quick Commands

```bash
# Run UI
python video_test_ui.py

# Or use batch file
RUN_UI.bat

# Test Twilio (if configured)
python test_twilio.py

# Train model
python train_yolov11.py

# Test model
python test_model.py
```

---

**That's it! Just double-click `RUN_UI.bat` and you're ready to go!** 🚀
