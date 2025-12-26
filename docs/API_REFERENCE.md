# TENJIN API Reference

This document provides detailed API documentation for the TENJIN Education Theory GraphRAG MCP Server.

## Table of Contents

- [MCP Tools](#mcp-tools)
- [MCP Resources](#mcp-resources)
- [MCP Prompts](#mcp-prompts)
- [Domain Entities](#domain-entities)
- [Services](#services)

---

## MCP Tools

### Theory Tools

#### `get_theory`

Retrieve a theory by its ID.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `theory_id` | string | Yes | The unique identifier of the theory |
| `include_related` | boolean | No | Include related theories (default: false) |

**Returns:**
```json
{
  "id": "theory-001",
  "name": "Constructivism",
  "name_ja": "構成主義",
  "category": "learning_theory",
  "priority": 5,
  "description": "Learning theory where learners actively construct knowledge...",
  "description_ja": "学習者が能動的に知識を構築する学習理論...",
  "theorists": ["Jean Piaget", "John Dewey"],
  "key_principles": ["Knowledge is actively constructed", ...],
  "applications": ["Inquiry-based learning", ...],
  "strengths": ["Promotes deep understanding", ...],
  "limitations": ["Time-intensive", ...]
}
```

---

#### `list_theories`

List all theories with optional filtering.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `limit` | integer | No | Maximum number of results (default: 50) |
| `offset` | integer | No | Number of results to skip (default: 0) |
| `sort_by` | string | No | Field to sort by: "name", "priority", "category" |
| `sort_order` | string | No | Sort order: "asc" or "desc" |

**Returns:**
```json
{
  "theories": [...],
  "total": 200,
  "limit": 50,
  "offset": 0
}
```

---

#### `get_theories_by_category`

Get theories filtered by category.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `category` | string | Yes | Category ID |
| `limit` | integer | No | Maximum results (default: 50) |

**Valid Categories:**
- `learning_theory` - Learning Theory (学習理論)
- `developmental` - Developmental Theory (発達理論)
- `instructional_design` - Instructional Design (教授法)
- `curriculum` - Curriculum Theory (カリキュラム)
- `motivation` - Motivation Theory (動機づけ)
- `assessment` - Assessment Theory (評価)
- `social_learning` - Social Learning (社会的学習)
- `asian_education` - Asian Education (東洋・アジア)
- `technology_enhanced` - Technology Enhanced (テクノロジー)
- `modern_education` - Modern Education (現代教育)
- `critical_alternative` - Critical & Alternative (批判的・代替)

---

### Search Tools

#### `search_theories`

Search theories by keyword.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `limit` | integer | No | Maximum results (default: 10) |

---

#### `semantic_search`

Perform semantic similarity search.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | Natural language query |
| `limit` | integer | No | Maximum results (default: 10) |
| `threshold` | float | No | Minimum similarity score (0-1) |

---

#### `hybrid_search`

Combine graph and vector search with LLM reranking.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `limit` | integer | No | Maximum results (default: 10) |
| `graph_weight` | float | No | Weight for graph results (0-1, default: 0.5) |
| `vector_weight` | float | No | Weight for vector results (0-1, default: 0.5) |
| `rerank` | boolean | No | Apply LLM reranking (default: true) |

---

### Graph Tools

#### `get_related_theories`

Get theories related to a given theory.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `theory_id` | string | Yes | Source theory ID |
| `relationship_types` | array[string] | No | Filter by relationship types |
| `depth` | integer | No | Traversal depth (default: 1, max: 3) |
| `limit` | integer | No | Maximum results (default: 20) |

**Relationship Types:**
- `influences` - Theory A influences Theory B
- `extends` - Theory A extends Theory B
- `contrasts_with` - Theories have contrasting views
- `complements` - Theories complement each other
- `derived_from` - Theory A is derived from Theory B
- `applied_in` - Theory is applied in context
- `evolved_into` - Theory A evolved into Theory B
- `integrates` - Theory integrates multiple concepts
- `critiques` - Theory A critiques Theory B
- `supports` - Theory A supports Theory B

---

#### `find_theory_path`

Find the shortest path between two theories.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `source_id` | string | Yes | Starting theory ID |
| `target_id` | string | Yes | Ending theory ID |
| `max_depth` | integer | No | Maximum path length (default: 5) |

**Returns:**
```json
{
  "path": ["theory-001", "theory-003", "theory-002"],
  "relationships": ["influences", "extends"],
  "length": 2
}
```

---

#### `get_theory_network`

Get the network around a theory.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `theory_id` | string | Yes | Center theory ID |
| `depth` | integer | No | Network depth (default: 2) |
| `include_metadata` | boolean | No | Include node metadata |

**Returns:**
```json
{
  "nodes": [
    {"id": "theory-001", "name": "Constructivism", "category": "learning_theory"},
    ...
  ],
  "edges": [
    {"source": "theory-001", "target": "theory-002", "type": "influences", "strength": 0.8},
    ...
  ]
}
```

---

### Analysis Tools

#### `compare_theories`

Compare multiple theories.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `theory_ids` | array[string] | Yes | List of theory IDs to compare (2-5) |
| `aspects` | array[string] | No | Comparison aspects |

**Returns:**
```json
{
  "theories": [...],
  "similarities": ["Both emphasize active learning", ...],
  "differences": ["Different views on social context", ...],
  "synthesis": "These theories complement each other in...",
  "recommendations": [...]
}
```

---

#### `analyze_theory`

Perform deep analysis of a theory.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `theory_id` | string | Yes | Theory to analyze |
| `context` | string | No | Educational context for analysis |
| `depth` | string | No | Analysis depth: "basic", "detailed", "comprehensive" |

---

### Citation Tools

#### `generate_citation`

Generate a citation for a theory.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `theory_id` | string | Yes | Theory ID |
| `style` | string | No | Citation style: "apa", "mla", "chicago", "harvard" |

**Returns:**
```json
{
  "citation": "Piaget, J. (1952). The origins of intelligence in children...",
  "style": "apa"
}
```

---

#### `export_citations`

Export citations in standard formats.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `theory_ids` | array[string] | Yes | Theory IDs to export |
| `format` | string | Yes | Export format: "bibtex", "ris" |

---

## MCP Resources

### Theory Resources

| URI Pattern | Description |
|-------------|-------------|
| `theories://all` | All theories in the database |
| `theories://category/{category}` | Theories in a specific category |
| `theories://priority/{level}` | Theories by priority level (1-5) |
| `theory://{theory_id}` | Single theory by ID |

### Theorist Resources

| URI Pattern | Description |
|-------------|-------------|
| `theorists://all` | All theorists |
| `theorist://{theorist_id}` | Single theorist by ID |

### Graph Resources

| URI Pattern | Description |
|-------------|-------------|
| `categories://all` | All categories |
| `relationships://all` | All relationships |
| `relationships://type/{type}` | Relationships by type |
| `graph://full` | Complete knowledge graph |
| `graph://theory/{theory_id}` | Subgraph around theory |

### Statistics Resources

| URI Pattern | Description |
|-------------|-------------|
| `statistics://theories` | Theory statistics |
| `statistics://categories` | Category statistics |

---

## MCP Prompts

### `lesson_plan`

Generate a lesson plan using educational theories.

**Arguments:**
| Name | Type | Description |
|------|------|-------------|
| `topic` | string | Lesson topic |
| `grade_level` | string | Target grade level |
| `duration` | string | Lesson duration |
| `learning_objectives` | string | Specific learning objectives |

---

### `theory_analysis`

Analyze a theory for practical application.

**Arguments:**
| Name | Type | Description |
|------|------|-------------|
| `theory_name` | string | Name of theory to analyze |
| `context` | string | Educational context |
| `audience` | string | Target audience |

---

### `theory_comparison`

Compare multiple theories.

**Arguments:**
| Name | Type | Description |
|------|------|-------------|
| `theories` | string | Comma-separated theory names |
| `focus_areas` | string | Areas to compare |

---

### `japanese_context`

Adapt theories for Japanese educational context.

**Arguments:**
| Name | Type | Description |
|------|------|-------------|
| `theory_name` | string | Theory to adapt |
| `school_level` | string | 小学校, 中学校, 高等学校, etc. |
| `subject` | string | Subject area |

---

## Domain Entities

### Theory

```python
class Theory:
    id: TheoryId
    name: str
    name_ja: str
    category: CategoryType
    priority: PriorityLevel
    theorist_names: list[str]
    description: str
    description_ja: str
    key_principles: list[str]
    applications: list[str]
    strengths: list[str]
    limitations: list[str]
```

### Theorist

```python
class Theorist:
    id: TheoristId
    name: str
    name_ja: str
    birth_year: int | None
    death_year: int | None
    nationality: str | None
    primary_field: str | None
    contributions: list[str]
    key_works: list[str]
    related_theory_ids: list[TheoryId]
```

### Category

```python
class Category:
    id: CategoryId
    name: str
    name_ja: str
    description: str
    description_ja: str
    theory_count: int
    color: str | None
```

### TheoryRelationship

```python
class TheoryRelationship:
    id: str
    source_id: TheoryId
    target_id: TheoryId
    relationship_type: RelationshipType
    strength: float  # 0.0 - 1.0
    description: str | None
```

---

## Services

### TheoryService

Core service for theory operations.

```python
class TheoryService:
    async def get_theory(theory_id: str) -> Theory | None
    async def list_theories(limit: int, offset: int) -> list[Theory]
    async def get_by_category(category: CategoryType) -> list[Theory]
    async def search_theories(query: str) -> list[Theory]
    async def get_statistics() -> dict
```

### SearchService

Hybrid search functionality.

```python
class SearchService:
    async def semantic_search(query: str, limit: int) -> list[SearchResult]
    async def hybrid_search(query: str, limit: int) -> list[SearchResult]
    async def find_similar(theory_id: str, limit: int) -> list[Theory]
```

### GraphService

Graph traversal and analysis.

```python
class GraphService:
    async def get_related_theories(theory_id: str, depth: int) -> list[dict]
    async def find_path(source: str, target: str) -> dict
    async def get_theory_network(theory_id: str, depth: int) -> dict
```

### AnalysisService

LLM-powered analysis.

```python
class AnalysisService:
    async def compare_theories(theory_ids: list[str]) -> dict
    async def analyze_theory(theory_id: str, context: str) -> dict
    async def synthesize_theories(theory_ids: list[str]) -> dict
```

---

## Error Handling

All tools return errors in a consistent format:

```json
{
  "error": {
    "code": "THEORY_NOT_FOUND",
    "message": "Theory with ID 'theory-999' not found",
    "details": {}
  }
}
```

**Common Error Codes:**
- `THEORY_NOT_FOUND` - Theory ID does not exist
- `INVALID_CATEGORY` - Invalid category specified
- `SEARCH_FAILED` - Search operation failed
- `GRAPH_ERROR` - Graph database error
- `LLM_ERROR` - LLM service error
- `VALIDATION_ERROR` - Input validation failed
