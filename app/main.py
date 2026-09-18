from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.database import engine, Base
from app.models import *  # Import all models to create tables
import os

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Manas Mitra", description="AI-Powered Mental Wellness Platform")

# Mount static files
os.makedirs("app/static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
from app.routers import auth, survey, games, activities, community, consultant, stats
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(survey.router, prefix="/survey", tags=["Survey"])
app.include_router(games.router, prefix="/games", tags=["Games"])
app.include_router(activities.router, prefix="/activities", tags=["Activities"])
app.include_router(community.router, prefix="/community", tags=["Community"])
app.include_router(consultant.router, prefix="/consultant", tags=["Consultant"])
app.include_router(stats.router, prefix="/stats", tags=["Stats"])

@app.on_event("startup")
async def startup_event():
    try:
        from data.seed_data import seed
        seed()
    except Exception as e:
        print(f"Startup seeding notice: {e}")


@app.get("/")
async def root():
    return RedirectResponse(url="/auth/login")

@app.get("/dashboard")
async def dashboard(request: Request):
    # Get user from cookie
    from app.services.auth_service import get_current_user_from_cookie
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        user = get_current_user_from_cookie(request, db)
        if not user:
            return RedirectResponse(url="/auth/login")
        if user.profile and not user.profile.survey_completed:
            return RedirectResponse(url="/survey/onboarding")
        
        # Get dashboard data
        from app.models.stats import MentalHealthScore, GameScore, DailyLog
        from app.models.activity import UserStreak
        
        latest_score = db.query(MentalHealthScore).filter(
            MentalHealthScore.user_id == user.id
        ).order_by(MentalHealthScore.calculated_at.desc()).first()
        
        active_streaks = db.query(UserStreak).filter(
            UserStreak.user_id == user.id,
            UserStreak.current_streak > 0
        ).all()
        
        recent_games = db.query(GameScore).filter(
            GameScore.user_id == user.id
        ).order_by(GameScore.played_at.desc()).limit(5).all()
        
        recent_logs = db.query(DailyLog).filter(
            DailyLog.user_id == user.id
        ).order_by(DailyLog.date.desc()).limit(7).all()
        
        import json
        interests = json.loads(user.profile.interests) if user.profile else []
        
        return templates.TemplateResponse("dashboard/index.html", {
            "request": request,
            "user": user,
            "wellness_score": latest_score.score if latest_score else (user.profile.wellness_score if user.profile else 50),
            "risk_level": latest_score.risk_level if latest_score else (user.profile.risk_level if user.profile else "unknown"),
            "active_streaks": active_streaks,
            "recent_games": recent_games,
            "recent_logs": recent_logs,
            "interests": interests,
            "active_page": "dashboard"
        })
    finally:
        db.close()
