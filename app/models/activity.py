from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # painting, music, dance, reading, cooking, etc.
    description = Column(Text, nullable=True)
    icon = Column(String(10), default="🎯")
    duration_minutes = Column(Integer, default=60)

    streaks = relationship("UserStreak", back_populates="activity")


class UserStreak(Base):
    __tablename__ = "user_streaks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_completed = Column(DateTime, nullable=True)
    total_completions = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="streaks")
    activity = relationship("Activity", back_populates="streaks")
    proofs = relationship("StreakProof", back_populates="streak", cascade="all, delete-orphan")


class StreakProof(Base):
    __tablename__ = "streak_proofs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    streak_id = Column(Integer, ForeignKey("user_streaks.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)  # image, video
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    streak = relationship("UserStreak", back_populates="proofs")


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tier = Column(Integer, nullable=False)  # 1=3days, 2=7days, 3=14days, etc.
    icon = Column(String(10), default="🎁")
    min_streak_days = Column(Integer, nullable=False)
    coupon_prefix = Column(String(20), default="MANAS")

    user_rewards = relationship("UserReward", back_populates="reward")


class UserReward(Base):
    __tablename__ = "user_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_id = Column(Integer, ForeignKey("rewards.id"), nullable=False)
    coupon_code = Column(String(50), unique=True, nullable=False)
    is_claimed = Column(Boolean, default=False)
    claimed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="rewards")
    reward = relationship("Reward", back_populates="user_rewards")
