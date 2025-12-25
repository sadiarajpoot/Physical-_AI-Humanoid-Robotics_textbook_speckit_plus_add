# Quickstart Guide: Book Embeddings Ingestion

This guide will help you get started with the Book Embeddings Ingestion tool quickly.

## Prerequisites

- Python 3.11+
- pip or uv package manager
- Cohere API key
- Qdrant Cloud account and API key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   cd backend
   ```

2. Install dependencies using uv (recommended):
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -e .
   ```

## Configuration

1. Create a `.env` file in the `backend` directory:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your credentials:
   ```env
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_API_KEY=your_qdrant_api_key_here
   QDRANT_HOST=your_qdrant_cluster_url_here
   QDRANT_COLLECTION_NAME=book_embeddings
   BOOK_URL=https://your-book-url.vercel.app
   ```

## Usage

### Basic Usage

Run the ingestion tool with default settings:
```bash
python main.py
```

### Command Line Options

Run with a specific book URL:
```bash
python main.py --url https://your-book-url.vercel.app
```

Customize chunk size and overlap:
```bash
python main.py --chunk-size 2000 --chunk-overlap 300
```

Run with verification:
```bash
python main.py --verify
```

Resume from last completed step:
```bash
python main.py --resume
```

See all options:
```bash
python main.py --help
```

## Example

To ingest a book from a Docusaurus site:
```bash
python main.py --url https://docusaurus.io/docs --collection-name my-book-embeddings --verify
```

This will:
1. Crawl all pages from the Docusaurus book
2. Extract clean text content
3. Chunk the text appropriately
4. Generate Cohere embeddings
5. Store embeddings in Qdrant with metadata
6. Verify the ingestion process

## Output

The tool will display progress as it:
- Crawls pages from the book
- Chunks the text content
- Generates embeddings
- Stores them in Qdrant

At the end, you'll see a summary like:
```
Ingestion Summary:
- Pages crawled: 25
- Text chunks generated: 142
- Embeddings generated: 142
- Embeddings stored: 142
- Progress: 4/4 steps completed
```

## Troubleshooting

- If you get API rate limit errors, reduce the rate of requests or upgrade your API plan
- If crawling fails, verify the URL is accessible and follows Docusaurus structure
- If storage fails, check your Qdrant credentials and collection permissions