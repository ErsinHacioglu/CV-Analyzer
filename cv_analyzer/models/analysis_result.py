from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .resume import Resume

if TYPE_CHECKING:
    from cv_analyzer.security.pii_sanitizer import PIIFinding


@dataclass
class AnalysisResult:
    resume: Resume
    category: str
    category_confidence: float
    match_score: float
    found_skills: list[str]
    missing_skills: list[str]
    recommendations: list[str] = field(default_factory=list)
    pii_finding: "PIIFinding | None" = None
    masked_text_preview: str = ""
    file_deleted: bool = False

    def summary(self) -> str:
        lines = [
            f"Kategori: {self.category} ({self.category_confidence:.0%})",
            f"Skor: {self.match_score:.0f}/100",
            f"Eşleşen: {', '.join(self.found_skills) or '-'}",
            f"Eksik: {', '.join(self.missing_skills) or '-'}",
        ]
        if self.recommendations:
            lines.append("Öneriler:")
            lines.extend(f"  - {rec}" for rec in self.recommendations)
        return "\n".join(lines)
