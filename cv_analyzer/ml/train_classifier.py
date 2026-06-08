import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from cv_analyzer.services.classifier import ResumeClassifier

DATASET_PATH = Path(__file__).resolve().parent.parent.parent / "gpt_dataset.csv"


def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATASET_PATH)
    df = df.rename(columns={"Category": "category", "Resume": "text"})
    return df.dropna(subset=["category", "text"])


def main() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Veri seti yok: {DATASET_PATH}")

    df = load_dataset()
    print(f"CV sayisi: {len(df)}")
    print(f"Kategori: {df['category'].nunique()}")

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["category"], test_size=0.2, random_state=42, stratify=df["category"]
    )

    train_df = pd.DataFrame({"text": X_train, "category": y_train})
    classifier = ResumeClassifier()
    classifier.train(train_df)

    y_pred = classifier._pipeline.predict(X_test.tolist())
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Model: {classifier.model_path}")
    print(f"Test accuracy: {accuracy:.1%}")
    print(classification_report(y_test, y_pred, zero_division=0))


if __name__ == "__main__":
    main()
