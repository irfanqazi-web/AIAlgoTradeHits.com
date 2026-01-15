"""
HomeFranchise RAG Query Tool
Query indexed franchise documents using Vertex AI Search + Gemini 2.5 Pro
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import argparse
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions
from google import genai
from google.protobuf import json_format

# Configuration
PROJECT_ID = "aialgotradehits"
LOCATION = "global"
ENGINE_ID = "homefranchise-search-engine"

def converse_with_engine(query: str) -> dict:
    """Use Vertex AI Search Conversational API for RAG queries"""
    client_options = ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    client = discoveryengine.ConversationalSearchServiceClient(client_options=client_options)

    serving_config = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_config"

    # Create a conversation query
    request = discoveryengine.ConverseConversationRequest(
        serving_config=serving_config,
        query=discoveryengine.TextInput(input=query),
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=5,
            include_citations=True,
            model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
                preamble="You are an expert franchise business consultant. Analyze the franchise documents and provide detailed, actionable insights."
            ),
        ),
    )

    try:
        response = client.converse_conversation(request=request)
        return {
            "reply": response.reply.summary.summary_text if response.reply.summary else "",
            "search_results": len(list(response.search_results)) if response.search_results else 0,
            "conversation_id": response.conversation.name if response.conversation else None
        }
    except Exception as e:
        return {"error": str(e), "reply": None}

def search_and_generate(query: str) -> dict:
    """Search documents and use Gemini 2.5 Pro for generation"""
    client_options = ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
    client = discoveryengine.SearchServiceClient(client_options=client_options)

    serving_config = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/engines/{ENGINE_ID}/servingConfigs/default_config"

    # Search request with summary
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=10,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                summary_result_count=10,
                include_citations=True,
                model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
                    preamble="You are an expert franchise business consultant. Based on the provided franchise documents, give detailed and practical advice."
                ),
            ),
        ),
    )

    try:
        response = client.search(request=request)

        # Extract summary (this uses Vertex AI LLM)
        summary_text = ""
        if hasattr(response, 'summary') and response.summary:
            summary_text = response.summary.summary_text or ""

        # Get document titles for reference
        docs_found = []
        for result in response.results:
            doc = result.document
            if hasattr(doc, 'derived_struct_data') and doc.derived_struct_data:
                derived = dict(doc.derived_struct_data)
                title = derived.get('title', doc.id if hasattr(doc, 'id') else 'Unknown')
                docs_found.append(title)

        # If no summary, use Gemini directly with document titles as context
        if not summary_text and docs_found:
            summary_text = generate_with_gemini(query, docs_found)

        return {
            "query": query,
            "response": summary_text,
            "documents_referenced": docs_found[:5],
            "total_results": len(docs_found)
        }

    except Exception as e:
        return {"error": str(e), "query": query}

def generate_with_gemini(query: str, doc_titles: list) -> str:
    """Fallback to Gemini 2.5 Pro for generation"""
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="us-central1"
    )

    context = f"Available franchise documents: {', '.join(doc_titles[:10])}"

    prompt = f"""Based on standard franchise business knowledge and the following indexed documents:

{context}

Answer this question about franchise business planning:
{query}

Provide practical, actionable advice based on franchise industry best practices.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Generation error: {e}"

def review_documents(focus_area: str = None) -> str:
    """Review franchise documents with optional focus area"""
    if focus_area:
        query = f"Review the franchise documents focusing on {focus_area}. Provide key insights, best practices, and recommendations."
    else:
        query = "Provide a comprehensive summary of all franchise documents. Include key business strategies, financial planning approaches, operational guidelines, and recommendations for starting a franchise business."

    result = search_and_generate(query)
    return result.get("response", result.get("error", "No response"))

def main():
    parser = argparse.ArgumentParser(description="Query HomeFranchise RAG System")
    parser.add_argument("query", nargs="?", help="Query to search franchise documents")
    parser.add_argument("--review", action="store_true", help="Get comprehensive document review")
    parser.add_argument("--focus", type=str, help="Focus area for review")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--converse", action="store_true", help="Use conversational search")

    args = parser.parse_args()

    print("="*60)
    print("HomeFranchise RAG Query System")
    print("Vertex AI Search + Gemini 2.5 Pro")
    print("="*60)

    if args.review or args.focus:
        print(f"\nPerforming document review{f' with focus: {args.focus}' if args.focus else ''}...")
        result = review_documents(args.focus)
        print("\n" + "-"*60)
        print("REVIEW RESULTS:")
        print("-"*60)
        print(result)
    elif args.query:
        print(f"\nQuery: {args.query}")

        if args.converse:
            result = converse_with_engine(args.query)
            response = result.get("reply") or result.get("error", "No response")
        else:
            result = search_and_generate(args.query)
            response = result.get("response") or result.get("error", "No response")

        print("\n" + "-"*60)
        print("RESPONSE:")
        print("-"*60)
        print(response)

        if args.verbose and 'documents_referenced' in result:
            print("\n" + "-"*60)
            print(f"Documents referenced: {result['documents_referenced']}")
            print(f"Total results: {result.get('total_results', 'N/A')}")
    else:
        # Default: show comprehensive review
        print("\nRunning comprehensive document review...")
        result = review_documents()
        print("\n" + "-"*60)
        print("DOCUMENT REVIEW SUMMARY:")
        print("-"*60)
        print(result)

if __name__ == "__main__":
    main()
