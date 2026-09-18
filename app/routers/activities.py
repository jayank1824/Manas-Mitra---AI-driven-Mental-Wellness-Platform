import os
import uuid
import json
from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import get_current_user_from_cookie
from app.services.reward_service import update_streak, get_user_rewards, get_next_reward
from app.models.activity import Activity, UserStreak, StreakProof, Reward, UserReward
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def activities_index(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    streaks = db.query(UserStreak).filter(UserStreak.user_id == user.id).all()
    user_interests = json.loads(user.profile.interests) if user.profile and user.profile.interests else []
    
    # Calculate max streak for next reward
    highest_streak = max([s.current_streak for s in streaks], default=0)
    next_reward = get_next_reward(db, user.id, highest_streak)
    
    return templates.TemplateResponse("activities/index.html", {
        "request": request,
        "user": user,
        "streaks": streaks,
        "interests": user_interests,
        "next_reward": next_reward,
        "active_page": "activities"
    })

@router.get("/streak/{streak_id}", response_class=HTMLResponse)
async def streak_detail(streak_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    streak = db.query(UserStreak).filter(UserStreak.id == streak_id, UserStreak.user_id == user.id).first()
    if not streak:
        return RedirectResponse(url="/activities", status_code=303)
        
    proofs = db.query(StreakProof).filter(StreakProof.streak_id == streak.id).order_by(StreakProof.uploaded_at.desc()).all()
    rewards = db.query(Reward).order_by(Reward.min_streak_days.asc()).all()
    
    return templates.TemplateResponse("activities/streak.html", {
        "request": request,
        "user": user,
        "streak": streak,
        "proofs": proofs,
        "rewards": rewards,
        "active_page": "activities"
    })

@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request, streak_id: int = None, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    streaks = db.query(UserStreak).filter(UserStreak.user_id == user.id).all()
    return templates.TemplateResponse("activities/upload.html", {
        "request": request,
        "user": user,
        "streaks": streaks,
        "selected_streak_id": streak_id,
        "active_page": "activities"
    })

@router.post("/upload-proof")
async def upload_proof(
    request: Request,
    streak_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    # Verify streak belongs to user
    streak = db.query(UserStreak).filter(UserStreak.id == streak_id, UserStreak.user_id == user.id).first()
    if not streak:
        return RedirectResponse(url="/activities", status_code=303)
        
    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
    filename = f"{user.id}_{streak_id}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    file_type = "video" if ext in [".mp4", ".mov", ".avi", ".webm"] else "image"
    relative_path = f"/static/uploads/{filename}"
    
    # Update streak
    update_streak(db, user.id, streak_id, relative_path, file_type)
    
    return RedirectResponse(url=f"/activities/streak/{streak_id}", status_code=303)

@router.get("/rewards", response_class=HTMLResponse)
async def rewards_view(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    earned_rewards = get_user_rewards(db, user.id)
    all_rewards = db.query(Reward).order_by(Reward.min_streak_days.asc()).all()
    
    streaks = db.query(UserStreak).filter(UserStreak.user_id == user.id).all()
    current_highest = max([s.current_streak for s in streaks], default=0)
    
    return templates.TemplateResponse("activities/rewards.html" if os.path.exists("app/templates/activities/rewards.html") else "activities/index.html", {
        "request": request,
        "user": user,
        "earned_rewards": earned_rewards,
        "all_rewards": all_rewards,
        "current_streak": current_highest,
        "active_page": "activities"
    })
