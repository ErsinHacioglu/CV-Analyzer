import json
from pathlib import Path

from cv_analyzer.models import Resume

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class ResumeScorer:

    REQUIRED_WEIGHT = 0.7
    PREFERRED_WEIGHT = 0.3

    def __init__(self, profiles_path: Path | None = None):
        with open(profiles_path or _DATA_DIR / "job_profiles.json", encoding="utf-8") as f:
            self.profiles = json.load(f)

    def score(self, resume: Resume, category: str) -> tuple[float, list[str], list[str]]:
        profile = self.profiles.get(category)
        if profile is None:
            return 0.0, [], []

        found_lower = {s.lower() for s in resume.skill_names}
        required = [s.lower() for s in profile["required_skills"]]
        preferred = [s.lower() for s in profile["preferred_skills"]]

        found_required = [s for s in required if s in found_lower]
        found_preferred = [s for s in preferred if s in found_lower]
        missing_required = [s for s in required if s not in found_lower]
        missing_preferred = [s for s in preferred if s not in found_lower]

        req_score = (len(found_required) / len(required) * 100) if required else 100
        pref_score = (len(found_preferred) / len(preferred) * 100) if preferred else 100
        total = req_score * self.REQUIRED_WEIGHT + pref_score * self.PREFERRED_WEIGHT

        missing = [s.title() for s in missing_required + missing_preferred]
        found = [s.title() for s in found_required + found_preferred]
        return round(total, 1), found, missing
