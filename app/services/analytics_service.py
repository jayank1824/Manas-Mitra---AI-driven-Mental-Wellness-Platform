import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.stats import DailyLog, GameScore, MentalHealthScore
from app.models.activity import UserStreak, Activity
from app.models.community import Post, Comment, MeetupRSVP

def _format_date(d) -> str:
    if isinstance(d, str):
        try:
            parsed = datetime.strptime(d[:10], "%Y-%m-%d")
            return parsed.strftime("%b %d")
        except Exception:
            return d
    elif hasattr(d, "strftime"):
        return d.strftime("%b %d")
    return str(d)

def get_wellness_trend(db: Session, user_id: int, days: int = 30) -> Dict:
    """Get wellness score trend over time."""
    scores = db.query(MentalHealthScore).filter(
        MentalHealthScore.user_id == user_id
    ).order_by(MentalHealthScore.calculated_at.desc()).limit(days).all()
    
    if not scores:
        return {"labels": ["Day 1"], "data": [50], "current": 50, "trend": "stable"}
        
    return {
        "labels": [_format_date(s.calculated_at) for s in reversed(scores)],
        "data": [s.score for s in reversed(scores)],
        "current": scores[0].score,
        "trend": calculate_trend([s.score for s in scores])
    }

def get_mood_trend(db: Session, user_id: int, days: int = 30) -> Dict:
    """Get mood and energy trend from daily logs."""
    logs = db.query(DailyLog).filter(
        DailyLog.user_id == user_id
    ).order_by(DailyLog.date.asc()).limit(days).all()
    
    if not logs:
        return {
            "labels": ["Today"],
            "moodData": [5],
            "energyData": [5]
        }
        
    return {
        "labels": [_format_date(log.date) for log in logs],
        "moodData": [log.mood_score for log in logs],
        "energyData": [log.energy_level for log in logs]
    }

def get_activity_stats(db: Session, user_id: int) -> Dict:
    """Get activity completion statistics."""
    streaks = db.query(UserStreak).filter(UserStreak.user_id == user_id).all()
    
    if not streaks:
        return {
            "labels": ["Painting", "Music", "Meditation"],
            "data": [0, 0, 0]
        }
        
    labels = []
    data = []
    for s in streaks:
        act = db.query(Activity).filter(Activity.id == s.activity_id).first()
        labels.append(act.name if act else f"Activity {s.activity_id}")
        data.append(s.total_completions or s.current_streak or 0)
        
    return {
        "labels": labels,
        "data": data
    }

def get_game_stats(db: Session, user_id: int) -> Dict:
    """Get game performance statistics across types."""
    scores = db.query(
        GameScore.game_type,
        func.avg(GameScore.score).label("avg_score")
    ).filter(
        GameScore.user_id == user_id
    ).group_by(GameScore.game_type).all()
    
    types = ["breathing", "bubble_wrap", "worry_destroyer", "zen_garden", "memory", "puzzle", "gratitude", "focus"]
    type_labels = ["Breathing", "Stress Popper", "Worry Dissolver", "Zen Garden", "Memory", "Word Therapy", "Gratitude", "Focus Flow"]
    data_map = {row.game_type: int(row.avg_score) for row in scores}
    
    return {
        "labels": type_labels,
        "data": [data_map.get(t, 0) for t in types]
    }

def get_community_engagement(db: Session, user_id: int) -> Dict:
    """Get community engagement metrics."""
    posts_count = db.query(Post).filter(Post.user_id == user_id).count()
    comments_count = db.query(Comment).filter(Comment.user_id == user_id).count()
    meetups_count = db.query(MeetupRSVP).filter(MeetupRSVP.user_id == user_id).count()
    
    return {
        "labels": ["Posts Shared", "Comments & Encouragement", "Meetups Joined"],
        "data": [max(posts_count, 1), max(comments_count, 2), max(meetups_count, 1)]
    }

def get_sleep_stress_correlation(db: Session, user_id: int) -> Dict:
    """Get sleep vs stress data for scatter plot."""
    logs = db.query(DailyLog).filter(DailyLog.user_id == user_id).order_by(DailyLog.date.desc()).limit(30).all()
    
    sleep_data = []
    stress_data = []
    
    if not logs:
        sleep_data = [{"x": "Day 1", "y": 7.0}]
        stress_data = [{"x": "Day 1", "y": 4}]
    else:
        for log in logs:
            date_str = _format_date(log.date)
            sleep_data.append({"x": date_str, "y": log.sleep_hours})
            stress_data.append({"x": date_str, "y": log.stress_level})
        
    return {
        "sleepData": sleep_data,
        "stressData": stress_data
    }

def get_overall_summary(db: Session, user_id: int) -> Dict:
    """Get overall dashboard summary statistics."""
    wellness = get_wellness_trend(db, user_id, 7)
    
    streaks = db.query(func.max(UserStreak.longest_streak)).filter(UserStreak.user_id == user_id).scalar() or 0
    total_activities = db.query(func.sum(UserStreak.total_completions)).filter(UserStreak.user_id == user_id).scalar() or 0
    games_played = db.query(func.count(GameScore.id)).filter(GameScore.user_id == user_id).scalar() or 0
    
    return {
        "current_score": wellness["current"],
        "trend": wellness["trend"],
        "longest_streak": streaks,
        "total_activities": total_activities,
        "games_played": games_played
    }

def calculate_trend(values: List[int]) -> str:
    """Calculate if trend is improving, declining, or stable."""
    if len(values) < 2:
        return "stable"
    mid = len(values) // 2
    recent = sum(values[:mid]) / max(mid, 1)
    older = sum(values[mid:]) / max(len(values) - mid, 1)
    diff = recent - older
    if diff > 5:
        return "improving"
    elif diff < -5:
        return "declining"
    return "stable"
