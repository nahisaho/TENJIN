# 要件仕様書: TENJIN 教育理論GraphRAG MCPサーバー

**ID**: REQ-001
**Feature**: TENJIN Education Theory GraphRAG MCP Server
**Version**: 1.0
**Created**: 2025-12-26
**Updated**: 2025-12-26
**Status**: Draft
**Author**: GitHub Copilot

---

## 1. 概要

### 1.1 背景

生成AIが教育コンテンツを生成する際、教育理論に基づいたエビデンスベースのコンテンツを生成することが求められている。既存のTENGIN-GraphRAG（参照実装）を基盤として、より高性能で拡張性の高いシステムを構築する。

### 1.2 目的

教育理論のナレッジグラフを構築し、**Model Context Protocol（MCP）サーバー**として公開することで、あらゆるMCP対応AIアプリケーション（Claude Desktop、VS Code、その他）が理論に基づいた教育コンテンツを生成できるようにする。

### 1.3 参照実装との差別化

| 観点 | 参照実装（TENGIN-GraphRAG） | TENJIN（本システム） |
|------|---------------------------|---------------------|
| LLM連携 | 限定的（埋め込みのみ） | esperantoによる統合LLM連携 |
| 推論機能 | なし | LLMベースの理論推論・推薦 |
| 教育理論数 | 38理論 | **200理論**（9カテゴリ網羅） |
| マルチモーダル | テキストのみ | 画像・音声対応（将来） |
| レコメンド | 単純検索 | RAG+LLM推論ハイブリッド |
| キャッシュ | シンプルTTL | 階層型インテリジェントキャッシュ |
| 分析機能 | 基本的 | 学習分析・トレンド分析 |
| データソース | 独自収集 | Educational-theory-research.md |

### 1.4 MCP（Model Context Protocol）

Model Context Protocol (MCP) は、AIアプリケーションと外部システムを接続するためのAnthropicが策定したオープンスタンダード。MCPサーバーは以下の3つのプリミティブを提供する：

| プリミティブ | 説明 | 制御主体 |
|-------------|------|---------|
| **Tools** | LLMが呼び出せる実行可能な関数 | Model |
| **Resources** | コンテキストとして提供する読み取り専用データ | Application |
| **Prompts** | 特定タスクのための再利用可能なテンプレート | User |

### 1.5 スコープ

| 項目 | スコープ内 | スコープ外 |
|------|-----------|-----------|
| MCPサーバー実装 | ✅ | |
| 教育理論ナレッジグラフ | ✅ | |
| esperanto LLM統合 | ✅ | |
| 高度な推論機能 | ✅ | |
| ハイブリッドRAG検索 | ✅ | |
| Tools（30+ツール） | ✅ | |
| Resources（理論・概念・エビデンス） | ✅ | |
| Prompts（教育テンプレート） | ✅ | |
| MCPクライアント実装 | | ❌ |
| 独自Web UI | | ❌ |
| モバイルアプリ | | ❌ |

---

## 2. システムアーキテクチャ

### 2.1 アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MCP Hosts (AI Applications)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │Claude Desktop│  │   VS Code    │  │  Claude Code │  │  Custom MCP App │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘  │
│         │                 │                 │                   │           │
│         └─────────────────┴─────────────────┴───────────────────┘           │
│                                     │                                        │
│                              MCP Clients                                     │
└─────────────────────────────────────┼────────────────────────────────────────┘
                                      │
                        ┌─────────────┴─────────────┐
                        │  JSON-RPC 2.0 (stdio/SSE)  │
                        └─────────────┬─────────────┘
                                      │
┌─────────────────────────────────────┴────────────────────────────────────────┐
│                      TENJIN Education Theory MCP Server                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                           MCP Interface Layer                          │  │
│  │                                                                        │  │
│  │  ┌──────────────────┐  ┌───────────────┐  ┌─────────────────────────┐  │  │
│  │  │   Tools (30+)    │  │  Resources    │  │      Prompts (15+)      │  │  │
│  │  │                  │  │               │  │                         │  │  │
│  │  │ • Search         │  │ • Theories    │  │ • Lesson Design         │  │  │
│  │  │ • Query          │  │ • Concepts    │  │ • Assessment Create     │  │  │
│  │  │ • Traverse       │  │ • Theorists   │  │ • Theory Explain        │  │  │
│  │  │ • Recommend      │  │ • Evidence    │  │ • Curriculum Plan       │  │  │
│  │  │ • Analyze        │  │ • Methods     │  │ • Case Study            │  │  │
│  │  │ • Generate       │  │ • Contexts    │  │ • Debate                │  │  │
│  │  └──────────────────┘  └───────────────┘  └─────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                        │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                        Application Layer                               │  │
│  │                                                                        │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  ┌───────────────┐  │  │
│  │  │   Search    │  │  Reasoning   │  │ Recommend  │  │   Analysis    │  │  │
│  │  │   Service   │  │   Service    │  │  Service   │  │   Service     │  │  │
│  │  │             │  │              │  │            │  │               │  │  │
│  │  │ • Semantic  │  │ • Inference  │  │ • Hybrid   │  │ • Trend       │  │  │
│  │  │ • Graph     │  │ • Deduction  │  │ • Context  │  │ • Pattern     │  │  │
│  │  │ • Hybrid    │  │ • Analogy    │  │ • Personal │  │ • Gap         │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────┘  └───────────────┘  │  │
│  │                                                                        │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  ┌───────────────┐  │  │
│  │  │   Graph     │  │   Citation   │  │   Cache    │  │   Content     │  │  │
│  │  │   Service   │  │   Service    │  │  Manager   │  │  Generator    │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────┘  └───────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                        │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                        Domain Layer (Core)                              │  │
│  │                                                                        │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐  │  │
│  │  │                         Entities                                  │  │  │
│  │  │                                                                   │  │  │
│  │  │  Theory | Theorist | Concept | Principle | Evidence | Method     │  │  │
│  │  │  Context | Paradigm | Relationship | Citation                    │  │  │
│  │  └──────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                        │  │
│  │  ┌─────────────────────────────────┬────────────────────────────────┐  │  │
│  │  │        Value Objects            │      Domain Services           │  │  │
│  │  │                                 │                                │  │  │
│  │  │  TheoryId | ConceptId           │  TheoryMatcher                 │  │  │
│  │  │  EvidenceLevel | RelationType   │  RelationshipResolver          │  │  │
│  │  │  CitationFormat | LearnerType   │  EvidenceEvaluator             │  │  │
│  │  └─────────────────────────────────┴────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                      │                                        │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                      Infrastructure Layer                              │  │
│  │                                                                        │  │
│  │  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │  │
│  │  │  Neo4j       │  │  ChromaDB   │  │  esperanto  │  │   External   │  │  │
│  │  │  Adapter     │  │  Adapter    │  │  Adapter    │  │   API Adaptr │  │  │
│  │  │              │  │             │  │             │  │              │  │  │
│  │  │  Graph DB    │  │  Vector DB  │  │  LLM/Embed  │  │  Reference   │  │  │
│  │  └──────────────┘  └─────────────┘  └─────────────┘  └──────────────┘  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
    ┌─────────────────────────────────┼─────────────────────────────────┐
    │                                 │                                 │
    ▼                                 ▼                                 ▼
┌──────────────┐            ┌──────────────┐              ┌──────────────────┐
│    Neo4j     │            │   ChromaDB   │              │    esperanto     │
│  Graph DB    │            │  Vector DB   │              │   LLM Gateway    │
│              │            │              │              │                  │
│ • 100+ 理論  │            │ • Embedding  │              │ • OpenAI         │
│ • 500+ 関係  │            │ • Semantic   │              │ • Anthropic      │
│ • メタデータ │            │   Index      │              │ • Google         │
└──────────────┘            └──────────────┘              │ • Ollama         │
                                                          │ • +15 providers  │
                                                          └──────────────────┘
```

### 2.2 トランスポート

| トランスポート | 用途 | 特徴 |
|---------------|------|------|
| **STDIO** | ローカル実行 | Claude Desktop、VS Code連携、低レイテンシ |
| **SSE (Server-Sent Events)** | リモート実行 | 複数クライアント対応、ストリーミング |

---

## 3. 機能要件（EARS形式）

### 3.1 ツールカテゴリ

TENJINは以下のカテゴリのMCP Toolsを提供する：

| カテゴリ | ツール数 | 説明 |
|---------|---------|------|
| **検索・クエリ** | 8 | 理論検索、概念検索、グラフクエリ |
| **推論・分析** | 6 | 理論推論、パターン分析、ギャップ分析 |
| **推薦** | 5 | コンテキスト推薦、パーソナライズ推薦 |
| **生成** | 6 | 引用生成、説明生成、サマリー生成 |
| **比較・評価** | 5 | 理論比較、エビデンス評価 |
| **システム** | 3 | ヘルス、メタデータ、統計 |

---

### 3.2 検索・クエリツール

#### REQ-TOOL-001: search_theories
**Type**: Event-driven
**Priority**: P0 (Critical)

```
WHEN a user submits a natural language query about educational theories,
the system SHALL perform hybrid search (semantic + keyword + graph)
AND return relevant theories ranked by composite relevance score.
```

**JSON Schema**:
```json
{
  "name": "search_theories",
  "description": "Search for educational theories using natural language. Combines semantic similarity, keyword matching, and graph relationships for comprehensive results.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Natural language search query"
      },
      "limit": {
        "type": "integer",
        "default": 10,
        "maximum": 50,
        "description": "Maximum results to return"
      },
      "search_mode": {
        "type": "string",
        "enum": ["semantic", "keyword", "graph", "hybrid"],
        "default": "hybrid",
        "description": "Search strategy"
      },
      "filters": {
        "type": "object",
        "properties": {
          "paradigm": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Filter by paradigm (behaviorism, cognitivism, etc.)"
          },
          "evidence_level": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Minimum evidence level"
          },
          "year_range": {
            "type": "object",
            "properties": {
              "from": { "type": "integer" },
              "to": { "type": "integer" }
            }
          }
        }
      }
    },
    "required": ["query"]
  }
}
```

**Acceptance Criteria**:
- [ ] セマンティック検索でコサイン類似度0.7以上の理論を取得
- [ ] グラフ検索で関連理論を2ホップまで探索
- [ ] 複合スコアでランキング
- [ ] フィルタ適用時は条件を満たす結果のみ返却
- [ ] 応答時間 < 500ms (キャッシュヒット時 < 50ms)

---

#### REQ-TOOL-002: get_theory
**Type**: Ubiquitous
**Priority**: P0 (Critical)

```
The system SHALL provide comprehensive details about a specific theory
including metadata, concepts, principles, evidence, and relationships.
```

**JSON Schema**:
```json
{
  "name": "get_theory",
  "description": "Get comprehensive details about a specific educational theory.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "theory_id": {
        "type": "string",
        "description": "Theory ID or exact name"
      },
      "include": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["concepts", "principles", "evidence", "theorists", "relationships", "methods", "all"]
        },
        "default": ["concepts", "principles"],
        "description": "Data to include in response"
      },
      "depth": {
        "type": "integer",
        "default": 1,
        "maximum": 3,
        "description": "Relationship traversal depth"
      }
    },
    "required": ["theory_id"]
  }
}
```

**Acceptance Criteria**:
- [ ] 有効なtheory_idで完全な理論詳細を返却
- [ ] includeパラメータで選択的データ取得
- [ ] 存在しないIDの場合は適切なエラーメッセージ
- [ ] 応答時間 < 200ms

---

#### REQ-TOOL-003: traverse_graph
**Type**: Event-driven
**Priority**: P0 (Critical)

```
WHEN a user wants to explore relationships between theories,
the system SHALL traverse the knowledge graph from a starting node
AND return related entities with relationship metadata.
```

**JSON Schema**:
```json
{
  "name": "traverse_graph",
  "description": "Traverse the theory knowledge graph to discover related theories, concepts, and theorists.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "start_id": {
        "type": "string",
        "description": "Starting node ID (theory, concept, or theorist)"
      },
      "start_type": {
        "type": "string",
        "enum": ["theory", "concept", "theorist"],
        "default": "theory"
      },
      "depth": {
        "type": "integer",
        "default": 2,
        "minimum": 1,
        "maximum": 5,
        "description": "Traversal depth"
      },
      "relation_types": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": [
            "BASED_ON", "EXTENDS", "CONTRADICTS", "COMPLEMENTS",
            "PROPOSED_BY", "INFLUENCED_BY", "HAS_CONCEPT", "HAS_PRINCIPLE",
            "SUPPORTS", "APPLIES_TO", "RELATED_TO"
          ]
        },
        "description": "Filter by relationship types"
      },
      "output_format": {
        "type": "string",
        "enum": ["tree", "graph", "list"],
        "default": "tree"
      }
    },
    "required": ["start_id"]
  }
}
```

**Acceptance Criteria**:
- [ ] 指定した深さまで正確にトラバース
- [ ] 関係タイプによるフィルタリングが機能
- [ ] 循環参照を適切に処理
- [ ] 出力形式に応じた適切なフォーマット
- [ ] 応答時間 < 300ms (depth=2の場合)

---

#### REQ-TOOL-004: search_concepts
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user searches for educational concepts,
the system SHALL search the concept index
AND return concepts with their associated theories.
```

**JSON Schema**:
```json
{
  "name": "search_concepts",
  "description": "Search for educational concepts and their associated theories.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Concept search query"
      },
      "limit": {
        "type": "integer",
        "default": 10
      },
      "include_theories": {
        "type": "boolean",
        "default": true,
        "description": "Include associated theories"
      }
    },
    "required": ["query"]
  }
}
```

---

#### REQ-TOOL-005: search_theorists
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user searches for educational theorists,
the system SHALL search the theorist index
AND return theorists with their contributions.
```

**JSON Schema**:
```json
{
  "name": "search_theorists",
  "description": "Search for educational theorists and their contributions.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string"
      },
      "limit": {
        "type": "integer",
        "default": 10
      },
      "include_theories": {
        "type": "boolean",
        "default": true
      }
    },
    "required": ["query"]
  }
}
```

---

#### REQ-TOOL-006: query_by_cypher
**Type**: Optional-feature
**Priority**: P2 (Medium)

```
WHERE advanced query mode is enabled,
the system SHALL execute validated Cypher queries
AND return raw graph data.
```

**JSON Schema**:
```json
{
  "name": "query_by_cypher",
  "description": "Execute a Cypher query against the knowledge graph (advanced users only).",
  "inputSchema": {
    "type": "object",
    "properties": {
      "cypher": {
        "type": "string",
        "description": "Cypher query (read-only operations only)"
      },
      "params": {
        "type": "object",
        "description": "Query parameters"
      }
    },
    "required": ["cypher"]
  }
}
```

**Security**:
- 読み取り専用クエリのみ許可
- クエリ検証による安全性確保
- タイムアウト設定（5秒）

---

#### REQ-TOOL-007: find_path
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user wants to find connections between two theories,
the system SHALL find the shortest path(s) between them
AND return the relationship chain.
```

**JSON Schema**:
```json
{
  "name": "find_path",
  "description": "Find the shortest path between two theories in the knowledge graph.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "from_id": {
        "type": "string",
        "description": "Starting theory ID"
      },
      "to_id": {
        "type": "string",
        "description": "Target theory ID"
      },
      "max_depth": {
        "type": "integer",
        "default": 5,
        "maximum": 10
      },
      "relation_types": {
        "type": "array",
        "items": { "type": "string" }
      }
    },
    "required": ["from_id", "to_id"]
  }
}
```

---

#### REQ-TOOL-008: get_related_entities
**Type**: Ubiquitous
**Priority**: P1 (High)

```
The system SHALL retrieve all entities directly related to a given entity.
```

**JSON Schema**:
```json
{
  "name": "get_related_entities",
  "description": "Get all entities directly related to a specific theory, concept, or theorist.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "entity_id": {
        "type": "string"
      },
      "entity_type": {
        "type": "string",
        "enum": ["theory", "concept", "theorist", "evidence", "method"]
      }
    },
    "required": ["entity_id", "entity_type"]
  }
}
```

---

### 3.3 推論・分析ツール（esperanto LLM統合）

#### REQ-TOOL-009: infer_applicable_theories
**Type**: Event-driven
**Priority**: P0 (Critical)

```
WHEN a user describes an educational scenario,
the system SHALL use LLM reasoning combined with graph search
to infer and recommend applicable theories with justifications.
```

**JSON Schema**:
```json
{
  "name": "infer_applicable_theories",
  "description": "Use AI reasoning to infer which educational theories are most applicable to a given scenario.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "scenario": {
        "type": "string",
        "description": "Description of the educational scenario"
      },
      "learner_profile": {
        "type": "object",
        "properties": {
          "age_group": {
            "type": "string",
            "enum": ["children", "adolescents", "adults", "elderly"]
          },
          "prior_knowledge": {
            "type": "string",
            "enum": ["novice", "intermediate", "advanced"]
          },
          "learning_style": {
            "type": "string",
            "enum": ["visual", "auditory", "kinesthetic", "reading"]
          }
        }
      },
      "constraints": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Constraints like 'online only', 'limited time', etc."
      },
      "goal": {
        "type": "string",
        "description": "Primary learning objective"
      },
      "reasoning_depth": {
        "type": "string",
        "enum": ["quick", "standard", "deep"],
        "default": "standard",
        "description": "Level of reasoning detail"
      }
    },
    "required": ["scenario"]
  }
}
```

**Acceptance Criteria**:
- [ ] esperantoを通じたLLM推論を実行
- [ ] グラフデータと推論結果を統合
- [ ] 各推薦に理論的根拠を付与
- [ ] 信頼度スコアを算出
- [ ] 応答時間 < 3秒

---

#### REQ-TOOL-010: analyze_theory_gaps
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user provides a curriculum or lesson plan,
the system SHALL analyze theoretical coverage
AND identify gaps in educational theory application.
```

**JSON Schema**:
```json
{
  "name": "analyze_theory_gaps",
  "description": "Analyze a curriculum or lesson plan for gaps in educational theory coverage.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Curriculum or lesson plan content"
      },
      "expected_theories": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Theories that should be covered"
      },
      "context": {
        "type": "string",
        "description": "Educational context (e.g., 'K-12 math', 'corporate training')"
      }
    },
    "required": ["content"]
  }
}
```

---

#### REQ-TOOL-011: deduce_relationships
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user asks about implicit relationships between theories,
the system SHALL use LLM reasoning to deduce and explain connections.
```

**JSON Schema**:
```json
{
  "name": "deduce_relationships",
  "description": "Use AI to deduce implicit relationships between educational theories that may not be explicitly stored in the graph.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "theory_ids": {
        "type": "array",
        "items": { "type": "string" },
        "minItems": 2,
        "maxItems": 5
      },
      "relationship_question": {
        "type": "string",
        "description": "Specific question about relationships"
      }
    },
    "required": ["theory_ids"]
  }
}
```

---

#### REQ-TOOL-012: analyze_evidence_strength
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user queries about evidence supporting a theory,
the system SHALL analyze and evaluate the strength of evidence
using established research evaluation criteria.
```

**JSON Schema**:
```json
{
  "name": "analyze_evidence_strength",
  "description": "Analyze and evaluate the strength of evidence supporting an educational theory.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "theory_id": {
        "type": "string"
      },
      "criteria": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["sample_size", "methodology", "replication", "meta_analysis", "recency"]
        },
        "default": ["methodology", "replication", "meta_analysis"]
      }
    },
    "required": ["theory_id"]
  }
}
```

---

#### REQ-TOOL-013: synthesize_theories
**Type**: Event-driven
**Priority**: P2 (Medium)

```
WHEN a user wants to combine multiple theories,
the system SHALL synthesize them into an integrated framework
with potential conflicts identified.
```

**JSON Schema**:
```json
{
  "name": "synthesize_theories",
  "description": "Synthesize multiple educational theories into an integrated framework.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "theory_ids": {
        "type": "array",
        "items": { "type": "string" },
        "minItems": 2,
        "maxItems": 5
      },
      "synthesis_goal": {
        "type": "string",
        "description": "Purpose of the synthesis"
      },
      "identify_conflicts": {
        "type": "boolean",
        "default": true
      }
    },
    "required": ["theory_ids"]
  }
}
```

---

#### REQ-TOOL-014: predict_learning_outcomes
**Type**: Event-driven
**Priority**: P2 (Medium)

```
WHEN a user provides a learning design,
the system SHALL predict likely learning outcomes
based on applied theories and evidence.
```

**JSON Schema**:
```json
{
  "name": "predict_learning_outcomes",
  "description": "Predict learning outcomes based on the educational theories applied in a learning design.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "learning_design": {
        "type": "string",
        "description": "Description of the learning design"
      },
      "theories_applied": {
        "type": "array",
        "items": { "type": "string" }
      },
      "learner_profile": {
        "type": "object"
      }
    },
    "required": ["learning_design"]
  }
}
```

---

### 3.4 推薦ツール

#### REQ-TOOL-015: recommend_theories
**Type**: Event-driven
**Priority**: P0 (Critical)

```
WHEN a user provides a learning context,
the system SHALL recommend theories using hybrid RAG approach
combining semantic search, graph traversal, and LLM reasoning.
```

**JSON Schema**:
```json
{
  "name": "recommend_theories",
  "description": "Get AI-powered theory recommendations for a specific educational context.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "context": {
        "type": "string",
        "description": "Educational context description"
      },
      "preferences": {
        "type": "object",
        "properties": {
          "paradigm_preference": {
            "type": "array",
            "items": { "type": "string" }
          },
          "evidence_threshold": {
            "type": "string",
            "enum": ["high", "medium", "any"]
          },
          "novelty": {
            "type": "string",
            "enum": ["established", "emerging", "any"]
          }
        }
      },
      "limit": {
        "type": "integer",
        "default": 5
      },
      "include_rationale": {
        "type": "boolean",
        "default": true
      }
    },
    "required": ["context"]
  }
}
```

---

#### REQ-TOOL-016: recommend_methods
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user describes a learning objective,
the system SHALL recommend teaching methods
aligned with relevant educational theories.
```

---

#### REQ-TOOL-017: recommend_assessments
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user describes learning goals and applied theories,
the system SHALL recommend appropriate assessment methods.
```

---

#### REQ-TOOL-018: recommend_adaptations
**Type**: Event-driven
**Priority**: P2 (Medium)

```
WHEN a user describes learner diversity,
the system SHALL recommend theory-based adaptations
for diverse learner needs.
```

---

#### REQ-TOOL-019: recommend_complementary_theories
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user is using a specific theory,
the system SHALL recommend complementary theories
that can enhance the educational approach.
```

---

### 3.5 生成ツール

#### REQ-TOOL-020: generate_citation
**Type**: Ubiquitous
**Priority**: P0 (Critical)

```
The system SHALL generate properly formatted academic citations
for theories, theorists, and evidence in multiple formats.
```

**JSON Schema**:
```json
{
  "name": "generate_citation",
  "description": "Generate academic citations for educational theories and research.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "entity_id": {
        "type": "string"
      },
      "entity_type": {
        "type": "string",
        "enum": ["theory", "evidence", "theorist"]
      },
      "format": {
        "type": "string",
        "enum": ["APA7", "MLA9", "Chicago", "Harvard", "IEEE", "Vancouver"],
        "default": "APA7"
      },
      "include_url": {
        "type": "boolean",
        "default": false
      }
    },
    "required": ["entity_id", "entity_type"]
  }
}
```

---

#### REQ-TOOL-021: generate_explanation
**Type**: Event-driven
**Priority**: P0 (Critical)

```
WHEN a user requests an explanation of a theory,
the system SHALL generate a clear, audience-appropriate explanation
using LLM capabilities.
```

**JSON Schema**:
```json
{
  "name": "generate_explanation",
  "description": "Generate a clear explanation of an educational theory tailored to the target audience.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "theory_id": {
        "type": "string"
      },
      "audience": {
        "type": "string",
        "enum": ["students", "teachers", "researchers", "general"],
        "default": "general"
      },
      "depth": {
        "type": "string",
        "enum": ["brief", "standard", "detailed"],
        "default": "standard"
      },
      "include_examples": {
        "type": "boolean",
        "default": true
      },
      "language": {
        "type": "string",
        "default": "en"
      }
    },
    "required": ["theory_id"]
  }
}
```

---

#### REQ-TOOL-022: generate_summary
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user requests a summary of multiple theories,
the system SHALL generate a comparative summary.
```

---

#### REQ-TOOL-023: generate_lesson_framework
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user provides learning objectives and context,
the system SHALL generate a theory-based lesson framework.
```

---

#### REQ-TOOL-024: generate_bibliography
**Type**: Event-driven
**Priority**: P2 (Medium)

```
WHEN a user provides a list of theories used,
the system SHALL generate a complete bibliography.
```

---

#### REQ-TOOL-025: generate_theory_map
**Type**: Event-driven
**Priority**: P2 (Medium)

```
WHEN a user requests a visual representation,
the system SHALL generate a theory relationship map in Mermaid format.
```

---

### 3.6 比較・評価ツール

#### REQ-TOOL-026: compare_theories
**Type**: Event-driven
**Priority**: P0 (Critical)

```
WHEN a user wants to compare theories,
the system SHALL provide structured comparison
across multiple dimensions.
```

**JSON Schema**:
```json
{
  "name": "compare_theories",
  "description": "Compare multiple educational theories across various dimensions.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "theory_ids": {
        "type": "array",
        "items": { "type": "string" },
        "minItems": 2,
        "maxItems": 5
      },
      "dimensions": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": [
            "core_principles",
            "applications",
            "evidence_base",
            "limitations",
            "historical_context",
            "learner_focus",
            "teacher_role",
            "assessment_approach"
          ]
        },
        "default": ["core_principles", "applications", "evidence_base"]
      },
      "output_format": {
        "type": "string",
        "enum": ["table", "narrative", "both"],
        "default": "both"
      }
    },
    "required": ["theory_ids"]
  }
}
```

---

#### REQ-TOOL-027: evaluate_theory_fit
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user provides a specific educational context,
the system SHALL evaluate how well a theory fits that context.
```

---

#### REQ-TOOL-028: identify_contradictions
**Type**: Event-driven
**Priority**: P1 (High)

```
WHEN a user combines multiple theories,
the system SHALL identify potential contradictions or conflicts.
```

---

#### REQ-TOOL-029: get_evidence
**Type**: Ubiquitous
**Priority**: P0 (Critical)

```
The system SHALL retrieve evidence supporting a theory
with quality indicators and source information.
```

---

#### REQ-TOOL-030: get_principles
**Type**: Ubiquitous
**Priority**: P0 (Critical)

```
The system SHALL retrieve core principles of a theory
with practical application guidelines.
```

---

### 3.7 システムツール

#### REQ-TOOL-031: get_system_health
**Type**: Ubiquitous
**Priority**: P0 (Critical)

```
The system SHALL provide health status of all components
including database connections and LLM availability.
```

---

#### REQ-TOOL-032: get_statistics
**Type**: Ubiquitous
**Priority**: P1 (High)

```
The system SHALL provide statistics about the knowledge graph
including entity counts and relationship distributions.
```

---

#### REQ-TOOL-033: get_schema
**Type**: Ubiquitous
**Priority**: P1 (High)

```
The system SHALL provide the knowledge graph schema
including entity types and relationship types.
```

---

## 4. MCP Resources

### 4.1 リソース一覧

| Resource URI | 説明 | MIME Type |
|--------------|------|-----------|
| `theory://list` | 全理論のリスト | application/json |
| `theory://{id}` | 特定理論の詳細 | application/json |
| `theory://{id}/concepts` | 理論の概念 | application/json |
| `theory://{id}/principles` | 理論の原則 | application/json |
| `theory://{id}/evidence` | 理論のエビデンス | application/json |
| `concept://list` | 全概念のリスト | application/json |
| `concept://{id}` | 特定概念の詳細 | application/json |
| `theorist://list` | 全理論家のリスト | application/json |
| `theorist://{id}` | 特定理論家の詳細 | application/json |
| `paradigm://list` | パラダイムのリスト | application/json |
| `paradigm://{id}` | パラダイムの詳細 | application/json |
| `evidence://list` | エビデンスリスト | application/json |
| `method://list` | 教授法リスト | application/json |
| `graph://schema` | グラフスキーマ | application/json |
| `graph://stats` | グラフ統計 | application/json |

### 4.2 リソース要件

#### REQ-RES-001: theory://list
**Type**: Ubiquitous
**Priority**: P0 (Critical)

```
The system SHALL provide a paginated list of all educational theories
with basic metadata (id, name, paradigm, description snippet).
```

**Acceptance Criteria**:
- [ ] デフォルトページサイズ: 20
- [ ] ソート: 名前順（デフォルト）、人気順、新着順
- [ ] フィルタ: パラダイム、エビデンスレベル
- [ ] 応答時間 < 100ms

---

#### REQ-RES-002: theory://{id}
**Type**: Ubiquitous
**Priority**: P0 (Critical)

```
The system SHALL provide complete details of a specific theory
as a structured JSON document.
```

---

## 5. MCP Prompts

### 5.1 プロンプト一覧

| Prompt Name | 説明 | Required Arguments |
|-------------|------|-------------------|
| `design_lesson` | 理論に基づいた授業設計 | topic, duration, level |
| `create_assessment` | 評価方法の設計 | learning_objectives, theory_ids |
| `explain_theory` | 理論の分かりやすい説明 | theory_id, audience |
| `plan_curriculum` | カリキュラム計画 | subject, duration, outcomes |
| `analyze_case` | ケーススタディ分析 | case_description |
| `debate_theories` | 理論のディベート | theory_ids, topic |
| `integrate_theories` | 理論統合の提案 | theory_ids, context |
| `troubleshoot_learning` | 学習課題の診断 | problem_description |
| `adapt_for_diversity` | 多様性への適応 | theory_id, diversity_factors |
| `create_activity` | 学習活動の設計 | theory_id, objective |
| `evaluate_design` | 教材評価 | material_description |
| `suggest_research` | 研究提案 | theory_id, gap_area |
| `translate_theory` | 理論の実践への翻訳 | theory_id, practical_context |
| `compare_approaches` | アプローチ比較 | approach_descriptions |
| `generate_rubric` | ルーブリック生成 | criteria, theory_alignment |

### 5.2 プロンプト要件

#### REQ-PRM-001: design_lesson
**Type**: Event-driven
**Priority**: P0 (Critical)

```
WHEN a user invokes the design_lesson prompt,
the system SHALL generate a theory-grounded lesson plan
including objectives, activities, and assessment aligned with selected theories.
```

**Prompt Template**:
```
Design a lesson on "{topic}" for {level} learners, lasting {duration} minutes.

Use the following educational theories as the foundation:
{theories_context}

The lesson plan should include:
1. Learning objectives (aligned with {theory_names})
2. Introduction/hook (based on {motivation_theory})
3. Main activities (applying {instructional_theories})
4. Assessment method (grounded in {assessment_theory})
5. Differentiation strategies
6. Materials needed
7. Theoretical justification for each component
```

---

#### REQ-PRM-002: explain_theory
**Type**: Event-driven
**Priority**: P0 (Critical)

```
WHEN a user invokes the explain_theory prompt,
the system SHALL generate a clear explanation
tailored to the specified audience.
```

---

## 6. 非機能要件

### 6.1 パフォーマンス要件

| 要件ID | 要件 | 目標値 |
|--------|------|--------|
| REQ-NFR-001 | 単純検索応答時間 | < 200ms |
| REQ-NFR-002 | ハイブリッド検索応答時間 | < 500ms |
| REQ-NFR-003 | LLM推論応答時間 | < 5秒 |
| REQ-NFR-004 | グラフトラバース応答時間 | < 300ms (depth≤3) |
| REQ-NFR-005 | キャッシュヒット率 | > 80% |
| REQ-NFR-006 | 同時接続数 | 100クライアント |
| REQ-NFR-007 | スループット | 1000 req/min |

### 6.2 スケーラビリティ要件

| 要件ID | 要件 | 目標値 |
|--------|------|--------|
| REQ-NFR-008 | 理論数 | 100+ |
| REQ-NFR-009 | 関係数 | 500+ |
| REQ-NFR-010 | ベクトルインデックスサイズ | 10,000+ |

### 6.3 可用性要件

| 要件ID | 要件 | 目標値 |
|--------|------|--------|
| REQ-NFR-011 | サービス稼働率 | 99.5% |
| REQ-NFR-012 | LLM フォールバック | 3プロバイダー |
| REQ-NFR-013 | グレースフルデグラデーション | LLMなしでも基本機能動作 |

### 6.4 セキュリティ要件

| 要件ID | 要件 |
|--------|------|
| REQ-NFR-014 | APIキーの安全な管理（環境変数） |
| REQ-NFR-015 | Cypherクエリのサニタイズ |
| REQ-NFR-016 | 入力検証（全パラメータ） |
| REQ-NFR-017 | レート制限（1000 req/min/client） |

---

## 7. データ要件

### 7.1 データソース

教育理論データは [References/Educational-theory-research.md](../../References/Educational-theory-research.md) に基づく。

### 7.2 教育理論カテゴリ（9カテゴリ・200理論）

| カテゴリ | 理論数 | 優先度5の割合 | 説明 |
|---------|--------|--------------|------|
| 学習理論 | 38 | 42% | 行動主義〜構成主義〜コネクティビズム |
| 教授法・指導法理論 | 32 | 47% | ソクラテス式〜インストラクショナルデザイン |
| 発達理論 | 18 | 50% | ピアジェ、ヴィゴツキー、エリクソン等 |
| 動機づけ理論 | 16 | 44% | 自己決定理論、成長マインドセット |
| 評価理論 | 12 | 50% | 形成的評価、真正性評価 |
| 社会的学習理論 | 18 | 56% | 協調学習、実践共同体 |
| 東洋・アジア教育理論 | 28 | 39% | 儒教思想、授業研究、学びの共同体 |
| テクノロジー活用理論 | 22 | 45% | TPACK、SAMRモデル、AI教育 |
| 現代教育理論 | 16 | 56% | 21世紀型スキル、SEL、STEM/STEAM |
| 批判的・オルタナティブ・特別支援 | 26 | - | モンテッソーリ、シュタイナー、UDL |

### 7.3 エンティティ

| エンティティ | 説明 | 目標数 |
|-------------|------|--------|
| Theory | 教育理論 | **200** |
| Theorist | 理論家 | 100+ |
| Concept | 概念 | 150+ |
| Principle | 原則 | 200+ |
| Evidence | エビデンス | 100+ |
| Method | 教授法 | 60+ |
| Context | 教育文脈 | 30+ |
| Category | 理論カテゴリ | 10 |
| Paradigm | パラダイム | 12 |

### 7.4 理論属性

| 属性 | 型 | 説明 | 例 |
|------|-----|------|-----|
| name_ja | string | 日本語名 | 認知発達理論 |
| name_en | string | 英語名 | Cognitive Development Theory |
| theorist | string | 提唱者 | Jean Piaget |
| priority | int (1-5) | 現代教育での重要度 | 5 |
| category | string | カテゴリ | 発達理論 |
| description | string | 説明 | 4段階の認知発達を説明 |
| era | string | 時代 | 20世紀 |
| region | string | 地域 | 西洋 |

### 7.5 関係

| 関係タイプ | 説明 |
|-----------|------|
| BASED_ON | 理論が基盤とする理論 |
| EXTENDS | 理論を拡張 |
| CONTRADICTS | 理論と矛盾 |
| COMPLEMENTS | 理論を補完 |
| PROPOSED_BY | 理論家が提唱 |
| INFLUENCED_BY | 影響を受けた |
| HAS_CONCEPT | 概念を含む |
| HAS_PRINCIPLE | 原則を含む |
| SUPPORTS | エビデンスが支持 |
| APPLIES_TO | 文脈に適用 |
| USES_METHOD | 教授法を使用 |
| BELONGS_TO | パラダイムに属する |
| BELONGS_TO_CATEGORY | カテゴリに属する |

### 7.6 パラダイム分類

| パラダイム | 説明 | 代表理論 |
|-----------|------|---------|
| Behaviorism | 行動主義 | 古典的条件づけ、オペラント条件づけ |
| Cognitivism | 認知主義 | 認知負荷理論、情報処理理論 |
| Constructivism | 構成主義 | 社会構成主義、発見学習 |
| Humanism | 人間主義 | 自己決定理論、自己実現理論 |
| Connectivism | コネクティビズム | コネクティビズム学習理論 |
| Social Learning | 社会学習 | 社会的学習理論、観察学習 |
| Experiential | 経験学習 | 経験学習サイクル |
| Instructional Design | 教授設計 | ガニェの9教授事象、ARCSモデル |
| Developmental | 発達理論 | 認知発達理論、最近接発達領域 |
| Neuroscience | 脳科学ベース | 脳ベースの学習 |

---

## 8. esperanto統合要件

### 8.1 サポートプロバイダー

| プロバイダー | LLM | Embedding | 用途 |
|-------------|-----|-----------|------|
| OpenAI | ✅ | ✅ | 主要プロバイダー |
| Anthropic | ✅ | - | Claude連携 |
| Google | ✅ | ✅ | Gemini統合 |
| Ollama | ✅ | ✅ | ローカル実行 |
| Azure OpenAI | ✅ | ✅ | エンタープライズ |
| Groq | ✅ | - | 高速推論 |
| Mistral | ✅ | ✅ | EU準拠 |

### 8.2 フォールバック戦略

```
WHEN primary LLM provider is unavailable,
the system SHALL attempt fallback providers in priority order
AND log the failover event.
```

**Priority Order**:
1. OpenAI (GPT-4o)
2. Anthropic (Claude 3.5)
3. Google (Gemini Pro)
4. Ollama (local fallback)

### 8.3 Embedding統合

```
The system SHALL use task-aware embeddings
optimized for educational content retrieval.
```

**Task Types**:
- `RETRIEVAL_QUERY` - 検索クエリ
- `RETRIEVAL_DOCUMENT` - ドキュメントインデックス
- `CLASSIFICATION` - 分類タスク
- `CLUSTERING` - クラスタリング

---

## 9. トレーサビリティマトリクス

| 要件ID | 設計 | テスト | ステータス |
|--------|------|--------|----------|
| REQ-TOOL-001 | DESIGN-001 | TEST-001 | Draft |
| REQ-TOOL-002 | DESIGN-001 | TEST-002 | Draft |
| REQ-TOOL-003 | DESIGN-001 | TEST-003 | Draft |
| ... | ... | ... | ... |

---

## 10. 用語集

| 用語 | 定義 |
|------|------|
| MCP | Model Context Protocol - AI連携のオープンスタンダード |
| GraphRAG | グラフベースのRetrieval Augmented Generation |
| esperanto | マルチプロバイダーLLM統合ライブラリ |
| Tool | MCPにおけるLLMが呼び出し可能な関数 |
| Resource | MCPにおける読み取り専用データ |
| Prompt | MCPにおける再利用可能なテンプレート |
| Theory | 教育・学習に関する体系化された理論 |
| Paradigm | 理論を分類する上位概念（認知主義など） |
| Evidence | 理論を支持する研究・エビデンス |

---

## 11. 変更履歴

| バージョン | 日付 | 変更内容 | 著者 |
|-----------|------|---------|------|
| 1.0 | 2025-12-26 | 初版作成 | GitHub Copilot |

---

**Document Status**: Draft
**Next Review**: Design Phase
**Approval Required**: Product Owner, Tech Lead
