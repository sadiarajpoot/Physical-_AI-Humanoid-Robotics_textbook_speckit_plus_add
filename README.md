# Physical AI & Humanoid Robotics RAG Chatbot

This project implements a RAG-based chatbot system that answers questions about the Physical AI & Humanoid Robotics textbook by retrieving relevant content from Qdrant and providing context-grounded responses.

## Features

- **RAG-Based Query Answering**: Answers questions using retrieved textbook content with semantic search
- **Context-Aware Responses**: Maintains awareness of conversation context for relevant responses
- **Grounded Responses**: Responses are strictly based on retrieved textbook content (no hallucination)
- **Automatic Retrieval**: Automatically retrieves relevant information from the textbook
- **Source Citation**: All responses include citations to source materials
- **FastAPI Backend**: REST API for integration with frontend applications
- **Structured Backend**: Well-organized modular architecture for maintainability

## Prerequisites

- Python 3.14+
- Google Gemini API key
- Cohere API key
- Qdrant API key and host URL
- Book embeddings already ingested in Qdrant

## Setup

1. **Install required packages**:
   ```bash
   pip install google-generativeai cohere qdrant-client python-dotenv
   ```

2. **Set up environment variables**:
   Create a `.env` file with:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_API_KEY=your_qdrant_api_key_here
   QDRANT_HOST=your_qdrant_host_url_here
   ```

3. **Verify Qdrant connection**:
   Ensure your book embeddings are already stored in Qdrant under the `book_embeddings` collection.

## Usage

### Interactive Mode
```bash
python agent.py
```
This starts an interactive CLI session where you can ask questions about the Physical AI & Humanoid Robotics textbook.

### Single Query Mode
```bash
python agent.py --query "What is Physical AI?"
```

### Test Mode
```bash
python agent.py --test
```
Runs a series of test queries to validate the agent's functionality.

## Example Queries

- "What is Physical AI?"
- "Explain humanoid robotics systems"
- "How does ROS 2 work?"
- "What are the applications of machine learning in robotics?"
- "Describe sensor fusion in humanoid robots"

## Expected Output

The agent will respond with answers grounded in the textbook content, citing the sources used to generate the response.

Example:
```
Agent: Physical AI is a field that combines artificial intelligence with physical systems...
Sources:
- https://physical-ai-humanoid-robotics-textb-seven-lime.vercel.app/docs/overview/what-is-physical-ai
```

## Architecture

The system is organized into a well-structured backend with the following components:

### Backend Structure
- **CLI**: Command-line interface for ingestion and management tasks (`backend/cli/`)
- **Config**: Configuration management and loading (`backend/config/`)
- **Embedders**: Text embedding and vectorization services (`backend/embedders/`)
- **Models**: Data models and validation schemas (`backend/models/`)
- **Parsers**: HTML parsing and content extraction (`backend/parsers/`)
- **Retrievers**: RAG-based information retrieval (`backend/retrievers/`)
- **Tools**: Utility tools and services (`backend/tools/`)
- **Utils**: General utility functions (`backend/utils/`)

### API Layer
- **FastAPI Server**: REST API endpoints for chat functionality (`api.py`)
- **RAG Agent**: Google Gemini-based agent with content grounding
- **Qdrant Integration**: Vector database for semantic search and retrieval

### Frontend Integration
- **Docusaurus Widget**: Chatbot widget integrated into textbook documentation
- **React Component**: Interactive chat interface with conversation history

## Troubleshooting

- If you get API key errors, verify your environment variables
- If no results are returned, check that the book embeddings are properly stored in Qdrant
- If responses seem unrelated to queries, verify the Cohere and Qdrant connections
- If you encounter import errors, ensure all dependencies are installed

## Note

This implementation uses Google's Gemini API for the agent functionality and reuses the existing RAG infrastructure (Cohere embeddings + Qdrant) for content retrieval. The agent ensures all responses are grounded in the textbook content and prevents hallucination of information outside the retrieved context.