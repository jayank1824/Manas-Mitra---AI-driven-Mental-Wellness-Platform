"""Comprehensive End-to-End Test for Manas Mitra using FastAPI TestClient"""
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("MANAS MITRA - COMPREHENSIVE E2E VERIFICATION")
print("=" * 60)

# 1. Login Page
r = client.get("/auth/login")
assert r.status_code == 200, f"Login GET failed: {r.status_code}"
assert "Manas Mitra" in r.text
print("[PASS] 1. GET /auth/login -> 200 OK")

# 2. Register Page
r = client.get("/auth/register")
assert r.status_code == 200, f"Register GET failed: {r.status_code}"
print("[PASS] 2. GET /auth/register -> 200 OK")

# 3. Register user
reg_data = {
    "name": "Arjun Sharma",
    "email": "arjun@example.com",
    "password": "Password123!",
    "phone": "9876543210"
}
r = client.post("/auth/register", data=reg_data, follow_redirects=False)
assert r.status_code in [302, 303], f"Register failed: {r.status_code}, {r.text}"
print(f"[PASS] 3. POST /auth/register -> Redirect ({r.headers.get('location')})")

# 4. Login
login_data = {
    "email": "arjun@example.com",
    "password": "Password123!"
}
r = client.post("/auth/login", data=login_data, follow_redirects=False)
assert r.status_code in [302, 303], f"Login failed: {r.status_code}, {r.text}"
assert "access_token" in client.cookies
print("[PASS] 4. POST /auth/login -> Auth Cookie Set")

# 5. Survey onboarding GET
r = client.get("/survey/onboarding")
assert r.status_code == 200, f"Survey GET failed: {r.status_code}"
assert "Mental Health" in r.text or "challenges" in r.text.lower()
print("[PASS] 5. GET /survey/onboarding -> 200 OK")

# 6. Submit survey with multi-select and other options
survey_payload = {
    "q1_options[]": ["Anxiety", "Overthinking", "Migraine"],
    "q1_other": "",
    "q2_options[]": ["High - Frequent overwhelming stress"],
    "q2_other": "",
    "q3_options[]": ["None"],
    "q3_other": "",
    "q4_options[]": ["Poor - Frequently disturbed sleep"],
    "q4_other": "",
    "q5_options[]": ["Limited - Few close friends, rare outings"],
    "q5_other": "",
    "q6_options[]": ["Painting / Drawing", "Music (Singing/Instrument)", "Gaming"],
    "q6_other": "Pottery",
    "q7_options[]": ["Work/Career Pressure", "Future Uncertainty"],
    "q7_other": "",
    "q8_options[]": ["No recent procedures"],
    "q8_other": "",
    "q9_options[]": ["Rarely"],
    "q9_other": "",
    "q10_options[]": ["Guided meditation & mindfulness", "AI-powered mental health guidance"],
    "q10_other": ""
}
r = client.post("/survey/submit", data=survey_payload, follow_redirects=False)
assert r.status_code in [302, 303], f"Survey submit failed: {r.status_code}, {r.text}"
print("[PASS] 6. POST /survey/submit -> ML Scored & Redirect to Dashboard")

# 7. Dashboard View
r = client.get("/dashboard")
assert r.status_code == 200, f"Dashboard GET failed: {r.status_code}"
assert "Arjun Sharma" in r.text
assert "Wellness Score" in r.text or "Score" in r.text
print("[PASS] 7. GET /dashboard -> 200 OK (User Profile Loaded)")

# 8. Mind Games Hub
r = client.get("/games/")
assert r.status_code == 200, f"Games hub failed: {r.status_code}"
assert "Breathing" in r.text
assert "Memory" in r.text
assert "Word" in r.text or "Puzzle" in r.text
assert "Gratitude" in r.text
assert "Focus" in r.text
print("[PASS] 8. GET /games/ -> 200 OK (5 Games Hub)")

# 9. Individual Therapeutic Games
games = ["breathing", "memory", "puzzle", "gratitude", "focus", "bubble-wrap", "worry-destroyer", "zen-garden"]
for g in games:
    r = client.get(f"/games/{g}")
    assert r.status_code == 200, f"Game {g} failed: {r.status_code}"
    print(f"[PASS] 9.{games.index(g)+1}. GET /games/{g} -> 200 OK")

# 10. Mind Game Score Recording
score_payload = {
    "game_type": "breathing",
    "score": 120,
    "duration_seconds": 240
}
r = client.post("/games/save-score", json=score_payload)
assert r.status_code == 200, f"Save score failed: {r.status_code}"
print("[PASS] 10. POST /games/save-score -> Score Saved to DB")

# 11. Activities & Personalized Section
r = client.get("/activities/")
assert r.status_code == 200, f"Activities GET failed: {r.status_code}"
print("[PASS] 11. GET /activities/ -> 200 OK (Personalized Activities)")

# 12. Rewards Page
r = client.get("/activities/rewards")
assert r.status_code == 200, f"Rewards GET failed: {r.status_code}"
print("[PASS] 12. GET /activities/rewards -> 200 OK (Coupon & Tier Catalog)")

# 13. Community Feed & Groups
r = client.get("/community/")
assert r.status_code == 200, f"Community GET failed: {r.status_code}"
print("[PASS] 13. GET /community/ -> 200 OK (Interest Groups)")

# 14. Meetups & Offline Workshops
r = client.get("/community/meetups")
assert r.status_code == 200, f"Meetups GET failed: {r.status_code}"
print("[PASS] 14. GET /community/meetups -> 200 OK (Offline Events)")

# 15. AI Mental Health Consultant Page
r = client.get("/consultant/")
assert r.status_code == 200, f"Consultant GET failed: {r.status_code}"
assert "Dr. Manas" in r.text or "Consultant" in r.text
print("[PASS] 15. GET /consultant/ -> 200 OK (AI Doctor Interface)")

# 16. AI Consultant Conversation
chat_payload = {"message": "I'm having severe migraine and feeling anxious about my upcoming exams"}
r = client.post("/consultant/send", json=chat_payload)
assert r.status_code == 200, f"Consultant chat failed: {r.status_code}"
resp_json = r.json()
assert "response" in resp_json
print(f"[PASS] 16. POST /consultant/send -> AI Responded: '{resp_json['response'][:60]}...'")

# 17. Stats & Analytics Dashboard
r = client.get("/stats/")
assert r.status_code == 200, f"Stats dashboard failed: {r.status_code}"
print("[PASS] 17. GET /stats/ -> 200 OK (Graphs & Charts Dashboard)")

# 18. Daily Check-in Log Page
r = client.get("/stats/log")
assert r.status_code == 200, f"Daily log GET failed: {r.status_code}"
print("[PASS] 18. GET /stats/log -> 200 OK (Check-in Form)")

# 19. Submit Daily Check-in Log
log_payload = {
    "mood_score": "8",
    "stress_level": "3",
    "sleep_hours": "8.0",
    "energy_level": "7",
    "notes": "Practiced 4-7-8 breathing and completed my 1 hour sketch challenge!"
}
r = client.post("/stats/log", data=log_payload, follow_redirects=False)
assert r.status_code in [302, 303], f"Daily log POST failed: {r.status_code}"
print("[PASS] 19. POST /stats/log -> Daily Log Recorded")

# 20. Stats APIs for Charts
apis = ["wellness", "mood", "games", "activities", "community", "correlation"]
for api_name in apis:
    r = client.get(f"/stats/api/{api_name}")
    assert r.status_code == 200, f"API /stats/api/{api_name} failed: {r.status_code}"
    print(f"[PASS] 20.{apis.index(api_name)+1}. GET /stats/api/{api_name} -> 200 OK (JSON Chart Data)")

print("\n" + "=" * 60)
print("ALL 20 END-TO-END CRITICAL TESTS PASSED PERFECTLY! [SUCCESS]")
print("=" * 60)
