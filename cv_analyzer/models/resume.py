from dataclasses import dataclass, field
from typing import Optional

from .skill import Skill


@dataclass
class Resume:
    raw_text: str
    filename: str = "unknown"
    skills: list[Skill] = field(default_factory=list)
    predicted_category: Optional[str] = None
    match_score: float = 0.0

    @property
    def skill_names(self) -> list[str]:
        return [skill.name for skill in self.skills]

    def add_skill(self, skill: Skill) -> None:
        if not any(existing.matches(skill.name) for existing in self.skills):
            self.skills.append(skill)

    def word_count(self) -> int:
        return len(self.raw_text.split())
