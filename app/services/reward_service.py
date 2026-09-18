import uuid
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.activity import UserStreak, StreakProof, Reward, UserReward, Activity
from app.models.user import UserProfile

def generate_coupon_code(prefix: str) -> str:
    """Generate unique coupon code like MANAS-CAFE-A1B2C3"""
    unique = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{unique}"

def update_streak(db: Session, user_id: int, streak_id: int, proof_path: str, file_type: str) -> dict:
    """
    Update user's streak after activity completion with proof.
    Returns dict with streak info and any new rewards earned.
    """
    streak = db.query(UserStreak).filter(UserStreak.id == streak_id, UserStreak.user_id == user_id).first()
    if not streak:
        return {"error": "Streak not found"}
    
    now = datetime.now(timezone.utc)
    today = now.date()
    
    # Check if already completed today
    if streak.last_completed:
        last_date = streak.last_completed.date() if hasattr(streak.last_completed, 'date') else streak.last_completed
        if str(last_date) == str(today):
            return {"error": "Already completed today", "streak": streak.current_streak}
    
    # Check if streak is broken (more than 1 day gap, with 1 grace day per week)
    if streak.last_completed:
        last_date = streak.last_completed.date() if hasattr(streak.last_completed, 'date') else streak.last_completed
        days_gap = (today - last_date).days if hasattr(last_date, '__sub__') else 1
        if days_gap > 2:  # More than 2 days = streak broken
            streak.current_streak = 1
        else:
            streak.current_streak += 1
    else:
        streak.current_streak = 1
    
    # Update streak
    streak.last_completed = now
    streak.total_completions += 1
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak
    
    # Save proof
    proof = StreakProof(
        user_id=user_id,
        streak_id=streak_id,
        file_path=proof_path,
        file_type=file_type
    )
    db.add(proof)
    
    # Check for new rewards
    new_rewards = check_and_award_rewards(db, user_id, streak.current_streak)
    
    db.commit()
    db.refresh(streak)
    
    return {
        "success": True,
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "total_completions": streak.total_completions,
        "new_rewards": new_rewards
    }

def check_and_award_rewards(db: Session, user_id: int, current_streak: int) -> list:
    """Check if user qualifies for new rewards and award them."""
    # Get all rewards the user hasn't earned yet
    earned_reward_ids = [ur.reward_id for ur in db.query(UserReward).filter(UserReward.user_id == user_id).all()]
    available_rewards = db.query(Reward).filter(
        Reward.min_streak_days <= current_streak,
        ~Reward.id.in_(earned_reward_ids) if earned_reward_ids else True
    ).all()
    
    new_rewards = []
    for reward in available_rewards:
        if reward.id not in earned_reward_ids:
            coupon = generate_coupon_code(reward.coupon_prefix)
            user_reward = UserReward(
                user_id=user_id,
                reward_id=reward.id,
                coupon_code=coupon
            )
            db.add(user_reward)
            new_rewards.append({
                "name": reward.name,
                "description": reward.description,
                "coupon_code": coupon,
                "icon": reward.icon
            })
    
    return new_rewards

def get_user_rewards(db: Session, user_id: int) -> list:
    """Get all rewards earned by user."""
    user_rewards = db.query(UserReward).filter(UserReward.user_id == user_id).all()
    result = []
    for ur in user_rewards:
        reward = db.query(Reward).filter(Reward.id == ur.reward_id).first()
        if reward:
            result.append({
                "name": reward.name,
                "description": reward.description,
                "icon": reward.icon,
                "coupon_code": ur.coupon_code,
                "tier": reward.tier,
                "min_streak_days": reward.min_streak_days,
                "claimed_at": ur.claimed_at.isoformat() if ur.claimed_at else None
            })
    return result

def get_next_reward(db: Session, user_id: int, current_streak: int) -> dict:
    """Get the next reward the user can earn."""
    earned_reward_ids = [ur.reward_id for ur in db.query(UserReward).filter(UserReward.user_id == user_id).all()]
    next_reward = db.query(Reward).filter(
        Reward.min_streak_days > current_streak,
        ~Reward.id.in_(earned_reward_ids) if earned_reward_ids else True
    ).order_by(Reward.min_streak_days.asc()).first()
    
    if next_reward:
        return {
            "name": next_reward.name,
            "icon": next_reward.icon,
            "days_needed": next_reward.min_streak_days,
            "days_remaining": next_reward.min_streak_days - current_streak
        }
    return None
