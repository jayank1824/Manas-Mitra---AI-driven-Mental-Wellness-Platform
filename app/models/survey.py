from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class SurveyQuestion(Base):
    __tablename__ = "survey_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON array of options
    category = Column(String(50), nullable=False)  # mental_health, medical, lifestyle, interests, support
    order_num = Column(Integer, nullable=False)

    responses = relationship("SurveyResponse", back_populates="question")


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("survey_questions.id"), nullable=False)
    selected_options = Column(Text, nullable=False)  # JSON array of selected option indices
    other_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="survey_responses")
    question = relationship("SurveyQuestion", back_populates="responses")
