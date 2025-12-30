#!/usr/bin/env python3
"""
FastAPI server for RAG-based question answering system
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory conversation store for multi-turn conversations
conversation_store = {}

# Define Pydantic models based on data-model.md
class QueryRequest(BaseModel):
    """Request model for the chat endpoint"""
    query: str = Field(..., min_length=1, max_length=10000, description="The main user query text")
    selected_text: str | None = Field(None, max_length=5000, description="Optional selected text context to enhance the query")
    conversation_id: str | None = Field(None, description="Identifier for maintaining conversation state")
    stream: bool | None = Field(False, description="Flag to indicate if streaming response is requested")

class ChatResponse(BaseModel):
    """Response model for the chat endpoint"""
    response: str = Field(..., description="The grounded response to the user query")
    sources: list[dict] | None = Field(default=[], description="List of source citations")
    conversation_id: str | None = Field(None, description="Conversation identifier if state tracking enabled")
    error: str | None = Field(None, description="Error message if processing failed")

# Import RAG agent and retrieval tools from backend
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from agent import GeminiRAGAgent, qdrant_retrieval_tool
from backend.config.config import get_config
from backend.retrievers.retriever import RAGRetriever

# Create FastAPI app instance
app = FastAPI(
    title="FastAPI RAG Chatbot API",
    description="API for RAG-based question answering system",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for the API"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error occurred",
            "detail": str(exc) if hasattr(exc, 'args') and exc.args else "Unknown error"
        }
    )

@app.exception_handler(422)  # Validation error
async def validation_exception_handler(request: Request, exc: Exception):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "detail": str(exc) if hasattr(exc, 'args') and exc.args else "Invalid input parameters"
        }
    )

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log incoming requests and outgoing responses"""
    start_time = datetime.now()
    logger.info(f"Request: {request.method} {request.url}")

    response = await call_next(request)

    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} in {process_time:.2f}s")

    return response

@app.get("/")
async def root():
    return {"message": "FastAPI RAG Chatbot API is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API status"""
    return {
        "status": "healthy",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: QueryRequest):
    """Chat endpoint that processes user queries with RAG system"""
    try:
        # Handle conversation state if conversation_id is provided
        conversation_id = request.conversation_id
        if conversation_id:
            # Initialize conversation in store if it doesn't exist
            if conversation_id not in conversation_store:
                conversation_store[conversation_id] = []

            # Add current query to conversation history
            conversation_store[conversation_id].append({
                "role": "user",
                "content": request.query,
                "timestamp": datetime.now().isoformat()
            })

        # For hybrid query support, combine query with selected_text if provided
        search_query = request.query
        if request.selected_text:
            # Combine the main query with selected text for enhanced context
            search_query = f"{request.query} Context: {request.selected_text}"

        # Perform retrieval to get sources
        retrieval_result = qdrant_retrieval_tool(query=search_query)
        passages = retrieval_result.get("passages", [])

        # Don't return sources in the response to provide direct answers without links
        sources = []

        # Create response directly from retrieved content to avoid agent issues
        if passages:
            # Select the most relevant passage based on similarity score
            # Sort passages by relevance score in descending order
            sorted_passages = sorted(passages, key=lambda x: x.get("similarity_score", 0.0), reverse=True)

            # Enhanced content selection - prioritize content that directly answers the query and is relevant
            best_content = ""
            query_lower = request.query.lower()

            # Define answer indicators to look for
            answer_indicators = ['is a', 'are', 'means', 'stands for', 'refers to', 'describes', 'explains', 'defined as', 'what is', 'what are', 'represents', 'represents a', 'overview', 'introduction to', 'module', 'topic', 'theme']

            # First, look for content that both has answer indicators AND is highly relevant to the query
            for passage in sorted_passages[:5]:  # Check more passages for better relevance
                content = passage.get("content", "")
                if content:
                    # Clean up the content by removing problematic Unicode characters
                    clean_content = content.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
                    content_lower = clean_content.lower()

                    # Check if this content directly answers the query
                    has_answer_indicators = any(indicator in content_lower for indicator in answer_indicators)

                    # Check relevance to query - count how many query terms appear in content
                    query_terms = [term for term in query_lower.split() if len(term) > 2 and term not in ['what', 'is', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of']]
                    relevant_terms = sum(1 for term in query_terms if term in content_lower)

                    # For greeting queries like "hi", look for introduction or overview content
                    is_greeting = query_lower in ['hi', 'hello', 'hey', 'greetings', 'help']

                    if (has_answer_indicators and relevant_terms >= 1) or is_greeting:
                        best_content = clean_content
                        break

            # If no direct answer found, try to find content that has answer indicators
            if not best_content.strip():
                for passage in sorted_passages[:3]:
                    content = passage.get("content", "")
                    if content:
                        clean_content = content.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
                        content_lower = clean_content.lower()

                        # Look for direct answers even if similarity score is lower
                        answer_indicators = ['is a', 'are', 'means', 'stands for', 'refers to', 'describes', 'explains', 'defined as', 'what is', 'what are', 'represents', 'represents a']
                        has_answer_indicators = any(indicator in content_lower for indicator in answer_indicators)

                        if has_answer_indicators:
                            best_content = clean_content
                            break

            # If no direct answer found, use the passage with highest similarity score
            if not best_content.strip():
                if sorted_passages:
                    top_passage = sorted_passages[0]
                    content = top_passage.get("content", "")
                    if content:
                        clean_content = content.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
                        best_content = clean_content

            # Truncate to reasonable length for focused responses
            if len(best_content) > 400:
                # Try to find a more natural break point (sentence or paragraph end)
                truncated_content = best_content[:400]
                last_sentence = truncated_content.rfind('.')
                last_paragraph = truncated_content.rfind('\n\n')

                # Use the closest natural break point before 400 chars if available
                break_point = max(last_sentence, last_paragraph)
                if break_point > 200:  # Only if it's reasonably long
                    best_content = best_content[:break_point + 1] + "..."
                else:
                    best_content = truncated_content + "..."

            response_text = best_content.strip()
        else:
            response_text = f"I couldn't find specific information about '{request.query}' in the Physical AI & Humanoid Robotics textbook."

        # Add response to conversation history if conversation_id is provided
        if conversation_id:
            conversation_store[conversation_id].append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now().isoformat()
            })

        return ChatResponse(
            response=response_text,
            sources=sources,
            conversation_id=conversation_id
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        return ChatResponse(
            response="",
            sources=[],
            conversation_id=request.conversation_id,
            error=str(e)
        )

def main():
    """Main function to run the FastAPI application with uvicorn"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()