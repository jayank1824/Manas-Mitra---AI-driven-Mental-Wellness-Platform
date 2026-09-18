import json
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services.auth_service import get_current_user_from_cookie
from app.services.ai_consultant import get_ai_response
from app.models.stats import ChatMessage

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class ChatPayload(BaseModel):
    message: str

@router.get("/", response_class=HTMLResponse)
async def consultant_chat_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user.id
    ).order_by(ChatMessage.created_at.asc()).limit(50).all()
    
    return templates.TemplateResponse("consultant/chat.html", {
        "request": request,
        "user": user,
        "messages": messages,
        "active_page": "consultant"
    })

@router.post("/send")
async def send_message(payload: ChatPayload, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
        
    user_msg_text = payload.message.strip()
    if not user_msg_text:
        return JSONResponse(status_code=400, content={"error": "Empty message"})
        
    # Save user message
    user_msg = ChatMessage(user_id=user.id, role="user", content=user_msg_text)
    db.add(user_msg)
    db.commit()
    
    # Get previous chat history
    history_records = db.query(ChatMessage).filter(
        ChatMessage.user_id == user.id
    ).order_by(ChatMessage.created_at.asc()).limit(20).all()
    
    chat_history = [{"role": m.role, "content": m.content} for m in history_records]
    
    # Build user context
    user_context = {
        "name": user.name,
        "wellness_score": user.profile.wellness_score if user.profile else 50,
        "risk_level": user.profile.risk_level if user.profile else "moderate",
        "interests": json.loads(user.profile.interests) if user.profile and user.profile.interests else []
    }
    
    # Get AI response
    ai_reply = await get_ai_response(user_msg_text, chat_history, user_context)
    
    # Save assistant message
    bot_msg = ChatMessage(user_id=user.id, role="assistant", content=ai_reply)
    db.add(bot_msg)
    db.commit()
    
    return {
        "status": "success",
        "response": ai_reply,
        "timestamp": bot_msg.created_at.strftime("%H:%M") if hasattr(bot_msg.created_at, "strftime") else ""
    }

@router.get("/history")
async def chat_history(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
        
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return [
        {"role": m.role, "content": m.content, "created_at": str(m.created_at)}
        for m in messages
    ]

@router.post("/clear")
async def clear_chat(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
        
    db.query(ChatMessage).filter(ChatMessage.user_id == user.id).delete()
    db.commit()
    return {"status": "cleared"}
