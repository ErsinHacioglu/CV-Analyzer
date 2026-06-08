import json
import re
from pathlib import Path

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from cv_analyzer.models import Resume, Skill, SkillLevel

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class SkillExtractor:

    def __init__(self, skills_db_path: Path | None = None):
        self._ensure_nltk_data()
        self.skills_db = self._load_skills_db(skills_db_path or _DATA_DIR / "skills_database.json")
        self._skill_patterns = self._build_patterns()
        self._stopwords = set(stopwords.words("english"))

    @staticmethod
    def _ensure_nltk_data() -> None:
        for resource in ("punkt", "punkt_tab", "stopwords"):
            try:
                nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}")
            except LookupError:
                nltk.download(resource, quiet=True)

    @staticmethod
    def _load_skills_db(path: Path) -> dict[str, list[str]]:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def _build_patterns(self) -> list[tuple[re.Pattern, str, str]]:
        patterns = []
        for category, skills in self.skills_db.items():
            for skill in skills:
                escaped = re.escape(skill).replace(r"\ ", r"[\s\-]?")
                pattern = re.compile(rf"\b{escaped}\b", re.IGNORECASE)
                patterns.append((pattern, skill, category))
        return patterns

    def extract(self, resume: Resume) -> Resume:
        text = resume.raw_text
        tokens = [t.lower() for t in word_tokenize(text) if t.lower() not in self._stopwords]

        for pattern, skill_name, category in self._skill_patterns:
            if pattern.search(text):
                level = self._infer_level(skill_name, tokens, text)
                resume.add_skill(Skill(name=skill_name.title(), category=category, level=level))

        return resume

    @staticmethod
    def _infer_level(skill_name: str, tokens: list[str], text: str) -> SkillLevel:
        skill_lower = skill_name.lower()
        advanced_keywords = ("expert", "advanced", "senior", "lead", "architect")
        beginner_keywords = ("beginner", "basic", "learning", "junior", "familiar")

        idx = text.lower().find(skill_lower)
        if idx != -1:
            window = text[max(0, idx - 30) : idx + len(skill_name) + 30].lower()
            if any(kw in window for kw in advanced_keywords):
                return SkillLevel.ADVANCED
            if any(kw in window for kw in beginner_keywords):
                return SkillLevel.BEGINNER

        count = tokens.count(skill_lower.split()[0]) if " " not in skill_lower else text.lower().count(skill_lower)
        if count >= 3:
            return SkillLevel.ADVANCED
        if count >= 2:
            return SkillLevel.INTERMEDIATE
        return SkillLevel.BEGINNER
