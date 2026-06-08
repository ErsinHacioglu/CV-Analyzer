from dataclasses import dataclass
from enum import Enum


class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class Skill:
    name: str
    category: str
    level: SkillLevel = SkillLevel.INTERMEDIATE

    def __str__(self) -> str:
        return self.name

    def matches(self, other_name: str) -> bool:
        return self.name.lower() == other_name.lower()
