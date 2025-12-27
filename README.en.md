# TENJIN - Education Theory GraphRAG MCP Server

<div align="center">

**Model Context Protocol (MCP) Server providing educational theory knowledge with GraphRAG**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.5+-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-MVP%20Complete-brightgreen.svg)]()

English | [日本語](README.md)

</div>

## Overview

TENJIN is an MCP server that provides 175+ educational theories using Graph + Vector RAG (Retrieval-Augmented Generation) technology. It enables AI assistants to leverage educational theory knowledge to support educators, researchers, and learners.

### Key Features

- 🎓 **175+ Educational Theories**: Comprehensive database spanning 9 categories including learning theories, developmental theories, and instructional methods
- 🔍 **Hybrid Search**: Graph structure search + vector similarity search + LLM reranking
- 🧠 **Advanced Inference**: Theory recommendations, gap analysis, relationship inference, evidence-based reasoning (NEW in v0.2)
- 🌐 **Multi-LLM Support**: Support for 15+ LLM providers via [esperanto](https://github.com/lfnovo/esperanto)
- 📚 **MCP Tools**: Theory search, analysis, comparison, recommendations, citation generation, and more
- 🇯🇵 **Bilingual Support**: Japanese and English
- 🏗️ **Clean Architecture**: 4-layer structure with high maintainability and testability
- 🛠️ **Theory Editor**: Web tool for editing and managing educational theory data

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker & Docker Compose (for Neo4j)
- Ollama or API Key (OpenAI, Anthropic, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/nahisaho/TENJIN.git
cd TENJIN

# Install dependencies (uv recommended)
pip install uv
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env file
```

### Start Database

```bash
# Start Neo4j
docker-compose up -d neo4j

# Wait for database to start (about 30 seconds on first run)
sleep 30
```

### Load Data

```bash
# Load educational theory data
uv run python -m scripts.load_data
```

### VS Code MCP Server Configuration

`.vscode/mcp.json` is already configured. Available in VS Code as `@tengin-graphrag`.

**Using Ollama (Recommended - Free):**

```json
{
  "servers": {
    "tengin-graphrag": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "tengin-server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "EMBEDDING_PROVIDER": "ollama",
        "EMBEDDING_MODEL": "nomic-embed-text",
        "OLLAMA_HOST": "http://localhost:11434"
      }
    }
  }
}
```

> **Note**: When using Ollama, download the model first with `ollama pull nomic-embed-text`.

**Using OpenAI (High Accuracy - Paid):**

```json
{
  "servers": {
    "tengin-graphrag": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "tengin-server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "EMBEDDING_PROVIDER": "openai",
        "EMBEDDING_MODEL": "text-embedding-3-small",
        "OPENAI_API_KEY": "sk-your-openai-key"
      }
    }
  }
}
```

**Using Azure OpenAI (Enterprise):**

```json
{
  "servers": {
    "tengin-graphrag": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "tengin-server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "EMBEDDING_PROVIDER": "azure",
        "EMBEDDING_MODEL": "text-embedding-3-small",
        "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com",
        "AZURE_OPENAI_API_KEY": "your-azure-openai-key",
        "AZURE_OPENAI_API_VERSION": "2024-02-01"
      }
    }
  }
}
```

### Integration with Claude Desktop

Add the following to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tenjin": {
      "command": "uv",
      "args": ["run", "tengin-server"],
      "cwd": "/path/to/TENJIN",
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "EMBEDDING_PROVIDER": "ollama",
        "EMBEDDING_MODEL": "nomic-embed-text"
      }
    }
  }
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Layer (MCP)                     │
│  ┌─────────┐ ┌───────────┐ ┌─────────┐ ┌─────────────────┐ │
│  │  Tools  │ │ Resources │ │ Prompts │ │ TenjinServer    │ │
│  │ (33+)   │ │ (15)      │ │ (15)    │ │                 │ │
│  └────┬────┘ └─────┬─────┘ └────┬────┘ └────────┬────────┘ │
└───────┼────────────┼────────────┼───────────────┼──────────┘
        │            │            │               │
┌───────┼────────────┼────────────┼───────────────┼──────────┐
│       ▼            ▼            ▼               ▼           │
│                   Application Layer                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐│
│  │TheoryService │ │SearchService │ │AnalysisService       ││
│  │GraphService  │ │Recommendation│ │CitationService       ││
│  │              │ │Service       │ │MethodologyService    ││
│  └──────┬───────┘ └──────┬───────┘ └───────────┬──────────┘│
└─────────┼────────────────┼─────────────────────┼───────────┘
          │                │                     │
┌─────────┼────────────────┼─────────────────────┼───────────┐
│         ▼                ▼                     ▼            │
│                    Domain Layer                             │
│  ┌────────────────┐ ┌──────────────┐ ┌───────────────────┐ │
│  │    Entities    │ │ Value Objects│ │Repository         │ │
│  │Theory,Theorist │ │TheoryId,     │ │Interfaces         │ │
│  │Category,etc.   │ │CategoryType  │ │                   │ │
│  └────────────────┘ └──────────────┘ └───────────────────┘ │
└────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼──────────────────────────────┐
│                             ▼                               │
│                  Infrastructure Layer                       │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────────────────┐ │
│  │ Neo4jAdapter│ │ChromaDB     │ │EsperantoAdapter       │ │
│  │ (Graph DB)  │ │Adapter      │ │(Multi-LLM)            │ │
│  │             │ │(Vector DB)  │ │                       │ │
│  └─────────────┘ └─────────────┘ └───────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

## MCP Tools

Key MCP tools:

| Tool | Description |
|------|-------------|
| `search_theories` | Search theories by keyword or semantic search |
| `get_theory` | Get detailed theory information |
| `traverse_graph` | Explore related theories via graph traversal |
| `compare_theories` | Compare and analyze multiple theories |
| `cite_theory` | Generate citations in APA/MLA format |

## Educational Theory Categories

| Category | Description | Count |
|----------|-------------|-------|
| Learning Theories | Behaviorism, Cognitivism, Constructivism, etc. | 38 |
| Developmental Theories | Cognitive development, Socio-emotional development, etc. | 18 |
| Instructional Methods | PBL, Flipped learning, Socratic method, etc. | 32 |
| Curriculum | Backward design, Spiral curriculum, etc. | 10 |
| Motivation | Self-determination theory, Growth mindset, etc. | 16 |
| Assessment | Formative assessment, Rubric assessment, etc. | 12 |
| Social Learning | Collaborative learning, Communities of practice, etc. | 18 |
| Eastern/Asian | Lesson study, Confucian educational philosophy, etc. | 28 |
| Technology | Connectivism, TPACK, etc. | 22 |

## Configuration

### Environment Variables

```bash
# Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Embedding (Ollama recommended)
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
OLLAMA_HOST=http://localhost:11434

# Or OpenAI
# EMBEDDING_PROVIDER=openai
# EMBEDDING_MODEL=text-embedding-3-small
# OPENAI_API_KEY=your-key

# Logging
LOG_LEVEL=INFO
```

### Supported Embedding Providers

The following providers are supported via esperanto:

| Provider | Model Example | Dimensions |
|----------|---------------|------------|
| **Ollama** (Recommended) | nomic-embed-text | 768 |
| OpenAI | text-embedding-3-small | 1536 |
| Google | text-embedding-004 | 768 |
| Azure OpenAI | text-embedding-ada-002 | 1536 |

## Tools

### Theory Editor

Web-based GUI tool for editing and managing educational theory data.

```bash
# Start Theory Editor
cd tools/theory-editor
python -m http.server 8080

# Open in browser
open http://localhost:8080
```

**Features:**
- Add, edit, and delete theories
- Filter by category and tags
- Version control and diff display
- Real-time sync to Neo4j (sync-server.py)
- JSON/CSV export

Details: [tools/theory-editor/README.md](tools/theory-editor/README.md)

## Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=tenjin --cov-report=html

# Specific tests
pytest tests/unit/test_entities.py -v
```

### Type Checking

```bash
mypy src/tenjin
```

### Code Formatting

```bash
ruff format src tests
ruff check --fix src tests
```

## Directory Structure

```
TENJIN/
├── .vscode/                 # VS Code settings
│   └── mcp.json             # MCP server configuration
├── src/tenjin/              # Main source code
│   ├── domain/              # Domain layer
│   │   ├── entities/        # Entities
│   │   ├── value_objects/   # Value objects
│   │   └── repositories/    # Repository interfaces
│   ├── application/         # Application layer
│   │   └── services/        # Business logic services
│   ├── infrastructure/      # Infrastructure layer
│   │   ├── adapters/        # External system adapters
│   │   └── config/          # Configuration
│   └── interface/           # Interface layer (MCP)
├── tools/                   # Development tools
│   └── theory-editor/       # Educational theory editor (Web GUI)
│       ├── index.html
│       ├── js/              # Modularized JS
│       ├── sync-server.py   # Neo4j sync server
│       └── docs/            # Documentation
├── data/theories/           # Educational theory JSON data
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
├── steering/                # Project memory (MUSUBI SDD)
├── storage/specs/           # Specifications
├── docker-compose.yml
└── pyproject.toml
```

## License

MIT License - See [LICENSE](LICENSE) for details

## Contributing

Pull requests are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Documentation

- [Installation Guide (Japanese)](docs/INSTALLATION_GUIDE.ja.md) - Setup instructions
- [Usage Guide (Japanese)](docs/USAGE_GUIDE.ja.md) - Basic usage
- [API Reference](docs/API_REFERENCE.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Theory Editor](tools/theory-editor/README.md)

## Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [esperanto](https://github.com/lfnovo/esperanto)
- [Neo4j](https://neo4j.com/)
- [Ollama](https://ollama.ai/)

---

**TENJIN** - Empowering AI with the wisdom of educational theories 🎓
