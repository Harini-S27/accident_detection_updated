"""
Simple test to check if UI window appears
"""

import tkinter as tk
import sys

print("=" * 70)
print("Testing UI Window Creation")
print("=" * 70)
print()

try:
    print("1. Creating root window...")
    root = tk.Tk()
    print("   ✓ Root window created")
    
    print("2. Setting window properties...")
    root.title("TEST - Accident Detection UI")
    root.geometry("700x500")
    print("   ✓ Properties set")
    
    print("3. Centering window...")
    root.update_idletasks()
    width = 700
    height = 500
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    print(f"   ✓ Window centered at ({x}, {y})")
    
    print("4. Bringing window to front...")
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, root.attributes, '-topmost', False)
    print("   ✓ Window brought to front")
    
    print("5. Adding test label...")
    label = tk.Label(root, text="TEST WINDOW - If you see this, UI works!", 
                     font=("Arial", 16, "bold"), bg="yellow")
    label.pack(pady=50)
    print("   ✓ Label added")
    
    print()
    print("=" * 70)
    print("WINDOW SHOULD BE VISIBLE NOW!")
    print("If you see a yellow window with text, UI is working!")
    print("=" * 70)
    print()
    print("Press Ctrl+C in this console to close the test window")
    print()
    
    root.mainloop()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")
