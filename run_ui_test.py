"""
Test script to run UI and catch any errors
"""

import sys
import traceback

print("=" * 70)
print("Testing UI Launch")
print("=" * 70)
print()

try:
    print("Step 1: Importing modules...")
    import tkinter as tk
    print("  ✓ Tkinter imported")
    
    from video_test_ui import AccidentDetectionUI
    print("  ✓ AccidentDetectionUI imported")
    print()
    
    print("Step 2: Creating root window...")
    root = tk.Tk()
    root.title("TEST - Accident Detection")
    root.geometry("700x500")
    print("  ✓ Root window created")
    print()
    
    print("Step 3: Creating UI components...")
    try:
        app = AccidentDetectionUI(root)
        print("  ✓ UI components created")
    except Exception as e:
        print(f"  ❌ ERROR creating UI: {e}")
        traceback.print_exc()
        print()
        print("Window will stay open so you can see the error...")
        error_label = tk.Label(root, text=f"ERROR: {str(e)}", fg='red', font=('Arial', 12))
        error_label.pack(pady=50)
    
    print()
    print("=" * 70)
    print("WINDOW SHOULD BE VISIBLE NOW!")
    print("Close the window to exit.")
    print("=" * 70)
    print()
    
    root.mainloop()
    
except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    traceback.print_exc()
    input("\nPress Enter to exit...")
