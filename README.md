# RepoLens 🔎

**RepoLens** is a read-only GitHub Repository RAG & Code Understanding Assistant that helps developers understand unfamiliar codebases using Retrieval-Augmented Generation (RAG), semantic code search, repository analysis, and LLM-powered reasoning.

Instead of manually searching through hundreds of files, a user can provide a public GitHub repository URL and ask questions about its structure, classes, functions, references, and implementation details.

## Features

- Accept a public GitHub repository URL
- Clone and analyze repositories locally
- Filter irrelevant, binary, generated, and oversized files
- Load source code and documentation
- Split code into meaningful chunks
- Use Python AST analysis for Python functions and classes
- Generate semantic embeddings using Sentence Transformers
- Store embeddings in ChromaDB
- Perform semantic code search
- Search source files for exact text or code patterns
- Find function and class definitions
- Find references to functions, classes, and symbols
- Read specific files and line ranges
- Display repository structure
- Use LangGraph to control the agent workflow
- Use Groq-hosted GPT-OSS for question answering and tool selection
- Return source-grounded answers with file and line references
- Provide a Streamlit web interface
- Use persistent repository-specific caching
- Reuse previously generated embeddings when a repository is loaded again
- Remain strictly read-only and do not modify GitHub repositories

## Architecture

```text
GitHub Repository
       ↓
Clone & Filter Files
       ↓
Document Loading
       ↓
Python AST / Code Chunking
       ↓
Sentence Transformer Embeddings
       ↓
ChromaDB
       ↓
User Question
       ↓
LangGraph Agent
       ↓
Semantic Search / Repository Tools
       ↓
Groq / GPT-OSS
       ↓
Source-Grounded Answer
```

## How It Works

### Repository indexing

When a repository is loaded for the first time, RepoLens:

1. Validates the GitHub URL.
2. Clones the repository using GitPython.
3. Filters irrelevant directories and unsupported files.
4. Checks file size and binary status.
5. Loads relevant source code and documentation.
6. Splits content into useful chunks.
7. Generates embeddings using `all-MiniLM-L6-v2`.
8. Stores embeddings and metadata in ChromaDB.
9. Saves repository index metadata for future reuse.

### Question answering

When a user asks a question:

1. The question enters the LangGraph workflow.
2. GPT-OSS determines whether repository tools are required.
3. The agent can use semantic search, code search, definition lookup, reference lookup, file lookup, or repository structure tools.
4. Relevant repository information is returned to the model.
5. The model generates an answer grounded in the retrieved repository content.
6. File paths and line numbers are included when available.

## Repository Tools

### Repository structure

Displays the directory and file structure of the repository.

### Semantic search

Uses vector similarity to find code and documentation related to a natural-language question.

### Code search

Performs case-insensitive text and code-pattern searches across repository files.

### Definition lookup

Uses Python AST analysis to find function and class definitions.

### Reference lookup

Finds textual references to a function, class, or symbol.

### File lookup

Reads a specific repository file or selected line range and returns numbered source code.

## Technology Stack

| Technology            | Purpose                               |
| --------------------- | ------------------------------------- |
| Python                | Core application                      |
| Streamlit             | Web interface                         |
| LangGraph             | Agent workflow                        |
| Groq                  | LLM inference                         |
| GPT-OSS               | Question answering and tool selection |
| Sentence Transformers | Semantic embeddings                   |
| all-MiniLM-L6-v2      | Embedding model                       |
| ChromaDB              | Vector database                       |
| GitPython             | Repository cloning                    |
| Python AST            | Code analysis                         |
| python-dotenv         | Environment configuration             |

## Project Structure

```text
github-rag-agent/
│
├── app/
│   ├── __init__.py
│   ├── agent_state.py
│   ├── basic_graph.py
│   ├── chunker.py
│   ├── code_search.py
│   ├── config.py
│   ├── definition_lookup.py
│   ├── document_loader.py
│   ├── embeddings.py
│   ├── github_loader.py
│   ├── groq_tools.py
│   ├── reference_lookup.py
│   ├── repository_agent_tools.py
│   ├── repository_tools.py
│   ├── streamlit_app.py
│   ├── vector_store.py
│   └── ...
│
├── tests/
├── data/
│   └── repositories/
├── chroma_db/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the project

```bash
git clone https://github.com/YOUR_USERNAME/github-rag-agent.git
cd github-rag-agent
```

### 2. Create the Conda environment

The project was developed using Python 3.11.

```bash
conda create -n github-rag python=3.11
conda activate github-rag
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `.env` in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Do not commit `.env` to GitHub.

## Running the Application

From the project root:

```bash
python -m streamlit run app/streamlit_app.py
```

Then open the local Streamlit URL, normally:

```text
http://localhost:8501
```

## Using RepoLens

### Step 1 — Load a repository

Enter a public GitHub repository URL.

Example:

```text
https://github.com/bottlepy/bottle
```

Click **Load Repository**.

The first load clones and indexes the repository.

### Step 2 — Ask a question

Example:

```text
Find the definition of the Bottle class.
```

RepoLens retrieves relevant source code and provides the file and line number.

### Step 3 — Switch repositories

Previously indexed repositories remain cached.

For example:

```text
Bottle
  ↓
Requests
  ↓
Flask
  ↓
Bottle
```

Returning to Bottle can reuse its existing repository files and embeddings.

## Demo Questions

A simple demonstration repository is:

```text
https://github.com/bottlepy/bottle
```

Recommended demo questions:

```text
Find the definition of the Bottle class.
```

```text
Find the definition of the route decorator.
```

```text
Show me the repository structure.
```

These demonstrate definition lookup, source retrieval, line references, and repository exploration.

## Persistent Caching

Each repository maintains its own local copy:

```text
data/
└── repositories/
    ├── bottlepy__bottle/
    ├── pallets__flask/
    └── psf__requests/
```

ChromaDB also maintains separate collections for different repositories.

When a previously indexed repository is loaded again, RepoLens can reuse its existing embeddings instead of generating them again.

The embedding model is also cached in memory during the application process.

## Code Chunking

Python source code is analyzed using the Python AST to identify meaningful structures such as:

- Functions
- Classes
- Methods

Chunks store metadata including:

```text
path
language
category
type
name
parent_class
start_line
end_line
```

This metadata connects retrieved results back to the original repository source.

## Embeddings

RepoLens uses:

```text
all-MiniLM-L6-v2
```

from Sentence Transformers.

The model produces 384-dimensional embeddings.

These embeddings allow semantically related source code and documentation to be retrieved even when the exact words in a question do not appear in the source.

## ChromaDB

ChromaDB stores:

- Code and documentation chunks
- Embeddings
- File paths
- Programming language
- Chunk type
- Function/class names
- Parent class
- Starting line
- Ending line

Each repository has its own vector collection.

## Agent Workflow

LangGraph manages the question-answering workflow:

```text
START
  ↓
Model
  ├── No tool required → END
  │
  └── Tool required
          ↓
        Tools
          ↓
        Model
          ↓
         END
```

The model can request repository tools when additional information is required.

## Read-Only Design

RepoLens is intentionally read-only.

It can:

- Clone repositories
- Read files
- Search files
- Analyze source code
- Retrieve definitions and references
- Generate explanations

It does not:

- Modify repository files
- Create commits
- Create branches
- Push changes
- Delete GitHub files
- Automatically apply code changes
- Execute repository code as part of the analysis workflow

## Testing

The project has been tested with public repositories including:

```text
https://github.com/pallets/flask
https://github.com/psf/requests
https://github.com/bottlepy/bottle
```

Testing covered repository loading, document loading, chunking, embeddings, semantic search, definition lookup, reference lookup, repository structure exploration, and agent-based questions.

## Performance

The first load of a repository requires:

- Cloning
- File scanning
- Document loading
- Chunking
- Embedding generation
- Vector storage

This can take some time for larger repositories.

Previously indexed repositories can reuse:

- Local repository files
- Existing ChromaDB collections
- Existing embeddings

This makes repeated repository switching considerably faster.

## Limitations

- Primarily designed for public GitHub repositories
- Large repositories take longer to index initially
- Code analysis is currently strongest for Python
- Retrieval quality depends on the embedding model and chunking strategy
- LLM responses depend on retrieved repository context
- GPT-OSS tool calling can occasionally produce malformed tool-call output
- Repository code is not executed during analysis
- The current system does not modify repositories

## Future Improvements

Potential improvements include:

- More reliable LLM tool calling
- Detailed indexing progress indicators
- Improved multi-language AST/code analysis
- Hybrid keyword and semantic search
- Search result reranking
- Better repository-level architecture analysis
- More comprehensive evaluation
- Additional Git hosting platforms
- More detailed source citations
- Optional code-generation assistance while preserving the read-only default

## Development Approach

The project was developed incrementally:

1. GitHub repository loading
2. Document loading
3. Code chunking
4. Embedding generation
5. ChromaDB vector storage
6. Semantic search
7. Repository search tools
8. Definition and reference lookup
9. LangGraph workflow
10. Groq / GPT-OSS integration
11. Streamlit interface
12. Persistent repository caching
13. Repository-specific vector indexes
14. UI polishing and demo testing

## Security

API keys are stored in `.env` and should never be committed.

The `.gitignore` excludes:

```text
.env
data/
chroma_db/
```

## Why This Project?

Understanding an unfamiliar codebase can require significant time, especially when repositories contain hundreds or thousands of files.

RepoLens explores how RAG and LLM-based agents can assist developers by connecting natural-language questions with actual source-code evidence.

The project combines:

- Retrieval-Augmented Generation
- Large Language Models
- Vector databases
- Semantic search
- Static code analysis
- Agent workflows
- GitHub repository processing
- Web application development

## Author

**Themiya Dulshan**

Computer Science Undergraduate  
AI/ML & Web Development | XR Enthusiast

## License

```text
MIT License
```
