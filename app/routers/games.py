from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services.auth_service import get_current_user_from_cookie
from app.models.stats import GameScore

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class ScorePayload(BaseModel):
    game_type: str
    score: int
    duration_seconds: int = 0

@router.get("/", response_class=HTMLResponse)
async def games_index(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    recent_scores = db.query(GameScore).filter(
        GameScore.user_id == user.id
    ).order_by(GameScore.played_at.desc()).limit(10).all()
    
    return templates.TemplateResponse("games/index.html", {
        "request": request,
        "user": user,
        "recent_scores": recent_scores,
        "active_page": "games"
    })

@router.get("/breathing", response_class=HTMLResponse)
async def game_breathing(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("games/breathing.html", {"request": request, "user": user, "active_page": "games"})

@router.get("/memory", response_class=HTMLResponse)
async def game_memory(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("games/memory.html", {"request": request, "user": user, "active_page": "games"})

@router.get("/puzzle", response_class=HTMLResponse)
async def game_puzzle(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("games/puzzle.html", {"request": request, "user": user, "active_page": "games"})

@router.get("/gratitude", response_class=HTMLResponse)
async def game_gratitude(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("games/gratitude.html", {"request": request, "user": user, "active_page": "games"})

@router.get("/focus", response_class=HTMLResponse)
async def game_focus(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("games/focus.html", {"request": request, "user": user, "active_page": "games"})

@router.get("/bubble-wrap", response_class=HTMLResponse)
async def game_bubble_wrap(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("games/bubble_wrap.html", {"request": request, "user": user, "active_page": "games"})

@router.get("/worry-destroyer", response_class=HTMLResponse)
async def game_worry_destroyer(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("games/worry_destroyer.html", {"request": request, "user": user, "active_page": "games"})

@router.get("/zen-garden", response_class=HTMLResponse)
async def game_zen_garden(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("games/zen_garden.html", {"request": request, "user": user, "active_page": "games"})


@router.post("/save-score")
async def save_score(request: Request, payload: ScorePayload, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
        
    game_score = GameScore(
        user_id=user.id,
        game_type=payload.game_type,
        score=payload.score,
        duration_seconds=payload.duration_seconds
    )
    db.add(game_score)
    db.commit()
    
    return {"status": "success", "score_id": game_score.id}
