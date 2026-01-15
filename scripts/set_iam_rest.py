"""
Set Cloud Run IAM policies using REST API to allow unauthenticated access
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.auth import default
from google.auth.transport.requests import AuthorizedSession

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'

SERVICES = [
    'daily-crypto-fetcher',
    'hourly-crypto-fetcher',
    'fivemin-top10-fetcher'
]

def make_service_public(service_name):
    """Make Cloud Run service publicly accessible using REST API"""
    print(f"\n{'='*70}")
    print(f"Making {service_name} publicly accessible...")
    print(f"{'='*70}")

    try:
        # Get credentials
        credentials, project = default()
        authed_session = AuthorizedSession(credentials)

        # Service resource name
        service_resource = f"projects/{PROJECT_ID}/locations/{REGION}/services/{service_name}"

        # Get current IAM policy
        get_url = f"https://run.googleapis.com/v2/{service_resource}:getIamPolicy"
        get_response = authed_session.get(get_url)

        if get_response.status_code != 200:
            print(f"✗ Failed to get current policy: {get_response.status_code}")
            print(f"Response: {get_response.text}")
            return False

        current_policy = get_response.json()
        print(f"Current policy retrieved successfully")

        # Prepare new policy with allUsers as invoker
        bindings = current_policy.get('bindings', [])

        # Check if invoker binding exists
        invoker_binding = None
        for binding in bindings:
            if binding.get('role') == 'roles/run.invoker':
                invoker_binding = binding
                break

        if invoker_binding:
            if 'allUsers' not in invoker_binding.get('members', []):
                invoker_binding['members'].append('allUsers')
                print(f"Added allUsers to existing invoker role")
            else:
                print(f"✓ allUsers already has invoker role")
        else:
            bindings.append({
                'role': 'roles/run.invoker',
                'members': ['allUsers']
            })
            print(f"Created new invoker role binding for allUsers")

        # Update policy
        new_policy = {
            'policy': {
                'bindings': bindings,
                'etag': current_policy.get('etag', '')
            }
        }

        # Set IAM policy
        set_url = f"https://run.googleapis.com/v2/{service_resource}:setIamPolicy"
        set_response = authed_session.post(set_url, json=new_policy)

        if set_response.status_code == 200:
            print(f"✓ {service_name} is now publicly accessible")
            return True
        else:
            print(f"✗ Failed to set policy: {set_response.status_code}")
            print(f"Response: {set_response.text}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*70)
    print("MAKING CLOUD RUN SERVICES PUBLICLY ACCESSIBLE")
    print("(Using REST API for Cloud Functions Gen2)")
    print("="*70)

    results = {}
    for service in SERVICES:
        results[service] = make_service_public(service)

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for service, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {service}")

    if all(results.values()):
        print("\n✓ All services are now publicly accessible!")
        print("\nNow triggering functions to populate BigQuery tables...")
        return True
    else:
        print("\n⚠ Some services failed to be made public")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
