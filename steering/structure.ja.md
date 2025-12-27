# Project Structure

**Project**: TENJIN
**Last Updated**: 2025-12-28
**Version**: 0.2.0

---

## Architecture Pattern

**Primary Pattern**: Clean Architecture + MCP Server

> このプロジェクトはClean Architecture（Onion Architecture）パターンを採用しています。
> ドメイン層を中心に、Application層、Infrastructure層、Interface層（MCP Tools/Resources/Prompts）を分離し、
> 依存性逆転の原則に基づいて構築されています。
>
> インターフェースとしてModel Context Protocol（MCP）サーバーを採用し、
> LLMアプリケーション（Claude Desktop、VS Code等）との統合を実現しています。
>
> esperantoライブラリによりマルチLLMプロバイダーをサポートし、
> プロバイダーに依存しない柔軟なアーキテクチャを実現しています。

---

## Architecture Layers (Language-Agnostic)

The following layer definitions apply regardless of programming language:

### Layer 1: Domain / Core

**Purpose**: Business logic and domain models
**Rules**:

- MUST NOT depend on any other layer
- Contains: Entities, Value Objects, Domain Services, Domain Events
- No framework dependencies, no I/O

**Language Examples**:
| Language | Location | Pattern |
|----------|----------|---------|
| TypeScript | `lib/{feature}/domain/` | Classes/Types |
| Rust | `{crate}/src/domain/` | Structs + Traits |
| Python | `src/{pkg}/domain/` | Dataclasses |
| Go | `internal/domain/` | Structs + Interfaces |
| Java | `src/main/.../domain/` | Classes + Records |

### Layer 2: Application / Use Cases

**Purpose**: Orchestrate domain logic, implement use cases
**Rules**:

- Depends only on Domain layer
- Contains: Application Services, Commands, Queries, DTOs
- No direct I/O (uses ports/interfaces)

**Language Examples**:
| Language | Location | Pattern |
|----------|----------|---------|
| TypeScript | `lib/{feature}/application/` | Service classes |
| Rust | `{crate}/src/application/` | Impl blocks |
| Python | `src/{pkg}/application/` | Service functions |
| Go | `internal/app/` | Service structs |
| Java | `src/main/.../application/` | @Service classes |

### Layer 3: Infrastructure / Adapters

**Purpose**: External integrations (DB, APIs, messaging)
**Rules**:

- Depends on Application layer (implements ports)
- Contains: Repositories, API Clients, Message Publishers
- All I/O operations here

**Language Examples**:
| Language | Location | Pattern |
|----------|----------|---------|
| TypeScript | `lib/{feature}/infrastructure/` | Repository impls |
| Rust | `{crate}/src/infrastructure/` | Trait impls |
| Python | `src/{pkg}/infrastructure/` | Repository classes |
| Go | `internal/infra/` | Interface impls |
| Java | `src/main/.../infrastructure/` | @Repository classes |

### Layer 4: Interface / Presentation

**Purpose**: Entry points (CLI, API, Web UI)
**Rules**:

- Depends on Application layer
- Contains: Controllers, CLI handlers, API routes
- Input validation and response formatting

**Language Examples**:
| Language | Location | Pattern |
|----------|----------|---------|
| TypeScript | `app/api/` or `cli/` | Route handlers |
| Rust | `{crate}/src/api/` or `cli/` | Axum handlers |
| Python | `src/{pkg}/api/` or `cli/` | FastAPI routes |
| Go | `cmd/` or `internal/api/` | HTTP handlers |
| Java | `src/main/.../api/` | @RestController |

### Layer Dependency Rules

```
┌─────────────────────────────────────────┐
│        Interface / Presentation         │ ← Entry points
├─────────────────────────────────────────┤
│        Application / Use Cases          │ ← Orchestration
├─────────────────────────────────────────┤
│        Infrastructure / Adapters        │ ← I/O & External
├─────────────────────────────────────────┤
│            Domain / Core                │ ← Pure business logic
└─────────────────────────────────────────┘

Dependency Direction: ↓ (outer → inner)
Domain layer has NO dependencies
```

---

## Directory Organization

### Root Structure

```
TENJIN/
├── .vscode/                  # VS Code設定
│   ├── mcp.json              # MCPサーバー設定
│   └── settings.json         # VS Code設定
├── src/                      # メインソースコード
│   └── tenjin/               # Pythonパッケージ
│       ├── __init__.py
│       ├── server.py         # MCPサーバーエントリーポイント
│       ├── domain/           # ドメイン層
│       ├── application/      # アプリケーション層
│       ├── infrastructure/   # インフラストラクチャ層
│       ├── tools/            # MCP Tools
│       ├── resources/        # MCP Resources
│       ├── prompts/          # MCP Prompts
│       └── scripts/          # CLIスクリプト
├── data/                     # 教育理論データ（JSON）
│   └── theories/             # 理論データファイル
├── tests/                    # テストスイート
│   ├── unit/                 # ユニットテスト
│   ├── integration/          # 統合テスト
│   └── e2e/                  # E2Eテスト
├── tools/                    # 開発支援ツール
│   └── theory-editor/        # 教育理論データエディター (Web GUI)
│       ├── index.html        # メインHTML
│       ├── styles.css        # スタイル
│       ├── app.js            # メインアプリケーション
│       ├── sync-server.py    # Neo4j同期サーバー (port 8081)
│       ├── js/               # モジュール化されたJS
│       │   ├── validation.js # バリデーション
│       │   ├── diff.js       # 差分計算
│       │   ├── storage.js    # ローカルストレージ
│       │   └── error-handler.js # エラーハンドリング
│       ├── docs/             # ドキュメント
│       │   ├── API.md        # APIリファレンス
│       │   └── ARCHITECTURE.md # アーキテクチャ
│       └── tests/            # E2Eテスト (Playwright)
├── scripts/                  # ユーティリティスクリプト
│   ├── load_data.py          # データローダー
│   └── generate_*.py         # データ生成スクリプト
├── docs/                     # ドキュメント
├── storage/                  # SDD アーティファクト
│   ├── specs/                # 要件、設計、タスク仕様
│   ├── changes/              # 変更差分仕様
│   └── archive/              # アーカイブ
├── steering/                 # プロジェクトメモリ
│   ├── structure.ja.md       # このファイル
│   ├── tech.ja.md            # 技術スタック
│   ├── product.ja.md         # プロダクトコンテキスト
│   └── rules/                # 憲法ガバナンス
├── templates/                # ドキュメントテンプレート
├── .gitignore                # Git除外設定
├── pyproject.toml            # Python プロジェクト設定
├── docker-compose.yml        # Docker 設定
└── README.md                 # プロジェクトREADME

# Note: References/ フォルダはローカル開発用（Git追跡外）
```

---

## Clean Architecture + MCP パターン

### Layer 1: Domain（ドメイン層）

```
src/tenjin/domain/
├── entities/                 # エンティティ
│   ├── theory.py             # Theory エンティティ
│   ├── theorist.py           # Theorist エンティティ
│   ├── concept.py            # Concept エンティティ
│   ├── principle.py          # Principle エンティティ
│   ├── evidence.py           # Evidence エンティティ
│   ├── method.py             # Method エンティティ
│   ├── context.py            # Context エンティティ
│   └── paradigm.py           # Paradigm エンティティ
├── value_objects/            # 値オブジェクト
│   ├── theory_id.py          # TheoryId
│   ├── evidence_level.py     # EvidenceLevel (high/medium/low)
│   ├── relation_type.py      # RelationType (BASED_ON等)
│   ├── citation_format.py    # CitationFormat (APA7等)
│   └── learner_type.py       # LearnerType
├── services/                 # ドメインサービス
│   ├── theory_matcher.py     # 理論マッチングロジック
│   ├── relation_resolver.py  # 関係解決ロジック
│   └── evidence_evaluator.py # エビデンス評価ロジック
├── repositories/             # リポジトリインターフェース
│   ├── theory_repository.py  # TheoryRepository ABC
│   ├── concept_repository.py # ConceptRepository ABC
│   └── graph_repository.py   # GraphRepository ABC
└── errors.py                 # ドメインエラー
```

**ルール**:
- 他の層に依存しない
- フレームワーク依存なし
- 純粋なビジネスロジックのみ

### Layer 2: Application（アプリケーション層）

```
src/tenjin/application/
├── services/                 # アプリケーションサービス
│   ├── search_service.py     # 検索サービス
│   ├── graph_service.py      # グラフクエリサービス
│   ├── inference_service.py  # LLM推論サービス (NEW)
│   ├── reasoning_service.py  # 推論サービス
│   ├── recommend_service.py  # 推薦サービス
│   ├── citation_service.py   # 引用生成サービス
│   ├── generation_service.py # コンテンツ生成サービス
│   ├── comparison_service.py # 比較サービス
│   └── cache_service.py      # キャッシュ管理
├── dto/                      # Data Transfer Objects
│   ├── search_dto.py         # 検索リクエスト/レスポンス
│   ├── theory_dto.py         # 理論DTO
│   └── recommendation_dto.py # 推薦DTO
├── ports/                    # ポート（インターフェース）
│   ├── llm_port.py           # LLMポート
│   ├── embedding_port.py     # Embeddingポート
│   └── cache_port.py         # キャッシュポート
└── use_cases/                # ユースケース
    ├── search_theories.py    # 理論検索
    ├── infer_applicable.py   # 適用可能理論推論
    └── generate_citation.py  # 引用生成
```

**ルール**:
- ドメイン層にのみ依存
- ポートを通じた外部アクセス
- ユースケースのオーケストレーション

### Layer 3: Infrastructure（インフラストラクチャ層）

```
src/tenjin/infrastructure/
├── adapters/                 # 外部システムアダプタ
│   ├── neo4j_adapter.py      # Neo4j アダプタ
│   ├── chromadb_adapter.py   # ChromaDB アダプタ
│   ├── esperanto_adapter.py  # esperanto LLM アダプタ
│   └── cache_adapter.py      # キャッシュアダプタ
├── repositories/             # リポジトリ実装
│   ├── neo4j_theory_repo.py  # Neo4j Theory リポジトリ
│   ├── neo4j_graph_repo.py   # Neo4j Graph リポジトリ
│   └── chroma_vector_repo.py # ChromaDB Vector リポジトリ
└── config/                   # 設定
    ├── settings.py           # 環境設定
    └── container.py          # DIコンテナ
```

**ルール**:
- アプリケーション層のポートを実装
- 外部システムとの通信
- 設定管理

### Layer 4: Interface（インターフェース層 - MCP）

```
src/tenjin/tools/             # MCP Tools
├── __init__.py
├── search/                   # 検索ツール
│   ├── search_theories.py
│   ├── search_concepts.py
│   └── get_theory.py
├── graph/                    # グラフツール
│   ├── traverse_graph.py
│   ├── find_path.py
│   └── get_related.py
├── reasoning/                # 推論ツール
│   ├── infer_applicable.py
│   ├── deduce_relations.py
│   └── analyze_gaps.py
├── generation/               # 生成ツール
│   ├── generate_citation.py
│   ├── generate_explanation.py
│   └── generate_summary.py
└── system/                   # システムツール
    ├── get_health.py
    └── get_statistics.py

src/tenjin/resources/         # MCP Resources
├── __init__.py
├── theory_resources.py       # theory:// リソース
├── concept_resources.py      # concept:// リソース
├── graph_resources.py        # graph:// リソース
└── theorist_resources.py     # theorist:// リソース

src/tenjin/prompts/           # MCP Prompts
├── __init__.py
├── design_lesson.py          # 授業設計プロンプト
├── create_assessment.py      # 評価設計プロンプト
├── explain_theory.py         # 理論説明プロンプト
└── plan_curriculum.py        # カリキュラム計画プロンプト
```

**ルール**:
- MCPプロトコルの実装
- 入力バリデーション
- レスポンスフォーマット

---

## Library-First Pattern (Article I)

すべての機能は最初にライブラリとして実装されます。
│   │   └── migration.sql
│   └── 002_create_sessions_table/
│       └── migration.sql
└── seed.ts               # Database seed data
```

### Database Guidelines

- **Migrations**: All schema changes via migrations
- **Naming**: snake_case for tables and columns
- **Indexes**: Index foreign keys and frequently queried columns

---

## Test Organization

### Test Structure

```
tests/
├── unit/                 # Unit tests (per library)
│   └── auth/
│       └── service.test.ts
├── integration/          # Integration tests (real services)
│   └── auth/
│       └── login.test.ts
├── e2e/                  # End-to-end tests
│   └── auth/
│       └── user-flow.test.ts
└── fixtures/             # Test data and fixtures
    └── users.ts
```

### Test Guidelines

- **Test-First**: Tests written BEFORE implementation (Article III)
- **Real Services**: Integration tests use real DB/cache (Article IX)
- **Coverage**: Minimum 80% coverage
- **Naming**: `*.test.ts` for unit, `*.integration.test.ts` for integration

---

## Documentation Organization

### Documentation Structure

```
docs/
├── architecture/         # Architecture documentation
│   ├── c4-diagrams/
│   └── adr/              # Architecture Decision Records
├── api/                  # API documentation
│   ├── openapi.yaml
│   └── graphql.schema
├── guides/               # Developer guides
│   ├── getting-started.md
│   └── contributing.md
└── runbooks/             # Operational runbooks
    ├── deployment.md
    └── troubleshooting.md
```

---

## SDD Artifacts Organization

### Storage Directory

```
storage/
├── specs/                # Specifications
│   ├── auth-requirements.md
│   ├── auth-design.md
│   ├── auth-tasks.md
│   └── payment-requirements.md
├── changes/              # Delta specifications (brownfield)
│   ├── add-2fa.md
│   └── upgrade-jwt.md
├── features/             # Feature tracking
│   ├── auth.json
│   └── payment.json
└── validation/           # Validation reports
    ├── auth-validation-report.md
    └── payment-validation-report.md
```

---

## Naming Conventions

### File Naming

- **TypeScript**: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **React Components**: `PascalCase.tsx` (e.g., `LoginForm.tsx`)
- **Utilities**: `camelCase.ts` (e.g., `formatDate.ts`)
- **Tests**: `*.test.ts` or `*.spec.ts`
- **Constants**: `SCREAMING_SNAKE_CASE.ts` (e.g., `API_ENDPOINTS.ts`)

### Directory Naming

- **Features**: `kebab-case` (e.g., `user-management/`)
- **Components**: `kebab-case` or `PascalCase` (consistent within project)

### Variable Naming

- **Variables**: `camelCase`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Types/Interfaces**: `PascalCase`
- **Enums**: `PascalCase`

---

## Integration Patterns

### Library → Application Integration

```typescript
// ✅ CORRECT: Application imports from library
import { AuthService } from '@/lib/auth';

const authService = new AuthService(repository);
const result = await authService.login(credentials);
```

```typescript
// ❌ WRONG: Library imports from application
// Libraries must NOT depend on application code
import { AuthContext } from '@/app/contexts/auth'; // Violation!
```

### Service → Repository Pattern

```typescript
// Service layer (business logic)
export class AuthService {
  constructor(private repository: UserRepository) {}

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    // Business logic here
    const user = await this.repository.findByEmail(credentials.email);
    // ...
  }
}

// Repository layer (data access)
export class UserRepository {
  constructor(private prisma: PrismaClient) {}

  async findByEmail(email: string): Promise<User | null> {
    return this.prisma.user.findUnique({ where: { email } });
  }
}
```

---

## Deployment Structure

### Deployment Units

**Projects** (independently deployable):

1. TENJIN - Main application

> ⚠️ **Simplicity Gate (Article VII)**: Maximum 3 projects initially.
> If adding more projects, document justification in Phase -1 Gate approval.

### Environment Structure

```
environments/
├── development/
│   └── .env.development
├── staging/
│   └── .env.staging
└── production/
    └── .env.production
```

---

## Multi-Language Support

### Language Policy

- **Primary Language**: English
- **Documentation**: English first (`.md`), then Japanese (`.ja.md`)
- **Code Comments**: English
- **UI Strings**: i18n framework

### i18n Organization

```
locales/
├── en/
│   ├── common.json
│   └── auth.json
└── ja/
    ├── common.json
    └── auth.json
```

---

## Version Control

### Branch Organization

- `main` - Production branch
- `develop` - Development branch
- `feature/*` - Feature branches
- `hotfix/*` - Hotfix branches
- `release/*` - Release branches

### Commit Message Convention

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Example**:

```
feat(auth): implement user login (REQ-AUTH-001)

Add login functionality with email and password authentication.
Session created with 24-hour expiry.

Closes REQ-AUTH-001
```

---

## Constitutional Compliance

This structure enforces:

- **Article I**: Library-first pattern in `lib/`
- **Article II**: CLI interfaces per library
- **Article III**: Test structure supports Test-First
- **Article VI**: Steering files maintain project memory

---

## Changelog

### Version 1.1 (Planned)

- [Future changes]

---

**Last Updated**: 2025-12-26
**Maintained By**: {{MAINTAINER}}
