import json
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import get_current_user_from_cookie
from app.services.analytics_service import (
    get_wellness_trend, get_mood_trend, get_activity_stats,
    get_game_stats, get_community_engagement, get_sleep_stress_correlation,
    get_overall_summary
)
from app.ml.trend_predictor import predict_wellness_trend, generate_insights
from app.models.stats import DailyLog

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def stats_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    summary = get_overall_summary(db, user.id)
    wellness_data = get_wellness_trend(db, user.id)
    mood_data = get_mood_trend(db, user.id)
    activity_data = get_activity_stats(db, user.id)
    game_data = get_game_stats(db, user.id)
    community_data = get_community_engagement(db, user.id)
    correlation_data = get_sleep_stress_correlation(db, user.id)
    
    prediction = predict_wellness_trend(db, user.id)
    insights = generate_insights(db, user.id)
    
    return templates.TemplateResponse("stats/dashboard.html", {
        "request": request,
        "user": user,
        "summary": summary,
        "wellness_data": json.dumps(wellness_data),
        "mood_data": json.dumps(mood_data),
        "activity_data": json.dumps(activity_data),
        "game_data": json.dumps(game_data),
        "community_data": json.dumps(community_data),
        "correlation_data": json.dumps(correlation_data),
        "prediction": prediction,
        "insights": insights,
        "active_page": "stats"
    })

@router.get("/log", response_class=HTMLResponse)
async def daily_log_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    recent_logs = db.query(DailyLog).filter(
        DailyLog.user_id == user.id
    ).order_by(DailyLog.date.desc()).limit(7).all()
    
    return templates.TemplateResponse("stats/log.html", {
        "request": request,
        "user": user,
        "recent_logs": recent_logs,
        "active_page": "log"
    })

@router.post("/log")
async def save_daily_log(
    request: Request,
    mood_score: int = Form(5),
    stress_level: int = Form(5),
    sleep_hours: float = Form(7.0),
    energy_level: int = Form(5),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Check if entry already exists for today
    existing = db.query(DailyLog).filter(
        DailyLog.user_id == user.id,
        DailyLog.date == today_str
    ).first()
    
    if existing:
        existing.mood_score = mood_score
        existing.stress_level = stress_level
        existing.sleep_hours = sleep_hours
        existing.energy_level = energy_level
        existing.notes = notes
    else:
        log = DailyLog(
            user_id=user.id,
            date=today_str,
            mood_score=mood_score,
            stress_level=stress_level,
            sleep_hours=sleep_hours,
            energy_level=energy_level,
            notes=notes
        )
        db.add(log)
        
    db.commit()
    return RedirectResponse(url="/stats", status_code=303)

@router.get("/api/wellness")
async def api_wellness(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return get_wellness_trend(db, user.id)

@router.get("/api/mood")
async def api_mood(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return get_mood_trend(db, user.id)

@router.get("/api/activities")
async def api_activities(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return get_activity_stats(db, user.id)

@router.get("/api/games")
async def api_games(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return get_game_stats(db, user.id)

@router.get("/api/community")
async def api_community(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return get_community_engagement(db, user.id)

@router.get("/api/correlation")
async def api_correlation(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return get_sleep_stress_correlation(db, user.id)
