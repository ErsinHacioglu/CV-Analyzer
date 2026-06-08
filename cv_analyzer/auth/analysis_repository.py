import json

from sqlalchemy import delete, select

from cv_analyzer.db import AnalysisRecord, get_session
from cv_analyzer.models import AnalysisResult


class AnalysisRepository:

    def save(self, user_id: int, result: AnalysisResult, filename: str = "unknown") -> int:
        pii_count = result.pii_finding.total_count if result.pii_finding else 0
        extracted = [
            {"name": s.name, "level": s.level.value, "category": s.category}
            for s in result.resume.skills
        ]

        record = AnalysisRecord(
            user_id=user_id,
            filename=filename,
            category=result.category,
            category_confidence=result.category_confidence,
            match_score=result.match_score,
            found_skills=json.dumps(result.found_skills, ensure_ascii=False),
            missing_skills=json.dumps(result.missing_skills, ensure_ascii=False),
            extracted_skills=json.dumps(extracted, ensure_ascii=False),
            recommendations=json.dumps(result.recommendations, ensure_ascii=False),
            masked_preview=result.masked_text_preview or "",
            pii_count=pii_count,
        )

        with get_session() as session:
            session.add(record)
            session.flush()
            return record.id

    def list_by_user(self, user_id: int, limit: int = 50) -> list[dict]:
        with get_session() as session:
            rows = session.scalars(
                select(AnalysisRecord)
                .where(AnalysisRecord.user_id == user_id)
                .order_by(AnalysisRecord.created_at.desc())
                .limit(limit)
            ).all()

            return [self._to_dict(row) for row in rows]

    def get_by_id(self, user_id: int, analysis_id: int) -> dict | None:
        with get_session() as session:
            row = session.scalar(
                select(AnalysisRecord).where(
                    AnalysisRecord.id == analysis_id,
                    AnalysisRecord.user_id == user_id,
                )
            )
            return self._to_dict(row) if row else None

    def delete_by_id(self, user_id: int, analysis_id: int) -> bool:
        with get_session() as session:
            result = session.execute(
                delete(AnalysisRecord).where(
                    AnalysisRecord.id == analysis_id,
                    AnalysisRecord.user_id == user_id,
                )
            )
            return result.rowcount > 0

    def delete_many(self, user_id: int, analysis_ids: list[int]) -> int:
        if not analysis_ids:
            return 0
        with get_session() as session:
            result = session.execute(
                delete(AnalysisRecord).where(
                    AnalysisRecord.user_id == user_id,
                    AnalysisRecord.id.in_(analysis_ids),
                )
            )
            return result.rowcount

    def delete_all_by_user(self, user_id: int) -> int:
        with get_session() as session:
            result = session.execute(
                delete(AnalysisRecord).where(AnalysisRecord.user_id == user_id)
            )
            return result.rowcount

    @staticmethod
    def _to_dict(row: AnalysisRecord) -> dict:
        return {
            "id": row.id,
            "filename": row.filename,
            "category": row.category,
            "category_confidence": row.category_confidence,
            "match_score": row.match_score,
            "found_skills": json.loads(row.found_skills),
            "missing_skills": json.loads(row.missing_skills),
            "extracted_skills": json.loads(row.extracted_skills),
            "recommendations": json.loads(row.recommendations),
            "masked_preview": row.masked_preview,
            "pii_count": row.pii_count,
            "created_at": row.created_at,
        }
