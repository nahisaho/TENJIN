# Contributing to TENJIN

TENJIN教育理論GraphRAG MCPサーバーへの貢献を歓迎します！

## 目次

- [行動規範](#行動規範)
- [貢献の方法](#貢献の方法)
- [開発環境のセットアップ](#開発環境のセットアップ)
- [コーディング規約](#コーディング規約)
- [テスト](#テスト)
- [プルリクエスト](#プルリクエスト)
- [教育理論データの追加](#教育理論データの追加)

---

## 行動規範

このプロジェクトでは、すべての参加者に対して敬意を持った建設的なコミュニケーションを求めます。教育に関するプロジェクトとして、学習と成長を促進する環境を維持します。

---

## 貢献の方法

### 1. バグ報告

バグを発見した場合は、GitHub Issueを作成してください：

- **タイトル**: 簡潔で明確な説明
- **環境**: OS、Pythonバージョン、依存関係のバージョン
- **再現手順**: バグを再現するための具体的な手順
- **期待される動作**: 本来どう動作すべきか
- **実際の動作**: 実際に何が起こったか
- **ログ・スクリーンショット**: 関連する情報

### 2. 機能提案

新機能のアイデアがある場合：

- **ユースケース**: どのような問題を解決するか
- **提案する解決策**: 具体的な実装案
- **代替案**: 検討した他のアプローチ
- **影響範囲**: 既存機能への影響

### 3. ドキュメント改善

- 誤字・脱字の修正
- 説明の明確化
- 使用例の追加
- 翻訳の追加・改善

### 4. コード貢献

- バグ修正
- 新機能の実装
- パフォーマンス改善
- テストの追加

---

## 開発環境のセットアップ

### 前提条件

- Python 3.11以上
- Docker & Docker Compose
- Git

### セットアップ手順

```bash
# リポジトリをクローン
git clone https://github.com/your-org/tenjin.git
cd tenjin

# 仮想環境を作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 開発用依存関係をインストール
pip install -e ".[dev]"

# pre-commitフックをインストール
pre-commit install

# Neo4jを起動
docker-compose up -d neo4j

# テストデータをロード
python scripts/load_data.py

# テストを実行
pytest
```

### IDE設定

#### VS Code

推奨拡張機能:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- Ruff (charliermarsh.ruff)

`.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.analysis.typeCheckingMode": "basic",
    "editor.formatOnSave": true,
    "python.formatting.provider": "black",
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter"
    }
}
```

---

## コーディング規約

### Python スタイル

- **フォーマッター**: Black (line-length: 88)
- **リンター**: Ruff
- **型チェック**: mypy (strict mode)
- **ドキュメント**: Google style docstrings

```python
def calculate_similarity(
    theory_a: Theory,
    theory_b: Theory,
    *,
    method: str = "cosine",
) -> float:
    """2つの理論間の類似度を計算する。

    Args:
        theory_a: 比較元の理論
        theory_b: 比較先の理論
        method: 類似度計算方法（"cosine", "euclidean", "jaccard"）

    Returns:
        0.0から1.0の範囲の類似度スコア

    Raises:
        ValueError: 無効なメソッドが指定された場合

    Example:
        >>> similarity = calculate_similarity(theory1, theory2)
        >>> print(f"Similarity: {similarity:.2f}")
    """
    if method not in ("cosine", "euclidean", "jaccard"):
        raise ValueError(f"Invalid method: {method}")
    
    # 実装...
    return score
```

### 命名規約

- **クラス**: PascalCase（`TheoryService`, `Neo4jAdapter`）
- **関数・メソッド**: snake_case（`get_theory`, `calculate_similarity`）
- **定数**: UPPER_SNAKE_CASE（`DEFAULT_TIMEOUT`, `MAX_RESULTS`）
- **プライベート**: 先頭アンダースコア（`_internal_method`）

### アーキテクチャガイドライン

Clean Architectureの原則に従います：

1. **Domain層**: ビジネスロジック、エンティティ、値オブジェクト
2. **Application層**: ユースケース、サービス
3. **Infrastructure層**: 外部サービス、データベース
4. **Interface層**: MCP、API

依存関係の方向:
```
Interface → Application → Domain
Infrastructure → Domain
```

### コミットメッセージ

Conventional Commitsを使用：

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

タイプ:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `style`: コードスタイル（フォーマット等）
- `refactor`: リファクタリング
- `perf`: パフォーマンス改善
- `test`: テスト追加・修正
- `chore`: ビルド、CI等

例:
```
feat(search): add hybrid search with graph and vector

Implement hybrid search combining Neo4j graph traversal
with ChromaDB vector similarity for improved results.

Closes #123
```

---

## テスト

### テスト構造

```
tests/
├── unit/              # ユニットテスト
│   ├── test_entities.py
│   ├── test_value_objects.py
│   └── test_services.py
├── integration/       # 統合テスト
│   ├── test_neo4j_adapter.py
│   └── test_mcp_tools.py
└── e2e/              # E2Eテスト
    └── test_mcp_server_e2e.py
```

### テストの実行

```bash
# すべてのテスト
pytest

# 特定のテストファイル
pytest tests/unit/test_entities.py

# カバレッジ付き
pytest --cov=src/tenjin --cov-report=html

# 並列実行
pytest -n auto

# 特定のマーカー
pytest -m "not slow"
```

### テスト作成ガイドライン

```python
import pytest
from tenjin.domain.entities import Theory

class TestTheory:
    """Theoryエンティティのテスト"""

    def test_create_theory_with_valid_data(
        self,
        sample_theory_data: dict,
    ) -> None:
        """有効なデータで理論を作成できることを確認"""
        # Arrange
        data = sample_theory_data

        # Act
        theory = Theory(**data)

        # Assert
        assert theory.id == data["id"]
        assert theory.name == data["name"]

    def test_create_theory_without_required_field_raises_error(self) -> None:
        """必須フィールドがない場合にエラーが発生することを確認"""
        with pytest.raises(ValueError):
            Theory(name="Test")  # id missing

    @pytest.mark.parametrize(
        "category,expected",
        [
            ("learning_theory", True),
            ("invalid", False),
        ],
    )
    def test_category_validation(
        self,
        category: str,
        expected: bool,
    ) -> None:
        """カテゴリーの検証が正しく機能することを確認"""
        # ...
```

### カバレッジ要件

- ユニットテスト: 80%以上
- 統合テスト: 主要なパスをカバー
- E2Eテスト: クリティカルなワークフロー

---

## プルリクエスト

### PRの作成

1. **フォークとブランチ**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **変更を実装**

3. **テストを追加・実行**:
   ```bash
   pytest
   ```

4. **リンティング**:
   ```bash
   ruff check src/
   black src/
   mypy src/
   ```

5. **コミット**:
   ```bash
   git commit -m "feat(search): add new search feature"
   ```

6. **プッシュ**:
   ```bash
   git push origin feature/my-feature
   ```

7. **PRを作成**

### PRテンプレート

```markdown
## 概要
<!-- 変更の概要を記述 -->

## 変更の種類
- [ ] バグ修正
- [ ] 新機能
- [ ] 破壊的変更
- [ ] ドキュメント更新

## 変更内容
<!-- 具体的な変更内容 -->

## テスト
<!-- 実施したテストの説明 -->
- [ ] ユニットテストを追加
- [ ] 既存テストがパス
- [ ] ローカルで動作確認

## チェックリスト
- [ ] コードがスタイルガイドに従っている
- [ ] ドキュメントを更新した
- [ ] テストを追加した
- [ ] すべてのテストがパスする

## 関連Issue
<!-- Closes #123 -->
```

### レビュープロセス

1. CIチェックがパス
2. 少なくとも1人のレビュー承認
3. コメントへの対応
4. マージ（squash merge推奨）

---

## 教育理論データの追加

### 新しい理論の追加

1. **theories.jsonに追加**:

```json
{
  "id": "new_theory",
  "name": "New Theory",
  "name_ja": "新理論",
  "category": "learning_theory",
  "priority": 4,
  "theorists": ["theorist_name"],
  "description": "English description...",
  "description_ja": "日本語の説明...",
  "key_principles": [
    "Principle 1",
    "Principle 2"
  ],
  "applications": [
    "Application 1"
  ],
  "strengths": [
    "Strength 1"
  ],
  "limitations": [
    "Limitation 1"
  ]
}
```

2. **theorists.jsonに追加**（必要に応じて）:

```json
{
  "id": "theorist_name",
  "name": "Theorist Name",
  "name_ja": "理論家の名前",
  "birth_year": 1900,
  "death_year": 2000,
  "nationality": "Country",
  "biography": "Biography...",
  "biography_ja": "経歴...",
  "major_works": [
    {"title": "Work Title", "year": 1950}
  ]
}
```

3. **relationships.jsonに追加**:

```json
{
  "source": "new_theory",
  "target": "existing_theory",
  "type": "extends",
  "description": "Description of relationship"
}
```

### カテゴリーの追加

1. **categories.jsonに追加**:

```json
{
  "id": "new_category",
  "name": "New Category",
  "name_ja": "新カテゴリー",
  "description": "Description...",
  "description_ja": "説明..."
}
```

2. **CategoryType列挙型を更新**（`value_objects.py`）

### データ品質チェックリスト

- [ ] 日本語と英語の両方の説明
- [ ] 正確な歴史的情報
- [ ] 適切な関連理論とのリンク
- [ ] 優先度の適切な設定
- [ ] 参考文献の明記

---

## 質問・サポート

- **GitHub Discussions**: 一般的な質問
- **GitHub Issues**: バグ報告・機能提案
- **Email**: tenjin@example.com

貢献してくださるすべての方に感謝します！🙏
