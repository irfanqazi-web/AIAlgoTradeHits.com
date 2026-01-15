"""
Fix file timestamps for files before 1980 (ZIP compatibility issue)
"""
import os
import sys
from datetime import datetime

def fix_timestamps(directory):
    """Fix timestamps for all files in directory before 1980"""
    min_date = datetime(1980, 1, 2)
    new_time = datetime(2024, 1, 1).timestamp()
    fixed = 0
    errors = 0

    for root, dirs, files in os.walk(directory):
        for name in files + dirs:
            path = os.path.join(root, name)
            try:
                stat = os.stat(path)
                mtime = datetime.fromtimestamp(stat.st_mtime)
                if mtime < min_date:
                    os.utime(path, (new_time, new_time))
                    fixed += 1
            except Exception as e:
                errors += 1
                continue

    return fixed, errors

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else r"C:\1AITrading\Trading\stock-price-app\node_modules"
    print(f"Fixing timestamps in: {target}")
    fixed, errors = fix_timestamps(target)
    print(f"Fixed {fixed} files, {errors} errors")
