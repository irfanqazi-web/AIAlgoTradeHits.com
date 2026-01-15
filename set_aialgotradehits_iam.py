"""
Set Cloud Run IAM policies to allow unauthenticated access for aialgotradehits project
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import run_v2
from google.iam.v1 import iam_policy_pb2, policy_pb2

PROJECT_ID = 'aialgotradehits'
REGION = 'us-central1'

SERVICES = [
    'crypto-trading-api',
    'trading-app',
    'ai-trading-intelligence',
    'smart-search',
    'twelvedata-fetcher'
]

def make_service_public(service_name):
    """Make Cloud Run service publicly accessible"""
    print(f"\nMaking {service_name} publicly accessible...")

    client = run_v2.ServicesClient()
    service_path = f"projects/{PROJECT_ID}/locations/{REGION}/services/{service_name}"

    try:
        request = iam_policy_pb2.GetIamPolicyRequest(resource=service_path)
        policy = client.get_iam_policy(request=request)

        binding = policy_pb2.Binding(
            role="roles/run.invoker",
            members=["allUsers"]
        )

        existing_binding = None
        for b in policy.bindings:
            if b.role == "roles/run.invoker":
                existing_binding = b
                break

        if existing_binding:
            if "allUsers" not in existing_binding.members:
                existing_binding.members.append("allUsers")
        else:
            policy.bindings.append(binding)

        set_request = iam_policy_pb2.SetIamPolicyRequest(
            resource=service_path,
            policy=policy
        )
        client.set_iam_policy(request=set_request)
        print(f"OK: {service_name} is now publicly accessible")
        return True

    except Exception as e:
        print(f"ERROR: {service_name} - {e}")
        return False


def main():
    print("Setting Cloud Run IAM for aialgotradehits project")
    print("="*60)

    for service in SERVICES:
        make_service_public(service)

    print("\nDone!")


if __name__ == "__main__":
    main()
