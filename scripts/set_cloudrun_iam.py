"""
Set Cloud Run IAM policies to allow unauthenticated access for Cloud Functions Gen2
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import run_v2
from google.iam.v1 import iam_policy_pb2, policy_pb2

PROJECT_ID = 'cryptobot-462709'
REGION = 'us-central1'

SERVICES = [
    'daily-crypto-fetcher',
    'hourly-crypto-fetcher',
    'fivemin-top10-fetcher'
]

def make_service_public(service_name):
    """Make Cloud Run service publicly accessible"""
    print(f"\n{'='*70}")
    print(f"Making {service_name} publicly accessible...")
    print(f"{'='*70}")

    client = run_v2.ServicesClient()
    service_path = f"projects/{PROJECT_ID}/locations/{REGION}/services/{service_name}"

    try:
        # Get current policy
        request = iam_policy_pb2.GetIamPolicyRequest(resource=service_path)
        policy = client.get_iam_policy(request=request)

        print(f"Current policy: {policy}")

        # Create new binding for allUsers
        binding = policy_pb2.Binding(
            role="roles/run.invoker",
            members=["allUsers"]
        )

        # Check if binding already exists
        existing_binding = None
        for b in policy.bindings:
            if b.role == "roles/run.invoker":
                existing_binding = b
                break

        if existing_binding:
            if "allUsers" not in existing_binding.members:
                existing_binding.members.append("allUsers")
                print(f"Added allUsers to existing invoker role")
            else:
                print(f"✓ allUsers already has invoker role")
        else:
            policy.bindings.append(binding)
            print(f"Added new invoker role binding for allUsers")

        # Set the updated policy
        set_request = iam_policy_pb2.SetIamPolicyRequest(
            resource=service_path,
            policy=policy
        )
        updated_policy = client.set_iam_policy(request=set_request)

        print(f"✓ {service_name} is now publicly accessible")
        print(f"Updated policy: {updated_policy}")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*70)
    print("MAKING CLOUD RUN SERVICES PUBLICLY ACCESSIBLE")
    print("(For Cloud Functions Gen2)")
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
        print("\nYou can now trigger the functions with:")
        print("  curl https://daily-crypto-fetcher-cnyn5l4u2a-uc.a.run.app")
        print("  curl https://hourly-crypto-fetcher-cnyn5l4u2a-uc.a.run.app")
        print("  curl https://fivemin-top10-fetcher-cnyn5l4u2a-uc.a.run.app")
    else:
        print("\n⚠ Some services failed to be made public")


if __name__ == "__main__":
    main()
