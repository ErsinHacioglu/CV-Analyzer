from cv_analyzer.models import AnalysisResult, Resume
from cv_analyzer.security import PIISanitizer
from cv_analyzer.services.classifier import ResumeClassifier
from cv_analyzer.services.file_parser import ParserFactory
from cv_analyzer.services.recommender import RecommendationEngine
from cv_analyzer.services.scorer import ResumeScorer
from cv_analyzer.services.skill_extractor import SkillExtractor


class CVAnalyzerPipeline:

    def __init__(self):
        self.skill_extractor = SkillExtractor()
        self.classifier = ResumeClassifier()
        self.scorer = ResumeScorer()
        self.recommender = RecommendationEngine()
        self.pii_sanitizer = PIISanitizer()

    def analyze_file(self, file_path: str, target_category: str | None = None) -> AnalysisResult:
        parser = ParserFactory.get_parser(file_path)
        resume = parser.parse(file_path)
        return self.analyze_resume(resume, target_category)

    def analyze_text(self, text: str, filename: str = "pasted_cv.txt", target_category: str | None = None) -> AnalysisResult:
        resume = Resume(raw_text=text, filename=filename)
        return self.analyze_resume(resume, target_category)

    def analyze_resume(self, resume: Resume, target_category: str | None = None) -> AnalysisResult:
        resume = self.skill_extractor.extract(resume)

        if target_category:
            category = target_category
            confidence = 1.0
        else:
            category, confidence = self.classifier.predict(resume.raw_text)

        score, found, missing = self.scorer.score(resume, category)
        resume.predicted_category = category
        resume.match_score = score

        recommendations = self.recommender.generate(resume, category, missing)
        pii_finding, masked_preview = self.pii_sanitizer.analyze(resume.raw_text)

        return AnalysisResult(
            resume=resume,
            category=category,
            category_confidence=confidence,
            match_score=score,
            found_skills=found,
            missing_skills=missing,
            recommendations=recommendations,
            pii_finding=pii_finding,
            masked_text_preview=masked_preview,
        )
