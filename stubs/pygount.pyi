"""Enough type stubs to satisfy Pyre."""

from pathlib import Path

class ProjectSummary:
    """Just a type stub."""

    total_code_count: int

    def add(self, analysis: SourceAnalysis) -> None:
        """Just a type stub."""

class SourceAnalysis:
    """Just a type stub."""

    @staticmethod
    def from_file(filepath: Path, name: str) -> SourceAnalysis:
        """Just a type stub."""
        return SourceAnalysis()
