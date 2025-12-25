# Tasks: Book Content Ingestion with Cohere Embeddings to Qdrant

**Feature**: Book Content Ingestion with Cohere Embeddings to Qdrant
**Branch**: `001-book-embeddings-ingestion`
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)
**Generated**: 2025-12-25 | **Status**: Ready for implementation

## Implementation Strategy

**MVP Scope**: User Story 1 (Crawl and Extract Book Content) - Provides a complete, independently testable foundation that can crawl Docusaurus book pages and extract clean text content.

**Incremental Delivery**: Each user story builds on the previous, with independently testable outcomes:
- US1: Crawling and text extraction capability
- US2: Text chunking and Cohere embedding generation
- US3: Storage in Qdrant with metadata and idempotency

**Parallel Opportunities**: Dependency setup, documentation, and configuration can be done in parallel with core functionality implementation.

---

## Phase 1: Setup

Setup tasks for project initialization and dependency management.

**Goal**: Establish project structure and development environment.

- [X] T001 Create backend/ directory structure
- [X] T002 Initialize UV project with pyproject.toml
- [X] T003 Add dependencies to pyproject.toml (cohere, qdrant-client, requests, beautifulsoup4, langchain-text-splitters, python-dotenv)
- [X] T004 Create .gitignore file for Python project
- [X] T005 Create initial .env file template
- [X] T006 Create README.md with project overview

---

## Phase 2: Foundational

Foundational tasks that block all user stories - these must complete before user story implementation.

**Goal**: Establish core infrastructure and utilities needed by all user stories.

- [X] T007 Create data models for Book Content, Text Chunk, and Embedding entities in backend/models.py
- [X] T008 Implement configuration loading from .env in backend/config.py
- [X] T009 Create utility functions for URL validation and processing in backend/utils.py
- [X] T010 Implement error handling base classes in backend/exceptions.py
- [X] T011 Create CLI argument parser in backend/cli.py
- [X] T012 Set up logging configuration in backend/logger.py

---

## Phase 3: User Story 1 - Crawl and Extract Book Content (Priority: P1)

As a RAG system developer, I want to crawl all pages from a deployed Docusaurus book site to extract clean text content so that I can create embeddings for retrieval-augmented generation.

**Independent Test**: Can be fully tested by running the crawler against a known book URL and verifying that text content is extracted without HTML tags, navigation elements, or other non-content elements.

**Acceptance Scenarios**:
1. Given a valid Vercel URL for a Docusaurus book, When I run the crawler, Then all book pages are visited and clean text content is extracted
2. Given a Docusaurus book with multiple chapters and sections, When I run the crawler, Then all text content is captured while excluding navigation, headers, footers, and UI elements

- [X] T013 [US1] Implement get_urls() function to discover all book pages from base URL in backend/main.py
- [X] T014 [P] [US1] Create HTML parsing utility to extract clean text content in backend/parsers.py
- [X] T015 [P] [US1] Implement navigation element filtering to exclude non-content elements in backend/parsers.py
- [X] T016 [US1] Implement URL crawling with requests and BeautifulSoup in backend/crawler.py
- [X] T017 [US1] Add error handling for inaccessible URLs in backend/crawler.py
- [X] T018 [US1] Implement rate limiting to avoid overwhelming the server in backend/crawler.py
- [X] T019 [US1] Add verification function to check all pages were processed in backend/verifier.py
- [X] T020 [US1] Integrate crawling functionality into main() orchestrator in backend/main.py
- [X] T021 [US1] Create basic test for crawling functionality in tests/test_crawling.py

---

## Phase 4: User Story 2 - Generate Cohere Embeddings from Text Chunks (Priority: P2)

As a RAG system developer, I want to chunk the extracted text and generate embeddings using Cohere models so that I can store semantic representations in a vector database.

**Independent Test**: Can be tested by providing text chunks as input and verifying that Cohere embeddings are generated successfully.

**Acceptance Scenarios**:
1. Given text content from book pages, When I run the chunking and embedding process, Then appropriately sized text chunks are created with corresponding Cohere embeddings
2. Given large book content that needs to be chunked, When I run the process, Then chunks are created with reasonable overlap to preserve context while fitting within embedding model limits

- [X] T022 [US2] Implement text chunking functionality using langchain-text-splitters in backend/chunker.py
- [X] T023 [US2] Add configuration for chunk size and overlap parameters in backend/config.py
- [X] T024 [US2] Create Cohere API client setup in backend/embedders.py
- [X] T025 [US2] Implement embedding generation function in backend/embedders.py
- [X] T026 [US2] Add error handling for Cohere API rate limits and errors in backend/embedders.py
- [X] T027 [US2] Implement batch processing for efficient embedding generation in backend/embedders.py
- [X] T028 [US2] Add validation to ensure chunks fit within Cohere model limits in backend/validators.py
- [X] T029 [US2] Integrate chunking and embedding into main() orchestrator in backend/main.py
- [X] T030 [US2] Create basic test for embedding functionality in tests/test_embeddings.py

---

## Phase 5: User Story 3 - Store Embeddings in Qdrant Vector Database (Priority: P3)

As a RAG system developer, I want to store the generated embeddings with metadata in Qdrare Cloud Free Tier so that they can be efficiently retrieved later.

**Independent Test**: Can be tested by storing sample embeddings and verifying they are accessible in the Qdrant collection.

**Acceptance Scenarios**:
1. Given Cohere embeddings with metadata, When I run the storage process, Then embeddings are uploaded to Qdrant with appropriate metadata
2. Given an existing collection in Qdrant, When I run the ingestion process again, Then the process is idempotent and doesn't create duplicate entries

- [X] T031 [US3] Create Qdrant client setup and collection management in backend/vector_store.py
- [X] T032 [US3] Define Qdrant collection schema with metadata fields in backend/vector_store.py
- [X] T033 [US3] Implement store_in_qdrant() function for embedding storage in backend/vector_store.py
- [X] T034 [US3] Add metadata handling for source URL, chapter/section, and text position in backend/vector_store.py
- [X] T035 [US3] Implement idempotency check to prevent duplicate entries in backend/vector_store.py
- [X] T036 [US3] Add error handling for Qdrant API limits and errors in backend/vector_store.py
- [X] T037 [US3] Create verification function to check embeddings were stored successfully in backend/verifier.py
- [X] T038 [US3] Implement resume functionality for interrupted ingestion in backend/resumer.py
- [X] T039 [US3] Integrate storage functionality into main() orchestrator in backend/main.py
- [X] T040 [US3] Create basic test for storage functionality in tests/test_storage.py

---

## Phase 6: Polish & Cross-Cutting Concerns

Final implementation tasks for a production-ready system.

**Goal**: Complete the implementation with verification, documentation, and quality improvements.

- [X] T041 Implement comprehensive verification and reporting functionality in backend/verifier.py
- [X] T042 Add progress tracking and status reporting to main() orchestrator in backend/main.py
- [X] T043 Create comprehensive README.md with setup and usage instructions
- [X] T044 Implement end-to-end test covering all user stories in tests/test_e2e.py
- [X] T045 Add command-line options for specifying book URL, Qdrant settings, and other parameters in backend/cli.py
- [X] T046 Create quickstart guide based on implementation in docs/quickstart.md
- [X] T047 Implement configuration validation at startup in backend/config.py
- [X] T048 Add proper logging throughout the application in all modules
- [X] T049 Create .env.example file with documentation for required environment variables
- [X] T050 Perform final integration testing and bug fixes

---

## Dependencies

User story completion order and dependencies:

- **US1 (P1)**: Foundation - no dependencies, can be implemented independently
- **US2 (P2)**: Depends on US1 (needs extracted text to chunk and embed)
- **US3 (P3)**: Depends on US2 (needs embeddings to store)

**Independent Test Criteria**:
- US1: Run crawler against test book URL and verify clean text extraction
- US2: Provide text chunks as input and verify Cohere embeddings are generated
- US3: Provide embeddings with metadata and verify they're stored in Qdrant with idempotency

---

## Parallel Execution Examples

Per-user-story parallel execution opportunities:

**US1 Parallel Tasks**:
- T014 [P] [US1] Create HTML parsing utility (backend/parsers.py)
- T015 [P] [US1] Implement navigation element filtering (backend/parsers.py)
- T016 [US1] Implement URL crawling (backend/crawler.py)

**US2 Parallel Tasks**:
- T022 [US2] Implement text chunking (backend/chunker.py)
- T024 [US2] Create Cohere API client (backend/embedders.py)

**US3 Parallel Tasks**:
- T031 [US3] Create Qdrant client setup (backend/vector_store.py)
- T034 [US3] Add metadata handling (backend/vector_store.py)