from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

_MODEL_DIR = Path(__file__).resolve().parent.parent / "ml" / "saved_models"
_MODEL_PATH = _MODEL_DIR / "resume_classifier.joblib"

DEFAULT_CATEGORIES = [
    "Backend Developer",
    "Cloud Engineer",
    "Data Scientist",
    "Frontend Developer",
    "Full Stack Developer",
    "Machine Learning Engineer",
    "Mobile App Developer (iOS/Android)",
    "Python Developer",
]


class ResumeClassifier:

    CATEGORIES = DEFAULT_CATEGORIES

    def __init__(self, model_path: Path | None = None):
        self.model_path = model_path or _MODEL_PATH
        self._pipeline: Pipeline | None = None
        if self.model_path.exists():
            self._pipeline = joblib.load(self.model_path)

    @property
    def is_trained(self) -> bool:
        return self._pipeline is not None

    @property
    def categories(self) -> list[str]:
        if self.is_trained:
            return list(self._pipeline.classes_)
        return self.CATEGORIES

    def train(self, training_data: pd.DataFrame) -> None:
        self._pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(max_features=8000, ngram_range=(1, 2), stop_words="english")),
            ("clf", LogisticRegression(max_iter=2000, random_state=42)),
        ])
        self._pipeline.fit(training_data["text"], training_data["category"])
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._pipeline, self.model_path)

    def predict(self, text: str) -> tuple[str, float]:
        if not self.is_trained:
            raise RuntimeError("Model eğitilmemiş.")
        proba = self._pipeline.predict_proba([text])[0]
        classes = self._pipeline.classes_
        best_idx = proba.argmax()
        return classes[best_idx], float(proba[best_idx])
