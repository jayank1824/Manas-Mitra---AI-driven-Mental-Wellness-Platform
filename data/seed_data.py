import os
import json
from app.database import SessionLocal, engine, Base
from app.models.survey import SurveyQuestion
from app.models.activity import Activity, Reward
from app.models.community import Community, Meetup
from app.models.user import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Seed Survey Questions
        if db.query(SurveyQuestion).count() == 0:
            logger.info("Seeding Survey Questions...")
            questions = [
                {
                    "text": "What mental health challenges are you currently facing?",
                    "options": ["Anxiety", "Depression", "Loneliness", "Overthinking", "Stress", "Insomnia", "Panic Attacks", "Cluster Headache", "Migraine", "Low Self-Esteem", "Anger Issues", "Social Anxiety"],
                    "category": "mental_health"
                },
                {
                    "text": "How would you rate your current stress level on a daily basis?",
                    "options": ["Very Low - I feel calm most days", "Low - Occasional minor stress", "Moderate - Regular but manageable stress", "High - Frequent overwhelming stress", "Very High - Constant severe stress"],
                    "category": "mental_health"
                },
                {
                    "text": "Do you have any diagnosed medical conditions?",
                    "options": ["None", "Hypertension", "Diabetes", "Thyroid Disorder", "Heart Condition", "Chronic Pain", "Neurological Disorder", "Autoimmune Disease", "Respiratory Issues"],
                    "category": "medical"
                },
                {
                    "text": "How is your sleep quality?",
                    "options": ["Excellent - 7-9 hours of restful sleep", "Good - Usually sleep well", "Fair - Sometimes struggle to sleep", "Poor - Frequently disturbed sleep", "Very Poor - Chronic insomnia or severe issues"],
                    "category": "lifestyle"
                },
                {
                    "text": "How would you describe your social life?",
                    "options": ["Very Active - Large friend circle, frequent socializing", "Active - Regular social interactions", "Moderate - Some friends, occasional meetups", "Limited - Few close friends, rare outings", "Isolated - Minimal social contact", "Prefer being alone"],
                    "category": "lifestyle"
                },
                {
                    "text": "What activities do you enjoy in your free time?",
                    "options": ["Painting / Drawing", "Music (Singing/Instrument)", "Dance", "Reading / Writing", "Cooking / Baking", "Gaming", "Photography", "Gardening", "Yoga / Meditation", "Sports / Exercise", "Crafts / DIY", "Watching Movies/Series"],
                    "category": "interests"
                },
                {
                    "text": "What are the primary causes of your stress or anxiety?",
                    "options": ["Work/Career Pressure", "Academic Stress", "Financial Worries", "Relationship Issues", "Family Problems", "Health Concerns", "Social Media Pressure", "Loneliness", "Future Uncertainty", "Past Trauma", "Lack of Purpose"],
                    "category": "mental_health"
                },
                {
                    "text": "Have you had any recent surgeries or medical procedures?",
                    "options": ["No recent procedures", "Minor surgery (last 6 months)", "Major surgery (last 12 months)", "Ongoing treatment/therapy", "Dental procedure", "Eye surgery", "Orthopedic procedure"],
                    "category": "medical"
                },
                {
                    "text": "How often do you exercise or engage in physical activity?",
                    "options": ["Daily (30+ minutes)", "4-5 times a week", "2-3 times a week", "Once a week", "Rarely", "Never"],
                    "category": "lifestyle"
                },
                {
                    "text": "What kind of support would help you most right now?",
                    "options": ["Professional therapy/counseling", "Peer support community", "Guided meditation & mindfulness", "Creative expression outlets", "Physical activities & exercises", "AI-powered mental health guidance", "Stress management techniques", "Social connection & meetups"],
                    "category": "support"
                }
            ]
            
            for i, q in enumerate(questions):
                db.add(SurveyQuestion(
                    question_text=q["text"],
                    options=json.dumps(q["options"]),
                    category=q["category"],
                    order_num=i + 1
                ))
            db.commit()

        # 2. Seed Activities
        if db.query(Activity).count() == 0:
            logger.info("Seeding Activities...")
            activities = [
                {"name": "Daily Sketch Challenge", "category": "Painting / Drawing", "desc": "Spend 15 mins sketching anything.", "icon": "🎨"},
                {"name": "Color Therapy Session", "category": "Painting / Drawing", "desc": "Coloring for relaxation.", "icon": "🖍️"},
                {"name": "Nature Drawing", "category": "Painting / Drawing", "desc": "Draw something from nature.", "icon": "🌿"},
                
                {"name": "Learn a New Song", "category": "Music", "desc": "Learn the lyrics or chords to a new song.", "icon": "🎵"},
                {"name": "Jam Session Practice", "category": "Music", "desc": "Practice an instrument for 30 mins.", "icon": "🎸"},
                
                {"name": "Freestyle Dance", "category": "Dance", "desc": "Put on a playlist and dance freely.", "icon": "💃"},
                {"name": "Learn a Choreography", "category": "Dance", "desc": "Follow a dance tutorial.", "icon": "🕺"},
                
                {"name": "Read 10 Pages", "category": "Reading", "desc": "Read at least 10 pages of a book.", "icon": "📚"},
                {"name": "Journaling", "category": "Writing", "desc": "Write down your thoughts for the day.", "icon": "✍️"},
                
                {"name": "Try a New Recipe", "category": "Cooking", "desc": "Cook something you've never made before.", "icon": "🍳"},
                
                {"name": "Puzzle Solving", "category": "Gaming", "desc": "Solve Sudoku, crosswords, or digital puzzles.", "icon": "🧩"},
                
                {"name": "Photo Walk", "category": "Photography", "desc": "Take a 20 min walk and snap 5 photos.", "icon": "📷"},
                
                {"name": "Water Plants", "category": "Gardening", "desc": "Tend to your indoor or outdoor plants.", "icon": "🪴"},
                
                {"name": "15 Min Yoga Flow", "category": "Yoga", "desc": "Follow a short yoga routine.", "icon": "🧘"},
                {"name": "Guided Meditation", "category": "Yoga", "desc": "Meditate for 10 minutes.", "icon": "🪷"}
            ]
            for act in activities:
                db.add(Activity(
                    name=act["name"],
                    category=act.get("category", "General"),
                    description=act.get("desc", ""),
                    icon=act.get("icon", "🎯"),
                    duration_minutes=30
                ))
            db.commit()

        # 3. Seed Rewards
        if db.query(Reward).count() == 0:
            logger.info("Seeding Rewards...")
            rewards = [
                {"name": "☕ Café Delight Coupon", "desc": "10% off at partner cafés", "tier": 1, "days": 3, "prefix": "MANAS-CAFE"},
                {"name": "🎬 Movie Night Voucher", "desc": "Free movie ticket at partner cinemas", "tier": 2, "days": 7, "prefix": "MANAS-MOVIE"},
                {"name": "🛍️ Shopping Spree", "desc": "15% off at partner retail stores", "tier": 3, "days": 14, "prefix": "MANAS-SHOP"},
                {"name": "✈️ Travel Explorer", "desc": "20% off on partner travel bookings", "tier": 4, "days": 21, "prefix": "MANAS-TRAVEL"},
                {"name": "🏆 Premium Wellness Bundle", "desc": "Restaurant + Spa + Concert combo", "tier": 5, "days": 30, "prefix": "MANAS-PREMIUM"},
                {"name": "📱 Tech Treat", "desc": "Gadget accessory voucher worth ₹1000", "tier": 6, "days": 45, "prefix": "MANAS-TECH"},
                {"name": "🎉 Grand Getaway", "desc": "Weekend getaway voucher", "tier": 7, "days": 60, "prefix": "MANAS-GETAWAY"},
                {"name": "💎 Diamond Wellness", "desc": "All rewards unlocked + exclusive membership", "tier": 8, "days": 90, "prefix": "MANAS-DIAMOND"}
            ]
            for r in rewards:
                db.add(Reward(
                    name=r["name"],
                    description=r["desc"],
                    tier=r["tier"],
                    min_streak_days=r["days"],
                    coupon_prefix=r["prefix"],
                    icon=r["name"].split()[0]
                ))
            db.commit()

        # 4. Seed Communities
        if db.query(Community).count() == 0:
            logger.info("Seeding Communities...")
            communities = [
                {"name": "Art Circle", "cat": "Painting / Drawing", "icon": "🎨", "desc": "Share your art and find inspiration."},
                {"name": "Music Lovers", "cat": "Music", "icon": "🎵", "desc": "Discuss songs, artists, and play instruments together."},
                {"name": "Dance Crew", "cat": "Dance", "icon": "💃", "desc": "For those who love to move to the beat."},
                {"name": "Book Club", "cat": "Reading", "icon": "📚", "desc": "Monthly reads and discussions."},
                {"name": "Cooking Club", "cat": "Cooking", "icon": "🍳", "desc": "Share recipes and cooking tips."},
                {"name": "Gamers Hub", "cat": "Gaming", "icon": "🎮", "desc": "Find teammates and discuss games."},
                {"name": "Photography Club", "cat": "Photography", "icon": "📷", "desc": "Share your captures and techniques."},
                {"name": "Garden Friends", "cat": "Gardening", "icon": "🪴", "desc": "Plant care tips and harvests."},
                {"name": "Yoga & Wellness", "cat": "Yoga", "icon": "🧘", "desc": "Mindfulness, meditation, and yoga practice."},
                {"name": "Writers Corner", "cat": "Writing", "icon": "✍️", "desc": "Share stories, poems, and journaling ideas."}
            ]
            for c in communities:
                db.add(Community(
                    name=c["name"],
                    interest_category=c["cat"],
                    description=c["desc"],
                    icon=c["icon"]
                ))
            db.commit()

        logger.info("Database seeded successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
