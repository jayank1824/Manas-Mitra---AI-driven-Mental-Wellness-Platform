import os
import uuid
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.services.auth_service import get_current_user_from_cookie
from app.models.user import User, UserProfile
from app.models.community import Community, CommunityMember, Post, Comment, Meetup, MeetupRSVP, PostLike, PeerConnection
from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def community_index(request: Request, q: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    memberships = db.query(CommunityMember).filter(CommunityMember.user_id == user.id).all()
    joined_ids = [m.community_id for m in memberships]
    
    # Query joined communities
    joined_query = db.query(Community).filter(Community.id.in_(joined_ids)) if joined_ids else None
    
    # Query discover communities
    discover_query = db.query(Community).filter(~Community.id.in_(joined_ids)) if joined_ids else db.query(Community)
    
    if q:
        search_filter = or_(
            Community.name.ilike(f"%{q}%"),
            Community.description.ilike(f"%{q}%"),
            Community.interest_category.ilike(f"%{q}%")
        )
        discover_query = discover_query.filter(search_filter)
        if joined_query:
            joined_query = joined_query.filter(search_filter)
            
    if category and category != "All":
        discover_query = discover_query.filter(Community.interest_category == category)
        if joined_query:
            joined_query = joined_query.filter(Community.interest_category == category)

    joined_communities = joined_query.all() if joined_query else []
    discover_communities = discover_query.all()
    
    # Peer Support Connectors (Available wellness buddies)
    peers = db.query(User).filter(User.id != user.id).limit(10).all()
    connected_peer_ids = [p.peer_id for p in db.query(PeerConnection).filter(PeerConnection.user_id == user.id, PeerConnection.status == "connected").all()]
    
    peer_connectors = []
    for p in peers:
        profile = db.query(UserProfile).filter(UserProfile.user_id == p.id).first()
        peer_connectors.append({
            "user": p,
            "profile": profile,
            "is_connected": p.id in connected_peer_ids
        })
    
    # Categories list for filter pills
    categories = ["All", "Anxiety & Stress", "Mindfulness & Meditation", "Art & Creative Therapy", "Fitness & Yoga", "Students & Academics", "General Support"]
    
    return templates.TemplateResponse("community/index.html", {
        "request": request,
        "user": user,
        "joined_communities": joined_communities,
        "discover_communities": discover_communities,
        "peer_connectors": peer_connectors,
        "categories": categories,
        "selected_q": q or "",
        "selected_category": category or "All",
        "active_page": "community"
    })

@router.post("/create")
async def create_community(
    request: Request,
    name: str = Form(...),
    interest_category: str = Form(...),
    description: str = Form(...),
    icon: str = Form("👥"),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    community = Community(
        name=name,
        interest_category=interest_category,
        description=description,
        icon=icon
    )
    db.add(community)
    db.commit()
    
    # Auto join creator as member
    member = CommunityMember(community_id=community.id, user_id=user.id)
    db.add(member)
    db.commit()
    
    return RedirectResponse(url=f"/community/{community.id}", status_code=303)

@router.get("/meetups", response_class=HTMLResponse)
async def meetups_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    meetups = db.query(Meetup).order_by(Meetup.date.asc()).all()
    user_rsvps = {r.meetup_id: r.status for r in db.query(MeetupRSVP).filter(MeetupRSVP.user_id == user.id).all()}
    communities = db.query(Community).all()
    
    return templates.TemplateResponse("community/meetups.html", {
        "request": request,
        "user": user,
        "meetups": meetups,
        "user_rsvps": user_rsvps,
        "communities": communities,
        "active_page": "community"
    })

@router.post("/meetups/create")
async def create_meetup(
    request: Request,
    community_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    location: str = Form(...),
    max_participants: int = Form(20),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    meetup = Meetup(
        community_id=community_id,
        title=title,
        description=description,
        date=date,
        time=time,
        location=location,
        max_participants=max_participants
    )
    db.add(meetup)
    db.commit()
    
    # Auto RSVP creator
    rsvp = MeetupRSVP(meetup_id=meetup.id, user_id=user.id, status="going")
    db.add(rsvp)
    db.commit()
    
    return RedirectResponse(url="/community/meetups", status_code=303)

@router.get("/{community_id}", response_class=HTMLResponse)
async def community_group(community_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    community = db.query(Community).filter(Community.id == community_id).first()
    if not community:
        return RedirectResponse(url="/community", status_code=303)
        
    is_member = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.user_id == user.id
    ).first() is not None
    
    # Get members list
    members = db.query(User).join(CommunityMember, User.id == CommunityMember.user_id).filter(CommunityMember.community_id == community_id).all()
    
    posts = db.query(Post).filter(Post.community_id == community_id).order_by(Post.created_at.desc()).all()
    meetups = db.query(Meetup).filter(Meetup.community_id == community_id).order_by(Meetup.date.asc()).all()
    
    # User's liked post IDs
    user_liked_post_ids = set(p.post_id for p in db.query(PostLike).filter(PostLike.user_id == user.id).all())
    
    return templates.TemplateResponse("community/group.html", {
        "request": request,
        "user": user,
        "community": community,
        "is_member": is_member,
        "members": members,
        "posts": posts,
        "meetups": meetups,
        "user_liked_post_ids": user_liked_post_ids,
        "active_page": "community"
    })

@router.post("/{community_id}/join")
async def join_community(community_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    existing = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.user_id == user.id
    ).first()
    
    if not existing:
        member = CommunityMember(community_id=community_id, user_id=user.id)
        db.add(member)
        db.commit()
        
    return RedirectResponse(url=f"/community/{community_id}", status_code=303)

@router.post("/{community_id}/leave")
async def leave_community(community_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    existing = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.user_id == user.id
    ).first()
    
    if existing:
        db.delete(existing)
        db.commit()
        
    return RedirectResponse(url="/community", status_code=303)

@router.post("/{community_id}/post")
async def create_post(
    community_id: int,
    request: Request,
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    image_path = None
    if image and image.filename:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        ext = os.path.splitext(image.filename)[1].lower() or ".jpg"
        filename = f"post_{user.id}_{uuid.uuid4().hex[:8]}{ext}"
        save_path = os.path.join(settings.UPLOAD_DIR, filename)
        with open(save_path, "wb") as f:
            f.write(await image.read())
        image_path = f"/static/uploads/{filename}"
        
    post = Post(
        community_id=community_id,
        user_id=user.id,
        content=content,
        image_path=image_path
    )
    db.add(post)
    db.commit()
    
    return RedirectResponse(url=f"/community/{community_id}", status_code=303)

@router.post("/{community_id}/posts/{post_id}/like")
async def like_post(community_id: int, post_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    existing = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == user.id).first()
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if existing:
        db.delete(existing)
        if post and post.likes_count > 0:
            post.likes_count -= 1
    else:
        like = PostLike(post_id=post_id, user_id=user.id)
        db.add(like)
        if post:
            post.likes_count += 1
            
    db.commit()
    return RedirectResponse(url=f"/community/{community_id}", status_code=303)

@router.post("/{community_id}/comment")
async def add_comment(
    community_id: int,
    request: Request,
    post_id: int = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    comment = Comment(
        post_id=post_id,
        user_id=user.id,
        content=content
    )
    db.add(comment)
    db.commit()
    
    return RedirectResponse(url=f"/community/{community_id}", status_code=303)

@router.post("/peers/{peer_id}/connect")
async def connect_peer(peer_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    existing = db.query(PeerConnection).filter(PeerConnection.user_id == user.id, PeerConnection.peer_id == peer_id).first()
    if not existing:
        conn = PeerConnection(user_id=user.id, peer_id=peer_id, status="connected")
        db.add(conn)
        db.commit()
        
    return RedirectResponse(url="/community", status_code=303)

@router.post("/peers/{peer_id}/disconnect")
async def disconnect_peer(peer_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    existing = db.query(PeerConnection).filter(PeerConnection.user_id == user.id, PeerConnection.peer_id == peer_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        
    return RedirectResponse(url="/community", status_code=303)

@router.post("/meetups/{meetup_id}/rsvp")
async def rsvp_meetup(
    meetup_id: int,
    request: Request,
    status: str = Form("going"),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    rsvp = db.query(MeetupRSVP).filter(
        MeetupRSVP.meetup_id == meetup_id,
        MeetupRSVP.user_id == user.id
    ).first()
    
    if rsvp:
        rsvp.status = status
    else:
        rsvp = MeetupRSVP(meetup_id=meetup_id, user_id=user.id, status=status)
        db.add(rsvp)
        
    db.commit()
    return RedirectResponse(url="/community/meetups", status_code=303)
