"""
Move all files from Aretec OneDrive to Desktop Trading folder
"""
import shutil
import os
from pathlib import Path

source = Path(r"C:\Users\irfan\OneDrive - Aretec, Inc\Desktop\1AITrading\Trading")
destination = Path(r"C:\Users\irfan\Desktop\1AITrading\Trading")

# Create destination if it doesn't exist
destination.mkdir(parents=True, exist_ok=True)

print("="*70)
print("MOVING FILES FROM ARETEC ONEDRIVE TO DESKTOP")
print("="*70)
print(f"\nSource: {source}")
print(f"Destination: {destination}")

# Exclude these directories
exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'dist'}
exclude_files = {'nul', '.DS_Store'}

copied_files = 0
copied_dirs = 0
skipped = 0

for item in source.rglob('*'):
    # Skip excluded directories
    if any(excl in item.parts for excl in exclude_dirs):
        continue

    # Skip excluded files
    if item.name in exclude_files:
        continue

    # Calculate relative path
    relative_path = item.relative_to(source)
    dest_path = destination / relative_path

    try:
        if item.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
            copied_dirs += 1
            if copied_dirs % 10 == 0:
                print(f"Created {copied_dirs} directories...")
        else:
            # Create parent directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(item, dest_path)
            copied_files += 1

            if copied_files % 50 == 0:
                print(f"Copied {copied_files} files...")

    except Exception as e:
        print(f"Error copying {item.name}: {e}")
        skipped += 1

print("\n" + "="*70)
print("COPY COMPLETE")
print("="*70)
print(f"\nDirectories created: {copied_dirs}")
print(f"Files copied: {copied_files}")
print(f"Skipped: {skipped}")
print(f"\nAll files are now in: {destination}")
print("="*70)
