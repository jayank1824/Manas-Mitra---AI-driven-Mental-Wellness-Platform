import numpy as np
from typing import Dict, List, Optional
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.stats import MentalHealthScore, DailyLog, GameScore
from app.models.activity import UserStreak

def predict_wellness_trend(db: Session, user_id: int) -> Dict:
    """
    Use linear regression to predict wellness score trajectory.
    Returns predicted score for next 7 days and improvement percentage.
    """
    scores = db.query(MentalHealthScore).filter(
        MentalHealthScore.user_id == user_id
    ).order_by(MentalHealthScore.calculated_at.asc()).all()
    
    if len(scores) < 3:
        return {"prediction": "Not enough data", "days_needed": 3 - len(scores)}
    
    X = np.array(range(len(scores))).reshape(-1, 1)
    y = np.array([s.score for s in scores])
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next 7 days
    future_X = np.array(range(len(scores), len(scores) + 7)).reshape(-1, 1)
    predictions = model.predict(future_X)
    predictions = np.clip(predictions, 0, 100)
    
    current = scores[-1].score
    predicted_end = predictions[-1]
    change_pct = ((predicted_end - current) / max(current, 1)) * 100
    
    return {
        "current_score": int(current),
        "predicted_score_7d": int(predicted_end),
        "change_percentage": round(change_pct, 1),
        "direction": "improving" if change_pct > 0 else "declining" if change_pct < 0 else "stable",
        "daily_predictions": [int(p) for p in predictions],
        "confidence": min(len(scores) / 30 * 100, 100)  # More data = more confidence
    }

def detect_anomalies(db: Session, user_id: int) -> List[Dict]:
    """Detect sudden drops in wellness score."""
    scores = db.query(MentalHealthScore).filter(
        MentalHealthScore.user_id == user_id
    ).order_by(MentalHealthScore.calculated_at.asc()).all()
    
    anomalies = []
    if len(scores) > 3:
        for i in range(1, len(scores)):
            drop = scores[i-1].score - scores[i].score
            if drop > 15:
                anomalies.append({
                    "date": scores[i].calculated_at.isoformat(),
                    "drop": drop,
                    "previous": scores[i-1].score,
                    "current": scores[i].score
                })
    return anomalies

def generate_insights(db: Session, user_id: int) -> List[str]:
    """Generate text insights from user data."""
    insights = []
    
    # 1. Wellness trend insight
    trend = predict_wellness_trend(db, user_id)
    if "change_percentage" in trend:
        if trend["change_percentage"] > 5:
            insights.append(f"Your wellness score has improved by {trend['change_percentage']}% recently! Keep up the good work.")
        elif trend["change_percentage"] < -5:
            insights.append("Your wellness score has dipped slightly. Make sure to take some time for yourself.")
            
    # 2. Activity consistency
    streaks = db.query(UserStreak).filter(UserStreak.user_id == user_id).all()
    if streaks:
        longest = max(streaks, key=lambda s: s.longest_streak)
        if longest.longest_streak > 3:
            insights.append(f"You have a great {longest.longest_streak}-day streak! Consistency is key.")
            
    # 3. Game preference
    game_counts = db.query(GameScore.game_type, func.count(GameScore.id).label('count')).filter(
        GameScore.user_id == user_id
    ).group_by(GameScore.game_type).order_by(func.count(GameScore.id).desc()).first()
    
    if game_counts:
        insights.append(f"You play {game_counts.game_type} most often. It seems to be your favorite way to unwind.")
        
    # 4. Sleep and stress correlation
    logs = db.query(DailyLog).filter(DailyLog.user_id == user_id).order_by(DailyLog.date.desc()).limit(14).all()
    if len(logs) >= 5:
        good_sleep = [l for l in logs if l.sleep_hours >= 7]
        bad_sleep = [l for l in logs if l.sleep_hours < 7]
        if good_sleep and bad_sleep:
            avg_stress_good = sum(l.stress_level for l in good_sleep) / len(good_sleep)
            avg_stress_bad = sum(l.stress_level for l in bad_sleep) / len(bad_sleep)
            if avg_stress_bad - avg_stress_good > 1:
                insights.append("We noticed your stress is noticeably higher on days you get less than 7 hours of sleep.")
                
    # 5. General encouragement based on logging
    if len(logs) > 0:
        insights.append(f"You've logged {len(logs)} daily check-ins recently. Tracking your feelings is a great step in mindfulness.")
    else:
        insights.append("Start logging your daily mood to receive more personalized insights!")

    # Fallbacks if not enough insights
    if len(insights) < 3:
        insights.append("Try practicing the 4-7-8 breathing technique when you feel overwhelmed.")
        insights.append("Connecting with our community can provide valuable support on tough days.")
        
    return insights[:5]
