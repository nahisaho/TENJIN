# Product Context

**Project**: TENJIN
**Last Updated**: 2025-12-28
**Version**: 0.2.2-dev
**Status**: 開発中（v0.2.2 WebSocket同期・エクスポート機能）

---

## Product Vision

**Vision Statement**: 教育理論に基づいたエビデンスベースの教育コンテンツ生成を、AI時代に最適化された形で実現する

> TENJINは、教育理論のナレッジグラフとGraphRAG技術を組み合わせ、複数のLLMプロバイダーを活用して、生成AIが理論的根拠を持った回答を生成できるようにする次世代システムです。単なる検索を超え、教育理論に基づいた推論・推薦・分析を提供することで、教育コンテンツの質を革新的に向上させます。

**Mission**: 教育理論のナレッジグラフを構築し、esperantoを通じたマルチLLM統合により、あらゆるAIアプリケーションに理論的文脈と推論能力を提供する

> 行動主義、認知主義、構成主義などの主要な学習理論から、ガニェの9教授事象、ARCSモデルなどの教授設計理論まで、体系的にナレッジグラフ化し、LLM推論を組み合わせたハイブリッドRAGアプローチで、生成AIの回答品質を飛躍的に向上させます。

---

## Product Overview

### What is TENJIN?

教育理論に特化した高性能GraphRAG MCPサーバー

> TENJINは、教育理論・学習理論のナレッジグラフデータベースと、esperantoライブラリによるマルチLLM統合を組み合わせたMCPサーバーです。Model Context Protocol（MCP）を通じて、Claude Desktop、VS Code、その他のMCP対応AIアプリケーションから、教育理論に基づいたエビデンスベースのコンテンツ生成が可能になります。
>
> 参照実装であるTENGIN-GraphRAGを基盤としつつ、以下の点で大幅に機能強化しています：
>
> - **esperantoによるマルチLLM統合**: 15以上のLLMプロバイダーをシームレスに切り替え
> - **ハイブリッドRAG**: セマンティック検索 + グラフトラバース + LLM推論の統合
> - **高度な推論機能**: 理論推薦、ギャップ分析、関係推論
> - **拡張されたナレッジグラフ**: 100以上の教育理論と500以上の関係
> - **インテリジェントキャッシュ**: 階層型キャッシュによる高速応答

### Problem Statement

**Problem**: 生成AIによる教育コンテンツは理論的根拠が欠如し、推論能力も限定的である

> 現在の生成AIは膨大なテキストデータで学習されていますが、教育理論を体系的に理解しているわけではありません。また、既存のRAGシステムは単純な検索に留まり、理論間の関係や文脈に基づく推論ができません。そのため、教育コンテンツを生成する際に以下の問題が発生します：
>
> - 教育理論の誤った解釈や混同
> - エビデンスに基づかない経験則的なアドバイス
> - 理論的背景の説明なしに「効果的」と主張
> - 相反する理論を無批判に混在させた回答
> - 出典・引用の不在
> - 学習者特性に応じた理論選択ができない
> - 複数理論の統合・合成ができない

### Solution

**Solution**: esperantoマルチLLM統合 + GraphRAG + 高度な推論機能

> TENJINは以下のアプローチで問題を解決します：
>
> 1. **構造化された理論データベース**: 100以上の教育理論を体系的に分類・格納
> 2. **関係性の明示**: 理論間の「基盤」「発展」「対立」「補完」関係をグラフで表現
> 3. **エビデンス追跡**: 各理論・原則に対するエビデンスレベルを管理
> 4. **ハイブリッドRAG検索**: セマンティック検索 + グラフトラバース + キーワード検索
> 5. **LLM推論統合**: esperantoによる複数LLMを活用した高度な推論
> 6. **引用生成**: 使用した理論と出典を明示した回答を生成
> 7. **パーソナライズ推薦**: 学習者特性・文脈に基づく理論推薦
> 8. **グレースフルデグラデーション**: LLM障害時も基本機能を維持

---

## Target Users

### Primary Users

#### User Persona 1: AIプロダクト開発者

**Demographics**:

- **Role**: ソフトウェアエンジニア / MLエンジニア
- **Organization Size**: EdTech企業、AI企業、スタートアップ
- **Technical Level**: 高い（API統合、システム設計経験あり）

**Goals**:

- 教育系AIプロダクトの回答品質向上
- LLMのハルシネーション抑制
- エビデンスベースのコンテンツ生成
- 複数LLMプロバイダーへの対応

**Pain Points**:

- LLMが教育理論を誤解釈する
- 出典・引用の自動生成が難しい
- 教育ドメイン知識の整備が困難
- LLMプロバイダーの切り替えが面倒

**Use Cases**:

- AI家庭教師サービスへのMCP統合
- 教育コンテンツ生成パイプラインへの組み込み
- 学習アドバイスボットの品質向上
- カリキュラム設計支援ツールの開発

---

#### User Persona 2: インストラクショナルデザイナー

**Demographics**:

- **Role**: 教育設計者 / e-Learning開発者
- **Organization Size**: 大学、企業研修部門、教育出版社
- **Technical Level**: 中程度（Claude Desktop/VS Codeは使える）

**Goals**:

- 理論に基づいた教材設計
- 設計根拠の明示と説明
- 最新の教育研究の活用
- 効率的な教材開発

**Pain Points**:

- 理論の適用方法がわからない
- 複数の理論の整合性確認が困難
- エビデンスの探索に時間がかかる
- 理論と実践の橋渡しが難しい

**Use Cases**:

- Claude Desktopでの教材設計支援
- 設計根拠文書の自動生成
- 理論間の関係理解
- 学習者に適した理論選択

---

#### User Persona 3: 教育研究者

**Demographics**:

- **Role**: 大学教員 / 教育学研究者
- **Organization Size**: 大学、研究機関
- **Technical Level**: 中〜高（研究ツールに慣れている）

**Goals**:

- 理論間の関係分析
- 研究文献の体系的整理
- 新しい理論的フレームワークの探索
- エビデンスの評価と統合

**Pain Points**:

- 文献レビューに膨大な時間がかかる
- 理論間の関係を俯瞰することが困難
- エビデンスレベルの評価が主観的になりがち

**Use Cases**:

- 文献レビュー支援
- 理論マップの作成
- エビデンス評価
- 研究ギャップの特定

---

### Secondary Users

- **教育コンサルタント**: 組織の研修設計に理論的根拠を提供
- **教師・講師**: 授業設計の理論的裏付けを取得
- **学生**: 教育理論の学習・理解支援

---

## Market & Business Context

### Market Opportunity

**Market Size**: グローバルEdTech市場は2025年に$400B超、AI教育ツール市場は急成長中

**Target Market**: 
- 教育系AIプロダクト開発企業
- インストラクショナルデザイン企業
- 企業研修部門
- 高等教育機関

> MCPの標準化により、AIアプリケーションからの統合需要が急増している。特にClaude Desktop、VS Code Copilotユーザーが主要ターゲット。

### Business Model

**Revenue Model**: オープンソース + エンタープライズサポート

- **オープンソース版**: 基本機能無料、コミュニティサポート
- **エンタープライズ版**: SLA、専用サポート、カスタマイズ

### Competitive Landscape

| 競合 | 強み | 弱み | 差別化ポイント |
|------|------|------|---------------|
| 汎用RAG | 汎用性 | 教育ドメイン特化なし | 教育理論に特化したナレッジグラフ |
| LangChain | エコシステム | 設定の複雑さ | MCP標準、esperantoによるシンプルさ |
| 教育データベース | データの正確性 | AI統合なし | MCP + LLM推論統合 |

---

## Core Product Capabilities

### Must-Have Features (MVP)

1. **MCP Server（30+ Tools）**
   - **Description**: 検索、推論、生成、比較の30以上のツールを提供
   - **User Value**: あらゆるMCPクライアントから教育理論にアクセス
   - **Priority**: P0 (Critical)

2. **ハイブリッドRAG検索**
   - **Description**: セマンティック + グラフ + キーワードの統合検索
   - **User Value**: 高精度な理論検索と関連情報取得
   - **Priority**: P0 (Critical)

3. **esperanto LLM統合**
   - **Description**: 15以上のLLMプロバイダーをサポート
   - **User Value**: プロバイダーに依存しない柔軟な運用
   - **Priority**: P0 (Critical)

4. **教育理論ナレッジグラフ**
   - **Description**: 100以上の理論と500以上の関係
   - **User Value**: 体系化された教育理論知識へのアクセス
   - **Priority**: P0 (Critical)

### High-Priority Features (Post-MVP)

5. **LLM推論機能**
   - **Description**: 理論推薦、ギャップ分析、関係推論
   - **User Value**: 単純検索を超えた高度な分析
   - **Priority**: P1 (High)

6. **引用・文献管理**
   - **Description**: APA7等複数フォーマットでの引用生成
   - **User Value**: 学術的な文書作成の効率化
   - **Priority**: P1 (High)

7. **プロンプトテンプレート**
   - **Description**: 授業設計、評価設計等の15以上のテンプレート
   - **User Value**: 定型タスクの効率化
   - **Priority**: P1 (High)

### Future Features (Roadmap)

8. **マルチモーダル対応**
   - **Description**: 図表、音声への拡張
   - **User Value**: リッチな教育コンテンツ生成
   - **Priority**: P2 (Medium)

9. **パーソナライゼーション**
   - **Description**: ユーザー履歴に基づく推薦最適化
   - **User Value**: より適切な理論推薦
   - **Priority**: P2 (Medium)

10. **分析ダッシュボード**
    - **Description**: 利用統計、トレンド分析
    - **User Value**: システム運用の可視化
    - **Priority**: P3 (Low)

---

## Product Principles

### Design Principles

1. **MCP標準準拠**
   - Model Context Protocolの仕様に完全準拠し、あらゆるMCPクライアントとの互換性を保証

2. **グレースフルデグラデーション**
   - LLM障害時も基本検索機能を維持し、可用性を確保

3. **プロバイダー非依存**
   - esperantoによりLLMプロバイダーを自由に切り替え可能

### User Experience Principles

1. **即時応答**
   - 検索 < 500ms、推論 < 5秒の応答時間を維持

2. **理論的根拠の明示**
   - すべての回答に理論的背景と出典を明示

---

## Success Metrics

### Key Performance Indicators (KPIs)

| メトリクス | 目標値 | 測定方法 |
|-----------|--------|---------|
| 検索精度 | > 90% | ユーザー評価 |
| 応答時間（検索） | < 500ms | システムログ |
| 応答時間（推論） | < 5s | システムログ |
| MCPクライアント統合数 | 5+ | 導入事例 |
| テストカバレッジ | > 90% | CI/CD |
| ユーザー満足度 | > 4.0/5.0 | アンケート |
| ---------------------------- | --------------------- | -------------- |
| **Daily Active Users (DAU)** | {{DAU_TARGET}}        | [How measured] |
| **Feature Adoption Rate**    | > {{ADOPTION_RATE}}%  | [How measured] |
| **User Retention (Day 7)**   | > {{RETENTION_RATE}}% | [How measured] |
| **Net Promoter Score (NPS)** | > {{NPS_TARGET}}      | [How measured] |

#### Technical Metrics

| Metric                      | Target  | Measurement             |
| --------------------------- | ------- | ----------------------- |
| **API Response Time (p95)** | < 200ms | Monitoring dashboard    |
| **Uptime**                  | 99.9%   | Status page             |
| **Error Rate**              | < 0.1%  | Error tracking (Sentry) |
| **Page Load Time**          | < 2s    | Web vitals              |

---

## Product Roadmap

### Phase 1: MVP (Months 1-3)

**Goal**: Launch minimum viable product

**Features**:

- [Feature 1]
- [Feature 2]
- [Feature 3]

**Success Criteria**:

- [Criterion 1]
- [Criterion 2]

---

### Phase 2: Growth (Months 4-6)

**Goal**: Achieve product-market fit

**Features**:

- [Feature 4]
- [Feature 5]
- [Feature 6]

**Success Criteria**:

- [Criterion 1]
- [Criterion 2]

---

### Phase 3: Scale (Months 7-12)

**Goal**: Scale to {{USER_TARGET}} users

**Features**:

- [Feature 7]
- [Feature 8]
- [Feature 9]

**Success Criteria**:

- [Criterion 1]
- [Criterion 2]

---

## User Workflows

### Primary Workflow 1: {{WORKFLOW_1_NAME}}

**User Goal**: {{USER_GOAL}}

**Steps**:

1. User [action 1]
2. System [response 1]
3. User [action 2]
4. System [response 2]
5. User achieves [goal]

**Success Criteria**:

- User completes workflow in < {{TIME}} minutes
- Success rate > {{SUCCESS_RATE}}%

---

### Primary Workflow 2: {{WORKFLOW_2_NAME}}

**User Goal**: {{USER_GOAL}}

**Steps**:

1. [Step 1]
2. [Step 2]
3. [Step 3]

**Success Criteria**:

- [Criterion 1]
- [Criterion 2]

---

## Business Domain

### Domain Concepts

Key concepts and terminology used in this domain:

1. **{{CONCEPT_1}}**: [Definition and importance]
2. **{{CONCEPT_2}}**: [Definition and importance]
3. **{{CONCEPT_3}}**: [Definition and importance]

**Example for SaaS Authentication**:

- **Identity Provider (IdP)**: Service that authenticates users
- **Single Sign-On (SSO)**: One login for multiple applications
- **Multi-Factor Authentication (MFA)**: Additional verification step

### Business Rules

1. **{{RULE_1}}**
   - [Description of business rule]
   - **Example**: [Concrete example]

2. **{{RULE_2}}**
   - [Description]
   - **Example**: [Example]

**Example for E-commerce**:

- **Inventory Reservation**: Reserved items held for 10 minutes during checkout
- **Refund Window**: Refunds allowed within 30 days of purchase

---

## Constraints & Requirements

### Business Constraints

- **Budget**: ${{BUDGET}}
- **Timeline**: {{TIMELINE}}
- **Team Size**: {{TEAM_SIZE}} engineers
- **Launch Date**: {{LAUNCH_DATE}}

### Compliance Requirements

- **{{COMPLIANCE_1}}**: [Description, e.g., GDPR, SOC 2, HIPAA]
- **{{COMPLIANCE_2}}**: [Description]
- **Data Residency**: [Requirements, e.g., EU data stays in EU]

### Non-Functional Requirements

- **Performance**: API response < 200ms (95th percentile)
- **Availability**: 99.9% uptime SLA
- **Scalability**: Support {{CONCURRENT_USERS}} concurrent users
- **Security**: OWASP Top 10 compliance
- **Accessibility**: WCAG 2.1 AA compliance

---

## Stakeholders

### Internal Stakeholders

| Role                    | Name                 | Responsibilities                  |
| ----------------------- | -------------------- | --------------------------------- |
| **Product Owner**       | {{PO_NAME}}          | Vision, roadmap, priorities       |
| **Tech Lead**           | {{TECH_LEAD_NAME}}   | Architecture, technical decisions |
| **Engineering Manager** | {{EM_NAME}}          | Team management, delivery         |
| **QA Lead**             | {{QA_LEAD_NAME}}     | Quality assurance, testing        |
| **Design Lead**         | {{DESIGN_LEAD_NAME}} | UX/UI design                      |

### External Stakeholders

| Role                        | Name        | Responsibilities            |
| --------------------------- | ----------- | --------------------------- |
| **Customer Advisory Board** | [Members]   | Product feedback            |
| **Investors**               | [Names]     | Funding, strategic guidance |
| **Partners**                | [Companies] | Integration, co-marketing   |

---

## Go-to-Market Strategy

### Launch Strategy

**Target Launch Date**: {{LAUNCH_DATE}}

**Launch Phases**:

1. **Private Beta** ({{START_DATE}} - {{END_DATE}})
   - Invite-only, 50 beta users
   - Focus: Gather feedback, fix critical bugs

2. **Public Beta** ({{START_DATE}} - {{END_DATE}})
   - Open signup
   - Focus: Validate product-market fit

3. **General Availability** ({{LAUNCH_DATE}})
   - Full public launch
   - Focus: Acquisition and growth

### Marketing Channels

- **{{CHANNEL_1}}**: [Strategy, e.g., Content marketing, SEO]
- **{{CHANNEL_2}}**: [Strategy, e.g., Social media, Twitter/LinkedIn]
- **{{CHANNEL_3}}**: [Strategy, e.g., Paid ads, Google/Facebook]
- **{{CHANNEL_4}}**: [Strategy, e.g., Partnerships, integrations]

---

## Risk Assessment

### Product Risks

| Risk       | Probability     | Impact          | Mitigation            |
| ---------- | --------------- | --------------- | --------------------- |
| {{RISK_1}} | High/Medium/Low | High/Medium/Low | [Mitigation strategy] |
| {{RISK_2}} | High/Medium/Low | High/Medium/Low | [Mitigation strategy] |

**Example Risks**:

- **Low adoption**: Users don't understand value → Clear onboarding, demos
- **Performance issues**: System slow at scale → Load testing, optimization
- **Security breach**: Data compromised → Security audit, penetration testing

---

## Customer Support

### Support Channels

- **Email**: support@{{COMPANY}}.com
- **Chat**: In-app live chat (business hours)
- **Documentation**: docs.{{COMPANY}}.com
- **Community**: Forum/Discord/Slack

### Support SLA

| Tier              | Response Time | Resolution Time |
| ----------------- | ------------- | --------------- |
| **Critical (P0)** | < 1 hour      | < 4 hours       |
| **High (P1)**     | < 4 hours     | < 24 hours      |
| **Medium (P2)**   | < 24 hours    | < 3 days        |
| **Low (P3)**      | < 48 hours    | Best effort     |

---

## Product Analytics

### Analytics Tools

- **{{ANALYTICS_TOOL_1}}**: [Purpose, e.g., Google Analytics, Mixpanel]
- **{{ANALYTICS_TOOL_2}}**: [Purpose, e.g., Amplitude, Heap]

### Events to Track

| Event               | Description            | Purpose           |
| ------------------- | ---------------------- | ----------------- |
| `user_signup`       | New user registration  | Track acquisition |
| `feature_used`      | User uses core feature | Track engagement  |
| `payment_completed` | User completes payment | Track conversion  |
| `error_occurred`    | User encounters error  | Track reliability |

---

## Localization & Internationalization

### Supported Languages

- **Primary**: English (en-US)
- **Secondary**: [Languages, e.g., Japanese (ja-JP), Spanish (es-ES)]

### Localization Strategy

- **UI Strings**: i18n framework (next-intl, react-i18next)
- **Date/Time**: Locale-aware formatting
- **Currency**: Multi-currency support
- **Right-to-Left (RTL)**: Support for Arabic, Hebrew (if needed)

---

## Data & Privacy

### Data Collection

**What data we collect**:

- User account information (email, name)
- Usage analytics (anonymized)
- Error logs (for debugging)

**What data we DON'T collect**:

- [Sensitive data we avoid, e.g., passwords (only hashed), payment details (tokenized)]

### Privacy Policy

- **GDPR Compliance**: Right to access, delete, export data
- **Data Retention**: [Retention period, e.g., 90 days for logs]
- **Third-Party Sharing**: [Who we share data with, why]

---

## Integrations

### Existing Integrations

| Integration       | Purpose   | Priority |
| ----------------- | --------- | -------- |
| {{INTEGRATION_1}} | [Purpose] | P0       |
| {{INTEGRATION_2}} | [Purpose] | P1       |

### Planned Integrations

| Integration       | Purpose   | Timeline |
| ----------------- | --------- | -------- |
| {{INTEGRATION_3}} | [Purpose] | Q2 2025  |
| {{INTEGRATION_4}} | [Purpose] | Q3 2025  |

---

## Changelog

### Version 1.1 (Planned)

- [Future product updates]

---

**Last Updated**: 2025-12-26
**Maintained By**: {{MAINTAINER}}
