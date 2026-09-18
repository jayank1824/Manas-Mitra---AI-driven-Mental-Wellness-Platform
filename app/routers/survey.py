from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json
from app.database import get_db
from app.services.auth_service import get_current_user_from_cookie
from app.models.survey import SurveyResponse
from app.models.user import UserProfile
from app.models.activity import UserStreak, Activity
from app.models.community import Community, CommunityMember
from app.models.stats import MentalHealthScore
from app.ml.mental_health_scorer import calculate_wellness_score

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/onboarding", response_class=HTMLResponse)
async def onboarding_get(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    return templates.TemplateResponse("survey/onboarding.html", {
        "request": request,
        "user": user,
        "hide_sidebar": True
    })

@router.post("/submit")
async def onboarding_post(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    form_data = await request.form()
    
    responses = []
    interests = []
    
    for i in range(1, 11):
        q_options = form_data.getlist(f"q{i}_options[]")
        q_other = form_data.get(f"q{i}_other", "")
        
        selected = [opt for opt in q_options if opt]
        
        responses.append({
            "question_id": i,
            "selected_options": selected,
            "other_text": q_other or ""
        })
        
        if i == 6:
            interests = list(selected)
            if q_other:
                interests.append(q_other)
                
        # Save to db
        db_response = SurveyResponse(
            user_id=user.id,
            question_id=i,
            selected_options=json.dumps(selected),
            other_text=q_other or ""
        )
        db.add(db_response)
        
    score, risk_level, factors = calculate_wellness_score(responses)
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if profile:
        profile.wellness_score = score
        profile.risk_level = risk_level
        profile.survey_completed = True
        profile.interests = json.dumps(interests)
    
    # Save initial mental health score log
    mh_score = MentalHealthScore(
        user_id=user.id,
        score=score,
        risk_level=risk_level,
        factors=json.dumps(factors)
    )
    db.add(mh_score)
    
    # Auto-join relevant communities based on interests
    interest_category_map = {
        "Painting / Drawing": "painting", "Painting/Drawing": "painting",
        "Music (Singing/Instrument)": "music", "Music": "music",
        "Dance": "dance",
        "Reading / Writing": "reading", "Reading/Writing": "reading",
        "Cooking / Baking": "cooking", "Cooking/Baking": "cooking",
        "Gaming": "gaming",
        "Photography": "photography",
        "Gardening": "gardening",
        "Yoga / Meditation": "yoga", "Yoga/Meditation": "yoga",
        "Sports / Exercise": "sports", "Sports/Exercise": "sports",
        "Crafts / DIY": "crafts", "Crafts/DIY": "crafts",
        "Watching Movies/Series": "movies",
    }
    
    for interest in interests:
        category = interest_category_map.get(interest, interest.lower().split("/")[0].split("(")[0].strip())
        
        # Join matching community
        community = db.query(Community).filter(
            Community.interest_category == category
        ).first()
        if community:
            existing = db.query(CommunityMember).filter(
                CommunityMember.community_id == community.id,
                CommunityMember.user_id == user.id
            ).first()
            if not existing:
                member = CommunityMember(community_id=community.id, user_id=user.id)
                db.add(member)
        
        # Create streaks for matching activities
        activities = db.query(Activity).filter(
            Activity.category == category
        ).all()
        for activity in activities:
            existing_streak = db.query(UserStreak).filter(
                UserStreak.user_id == user.id,
                UserStreak.activity_id == activity.id
            ).first()
            if not existing_streak:
                streak = UserStreak(user_id=user.id, activity_id=activity.id)
                db.add(streak)
    
    db.commit()
    
    return RedirectResponse(url="/dashboard", status_code=303)
