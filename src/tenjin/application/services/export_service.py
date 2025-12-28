"""ExportService - データエクスポート機能."""

import json
from datetime import datetime
from typing import Any

from ...domain.entities.theory import Theory
from ...domain.repositories.theory_repository import TheoryRepository
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class ExportService:
    """Service for exporting theory data in various formats."""

    def __init__(self, theory_repository: TheoryRepository) -> None:
        """Initialize export service.

        Args:
            theory_repository: Repository for theory data.
        """
        self._theory_repo = theory_repository

    async def export_json(
        self,
        theory_ids: list[str] | None = None,
        categories: list[str] | None = None,
        include_metadata: bool = True,
    ) -> dict[str, Any]:
        """Export theories as JSON.

        Args:
            theory_ids: Specific theory IDs to export, or None for all.
            categories: Filter by categories.
            include_metadata: Include export metadata.

        Returns:
            JSON-serializable dictionary.
        """
        theories = await self._get_theories(theory_ids, categories)

        result: dict[str, Any] = {
            "theories": [self._theory_to_dict(t) for t in theories],
        }

        if include_metadata:
            result["metadata"] = {
                "version": "2.0.0",
                "exported_at": datetime.now().isoformat(),
                "total_theories": len(theories),
                "format": "tenjin-theories-v2",
            }

        logger.info(f"Exported {len(theories)} theories as JSON")
        return result

    async def export_markdown(
        self,
        theory_ids: list[str] | None = None,
        categories: list[str] | None = None,
        language: str = "ja",
        include_toc: bool = True,
    ) -> str:
        """Export theories as Markdown document.

        Args:
            theory_ids: Specific theory IDs to export, or None for all.
            categories: Filter by categories.
            language: Output language ("ja" or "en").
            include_toc: Include table of contents.

        Returns:
            Markdown formatted string.
        """
        theories = await self._get_theories(theory_ids, categories)

        # Group by category
        by_category: dict[str, list[Theory]] = {}
        for t in theories:
            cat = t.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(t)

        # Build markdown
        lines: list[str] = []

        # Header
        title = "教育理論カタログ" if language == "ja" else "Educational Theories Catalog"
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"*生成日: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append(f"*理論数: {len(theories)}*")
        lines.append("")

        # Table of contents
        if include_toc:
            toc_title = "目次" if language == "ja" else "Table of Contents"
            lines.append(f"## {toc_title}")
            lines.append("")
            for category in sorted(by_category.keys()):
                cat_name = self._get_category_name(category, language)
                anchor = category.lower().replace(" ", "-")
                lines.append(f"- [{cat_name}](#{anchor})")
            lines.append("")

        # Content by category
        for category in sorted(by_category.keys()):
            cat_name = self._get_category_name(category, language)
            lines.append(f"## {cat_name}")
            lines.append("")

            for theory in sorted(by_category[category], key=lambda t: t.priority.value):
                lines.extend(self._theory_to_markdown(theory, language))
                lines.append("")

        logger.info(f"Exported {len(theories)} theories as Markdown")
        return "\n".join(lines)

    async def export_csv(
        self,
        theory_ids: list[str] | None = None,
        categories: list[str] | None = None,
    ) -> str:
        """Export theories as CSV.

        Args:
            theory_ids: Specific theory IDs to export, or None for all.
            categories: Filter by categories.

        Returns:
            CSV formatted string.
        """
        theories = await self._get_theories(theory_ids, categories)

        # CSV header
        headers = [
            "id", "name", "name_ja", "category", "priority",
            "theorists", "description", "description_ja",
            "key_principles", "applications", "strengths", "limitations",
        ]

        lines = [",".join(headers)]

        for t in theories:
            row = [
                self._csv_escape(t.id.value),
                self._csv_escape(t.name),
                self._csv_escape(t.name_ja or ""),
                self._csv_escape(t.category.value),
                str(t.priority.value),
                self._csv_escape("; ".join(t.theorists)),
                self._csv_escape(t.description),
                self._csv_escape(t.description_ja or ""),
                self._csv_escape("; ".join(t.key_principles)),
                self._csv_escape("; ".join(t.applications)),
                self._csv_escape("; ".join(t.strengths)),
                self._csv_escape("; ".join(t.limitations)),
            ]
            lines.append(",".join(row))

        logger.info(f"Exported {len(theories)} theories as CSV")
        return "\n".join(lines)

    async def _get_theories(
        self,
        theory_ids: list[str] | None = None,
        categories: list[str] | None = None,
    ) -> list[Theory]:
        """Get theories based on filters.

        Args:
            theory_ids: Specific IDs to get.
            categories: Category filters.

        Returns:
            List of theories.
        """
        if theory_ids:
            theories = []
            for tid in theory_ids:
                theory = await self._theory_repo.get_by_id(tid)
                if theory:
                    theories.append(theory)
            return theories
        else:
            all_theories = await self._theory_repo.get_all()
            if categories:
                return [t for t in all_theories if t.category.value in categories]
            return list(all_theories)

    def _theory_to_dict(self, theory: Theory) -> dict[str, Any]:
        """Convert theory to dictionary."""
        return {
            "id": theory.id.value,
            "name": theory.name,
            "name_ja": theory.name_ja,
            "category": theory.category.value,
            "priority": theory.priority.value,
            "theorists": list(theory.theorists),
            "description": theory.description,
            "description_ja": theory.description_ja,
            "key_principles": list(theory.key_principles),
            "applications": list(theory.applications),
            "strengths": list(theory.strengths),
            "limitations": list(theory.limitations),
        }

    def _theory_to_markdown(self, theory: Theory, language: str) -> list[str]:
        """Convert theory to markdown lines."""
        lines: list[str] = []

        # Title
        name = theory.name_ja if language == "ja" and theory.name_ja else theory.name
        lines.append(f"### {name}")
        lines.append("")

        # Metadata
        if language == "ja":
            lines.append(f"**ID**: `{theory.id.value}`")
            lines.append(f"**カテゴリ**: {self._get_category_name(theory.category.value, language)}")
            lines.append(f"**優先度**: {'★' * (6 - theory.priority.value)}")
            if theory.theorists:
                lines.append(f"**提唱者**: {', '.join(theory.theorists)}")
        else:
            lines.append(f"**ID**: `{theory.id.value}`")
            lines.append(f"**Category**: {theory.category.value}")
            lines.append(f"**Priority**: {'★' * (6 - theory.priority.value)}")
            if theory.theorists:
                lines.append(f"**Theorists**: {', '.join(theory.theorists)}")

        lines.append("")

        # Description
        desc = theory.description_ja if language == "ja" and theory.description_ja else theory.description
        lines.append(desc)
        lines.append("")

        # Key principles
        if theory.key_principles:
            title = "主要原則" if language == "ja" else "Key Principles"
            lines.append(f"**{title}**:")
            for p in theory.key_principles:
                lines.append(f"- {p}")
            lines.append("")

        # Applications
        if theory.applications:
            title = "応用例" if language == "ja" else "Applications"
            lines.append(f"**{title}**:")
            for a in theory.applications:
                lines.append(f"- {a}")
            lines.append("")

        lines.append("---")
        return lines

    def _get_category_name(self, category: str, language: str) -> str:
        """Get localized category name."""
        if language != "ja":
            return category

        names = {
            "learning_theory": "学習理論",
            "instructional_design": "インストラクショナルデザイン",
            "assessment": "評価",
            "cognitive_science": "認知科学",
            "motivation": "動機づけ",
            "social_learning": "社会的学習",
            "technology_enhanced": "テクノロジー活用",
            "special_education": "特別支援教育",
        }
        return names.get(category, category)

    def _csv_escape(self, value: str) -> str:
        """Escape value for CSV."""
        if "," in value or '"' in value or "\n" in value:
            return '"' + value.replace('"', '""') + '"'
        return value
