import json
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.activity import Activity, UserStreak

def get_recommended_activities(db: Session, user_id: int, interests: List[str]) -> List[Dict]:
    """Get personalized activity recommendations based on user interests and history."""
    all_activities = db.query(Activity).all()
    
    # Simple recommendation heuristic based on interests match
    recommended = []
    for act in all_activities:
        score = 0
        if act.category.lower() in [i.lower() for i in interests]:
            score += 10
        # Give a base score to ensure we return some activities
        score += 1
        
        recommended.append({
            "id": act.id,
            "name": act.name,
            "category": act.category,
            "description": act.description,
            "icon": act.icon,
            "duration_minutes": act.duration_minutes,
            "score": score
        })
        
    # Sort by score descending
    recommended.sort(key=lambda x: x["score"], reverse=True)
    return recommended[:6]  # Return top 6 recommendations

def get_recommended_games(db: Session, user_id: int, risk_level: str) -> List[Dict]:
    """Recommend games based on mental health needs."""
    games = [
        {"name": "Stress Popper", "type": "anxiety", "desc": "Pop bubble wrap to vent frustration and relieve stress.", "url": "/games/bubble-wrap"},
        {"name": "Worry Dissolver", "type": "anxiety", "desc": "Shatter negative thoughts into stardust with affirmations.", "url": "/games/worry-destroyer"},
        {"name": "Zen Sand Garden", "type": "anxiety", "desc": "Rake smooth sand patterns & arrange peaceful stones.", "url": "/games/zen-garden"},
        {"name": "Breathing Exercise", "type": "anxiety", "desc": "Box breathing to reduce panic and anxiety.", "url": "/games/breathing"},
        {"name": "Gratitude Journal", "type": "low_mood", "desc": "Write 3 things you are grateful for.", "url": "/games/gratitude"},
        {"name": "Memory Match", "type": "poor_focus", "desc": "A game to improve concentration.", "url": "/games/memory"}
    ]
    
    recommended = []
    for game in games:
        if risk_level == "High Anxiety" and game["type"] == "anxiety":
            recommended.append(game)
        elif risk_level == "Low Mood" and game["type"] == "low_mood":
            recommended.append(game)
        elif risk_level == "Poor Focus" and game["type"] == "poor_focus":
            recommended.append(game)
            
    # Fallback
    if not recommended:
        recommended = games
        
    return recommended

def get_daily_challenge(db: Session, user_id: int) -> Dict:
    """Generate a personalized daily challenge."""
    return {
        "title": "Drink 2L of Water",
        "description": "Hydration is key to mental clarity and energy. Track your water intake today.",
        "points": 50,
        "completed": False
    }
