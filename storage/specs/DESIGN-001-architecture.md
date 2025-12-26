# アーキテクチャ設計書: TENJIN 教育理論GraphRAG MCPサーバー

**ID**: DESIGN-001
**Feature**: TENJIN Education Theory GraphRAG MCP Server
**Version**: 1.0
**Created**: 2025-12-26
**Updated**: 2025-12-26
**Status**: Draft
**Related Requirements**: REQ-001-tenjin-education-graphrag v1.0
**Author**: GitHub Copilot

---

## 1. C4モデル

### 1.1 Level 1: System Context Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            External Systems & Users                               │
└──────────────────────────────────────────────────────────────────────────────────┘

         ┌──────────────────┐            ┌──────────────────┐
         │   AI Developers  │            │   Instructional  │
         │                  │            │    Designers     │
         └────────┬─────────┘            └────────┬─────────┘
                  │                               │
         ┌────────┴─────────┐            ┌────────┴─────────┐
         │  Claude Desktop  │            │     VS Code      │
         │                  │            │   GitHub Copilot │
         └────────┬─────────┘            └────────┬─────────┘
                  │                               │
         ┌────────┴─────────┐            ┌────────┴─────────┐
         │   Claude Code    │            │    Custom MCP    │
         │      CLI         │            │   Applications   │
         └────────┬─────────┘            └────────┬─────────┘
                  │                               │
                  └───────────────┬───────────────┘
                                  │
                    MCP Protocol (JSON-RPC 2.0)
                      STDIO / Streamable HTTP
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                                                                   │
│                    TENJIN Education Theory MCP Server                             │
│                                                                                   │
│   ┌─────────────────────────────────────────────────────────────────────────┐    │
│   │                                                                          │    │
│   │  • 200教育理論のナレッジグラフ（9カテゴリ）                              │    │
│   │  • esperantoによるマルチLLM統合（15+プロバイダー）                       │    │
│   │  • 33個のMCP Tools / 15 Resources / 15 Prompts                          │    │
│   │  • ハイブリッドRAG（Graph + Vector）                                     │    │
│   │  • LLMベース推論・分析・推薦機能                                         │    │
│   │                                                                          │    │
│   └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                   │
└──────────────────────────────────────────────────────────────────────────────────┘
         │                  │                   │                  │
         ▼                  ▼                   ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   esperanto  │   │   Graph DB   │   │  Vector DB   │   │  Education   │
│   LLM APIs   │   │    Neo4j     │   │   ChromaDB   │   │   Theory     │
│  (15+ providers) │   └──────────────┘   └──────────────┘   │    Data      │
└──────────────┘                                             └──────────────┘
```

### 1.2 Level 2: Container Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                          TENJIN Education Theory MCP Server                               │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                              MCP Interface Layer                                     │ │
│  │                               (FastMCP SDK 1.5+)                                     │ │
│  │                                                                                      │ │
│  │   ┌──────────────────────┐  ┌───────────────────┐  ┌────────────────────────────┐   │ │
│  │   │    Tools (33個)      │  │  Resources (15)   │  │      Prompts (15)          │   │ │
│  │   │                      │  │                   │  │                            │   │ │
│  │   │ • Search/Query (8)   │  │ • theory://       │  │ • design_lesson            │   │ │
│  │   │ • Reasoning (6)      │  │ • concept://      │  │ • create_assessment        │   │ │
│  │   │ • Recommend (5)      │  │ • theorist://     │  │ • explain_theory           │   │ │
│  │   │ • Generate (6)       │  │ • evidence://     │  │ • curriculum_plan          │   │ │
│  │   │ • Compare (5)        │  │ • method://       │  │ • theory_debate            │   │ │
│  │   │ • System (3)         │  │ • graph://        │  │ • case_study               │   │ │
│  │   │                      │  │ • context://      │  │                            │   │ │
│  │   │ @mcp.tool()          │  │ @mcp.resource()   │  │ @mcp.prompt()              │   │ │
│  │   └──────────┬───────────┘  └─────────┬─────────┘  └──────────────┬─────────────┘   │ │
│  │              │                        │                           │                 │ │
│  │              └────────────────────────┼───────────────────────────┘                 │ │
│  │                                       │                                             │ │
│  │                              Transport Layer                                        │ │
│  │              ┌────────────────────────┴────────────────────────┐                    │ │
│  │              │                                                 │                    │ │
│  │       ┌──────┴──────┐                             ┌────────────┴────────────┐       │ │
│  │       │    STDIO    │                             │    Streamable HTTP      │       │ │
│  │       │  Transport  │                             │       Transport         │       │ │
│  │       │ (local/dev) │                             │   (remote/multi-client) │       │ │
│  │       └─────────────┘                             └─────────────────────────┘       │ │
│  └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                           │                                              │
│                                           ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                           Application Layer (Services)                              │ │
│  │                                                                                      │ │
│  │ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐ │ │
│  │ │  Search Service │ │Reasoning Service│ │Recommend Service│ │  Generation Service │ │ │
│  │ │                 │ │                 │ │                 │ │                     │ │ │
│  │ │ • Semantic      │ │ • Analyze       │ │ • Context-based │ │ • Lesson Plan       │ │ │
│  │ │ • Hybrid RAG    │ │ • Synthesize    │ │ • Learner-based │ │ • Assessment        │ │ │
│  │ │ • Full-text     │ │ • Infer         │ │ • Curriculum    │ │ • Learning Path     │ │ │
│  │ └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────────┘ │ │
│  │                                                                                      │ │
│  │ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐ │ │
│  │ │  Graph Service  │ │Citation Service │ │ Compare Service │ │   Cache Service     │ │ │
│  │ │                 │ │                 │ │                 │ │                     │ │ │
│  │ │ • Traversal     │ │ • APA/MLA/etc   │ │ • Side-by-side  │ │ • L1: In-memory     │ │ │
│  │ │ • Subgraph      │ │ • Bibliography  │ │ • Evolution     │ │ • L2: Redis         │ │ │
│  │ │ • Path finding  │ │ • Source track  │ │ • Strengths     │ │ • L3: Persistent    │ │ │
│  │ └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                           │                                              │
│                                           ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                              Domain Layer (Core)                                     │ │
│  │                                                                                      │ │
│  │   ┌─────────────────────────────────────────────────────────────────────────────┐   │ │
│  │   │                              Entities                                        │   │ │
│  │   │                                                                              │   │ │
│  │   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │   │ │
│  │   │  │  Theory  │  │ Theorist │  │ Concept  │  │Principle │  │  Evidence    │   │   │ │
│  │   │  │          │  │          │  │          │  │          │  │              │   │   │ │
│  │   │  │ - id     │  │ - id     │  │ - id     │  │ - id     │  │ - id         │   │   │ │
│  │   │  │ - name_ja│  │ - name   │  │ - name   │  │ - content│  │ - study_type │   │   │ │
│  │   │  │ - name_en│  │ - era    │  │ - theory │  │ - theory │  │ - source     │   │   │ │
│  │   │  │ - priority│ │ - region │  │          │  │          │  │ - evidence_level│  │   │ │
│  │   │  │ - category│ │          │  │          │  │          │  │              │   │   │ │
│  │   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │   │ │
│  │   │                                                                              │   │ │
│  │   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │   │ │
│  │   │  │  Method  │  │ Context  │  │ Category │  │ Paradigm │                     │   │ │
│  │   │  │          │  │          │  │          │  │          │                     │   │ │
│  │   │  │ - id     │  │ - id     │  │ - name   │  │ - name   │                     │   │ │
│  │   │  │ - name   │  │ - type   │  │ - count  │  │ - desc   │                     │   │ │
│  │   │  │ - steps  │  │ - domain │  │ - priority_5_ratio│  │ - theories │         │   │ │
│  │   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘                     │   │ │
│  │   └─────────────────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                                      │ │
│  │   ┌─────────────────────────────────────────────────────────────────────────────┐   │ │
│  │   │                          Repository Interfaces                               │   │ │
│  │   │                                                                              │   │ │
│  │   │  TheoryRepository  │  ConceptRepository  │  GraphRepository                 │   │ │
│  │   │  EvidenceRepository │  MethodRepository  │  VectorRepository                │   │ │
│  │   └─────────────────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                                      │ │
│  │   ┌─────────────────────────────────────────────────────────────────────────────┐   │ │
│  │   │                             Value Objects                                    │   │ │
│  │   │                                                                              │   │ │
│  │   │  TheoryCategory  │  EvidenceLevel  │  CitationFormat  │  Priority           │   │ │
│  │   │  LearnerProfile  │  EducationContext │  RecommendationScore                 │   │ │
│  │   └─────────────────────────────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                           │                                              │
│                                           ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                         Infrastructure Layer (Adapters)                             │ │
│  │                                                                                      │ │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌─────────────────────────────────┐  │ │
│  │  │   Neo4j Adapter   │  │  ChromaDB Adapter │  │      esperanto Adapter          │  │ │
│  │  │                   │  │                   │  │                                 │  │ │
│  │  │ • Cypher queries  │  │ • Vector search   │  │ • Multi-provider LLM            │  │ │
│  │  │ • Graph traversal │  │ • Embedding store │  │ • Chat completion               │  │ │
│  │  │ • Node CRUD       │  │ • Similarity      │  │ • Embedding generation          │  │ │
│  │  │ • Relationship    │  │ • Metadata filter │  │ • Streaming support             │  │ │
│  │  └───────────────────┘  └───────────────────┘  └─────────────────────────────────┘  │ │
│  │                                                                                      │ │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌─────────────────────────────────┐  │ │
│  │  │   Cache Adapter   │  │  Config Manager   │  │       Logger/Metrics            │  │ │
│  │  │                   │  │                   │  │                                 │  │ │
│  │  │ • In-memory       │  │ • Environment     │  │ • structlog                     │  │ │
│  │  │ • Redis           │  │ • Settings        │  │ • OpenTelemetry                 │  │ │
│  │  │ • TTL management  │  │ • Validation      │  │ • Prometheus metrics            │  │ │
│  │  └───────────────────┘  └───────────────────┘  └─────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                           │
└──────────────────────────────────────────────────────────────────────────────────────────┘
         │                    │                    │                     │
         ▼                    ▼                    ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐      ┌──────────────┐
│    Neo4j     │      │   ChromaDB   │     │   LLM APIs   │      │    Redis     │
│  Graph DB    │      │  Vector DB   │     │ (esperanto)  │      │   (Cache)    │
│              │      │              │     │              │      │              │
│ 200 theories │      │ Embeddings   │     │ OpenAI       │      │  Optional    │
│ 9 categories │      │ Similarity   │     │ Anthropic    │      │              │
│              │      │              │     │ Google       │      │              │
└──────────────┘      └──────────────┘     │ Ollama...    │      └──────────────┘
                                           └──────────────┘
```

### 1.3 Level 3: MCP Primitives Component

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                                MCP Primitives Layer                                         │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                           Tools (33個) - Model-controlled                           │    │
│  ├────────────────────────────────────────────────────────────────────────────────────┤    │
│  │                                                                                     │    │
│  │  Search/Query (8)                                                                   │    │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐ │    │
│  │  │ search_theories  │ │ search_concepts  │ │ search_theorists │ │ search_evidence│ │    │
│  │  │ セマンティック検索│ │ 概念検索         │ │ 理論家検索       │ │ エビデンス検索 │ │    │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ └────────────────┘ │    │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐ │    │
│  │  │ search_methods   │ │ hybrid_search    │ │ full_text_search │ │ filter_by_     │ │    │
│  │  │ 教授法検索       │ │ ハイブリッドRAG  │ │ 全文検索         │ │ category       │ │    │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ └────────────────┘ │    │
│  │                                                                                     │    │
│  │  Reasoning/Analysis (6)                                                             │    │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐ │    │
│  │  │ analyze_theory   │ │ synthesize_      │ │ infer_           │ │ evaluate_      │ │    │
│  │  │ 理論分析(LLM)    │ │ theories         │ │ applications     │ │ evidence       │ │    │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ └────────────────┘ │    │
│  │  ┌──────────────────┐ ┌──────────────────┐                                         │    │
│  │  │ explain_         │ │ critique_theory  │                                         │    │
│  │  │ relationship     │ │ 批判的分析       │                                         │    │
│  │  └──────────────────┘ └──────────────────┘                                         │    │
│  │                                                                                     │    │
│  │  Recommendation (5)                                                                 │    │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐ │    │
│  │  │ recommend_for_   │ │ recommend_for_   │ │ recommend_for_   │ │ recommend_     │ │    │
│  │  │ context          │ │ learner          │ │ curriculum       │ │ integration    │ │    │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ └────────────────┘ │    │
│  │  ┌──────────────────┐                                                              │    │
│  │  │ recommend_       │                                                              │    │
│  │  │ complementary    │                                                              │    │
│  │  └──────────────────┘                                                              │    │
│  │                                                                                     │    │
│  │  Generation (6)                                                                     │    │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐ │    │
│  │  │ generate_lesson  │ │ generate_        │ │ generate_        │ │ generate_      │ │    │
│  │  │ _plan            │ │ assessment       │ │ learning_path    │ │ activity       │ │    │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ └────────────────┘ │    │
│  │  ┌──────────────────┐ ┌──────────────────┐                                         │    │
│  │  │ generate_rubric  │ │ generate_        │                                         │    │
│  │  │ ルーブリック生成 │ │ explanation      │                                         │    │
│  │  └──────────────────┘ └──────────────────┘                                         │    │
│  │                                                                                     │    │
│  │  Comparison (5)                                                                     │    │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐ │    │
│  │  │ compare_theories │ │ compare_         │ │ compare_methods  │ │ trace_         │ │    │
│  │  │ 理論比較         │ │ paradigms        │ │ 教授法比較       │ │ evolution      │ │    │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘ └────────────────┘ │    │
│  │  ┌──────────────────┐                                                              │    │
│  │  │ analyze_         │                                                              │    │
│  │  │ strengths        │                                                              │    │
│  │  └──────────────────┘                                                              │    │
│  │                                                                                     │    │
│  │  System (3)                                                                         │    │
│  │  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐                    │    │
│  │  │ get_graph_stats  │ │ health_check     │ │ get_schema       │                    │    │
│  │  │ グラフ統計       │ │ ヘルスチェック   │ │ スキーマ取得     │                    │    │
│  │  └──────────────────┘ └──────────────────┘ └──────────────────┘                    │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         Resources (15) - Application-controlled                     │    │
│  ├────────────────────────────────────────────────────────────────────────────────────┤    │
│  │                                                                                     │    │
│  │  theory://list              │  theory://{id}            │  theory://{category}/list │    │
│  │  concept://list             │  concept://{id}           │  concept://{theory_id}    │    │
│  │  theorist://list            │  theorist://{id}          │  theorist://{era}         │    │
│  │  evidence://{theory_id}     │  method://list            │  method://{id}            │    │
│  │  context://list             │  graph://schema           │  graph://stats            │    │
│  │                                                                                     │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                           Prompts (15) - User-controlled                            │    │
│  ├────────────────────────────────────────────────────────────────────────────────────┤    │
│  │                                                                                     │    │
│  │  design_lesson       │  create_assessment     │  explain_theory      │              │    │
│  │  授業設計            │  評価作成              │  理論解説            │              │    │
│  │                      │                        │                      │              │    │
│  │  curriculum_plan     │  theory_debate         │  case_study          │              │    │
│  │  カリキュラム計画    │  理論討論              │  事例研究            │              │    │
│  │                      │                        │                      │              │    │
│  │  learner_analysis    │  theory_application    │  research_summary    │              │    │
│  │  学習者分析          │  理論適用              │  研究要約            │              │    │
│  │                      │                        │                      │              │    │
│  │  compare_approaches  │  troubleshoot_learning │  design_activity     │              │    │
│  │  アプローチ比較      │  学習トラブルシュート  │  活動設計            │              │    │
│  │                      │                        │                      │              │    │
│  │  feedback_guide      │  theory_integration    │  assessment_rubric   │              │    │
│  │  フィードバックガイド│  理論統合              │  評価ルーブリック    │              │    │
│  │                                                                                     │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                             │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.4 Level 4: esperanto Integration Component

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                             esperanto LLM Integration Layer                                 │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                           esperanto Adapter                                         │    │
│  │                                                                                     │    │
│  │  from esperanto import LanguageModelRouter, EmbeddingModelRouter                   │    │
│  │                                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐   │    │
│  │  │                      LanguageModelRouter                                     │   │    │
│  │  │                                                                              │   │    │
│  │  │  • chat() - Chat completion (sync/async)                                     │   │    │
│  │  │  • stream_chat() - Streaming completion                                      │   │    │
│  │  │  • Provider failover support                                                 │   │    │
│  │  │                                                                              │   │    │
│  │  │  Supported Providers:                                                        │   │    │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │    │
│  │  │  │ OpenAI   │ │Anthropic │ │ Google   │ │  Groq    │ │ Mistral  │           │   │    │
│  │  │  │ GPT-4o   │ │Claude 3.5│ │ Gemini   │ │ Llama    │ │ Large    │           │   │    │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘           │   │    │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │   │    │
│  │  │  │  Ollama  │ │  Azure   │ │Together  │ │ Vertex   │ │Bedrock   │           │   │    │
│  │  │  │  Local   │ │ OpenAI   │ │   AI     │ │   AI     │ │  AWS     │           │   │    │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘           │   │    │
│  │  └─────────────────────────────────────────────────────────────────────────────┘   │    │
│  │                                                                                     │    │
│  │  ┌─────────────────────────────────────────────────────────────────────────────┐   │    │
│  │  │                     EmbeddingModelRouter                                     │   │    │
│  │  │                                                                              │   │    │
│  │  │  • embed() - Single/batch embedding                                          │   │    │
│  │  │  • embed_documents() - Document embedding                                    │   │    │
│  │  │                                                                              │   │    │
│  │  │  Models: text-embedding-3-small/large, Voyage, Cohere, etc.                  │   │    │
│  │  └─────────────────────────────────────────────────────────────────────────────┘   │    │
│  │                                                                                     │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                          LLM Service Configuration                                  │    │
│  │                                                                                     │    │
│  │  class LLMConfig(BaseSettings):                                                    │    │
│  │      # Primary provider                                                            │    │
│  │      llm_provider: str = "openai"                                                  │    │
│  │      llm_model: str = "gpt-4o-mini"                                                │    │
│  │                                                                                     │    │
│  │      # Fallback providers                                                          │    │
│  │      fallback_providers: list[str] = ["anthropic", "ollama"]                       │    │
│  │                                                                                     │    │
│  │      # Embedding                                                                   │    │
│  │      embedding_provider: str = "openai"                                            │    │
│  │      embedding_model: str = "text-embedding-3-small"                               │    │
│  │                                                                                     │    │
│  │      # Settings                                                                    │    │
│  │      temperature: float = 0.7                                                      │    │
│  │      max_tokens: int = 4096                                                        │    │
│  │      timeout: int = 30                                                             │    │
│  │                                                                                     │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                             │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. ディレクトリ構造

```
TENJIN/
├── src/                               # MCP Server Source
│   └── tenjin/                        # Main package
│       ├── __init__.py
│       ├── server.py                  # MCP Server entry point
│       │
│       ├── interface/                 # MCP Interface Layer
│       │   ├── __init__.py
│       │   ├── tools/                 # MCP Tools (33個)
│       │   │   ├── __init__.py
│       │   │   ├── search_tools.py    # search_*, hybrid_search (8)
│       │   │   ├── reasoning_tools.py # analyze_*, synthesize_* (6)
│       │   │   ├── recommend_tools.py # recommend_* (5)
│       │   │   ├── generate_tools.py  # generate_* (6)
│       │   │   ├── compare_tools.py   # compare_*, trace_* (5)
│       │   │   └── system_tools.py    # health, stats, schema (3)
│       │   │
│       │   ├── resources/             # MCP Resources (15)
│       │   │   ├── __init__.py
│       │   │   ├── theory_resources.py
│       │   │   ├── concept_resources.py
│       │   │   ├── theorist_resources.py
│       │   │   ├── evidence_resources.py
│       │   │   ├── method_resources.py
│       │   │   └── graph_resources.py
│       │   │
│       │   └── prompts/               # MCP Prompts (15)
│       │       ├── __init__.py
│       │       ├── lesson_prompts.py
│       │       ├── assessment_prompts.py
│       │       ├── analysis_prompts.py
│       │       └── integration_prompts.py
│       │
│       ├── application/               # Application Layer (Services)
│       │   ├── __init__.py
│       │   └── services/
│       │       ├── __init__.py
│       │       ├── search_service.py
│       │       ├── reasoning_service.py
│       │       ├── recommend_service.py
│       │       ├── generation_service.py
│       │       ├── graph_service.py
│       │       ├── citation_service.py
│       │       ├── compare_service.py
│       │       └── cache_service.py
│       │
│       ├── domain/                    # Domain Layer (Core)
│       │   ├── __init__.py
│       │   ├── entities/
│       │   │   ├── __init__.py
│       │   │   ├── theory.py
│       │   │   ├── theorist.py
│       │   │   ├── concept.py
│       │   │   ├── principle.py
│       │   │   ├── evidence.py
│       │   │   ├── method.py
│       │   │   ├── context.py
│       │   │   ├── category.py
│       │   │   └── paradigm.py
│       │   │
│       │   ├── repositories/
│       │   │   ├── __init__.py
│       │   │   ├── theory_repository.py
│       │   │   ├── concept_repository.py
│       │   │   ├── graph_repository.py
│       │   │   └── vector_repository.py
│       │   │
│       │   └── value_objects/
│       │       ├── __init__.py
│       │       ├── theory_category.py
│       │       ├── evidence_level.py
│       │       ├── citation_format.py
│       │       ├── priority.py
│       │       ├── learner_profile.py
│       │       └── education_context.py
│       │
│       └── infrastructure/            # Infrastructure Layer (Adapters)
│           ├── __init__.py
│           ├── adapters/
│           │   ├── __init__.py
│           │   ├── neo4j_adapter.py
│           │   ├── chromadb_adapter.py
│           │   ├── esperanto_adapter.py
│           │   ├── cache_adapter.py
│           │   └── embedding_adapter.py
│           │
│           ├── repositories/
│           │   ├── __init__.py
│           │   ├── neo4j_theory_repository.py
│           │   ├── neo4j_graph_repository.py
│           │   └── chromadb_vector_repository.py
│           │
│           └── config/
│               ├── __init__.py
│               ├── settings.py
│               └── logging.py
│
├── data/                              # Education Theory Data (200理論)
│   ├── theories/                      # JSONデータ
│   │   ├── learning_theories.json          # 学習理論 (38)
│   │   ├── instructional_theories.json     # 教授法理論 (32)
│   │   ├── developmental_theories.json     # 発達理論 (18)
│   │   ├── motivation_theories.json        # 動機づけ理論 (16)
│   │   ├── assessment_theories.json        # 評価理論 (12)
│   │   ├── social_learning_theories.json   # 社会的学習理論 (18)
│   │   ├── asian_theories.json             # 東洋・アジア理論 (28)
│   │   ├── technology_theories.json        # テクノロジー理論 (22)
│   │   ├── modern_theories.json            # 現代教育理論 (16)
│   │   └── alternative_theories.json       # 批判的/オルタナティブ (26)
│   │
│   ├── relationships/                 # 関係データ
│   │   └── theory_relationships.json
│   │
│   ├── theorists/                     # 理論家データ
│   │   └── theorists.json
│   │
│   └── schema/                        # スキーマ定義
│       └── graph_schema.json
│
├── tests/                             # Tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_neo4j.py
│   │   ├── test_chromadb.py
│   │   └── test_esperanto.py
│   └── e2e/
│       ├── __init__.py
│       └── test_mcp_server.py
│
├── docs/                              # Documentation
│   ├── API_REFERENCE.md
│   ├── USAGE_GUIDE.md
│   ├── MCP_INTEGRATION.md
│   └── EDUCATION_THEORIES.md
│
├── storage/                           # SDD Artifacts
│   ├── specs/
│   ├── archive/
│   └── changes/
│
├── steering/                          # Project Memory
│   ├── product.ja.md
│   ├── tech.ja.md
│   ├── structure.ja.md
│   ├── project.yml
│   └── rules/
│       └── constitution.md
│
├── References/                        # Reference Materials
│   ├── Educational-theory-research.md  # 200理論データソース
│   └── TENGIN-GraphRAG/               # 参照実装
│
├── templates/                         # Templates
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 3. データフロー

### 3.1 MCP Tool Call Flow (LLM推論あり)

```
MCP Host                 TENJIN Server                     Services                    Infrastructure
   │                          │                               │                              │
   │ tools/call               │                               │                              │
   │ "analyze_theory"         │                               │                              │
   │──────────────────────────▶                               │                              │
   │                          │                               │                              │
   │                          │ @mcp.tool()                   │                              │
   │                          │──────────────────────────────▶│                              │
   │                          │                               │                              │
   │                          │                               │ get_theory()                 │
   │                          │                               │─────────────────────────────▶│
   │                          │                               │                              │
   │                          │                               │◀─────────────────────────────│
   │                          │                               │        Theory data           │
   │                          │                               │                              │
   │                          │                               │ esperanto.chat()             │
   │                          │                               │─────────────────────────────▶│
   │                          │                               │                              │
   │                          │                               │◀─────────────────────────────│
   │                          │                               │        LLM Analysis          │
   │                          │                               │                              │
   │                          │◀──────────────────────────────│                              │
   │                          │     Analyzed Result           │                              │
   │                          │                               │                              │
   │◀──────────────────────────                               │                              │
   │  Tool Result (content[])  │                               │                              │
   │                          │                               │                              │
```

### 3.2 Hybrid RAG Search Flow

```
Query ──▶ ┌─────────────────────────────────────────────────────────────┐
          │                     Hybrid Search                           │
          │                                                             │
          │    ┌───────────────┐          ┌───────────────┐            │
          │    │ Vector Search │          │  Graph Search │            │
          │    │  (ChromaDB)   │          │    (Neo4j)    │            │
          │    │               │          │               │            │
          │    │ Semantic      │          │ Cypher Query  │            │
          │    │ Similarity    │          │ Traversal     │            │
          │    └───────┬───────┘          └───────┬───────┘            │
          │            │                          │                     │
          │            └──────────┬───────────────┘                     │
          │                       │                                     │
          │                       ▼                                     │
          │            ┌───────────────────┐                           │
          │            │   Result Fusion    │                           │
          │            │ (Reciprocal Rank)  │                           │
          │            └─────────┬─────────┘                           │
          │                      │                                      │
          │                      ▼                                      │
          │            ┌───────────────────┐                           │
          │            │   LLM Reranking   │                           │
          │            │   (esperanto)     │                           │
          │            └─────────┬─────────┘                           │
          │                      │                                      │
          └──────────────────────┼──────────────────────────────────────┘
                                 │
                                 ▼
                          Ranked Results
```

### 3.3 Resource Read Flow

```
MCP Host ──▶ resources/read {uri: "theory://T001"} ──▶ Resource Handler
                                                             │
                                                             ▼
                                              ┌───────────────────────────┐
                                              │ Parse URI                 │
                                              │ theory://{id}             │
                                              └─────────────┬─────────────┘
                                                            │
                                                            ▼
                                              ┌───────────────────────────┐
                                              │ TheoryRepository          │
                                              │ get_by_id(id)             │
                                              └─────────────┬─────────────┘
                                                            │
                                                            ▼
                                              ┌───────────────────────────┐
                                              │ Format as Resource        │
                                              │ Content                   │
                                              └─────────────┬─────────────┘
                                                            │
                                                            ▼
MCP Host ◀─────────────────── Resource Content (JSON) ◀─────┘
```

---

## 4. 技術スタック

| 領域 | 技術 | バージョン | 理由 |
|------|------|-----------|------|
| 言語 | Python | 3.11+ | FastMCP/esperanto対応、型ヒント |
| MCP SDK | FastMCP (`mcp[cli]`) | 1.5+ | Anthropic公式、デコレータAPI |
| LLM統合 | esperanto | 2.12+ | 15+プロバイダー、統一API |
| Graph DB | Neo4j | 5.x | 成熟、Cypher、可視化 |
| Vector DB | ChromaDB | 0.5+ | ローカル開発容易、軽量 |
| Validation | Pydantic | 2.0+ | 型安全、設定管理 |
| Async | asyncio | - | 非同期MCP処理 |
| Cache | Redis/In-memory | - | 階層型キャッシュ |
| Testing | pytest | 8.0+ | pytest-asyncio対応 |
| Linting | ruff | 0.4+ | 高速、包括的 |
| Package | uv | latest | 高速、MCP推奨 |

---

## 5. ADR（Architecture Decision Records）

### ADR-001: esperanto採用

| 項目 | 内容 |
|------|------|
| **決定** | LLM統合にesperantoを採用 |
| **理由** | 15+プロバイダー対応、統一API、フォールバック機能 |
| **代替案** | 直接SDK利用、LangChain、LiteLLM |
| **結果** | マルチプロバイダー対応が容易、ベンダーロックイン回避 |

### ADR-002: Clean Architecture採用

| 項目 | 内容 |
|------|------|
| **決定** | 4層Clean Architectureを採用 |
| **理由** | テスト容易性、依存性逆転、変更容易性 |
| **代替案** | 単純な3層アーキテクチャ |
| **結果** | MCP/DB/LLMの入れ替えが容易 |

### ADR-003: ハイブリッドRAG採用

| 項目 | 内容 |
|------|------|
| **決定** | Graph検索 + Vector検索のハイブリッドRAG |
| **理由** | 構造的クエリと意味的クエリの両立 |
| **代替案** | Vector-onlyまたはGraph-only |
| **結果** | 精度向上、多様なクエリ対応 |

---

## 6. トレーサビリティマトリクス

| 要件ID | 設計コンポーネント | ファイル |
|--------|-------------------|---------|
| TOOL-001~008 (Search) | Search Tools | `interface/tools/search_tools.py` |
| TOOL-009~014 (Reasoning) | Reasoning Tools | `interface/tools/reasoning_tools.py` |
| TOOL-015~019 (Recommend) | Recommend Tools | `interface/tools/recommend_tools.py` |
| TOOL-020~025 (Generate) | Generate Tools | `interface/tools/generate_tools.py` |
| TOOL-026~030 (Compare) | Compare Tools | `interface/tools/compare_tools.py` |
| TOOL-031~033 (System) | System Tools | `interface/tools/system_tools.py` |
| RESOURCE-* | Resources | `interface/resources/*.py` |
| PROMPT-* | Prompts | `interface/prompts/*.py` |
| NFR-001 (MCP準拠) | Server | `server.py` |
| NFR-002 (esperanto) | Adapter | `infrastructure/adapters/esperanto_adapter.py` |
| DATA-001 (200理論) | Domain/Data | `domain/entities/`, `data/theories/` |

---

## 変更履歴

| バージョン | 日付 | 変更者 | 変更内容 |
|-----------|------|--------|---------|
| 1.0 | 2025-12-26 | GitHub Copilot | 初版作成（TENGIN-GraphRAG参照） |
