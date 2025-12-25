# Book Embeddings Ingestion Tool

A Python application to crawl Docusaurus book pages, generate Cohere embeddings, and store them in Qdrant Cloud Free Tier.

## Features

- Crawls all pages from a deployed Docusaurus book site
- Extracts clean text content while filtering out HTML tags and navigation elements
- Chunks text appropriately for embedding generation
- Generates embeddings using Cohere models
- Stores embeddings with metadata in Qdrant vector database
- Idempotent operation (safe to run multiple times)
- Verifiable ingestion process

## Requirements

- Python 3.11+
- UV package manager (optional but recommended)

## Installation

1. Clone the repository
2. Navigate to the `backend` directory
3. Install dependencies:

```bash
uv sync  # If using UV
# OR
pip install -r requirements.txt  # If using pip directly
```

## Configuration

Create a `.env` file in the backend directory with the following variables:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_HOST=your_qdrant_cluster_url_here
QDRANT_COLLECTION_NAME=book_embeddings
BOOK_URL=https://your-book-url.vercel.app
```

## Usage

Run the ingestion pipeline:

```bash
python main.py --url https://your-book-url.vercel.app
```

Or use environment variables to specify the book URL:

```bash
python main.py
```

## License

[Specify your license here]