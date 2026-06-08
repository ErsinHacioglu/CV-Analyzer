from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    analyses: Mapped[list["AnalysisRecord"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class AnalysisRecord(Base):
    __tablename__ = "analysis_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), default="unknown")
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    category_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    found_skills: Mapped[str] = mapped_column(Text, default="[]")
    missing_skills: Mapped[str] = mapped_column(Text, default="[]")
    extracted_skills: Mapped[str] = mapped_column(Text, default="[]")
    recommendations: Mapped[str] = mapped_column(Text, default="[]")
    masked_preview: Mapped[str] = mapped_column(Text, default="")
    pii_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="analyses")
