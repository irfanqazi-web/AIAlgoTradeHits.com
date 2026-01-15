"""
How to Feed Documents to Gemini 2.5 API for Training/Context
Developer: irfan.qazi@aialgotradehits.com

This script demonstrates multiple methods to feed trading documentation
to Gemini 2.5 for context-aware Text-to-SQL and trading analysis.
"""

import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
from typing import Dict, List, Any

# Method 1: Using google-genai SDK (Recommended)
def method1_google_genai():
    """
    Using the google-genai SDK with Gemini 2.5
    Installation: pip install google-genai
    """
    print("=" * 60)
    print("Method 1: Using google-genai SDK")
    print("=" * 60)

    code_example = '''
from google import genai
from google.genai import types

# Initialize client with your API key
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

# Load your documentation
with open("TRADING_TABLE_DOCUMENTATION.md", "r", encoding="utf-8") as f:
    doc_content = f.read()

# Method A: Include documentation as system instruction
response = client.models.generate_content(
    model="gemini-2.5-flash",  # or gemini-2.5-pro for complex queries
    config=types.GenerateContentConfig(
        system_instruction=f"""You are a trading analytics SQL expert.
Use this schema documentation to generate accurate BigQuery SQL queries:

{doc_content}

Always use fully qualified table names: `aialgotradehits.crypto_trading_data.table_name`
"""
    ),
    contents=["Generate SQL to find oversold tech stocks"]
)

print(response.text)

# Method B: Include documentation as part of the prompt
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[f"""
REFERENCE DOCUMENTATION:
{doc_content}

TASK: Generate a BigQuery SQL query to find the top 10 crypto gainers today.
Return only the SQL query.
"""]
)

print(response.text)
'''
    print(code_example)

def method2_vertex_ai():
    """
    Using Vertex AI SDK for enterprise deployments
    """
    print("\n" + "=" * 60)
    print("Method 2: Using Vertex AI (Enterprise)")
    print("=" * 60)

    code_example = '''
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# Initialize Vertex AI
vertexai.init(project="aialgotradehits", location="us-central1")

# Load the model
model = GenerativeModel("gemini-2.5-pro")

# Load documentation
with open("TRADING_TABLE_DOCUMENTATION.md", "r", encoding="utf-8") as f:
    doc_content = f.read()

# Create a chat session with context
chat = model.start_chat(history=[
    {
        "role": "user",
        "parts": [f"Here is the trading database documentation for reference: {doc_content[:50000]}"]
    },
    {
        "role": "model",
        "parts": ["I've reviewed the trading database documentation. I understand the table schemas, column definitions, and trading terminology. I'm ready to help generate SQL queries."]
    }
])

# Now ask questions with full context
response = chat.send_message("Generate SQL to find stocks with RSI below 30 and bullish MACD")
print(response.text)
'''
    print(code_example)

def method3_file_upload():
    """
    Using Gemini's file upload capability for large documents
    """
    print("\n" + "=" * 60)
    print("Method 3: File Upload (for large documents)")
    print("=" * 60)

    code_example = '''
from google import genai
from google.genai import types

client = genai.Client(api_key="YOUR_API_KEY")

# Upload the documentation file
uploaded_file = client.files.upload(
    file="TRADING_TABLE_DOCUMENTATION.md",
    config=types.UploadFileConfig(display_name="trading_schema")
)

# Wait for processing
import time
while uploaded_file.state == "PROCESSING":
    time.sleep(1)
    uploaded_file = client.files.get(name=uploaded_file.name)

# Use the uploaded file in your prompt
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        uploaded_file,
        "Based on this schema documentation, generate SQL to find oversold cryptos"
    ]
)

print(response.text)
'''
    print(code_example)

def method4_context_caching():
    """
    Using Gemini's context caching for repeated queries
    """
    print("\n" + "=" * 60)
    print("Method 4: Context Caching (Cost Efficient)")
    print("=" * 60)

    code_example = '''
from google import genai
from google.genai import types
from datetime import timedelta

client = genai.Client(api_key="YOUR_API_KEY")

# Load documentation
with open("TRADING_TABLE_DOCUMENTATION.md", "r", encoding="utf-8") as f:
    doc_content = f.read()

# Create a cached context (valid for specified duration)
cache = client.caches.create(
    model="gemini-2.5-flash",
    config=types.CreateCachedContentConfig(
        display_name="trading_schema_cache",
        contents=[doc_content],
        ttl=timedelta(hours=1)  # Cache for 1 hour
    )
)

# Use the cached context for multiple queries (cost-efficient)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    cached_content=cache.name,
    contents=["Generate SQL for top 10 stock gainers"]
)

print(response.text)

# Subsequent queries reuse the cached context
response2 = client.models.generate_content(
    model="gemini-2.5-flash",
    cached_content=cache.name,
    contents=["Now find oversold stocks in the technology sector"]
)

print(response2.text)
'''
    print(code_example)

def method5_embeddings_rag():
    """
    Using embeddings for RAG (Retrieval Augmented Generation)
    """
    print("\n" + "=" * 60)
    print("Method 5: RAG with Embeddings (Advanced)")
    print("=" * 60)

    code_example = '''
from google import genai
from google.genai import types
import numpy as np

client = genai.Client(api_key="YOUR_API_KEY")

# Split documentation into chunks
def chunk_document(content: str, chunk_size: int = 1000) -> list:
    chunks = []
    for i in range(0, len(content), chunk_size):
        chunks.append(content[i:i+chunk_size])
    return chunks

# Load and chunk documentation
with open("TRADING_TABLE_DOCUMENTATION.md", "r", encoding="utf-8") as f:
    doc_content = f.read()

chunks = chunk_document(doc_content)

# Generate embeddings for each chunk
embeddings = []
for chunk in chunks:
    result = client.models.embed_content(
        model="text-embedding-004",
        contents=chunk
    )
    embeddings.append({
        "text": chunk,
        "embedding": result.embedding
    })

# Function to find relevant chunks based on query
def find_relevant_chunks(query: str, embeddings: list, top_k: int = 3) -> list:
    query_embedding = client.models.embed_content(
        model="text-embedding-004",
        contents=query
    ).embedding

    # Calculate cosine similarity
    similarities = []
    for item in embeddings:
        similarity = np.dot(query_embedding, item["embedding"])
        similarities.append((similarity, item["text"]))

    # Return top-k most relevant chunks
    similarities.sort(reverse=True)
    return [text for _, text in similarities[:top_k]]

# Use RAG for query
user_query = "How do I find oversold stocks?"
relevant_chunks = find_relevant_chunks(user_query, embeddings)

# Generate response with relevant context
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[f"""
RELEVANT DOCUMENTATION:
{chr(10).join(relevant_chunks)}

USER QUESTION: {user_query}

Generate a BigQuery SQL query that answers this question.
"""]
)

print(response.text)
'''
    print(code_example)

def create_complete_example():
    """Create a complete working example"""
    print("\n" + "=" * 60)
    print("Complete Working Example")
    print("=" * 60)

    example_code = '''
#!/usr/bin/env python3
"""
Complete Example: Feed Trading Documentation to Gemini 2.5
Run: python feed_trading_docs.py
"""

import os
from google import genai
from google.genai import types

# Configuration
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
MODEL = "gemini-2.5-flash"  # or "gemini-2.5-pro"

def main():
    # Initialize client
    client = genai.Client(api_key=API_KEY)

    # Load all documentation files
    doc_files = [
        "TRADING_TABLE_DOCUMENTATION.md",
        "AGENTIC_TEXT_TO_SQL_STRATEGY.md",
        "GCP_ADK_IMPLEMENTATION_GUIDE.md"
    ]

    combined_docs = ""
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            with open(doc_file, "r", encoding="utf-8") as f:
                combined_docs += f"\\n\\n=== {doc_file} ===\\n\\n"
                combined_docs += f.read()[:30000]  # Limit size

    # Create system instruction with trading context
    system_instruction = f"""You are an expert SQL developer for the AIAlgoTradeHits trading platform.

PROJECT: aialgotradehits
DATASET: crypto_trading_data

Your task is to convert natural language trading queries into accurate BigQuery SQL.

DOCUMENTATION:
{combined_docs[:50000]}

RULES:
1. Always use fully qualified table names: `aialgotradehits.crypto_trading_data.table_name`
2. Always include ORDER BY and LIMIT clauses
3. Handle NULL values appropriately
4. For latest data, use ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY datetime DESC)
5. Only generate SELECT statements
"""

    # Create interactive session
    print("Trading SQL Assistant Ready!")
    print("Type your query (or 'quit' to exit):\\n")

    while True:
        query = input("Query> ").strip()
        if query.lower() in ['quit', 'exit', 'q']:
            break
        if not query:
            continue

        try:
            response = client.models.generate_content(
                model=MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1
                ),
                contents=[query]
            )

            print(f"\\nSQL:\\n{response.text}\\n")

        except Exception as e:
            print(f"Error: {e}\\n")

    print("Goodbye!")

if __name__ == "__main__":
    main()
'''
    print(example_code)

def show_api_key_setup():
    """Show how to set up API key"""
    print("\n" + "=" * 60)
    print("API Key Setup")
    print("=" * 60)

    instructions = '''
1. Go to: https://aistudio.google.com/app/apikey

2. Click "Create API Key"

3. Copy the key and set as environment variable:

   Windows (PowerShell):
   $env:GEMINI_API_KEY = "your-api-key-here"

   Windows (CMD):
   set GEMINI_API_KEY=your-api-key-here

   Linux/Mac:
   export GEMINI_API_KEY="your-api-key-here"

4. For permanent setup (Windows):
   - Open System Properties > Advanced > Environment Variables
   - Add new User variable: GEMINI_API_KEY = your-key

5. Verify:
   python -c "import os; print(os.environ.get('GEMINI_API_KEY', 'NOT SET'))"
'''
    print(instructions)

def main():
    print("=" * 70)
    print("How to Feed Documents to Gemini 2.5 API")
    print("AIAlgoTradeHits Training Guide")
    print("=" * 70)

    show_api_key_setup()
    method1_google_genai()
    method2_vertex_ai()
    method3_file_upload()
    method4_context_caching()
    method5_embeddings_rag()
    create_complete_example()

    print("\n" + "=" * 70)
    print("Summary: Choose the Right Method")
    print("=" * 70)
    print("""
1. System Instruction (Method 1): Best for consistent context across queries
2. Vertex AI (Method 2): Best for enterprise with GCP integration
3. File Upload (Method 3): Best for very large documents (>100KB)
4. Context Caching (Method 4): Best for cost efficiency with repeated queries
5. RAG with Embeddings (Method 5): Best for searching large knowledge bases

RECOMMENDED FOR AIAlgoTradeHits:
- Start with Method 1 (System Instruction) for simplicity
- Move to Method 4 (Context Caching) for production to reduce costs
- Use Method 5 (RAG) when documentation exceeds model context limits
""")

if __name__ == "__main__":
    main()
