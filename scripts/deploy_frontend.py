"""
Deploy trading frontend to Cloud Run
Creates a clean deploy directory with proper timestamps
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(r"C:\1AITrading\Trading\stock-price-app")
DEPLOY_DIR = BASE_DIR / "deploy-clean"
DIST_DIR = BASE_DIR / "dist"

def main():
    print("Creating clean deploy directory...")

    # Remove existing deploy-clean
    if DEPLOY_DIR.exists():
        shutil.rmtree(DEPLOY_DIR)

    DEPLOY_DIR.mkdir()

    # Copy dist contents
    print("Copying dist folder...")
    for item in DIST_DIR.iterdir():
        if item.is_dir():
            shutil.copytree(item, DEPLOY_DIR / item.name)
        else:
            shutil.copy2(item, DEPLOY_DIR / item.name)

    # Copy nginx.conf
    print("Copying nginx.conf...")
    shutil.copy2(BASE_DIR / "nginx.conf", DEPLOY_DIR / "nginx.conf")

    # Create Dockerfile
    print("Creating Dockerfile...")
    dockerfile_content = '''FROM nginx:alpine
COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
'''
    (DEPLOY_DIR / "Dockerfile").write_text(dockerfile_content)

    # Touch all files to set current timestamp
    print("Fixing timestamps...")
    now = datetime.now().timestamp()
    for root, dirs, files in os.walk(DEPLOY_DIR):
        for name in files:
            filepath = Path(root) / name
            os.utime(filepath, (now, now))
        for name in dirs:
            dirpath = Path(root) / name
            os.utime(dirpath, (now, now))

    print(f"\nDeploy directory created at: {DEPLOY_DIR}")
    print("\nContents:")
    for item in DEPLOY_DIR.iterdir():
        print(f"  {item.name}")

    # Deploy to Cloud Run
    print("\nDeploying to Cloud Run...")
    result = subprocess.run([
        "gcloud", "run", "deploy", "trading-app",
        "--source", str(DEPLOY_DIR),
        "--region", "us-central1",
        "--project", "aialgotradehits",
        "--allow-unauthenticated",
        "--port", "8080"
    ], capture_output=True, text=True)

    print(result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr)

    return result.returncode

if __name__ == "__main__":
    exit(main())
