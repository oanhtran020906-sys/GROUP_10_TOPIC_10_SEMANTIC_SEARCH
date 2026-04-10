"""
Chạy script insert - Dùng đường dẫn tuyệt đối
Double-click file này để chạy
"""

import subprocess
import sys
import os

# Đường dẫn đến python (dùng anaconda)
python_path = r"C:\Users\TVPC\anaconda3\python.exe"

# Đường dẫn đến script
script_path = os.path.join(os.path.dirname(__file__), "scripts", "insert_products_vector.py")

# Chạy script
print("=" * 50)
print("Running insert_products_vector.py...")
print("=" * 50)

result = subprocess.run([python_path, script_path], capture_output=False)

if result.returncode == 0:
    print("\n✅ Script completed successfully!")
else:
    print(f"\n❌ Script failed with code: {result.returncode}")

input("\nPress Enter to exit...")