"""
HomeFranchise RAG Setup with Vertex AI Search and Gemini 2.5 Pro
Uses Discovery Engine for document indexing and Gemini for generation
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import time
from google.cloud import discoveryengine_v1 as discoveryengine
from google.cloud import storage
from google.api_core.client_options import ClientOptions
from google import genai
from google.genai import types

# Configuration
PROJECT_ID = "aialgotradehits"
LOCATION = "global"  # Discovery Engine uses global location
BUCKET_NAME = "homefranchise-documents"
DATA_STORE_ID = "homefranchise-datastore"
ENGINE_ID = "homefranchise-search-engine"

def create_data_store():
    """Create a Vertex AI Search data store"""
    print("Creating Vertex AI Search Data Store...")

    client_options = ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    client = discoveryengine.DataStoreServiceClient(client_options=client_options)

    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"

    data_store = discoveryengine.DataStore(
        display_name="HomeFranchise Documents",
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
    )

    request = discoveryengine.CreateDataStoreRequest(
        parent=parent,
        data_store=data_store,
        data_store_id=DATA_STORE_ID,
    )

    try:
        operation = client.create_data_store(request=request)
        print("Waiting for data store creation...")
        response = operation.result(timeout=300)
        print(f"Data store created: {response.name}")
        return response
    except Exception as e:
        if "already exists" in str(e):
            print(f"Data store already exists: {DATA_STORE_ID}")
            return client.get_data_store(
                name=f"{parent}/dataStores/{DATA_STORE_ID}"
            )
        raise e

def import_documents():
    """Import documents from GCS to the data store"""
    print("\nImporting documents from GCS bucket...")

    client_options = ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    client = discoveryengine.DocumentServiceClient(client_options=client_options)

    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{DATA_STORE_ID}/branches/default_branch"

    # GCS source configuration
    gcs_source = discoveryengine.GcsSource(
        input_uris=[
            f"gs://{BUCKET_NAME}/app_docs/*",
            f"gs://{BUCKET_NAME}/franchise_plans/*"
        ],
        data_schema="content"  # Use unstructured content schema
    )

    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=gcs_source,
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )

    try:
        operation = client.import_documents(request=request)
        print("Document import started. This may take several minutes...")
        response = operation.result(timeout=600)
        print(f"Import completed: {response}")
        return response
    except Exception as e:
        print(f"Import error: {e}")
        raise e

def create_search_engine():
    """Create a search engine for the data store"""
    print("\nCreating Search Engine...")

    client_options = ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    client = discoveryengine.EngineServiceClient(client_options=client_options)

    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection"

    engine = discoveryengine.Engine(
        display_name="HomeFranchise Search Engine",
        solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
        search_engine_config=discoveryengine.Engine.SearchEngineConfig(
            search_tier=discoveryengine.SearchTier.SEARCH_TIER_ENTERPRISE,
            search_add_ons=[discoveryengine.SearchAddOn.SEARCH_ADD_ON_LLM],
        ),
        data_store_ids=[DATA_STORE_ID],
    )

    request = discoveryengine.CreateEngineRequest(
        parent=parent,
        engine=engine,
        engine_id=ENGINE_ID,
    )

    try:
        operation = client.create_engine(request=request)
        print("Waiting for engine creation...")
        response = operation.result(timeout=600)
        print(f"Engine created: {response.name}")
        return response
    except Exception as e:
        if "already exists" in str(e):
            print(f"Engine already exists: {ENGINE_ID}")
            return None
        raise e

def search_documents(query: str, num_results: int = 10):
    """Search the data store"""
    print(f"\nSearching for: {query}")

    client_options = ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    client = discoveryengine.SearchServiceClient(client_options=client_options)

    serving_config = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{DATA_STORE_ID}/servingConfigs/default_config"

    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=num_results,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True,
                max_snippet_count=3,
            ),
            summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=5,
                include_citations=True,
                model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                    version="stable"
                ),
            ),
            extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                max_extractive_answer_count=3,
                max_extractive_segment_count=3,
            ),
        ),
    )

    try:
        response = client.search(request=request)
        return response
    except Exception as e:
        print(f"Search error: {e}")
        return None

def query_with_gemini(context: str, query: str) -> str:
    """Use Gemini 2.5 Pro to generate response with RAG context"""

    # Initialize client with Vertex AI
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="us-central1"
    )

    prompt = f"""Based on the following franchise document context, answer the question.

CONTEXT FROM FRANCHISE DOCUMENTS:
{context}

QUESTION: {query}

Provide a comprehensive answer based on the document context. Include specific references to documents when possible.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Gemini error: {e}"

def rag_query(query: str) -> dict:
    """Combined RAG query: search documents + generate response"""
    print(f"\n{'='*60}")
    print(f"RAG Query: {query}")
    print('='*60)

    # Step 1: Search documents
    search_response = search_documents(query)

    if not search_response:
        return {"error": "Search failed", "query": query}

    # Step 2: Extract context from search results
    context_parts = []
    results_info = []

    if hasattr(search_response, 'summary') and search_response.summary:
        context_parts.append(f"Summary: {search_response.summary.summary_text}")

    for result in search_response.results:
        doc = result.document
        doc_info = {
            "id": doc.id if hasattr(doc, 'id') else "unknown",
            "title": doc.struct_data.get("title", "Unknown") if hasattr(doc, 'struct_data') else "Unknown"
        }

        # Get snippets
        if hasattr(result, 'snippets'):
            for snippet in result.snippets:
                context_parts.append(snippet.snippet)

        # Get extractive answers
        if hasattr(result.document, 'derived_struct_data'):
            derived = result.document.derived_struct_data
            if 'extractive_answers' in derived:
                for answer in derived['extractive_answers']:
                    if 'content' in answer:
                        context_parts.append(answer['content'])

        results_info.append(doc_info)

    context = "\n\n".join(context_parts[:10])  # Limit context

    # Step 3: Generate response with Gemini
    print("\nGenerating response with Gemini...")
    gemini_response = query_with_gemini(context, query)

    return {
        "query": query,
        "search_results_count": len(list(search_response.results)) if search_response.results else 0,
        "context_excerpts": len(context_parts),
        "gemini_response": gemini_response,
        "documents_found": results_info[:5]
    }

def interactive_review():
    """Interactive document review session"""
    print("\n" + "="*60)
    print("HomeFranchise Document Review Interface")
    print("Powered by Vertex AI Search + Gemini")
    print("Type 'quit' to exit")
    print("="*60)

    # Sample queries to start
    sample_queries = [
        "What are the key elements of a successful franchise business plan?",
        "What financial projections should be included in a franchise plan?",
        "What are best practices for franchise operations management?",
        "What marketing strategies are recommended for new franchises?",
        "What legal considerations are mentioned for franchise businesses?"
    ]

    print("\nSample queries you can try:")
    for i, q in enumerate(sample_queries, 1):
        print(f"  {i}. {q}")

    while True:
        print("\n")
        user_input = input("Enter query (or number 1-5 for sample, 'quit' to exit): ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if user_input.isdigit() and 1 <= int(user_input) <= 5:
            query = sample_queries[int(user_input) - 1]
        else:
            query = user_input

        if not query:
            continue

        try:
            result = rag_query(query)
            print("\n" + "-"*60)
            print("RESPONSE:")
            print("-"*60)
            print(result.get("gemini_response", "No response"))
            print("\n" + "-"*60)
            print(f"Documents searched: {result.get('search_results_count', 0)}")
            print(f"Context excerpts used: {result.get('context_excerpts', 0)}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main execution"""
    print("="*60)
    print("HomeFranchise RAG Setup")
    print("Vertex AI Search + Gemini 2.5 Pro")
    print("="*60)

    # Set up environment
    os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID

    # Step 1: Create data store
    print("\n[Step 1/4] Creating Data Store...")
    data_store = create_data_store()

    # Step 2: Import documents
    print("\n[Step 2/4] Importing Documents...")
    import_documents()

    # Step 3: Create search engine
    print("\n[Step 3/4] Creating Search Engine...")
    create_search_engine()

    # Wait for indexing
    print("\n[Step 4/4] Waiting for indexing (60 seconds)...")
    time.sleep(60)

    # Start interactive review
    interactive_review()

if __name__ == "__main__":
    main()
