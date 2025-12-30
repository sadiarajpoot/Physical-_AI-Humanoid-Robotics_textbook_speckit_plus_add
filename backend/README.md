# Backend Structure

This directory contains all backend components for the RAG chatbot system, organized into logical modules:

## Directory Structure

```
backend/
├── cli/              # Command-line interface components
│   ├── cli.py        # CLI utilities and commands
│   └── main.py       # Main application entry point
├── config/           # Configuration management
│   └── config.py     # Configuration classes and loading
├── embedders/        # Embedding and vectorization components
│   └── embedders.py  # Cohere and other embedding implementations
├── models/           # Data models and schemas
│   └── models.py     # Pydantic models and data structures
├── parsers/          # HTML/content parsing utilities
│   └── parsers.py    # Content extraction from web pages
├── retrievers/       # RAG retrieval components
│   ├── retriever.py  # Main RAG retriever implementation
│   └── rag_retriever.py # RAG-specific retrieval logic
├── tools/            # Utility tools and services
│   ├── crawler.py    # Web crawling functionality
│   ├── discover_urls.py # URL discovery utilities
│   ├── resumer.py    # Resumable operations
│   ├── vector_store.py # Vector database operations
│   └── verifier.py   # Data verification utilities
├── utils/            # General utility functions
│   ├── chunker.py    # Text chunking utilities
│   ├── exceptions.py # Custom exception classes
│   ├── logger.py     # Logging utilities
│   ├── utils.py      # General utility functions
│   └── validators.py # Data validation utilities
├── tests/            # Test files
│   ├── test_crawling.py
│   ├── test_e2e.py
│   ├── test_embeddings.py
│   └── test_storage.py
├── _config/          # Configuration files
│   ├── .env          # Environment variables
│   ├── .gitignore    # Git ignore rules
│   ├── pyproject.toml # Project configuration
│   └── book_embeddings_ingestion.egg-info # Package info
├── _docs/            # Documentation files
├── _logs/            # Log files
│   └── book_ingestion.log # Ingestion logs
└── __pycache__/      # Python cache files
```

## Key Components

- **CLI**: Command-line interface for ingestion and management tasks
- **Config**: Centralized configuration management
- **Embedders**: Text embedding and vectorization services
- **Models**: Data structures and validation schemas
- **Parsers**: HTML parsing and content extraction
- **Retrievers**: RAG-based information retrieval
- **Tools**: Supporting utilities and services
- **Utils**: General-purpose helper functions
- **Tests**: Unit and integration tests

## Usage

Most components can be imported directly from their respective modules. The main entry point is typically through `cli/main.py` for command-line operations or through the API endpoints in the main project.