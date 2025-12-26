"""CitationService - Citation and bibliography generation operations."""

from datetime import datetime
from typing import Any

from ...domain.entities.theory import Theory
from ...domain.entities.theorist import Theorist
from ...domain.repositories.theory_repository import TheoryRepository
from ...domain.value_objects.theory_id import TheoryId
from ...infrastructure.config.logging import get_logger

logger = get_logger(__name__)


class CitationService:
    """Service for citation generation operations.

    Provides citation formatting in multiple styles
    (APA, MLA, Chicago, Harvard) for theories and theorists.
    """

    def __init__(self, theory_repository: TheoryRepository) -> None:
        """Initialize citation service.

        Args:
            theory_repository: Repository for theory data.
        """
        self._theory_repo = theory_repository

    async def generate_citation(
        self,
        theory_id: str,
        style: str = "apa",
        include_url: bool = True,
    ) -> dict[str, Any]:
        """Generate citation for a theory.

        Args:
            theory_id: Theory identifier.
            style: Citation style (apa, mla, chicago, harvard).
            include_url: Whether to include URL if available.

        Returns:
            Formatted citation.
        """
        try:
            tid = TheoryId.from_string(theory_id)
            theory = await self._theory_repo.get_by_id(tid)
        except ValueError:
            return {"error": "Invalid theory ID"}

        if not theory:
            return {"error": "Theory not found"}

        # Get primary theorist
        theorists = getattr(theory, "theorists", [])
        primary_theorist = theorists[0] if theorists else None

        style = style.lower()
        formatters = {
            "apa": self._format_apa,
            "mla": self._format_mla,
            "chicago": self._format_chicago,
            "harvard": self._format_harvard,
        }

        formatter = formatters.get(style, self._format_apa)
        citation = formatter(theory, primary_theorist, include_url)

        return {
            "theory_id": theory_id,
            "theory_name": theory.name,
            "style": style,
            "citation": citation,
            "in_text": self._generate_in_text_citation(theory, primary_theorist, style),
        }

    def _format_apa(
        self,
        theory: Theory,
        theorist: Theorist | None,
        include_url: bool,
    ) -> str:
        """Format citation in APA 7th edition style.

        Args:
            theory: Theory entity.
            theorist: Primary theorist.
            include_url: Include URL flag.

        Returns:
            APA formatted citation.
        """
        year = getattr(theory, "year", None) or datetime.now().year
        
        if theorist:
            author = f"{theorist.last_name}, {theorist.first_name[0]}."
        else:
            author = "Unknown"

        # Format: Author. (Year). Title. Source. URL
        citation = f"{author} ({year}). {theory.name}: {theory.description[:100]}."
        
        if include_url and hasattr(theory, "url") and theory.url:
            citation += f" Retrieved from {theory.url}"

        return citation

    def _format_mla(
        self,
        theory: Theory,
        theorist: Theorist | None,
        include_url: bool,
    ) -> str:
        """Format citation in MLA 9th edition style.

        Args:
            theory: Theory entity.
            theorist: Primary theorist.
            include_url: Include URL flag.

        Returns:
            MLA formatted citation.
        """
        year = getattr(theory, "year", None) or datetime.now().year

        if theorist:
            author = f"{theorist.last_name}, {theorist.first_name}"
        else:
            author = "Unknown"

        # Format: Author. "Title." Source, Year.
        citation = f'{author}. "{theory.name}." Educational Theory Database, {year}.'

        if include_url and hasattr(theory, "url") and theory.url:
            citation += f" {theory.url}."

        return citation

    def _format_chicago(
        self,
        theory: Theory,
        theorist: Theorist | None,
        include_url: bool,
    ) -> str:
        """Format citation in Chicago 17th edition style.

        Args:
            theory: Theory entity.
            theorist: Primary theorist.
            include_url: Include URL flag.

        Returns:
            Chicago formatted citation.
        """
        year = getattr(theory, "year", None) or datetime.now().year

        if theorist:
            author = f"{theorist.last_name}, {theorist.first_name}"
        else:
            author = "Unknown"

        # Format: Author. "Title." Source. Year. URL.
        citation = f'{author}. "{theory.name}." In Educational Theory Database. {year}.'

        if include_url and hasattr(theory, "url") and theory.url:
            citation += f" {theory.url}."

        return citation

    def _format_harvard(
        self,
        theory: Theory,
        theorist: Theorist | None,
        include_url: bool,
    ) -> str:
        """Format citation in Harvard style.

        Args:
            theory: Theory entity.
            theorist: Primary theorist.
            include_url: Include URL flag.

        Returns:
            Harvard formatted citation.
        """
        year = getattr(theory, "year", None) or datetime.now().year

        if theorist:
            author = f"{theorist.last_name}, {theorist.first_name[0]}."
        else:
            author = "Unknown"

        # Format: Author (Year) Title, Source.
        citation = f"{author} ({year}) {theory.name}, Educational Theory Database."

        if include_url and hasattr(theory, "url") and theory.url:
            access_date = datetime.now().strftime("%d %B %Y")
            citation += f" Available at: {theory.url} (Accessed: {access_date})."

        return citation

    def _generate_in_text_citation(
        self,
        theory: Theory,
        theorist: Theorist | None,
        style: str,
    ) -> str:
        """Generate in-text citation.

        Args:
            theory: Theory entity.
            theorist: Primary theorist.
            style: Citation style.

        Returns:
            In-text citation format.
        """
        year = getattr(theory, "year", None) or datetime.now().year

        if theorist:
            last_name = theorist.last_name
        else:
            last_name = "Unknown"

        if style == "mla":
            return f'({last_name})'
        elif style == "chicago":
            return f'({last_name}, {year})'
        else:  # APA, Harvard
            return f'({last_name}, {year})'

    async def generate_bibliography(
        self,
        theory_ids: list[str],
        style: str = "apa",
        sort_by: str = "author",
    ) -> dict[str, Any]:
        """Generate bibliography for multiple theories.

        Args:
            theory_ids: List of theory IDs.
            style: Citation style.
            sort_by: Sort order (author, year, title).

        Returns:
            Formatted bibliography.
        """
        citations = []

        for tid_str in theory_ids:
            result = await self.generate_citation(tid_str, style)
            if "error" not in result:
                citations.append({
                    "theory_id": tid_str,
                    "theory_name": result["theory_name"],
                    "citation": result["citation"],
                })

        # Sort citations
        if sort_by == "author":
            citations.sort(key=lambda c: c["citation"])
        elif sort_by == "year":
            # Extract year from citation for sorting
            def extract_year(c):
                import re
                match = re.search(r'\((\d{4})\)', c["citation"])
                return int(match.group(1)) if match else 0
            citations.sort(key=extract_year)
        elif sort_by == "title":
            citations.sort(key=lambda c: c["theory_name"])

        # Format as bibliography
        bibliography_text = "\n\n".join(c["citation"] for c in citations)

        return {
            "style": style,
            "sort_by": sort_by,
            "count": len(citations),
            "citations": citations,
            "formatted_bibliography": bibliography_text,
        }

    async def export_citations(
        self,
        theory_ids: list[str],
        format: str = "bibtex",
    ) -> dict[str, Any]:
        """Export citations in various formats.

        Args:
            theory_ids: List of theory IDs.
            format: Export format (bibtex, ris, endnote).

        Returns:
            Exported citations.
        """
        entries = []

        for tid_str in theory_ids:
            try:
                tid = TheoryId.from_string(tid_str)
                theory = await self._theory_repo.get_by_id(tid)
            except ValueError:
                continue

            if not theory:
                continue

            theorists = getattr(theory, "theorists", [])
            primary_theorist = theorists[0] if theorists else None
            year = getattr(theory, "year", None) or datetime.now().year

            if format == "bibtex":
                entry = self._to_bibtex(theory, primary_theorist, year)
            elif format == "ris":
                entry = self._to_ris(theory, primary_theorist, year)
            elif format == "endnote":
                entry = self._to_endnote(theory, primary_theorist, year)
            else:
                entry = self._to_bibtex(theory, primary_theorist, year)

            entries.append(entry)

        return {
            "format": format,
            "count": len(entries),
            "content": "\n\n".join(entries),
        }

    def _to_bibtex(
        self,
        theory: Theory,
        theorist: Theorist | None,
        year: int,
    ) -> str:
        """Convert to BibTeX format.

        Args:
            theory: Theory entity.
            theorist: Primary theorist.
            year: Publication year.

        Returns:
            BibTeX entry.
        """
        # Generate unique key
        key = theory.name.lower().replace(" ", "_")[:20]
        if theorist:
            key = f"{theorist.last_name.lower()}_{year}_{key}"

        author = f"{theorist.last_name}, {theorist.first_name}" if theorist else "Unknown"

        return f"""@misc{{{key},
  author = {{{author}}},
  title = {{{theory.name}}},
  year = {{{year}}},
  note = {{{theory.description[:200]}}}
}}"""

    def _to_ris(
        self,
        theory: Theory,
        theorist: Theorist | None,
        year: int,
    ) -> str:
        """Convert to RIS format.

        Args:
            theory: Theory entity.
            theorist: Primary theorist.
            year: Publication year.

        Returns:
            RIS entry.
        """
        author = f"{theorist.last_name}, {theorist.first_name}" if theorist else "Unknown"

        return f"""TY  - GEN
AU  - {author}
TI  - {theory.name}
PY  - {year}
AB  - {theory.description[:200]}
ER  -"""

    def _to_endnote(
        self,
        theory: Theory,
        theorist: Theorist | None,
        year: int,
    ) -> str:
        """Convert to EndNote format.

        Args:
            theory: Theory entity.
            theorist: Primary theorist.
            year: Publication year.

        Returns:
            EndNote entry.
        """
        author = f"{theorist.last_name}, {theorist.first_name}" if theorist else "Unknown"

        return f"""%0 Generic
%A {author}
%T {theory.name}
%D {year}
%X {theory.description[:200]}"""

    async def get_citation_preview(
        self,
        theory_id: str,
    ) -> dict[str, Any]:
        """Get citation in all supported styles.

        Args:
            theory_id: Theory identifier.

        Returns:
            Citations in all styles.
        """
        styles = ["apa", "mla", "chicago", "harvard"]
        previews = {}

        for style in styles:
            result = await self.generate_citation(theory_id, style)
            if "error" not in result:
                previews[style] = {
                    "full": result["citation"],
                    "in_text": result["in_text"],
                }

        if not previews:
            return {"error": "Theory not found"}

        return {
            "theory_id": theory_id,
            "styles": previews,
        }
