from cv_analyzer.models import Resume
from cv_analyzer.models.skill import SkillLevel


class RecommendationEngine:

    SKILL_ADVICE: dict[str, str] = {
        "docker": "Konteyner tarafı için öğrenmen iyi olur.",
        "kubernetes": "Büyük projelerde lazım oluyor.",
        "aws": "Bulut tarafında sık aranıyor.",
        "react": "Frontend'de çok kullanılıyor.",
        "scikit-learn": "ML projelerinde temel.",
        "sql": "Veri tarafı için şart.",
        "git": "Ekip çalışmasında kullanılıyor.",
        "tensorflow": "Derin öğrenme için.",
        "pytorch": "ML tarafında popüler.",
        "terraform": "Altyapı yönetimi için.",
        "flutter": "Mobil için tek kod tabanı.",
        "kotlin": "Android için.",
        "swift": "iOS için.",
    }

    CATEGORY_ROADMAPS: dict[str, list[str]] = {
        "Backend Developer": ["docker", "kubernetes", "aws", "redis"],
        "Frontend Developer": ["typescript", "next.js", "figma"],
        "Data Scientist": ["tensorflow", "pytorch", "spark"],
        "Cloud Engineer": ["terraform", "kubernetes", "ansible"],
        "Full Stack Developer": ["docker", "aws", "kubernetes"],
        "Python Developer": ["fastapi", "docker", "aws"],
        "Mobile App Developer (iOS/Android)": ["flutter", "kotlin", "firebase"],
        "Machine Learning Engineer": ["kubernetes", "docker", "pytorch"],
    }

    def generate(self, resume: Resume, category: str, missing_skills: list[str]) -> list[str]:
        recommendations: list[str] = []
        found_names = {s.lower() for s in resume.skill_names}
        strong_skills = [s for s in resume.skills if s.level in (SkillLevel.ADVANCED, SkillLevel.INTERMEDIATE)]

        if strong_skills and missing_skills:
            strong = strong_skills[0].name
            top_missing = missing_skills[0]
            recommendations.append(
                f"{strong} iyi ama {top_missing} eksik. {top_missing} öğrenmeni öneririm."
            )

        for skill in missing_skills[:3]:
            advice = self.SKILL_ADVICE.get(skill.lower())
            if advice:
                recommendations.append(f"{skill}: {advice}")

        roadmap = self.CATEGORY_ROADMAPS.get(category, [])
        next_skills = [s.title() for s in roadmap if s not in found_names][:2]
        if next_skills:
            recommendations.append(f"Sonraki adım: {', '.join(next_skills)}")

        if not recommendations:
            recommendations.append("CV bu role uygun görünüyor.")

        return recommendations
