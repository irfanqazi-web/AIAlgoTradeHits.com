"""Debug script to inspect search results structure"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
import json

PROJECT_ID = "aialgotradehits"
LOCATION = "global"
ENGINE_ID = "homefranchise-search-engine"
DATA_STORE_ID = "homefranchise-datastore"

def list_documents():
    """List documents in the data store"""
    print("="*60)
    print("Listing indexed documents...")
    print("="*60)

    client_options = ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    client = discoveryengine.DocumentServiceClient(client_options=client_options)

    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{DATA_STORE_ID}/branches/default_branch"

    try:
        docs = client.list_documents(parent=parent)
        count = 0
        for doc in docs:
            count += 1
            print(f"\n{count}. Document ID: {doc.name.split('/')[-1]}")
            if hasattr(doc, 'struct_data') and doc.struct_data:
                data = dict(doc.struct_data)
                for key in ['title', 'link']:
                    if key in data:
                        print(f"   {key}: {data[key]}")

        print(f"\nTotal documents: {count}")
    except Exception as e:
        print(f"Error listing documents: {e}")

def search_debug(query: str):
    """Search and show raw response structure"""
    print("\n" + "="*60)
    print(f"Debug Search: {query}")
    print("="*60)

    client_options = ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    client = discoveryengine.SearchServiceClient(client_options=client_options)

    serving_config = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_config"

    # Simple search request
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=5,
    )

    try:
        response = client.search(request=request)

        # Check summary
        if hasattr(response, 'summary') and response.summary:
            print(f"\nSUMMARY: {response.summary.summary_text[:200]}..." if response.summary.summary_text else "\nSUMMARY: None")

        # Check results
        count = 0
        for result in response.results:
            count += 1
            print(f"\n--- Result {count} ---")
            doc = result.document

            print(f"Doc ID: {doc.id if hasattr(doc, 'id') else 'N/A'}")
            print(f"Doc name: {doc.name if hasattr(doc, 'name') else 'N/A'}")

            if hasattr(doc, 'struct_data') and doc.struct_data:
                data = dict(doc.struct_data)
                print(f"Struct data keys: {list(data.keys())}")
                if 'title' in data:
                    print(f"Title: {data['title']}")
                if 'content' in data:
                    print(f"Content preview: {str(data['content'])[:200]}...")

            if hasattr(doc, 'derived_struct_data') and doc.derived_struct_data:
                derived = dict(doc.derived_struct_data)
                print(f"Derived struct data keys: {list(derived.keys())}")
                if 'snippets' in derived:
                    print(f"Snippets: {derived['snippets']}")
                if 'extractive_answers' in derived:
                    print(f"Extractive answers count: {len(derived['extractive_answers'])}")
                    for i, ans in enumerate(derived['extractive_answers'][:2]):
                        try:
                            # Convert to dict/string
                            ans_dict = dict(ans) if hasattr(ans, 'items') else str(ans)
                            print(f"  Answer {i}: {str(ans_dict)[:300]}...")
                        except Exception as e:
                            print(f"  Answer {i} error: {e}")
                if 'title' in derived:
                    print(f"Derived title: {derived['title']}")
                if 'link' in derived:
                    print(f"Link: {derived['link']}")

        print(f"\nTotal results: {count}")

    except Exception as e:
        print(f"Search error: {e}")

if __name__ == "__main__":
    list_documents()
    search_debug("business plan")
