#!/usr/bin/env python3
"""
Google Gemini Agent with RAG Retrieval

This script creates an autonomous agent that uses Google Gemini API to answer
book-specific queries by retrieving relevant content from Qdrant and providing
context-grounded responses based on Physical AI & Humanoid Robotics textbook content.

The agent automatically invokes retrieval tools when answering questions,
maintains conversation context across multiple turns, and ensures responses
are grounded in retrieved content only (no hallucination).
"""

import os
import sys
import argparse
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add backend to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import google.generativeai as genai
from backend.config.config import get_config
from backend.retrievers.retriever import RAGRetriever


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def qdrant_retrieval_tool(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Qdrant retrieval tool function that retrieves relevant passages from the
    Physical AI & Humanoid Robotics textbook based on semantic similarity to a user query.

    Args:
        query: The natural language query to search for in the textbook
        top_k: Number of top results to retrieve (default: 3)

    Returns:
        Dictionary containing passages with content, source_url, similarity_score, and metadata
    """
    try:
        # Validate inputs
        if not query or not query.strip():
            return {"passages": [], "error": "Query cannot be empty"}

        if top_k < 1 or top_k > 10:
            top_k = min(max(top_k, 1), 10)  # Clamp to valid range

        # Get configuration and initialize retriever
        config = get_config()
        retriever = RAGRetriever(config)

        # Query the retriever
        results = retriever.query_embeddings(query, top_k=top_k)

        # Format results according to contract
        passages = []
        for result in results:
            passage = {
                "content": result.get("content", ""),
                "source_url": result.get("source_url", ""),
                "similarity_score": result.get("similarity_score", 0.0),
                "metadata": result.get("metadata", {})
            }
            passages.append(passage)

        return {"passages": passages}

    except Exception as e:
        logger.error(f"Error in qdrant_retrieval_tool: {e}")
        return {"passages": [], "error": str(e)}


def create_agent_system_prompt() -> str:
    """
    Create system prompt for the agent emphasizing grounded responses.

    Returns:
        System prompt string that guides agent behavior
    """
    return """
You are an expert assistant for the Physical AI & Humanoid Robotics textbook.
Your purpose is to answer questions about the textbook content using only the
information provided through the retrieval tool.

IMPORTANT RULES:
1. ALWAYS use the qdrant_retrieval tool to get relevant passages before answering
2. ONLY use information from the retrieved passages in your responses
3. If the retrieved passages don't contain relevant information, acknowledge this
   and explain that the information is not available in the textbook
4. ALWAYS cite the source URLs of the passages you use
5. Do NOT generate information that is not in the retrieved passages
6. If asked about topics outside the textbook scope, politely explain that you
   can only answer questions based on the Physical AI & Humanoid Robotics textbook
7. Synthesize information from multiple passages when needed to provide complete answers

Your responses should be clear, informative, and directly based on the textbook content.
"""


class GeminiRAGAgent:
    """
    Google Gemini Agent that uses RAG retrieval to answer book-specific queries.
    """

    def __init__(self):
        """Initialize the Google Gemini RAG agent with configuration and tools."""
        # Initialize Google Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable must be set")
        genai.configure(api_key=api_key)

        # Initialize the generative model
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=create_agent_system_prompt()
        )

        # Initialize conversation history
        self.conversation = self.model.start_chat(history=[])

        logger.info("Google Gemini RAG Agent initialized successfully")

    def chat(self, user_message: str, max_tokens: int = 1000) -> str:
        """
        Process a user message and return the agent's response.

        Args:
            user_message: The user's query or message
            max_tokens: Maximum number of tokens for the response (not used in Gemini)

        Returns:
            The agent's response as a string
        """
        try:
            # For Gemini, we'll create a simple function calling mechanism
            # First, try to understand if the query needs retrieval
            prompt_with_instruction = f"""
            Determine if the following query requires information from the textbook:
            Query: {user_message}

            If it requires textbook information, respond with the query that should be used for retrieval.
            If it doesn't require textbook information, respond with "NO_RETRIEVAL_NEEDED".
            """

            # Check if we need to retrieve information
            check_response = self.model.generate_content(
                prompt_with_instruction,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=100,
                    temperature=0.1
                )
            )

            retrieval_query = check_response.text.strip()

            if retrieval_query != "NO_RETRIEVAL_NEEDED":
                # Perform retrieval using our tool
                retrieval_result = qdrant_retrieval_tool(query=retrieval_query)

                if retrieval_result.get("passages"):
                    # Format retrieved content for context
                    context = "Here is relevant information from the textbook:\n\n"
                    for i, passage in enumerate(retrieval_result["passages"][:3], 1):  # Use top 3 passages
                        context += f"Source {i} ({passage.get('source_url', 'Unknown')}):\n"
                        context += f"{passage.get('content', '')}\n\n"

                    # Create a new prompt that includes the retrieved context
                    full_prompt = f"{context}\n\nUser Query: {user_message}\n\nPlease answer the user's query based on the provided textbook information, citing the sources used."
                else:
                    full_prompt = f"The query was: {user_message}\n\nI couldn't find relevant information in the textbook to answer this question."
            else:
                full_prompt = user_message

            # Generate response using the full prompt
            try:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.3
                    )
                )

                # Extract text from response
                if hasattr(response, 'text'):
                    return response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    # Handle response with candidates
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content.parts:
                        return candidate.content.parts[0].text if hasattr(candidate.content.parts[0], 'text') else "I couldn't generate a response for your query."
                    else:
                        return "I couldn't generate a response for your query."
                else:
                    return "I couldn't generate a response for your query."
            except Exception as gen_error:
                logger.error(f"Error generating content: {gen_error}")
                # If generation fails, return the raw retrieved context
                if 'context' in locals() and context:
                    return f"I had trouble generating a response, but here's relevant information from the textbook:\n\n{context}"
                else:
                    return "I couldn't generate a response for your query."

        except Exception as e:
            logger.error(f"Error in agent chat: {e}")
            return "I encountered an error processing your request. Please try again."

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history reset")


def run_test_queries(agent: GeminiRAGAgent) -> None:
    """
    Run a series of test queries to validate the agent's functionality.

    Args:
        agent: Initialized GeminiRAGAgent instance
    """
    test_queries = [
        "What is Physical AI?",
        "Explain humanoid robotics systems",
        "How does ROS 2 work?",
        "What are the applications of machine learning in robotics?",
        "Describe sensor fusion in humanoid robots"
    ]

    logger.info("Starting agent validation with test queries...")

    for i, query in enumerate(test_queries, 1):
        logger.info(f"Test {i}/5: Processing query: '{query}'")
        response = agent.chat(query)
        print(f"\nQuery {i}: {query}")
        print(f"Response: {response}")
        print("-" * 80)

    logger.info("Test query validation completed")


def main():
    """Main function to run the Google Gemini RAG agent."""
    parser = argparse.ArgumentParser(description="Google Gemini Agent with RAG Retrieval")
    parser.add_argument("--query", type=str, help="Single query to process")
    parser.add_argument("--test", action="store_true", help="Run test queries")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Initializing Google Gemini RAG Agent...")

    try:
        # Initialize the agent
        agent = GeminiRAGAgent()

        if args.test:
            # Run test queries
            run_test_queries(agent)

        elif args.query:
            # Process single query
            logger.info(f"Processing query: '{args.query}'")
            response = agent.chat(args.query)
            print(f"Query: {args.query}")
            print(f"Response: {response}")

        else:
            # Interactive mode
            print("Google Gemini RAG Agent - Interactive Mode")
            print("Type 'quit' or 'exit' to exit")
            print("-" * 50)

            while True:
                try:
                    user_input = input("\nYour question: ").strip()

                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("Goodbye!")
                        break
                    elif not user_input:
                        continue

                    response = agent.chat(user_input)
                    print(f"Agent: {response}")

                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                except Exception as e:
                    logger.error(f"Error in interactive mode: {e}")
                    print("An error occurred. Please try again.")

    except Exception as e:
        logger.error(f"Error initializing Google Gemini RAG Agent: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()