"""
Deploy All Platforms to Google Cloud Run
Deploys: KaamyabPakistan, YouInvent, HomeFranchise, NoCodeAI + Shared Backend
"""

import subprocess
import sys
import os

PROJECT_ID = 'aialgotradehits'
REGION = 'us-central1'

# Platform configurations
PLATFORMS = {
    'shared-backend': {
        'source': 'shared_backend',
        'service': 'unified-platform-api',
        'port': 8080,
        'memory': '512Mi',
        'cpu': '1',
        'min_instances': 0,
        'max_instances': 10,
    },
    'kaamyabpakistan': {
        'source': 'kaamyabpakistan_app',
        'service': 'kaamyabpakistan',
        'port': 80,
        'memory': '256Mi',
        'domain': 'kaamyabpakistan.org',
    },
    'youinvent': {
        'source': 'youinvent_app',
        'service': 'youinvent',
        'port': 80,
        'memory': '256Mi',
        'domain': 'youinvent.tech',
    },
    'homefranchise': {
        'source': 'homefranchise_app',
        'service': 'homefranchise',
        'port': 80,
        'memory': '256Mi',
        'domain': 'homefranchise.biz',
    },
    'nocodeai': {
        'source': 'nocodeai_app',
        'service': 'nocodeai',
        'port': 80,
        'memory': '256Mi',
        'domain': 'nocodeai.cloud',
    },
}


def run_command(cmd, description):
    """Run a shell command and return success status."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    print(f"  Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def create_frontend_dockerfile(app_dir):
    """Create Dockerfile for static frontend apps."""
    dockerfile_content = """# Static Frontend App
FROM nginx:alpine

# Copy static files
COPY index.html /usr/share/nginx/html/
COPY *.css /usr/share/nginx/html/ 2>/dev/null || true
COPY *.js /usr/share/nginx/html/ 2>/dev/null || true
COPY assets/ /usr/share/nginx/html/assets/ 2>/dev/null || true

# Nginx config for SPA
RUN echo 'server { \\
    listen 80; \\
    server_name _; \\
    root /usr/share/nginx/html; \\
    index index.html; \\
    location / { \\
        try_files $uri $uri/ /index.html; \\
    } \\
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""
    dockerfile_path = os.path.join(app_dir, 'Dockerfile')
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)
    print(f"  Created Dockerfile in {app_dir}")


def deploy_backend():
    """Deploy the shared backend API."""
    config = PLATFORMS['shared-backend']

    cmd = [
        'gcloud', 'run', 'deploy', config['service'],
        '--source', config['source'],
        '--platform', 'managed',
        '--region', REGION,
        '--project', PROJECT_ID,
        '--allow-unauthenticated',
        '--port', str(config['port']),
        '--memory', config['memory'],
        '--cpu', config['cpu'],
        '--min-instances', str(config['min_instances']),
        '--max-instances', str(config['max_instances']),
        '--set-env-vars', f'GCP_PROJECT_ID={PROJECT_ID},BQ_DATASET=kaamyabpakistan_data,NODE_ENV=production',
    ]

    return run_command(cmd, f"Deploying {config['service']} (Shared Backend)")


def deploy_frontend(platform_name):
    """Deploy a frontend app."""
    config = PLATFORMS[platform_name]
    app_dir = config['source']

    # Create Dockerfile if needed
    dockerfile_path = os.path.join(app_dir, 'Dockerfile')
    if not os.path.exists(dockerfile_path):
        create_frontend_dockerfile(app_dir)

    # For KaamyabPakistan, use the new index file
    if platform_name == 'kaamyabpakistan':
        src = os.path.join(app_dir, 'index_new.html')
        dst = os.path.join(app_dir, 'index.html')
        if os.path.exists(src):
            import shutil
            shutil.copy(src, dst)
            print(f"  Copied index_new.html to index.html for deployment")

    cmd = [
        'gcloud', 'run', 'deploy', config['service'],
        '--source', app_dir,
        '--platform', 'managed',
        '--region', REGION,
        '--project', PROJECT_ID,
        '--allow-unauthenticated',
        '--port', str(config['port']),
        '--memory', config['memory'],
    ]

    return run_command(cmd, f"Deploying {config['service']} ({platform_name})")


def get_service_url(service_name):
    """Get the URL of a deployed Cloud Run service."""
    cmd = [
        'gcloud', 'run', 'services', 'describe', service_name,
        '--platform', 'managed',
        '--region', REGION,
        '--project', PROJECT_ID,
        '--format', 'value(status.url)'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def main():
    print("=" * 60)
    print("  UNIFIED PLATFORM DEPLOYMENT")
    print("=" * 60)
    print(f"  Project: {PROJECT_ID}")
    print(f"  Region: {REGION}")
    print("=" * 60)

    results = {}

    # 1. Deploy Backend First
    print("\n[1/5] Deploying Shared Backend API...")
    results['backend'] = deploy_backend()

    # Get backend URL for frontend configuration
    backend_url = get_service_url('unified-platform-api')
    if backend_url:
        print(f"\n  Backend URL: {backend_url}")

    # 2. Deploy Frontends
    frontend_platforms = ['kaamyabpakistan', 'youinvent', 'homefranchise', 'nocodeai']

    for i, platform in enumerate(frontend_platforms, 2):
        print(f"\n[{i}/5] Deploying {platform.upper()}...")
        results[platform] = deploy_frontend(platform)

    # Summary
    print("\n" + "=" * 60)
    print("  DEPLOYMENT SUMMARY")
    print("=" * 60)

    for name, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"  {name}: {status}")

    print("\n" + "-" * 60)
    print("  SERVICE URLS:")
    print("-" * 60)

    services = ['unified-platform-api', 'kaamyabpakistan', 'youinvent', 'homefranchise', 'nocodeai']
    for service in services:
        url = get_service_url(service)
        if url:
            print(f"  {service}: {url}")

    print("\n" + "=" * 60)
    print("  Deployment complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
