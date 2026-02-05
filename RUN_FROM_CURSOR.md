# 🚀 How to Run from Cursor IDE

## Method 1: Terminal in Cursor (RECOMMENDED)

1. **Open Terminal in Cursor:**
   - Press `Ctrl + `` (backtick key)
   - OR Go to: **Terminal** → **New Terminal**

2. **Type this command:**
   ```bash
   python video_test_ui.py
   ```

3. **Press Enter**

4. **The UI window should appear!**

---

## Method 2: Run Button

1. **Open `video_test_ui.py`** in the editor
2. **Click the ▶ Run button** at the top right
3. **OR press `F5`**

---

## Method 3: Right-Click Method

1. **In the left sidebar**, find `video_test_ui.py`
2. **Right-click** on it
3. **Select**: "Run Python File in Terminal"

---

## If Window Doesn't Appear

### Check Terminal Output
Look at the terminal for:
- ✅ Success messages: "✓ Tkinter window created", "✓ UI components created"
- ❌ Error messages: Any red error text

### Common Issues:

1. **Window is minimized**
   - Check Windows taskbar
   - Look for "Accident Severity Detection" icon

2. **Window is behind other windows**
   - Press **Alt + Tab** to cycle through windows
   - Look for the UI window

3. **Import error**
   - Check terminal for import errors
   - Run: `pip install -r requirements.txt`

4. **Window opens and closes immediately**
   - There might be an error during UI creation
   - Check terminal for error messages
   - Try: `python run_ui_test.py` for detailed error info

---

## Quick Test

Run this to test if tkinter works:
```bash
python test_ui_simple.py
```

If you see a yellow test window, tkinter is working!

---

## Still Not Working?

Share the terminal output/error messages and I'll help fix it!
