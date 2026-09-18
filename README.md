# 🧠 Manas Mitra 2.0 

> **AI-Powered Mental Wellness & Habit-Building Platform**  
> Helping users navigate mental health challenges, build positive lifestyle habits, connect with interest communities, and access supportive AI consultation.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)](https://fastapi.tiangolo.com/)

---

## ✨ Features

- **🩺 Mental Health Assessment & Scoring:** Comprehensive onboarding survey with ML-driven wellness score calculation (0-100) and personalized risk evaluation.
- **🎮 Therapeutic Mind Games:** Cognitive behavioral therapy (CBT)-grounded interactive games including:
  - 🫧 **Breathing Bubble:** 4-7-8 and Box Breathing paced relaxation
  - 🧠 **Memory Flip:** Visual pattern and working memory exercise
  - 🧩 **Mind Puzzle:** Focus and cognitive engagement
  - ✨ **Gratitude Jar:** Daily positive affirmation and gratitude logging
  - 🎯 **Focus Matrix:** Attention training and distraction resistance
  - 🎈 **Bubble Wrap Pop:** Instant stress relief
  - 🔥 **Worry Destroyer:** Write and incinerate worries
  - 🪨 **Zen Rock Garden:** Meditative kinetic stone balance
- **🔥 Habit & Activity Streaks:** Personalized daily activities matched to user interests with streak tracking and milestones.
- **🎁 Rewards System:** Earn discount coupons, wellness vouchers, and tier badges as streaks grow.
- **👥 Interest Communities & Meetups:** Connect with like-minded individuals across Art, Music, Books, Yoga, Gaming, and attend local offline meetups.
- **🤖 Dr. Manas - AI Consultant:** Real-time conversational AI consultant powered by Google Gemini API with clinical CBT guidelines, empathetic active listening, and built-in crisis helpline safety triggers.
- **📊 Analytics & Mood Tracking:** Interactive charts showing wellness trends, mood fluctuations, sleep vs stress correlations, and activity consistency.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python 3.11+)
- **Database:** SQLite / PostgreSQL (SQLAlchemy ORM)
- **Frontend:** Jinja2 Templates, Tailwind CSS, Alpine.js, Chart.js
- **AI & ML:** Google Gemini 2.5 (`google-genai`), Scikit-learn, Pandas, NumPy
- **Authentication:** JWT with HttpOnly secure session cookies & PBKDF2 / BCrypt password hashing
- **Deployment:** Render (with Blueprint `render.yaml` and automatic database seeding)

---

## 🚀 Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/jayank1824/Manas-Mitra---AI-driven-Mental-Wellness-Platform.git
cd Manas-Mitra---AI-driven-Mental-Wellness-Platform
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and add your configuration:
```env
SECRET_KEY=your-random-secret-key
GEMINI_API_KEY=your-google-gemini-api-key
```

### 5. Seed initial data (optional, auto-seeded on startup)
```bash
python -m data.seed_data
```

### 6. Run the development server
```bash
uvicorn app.main:app --reload --port 8000
```
Open your browser at `http://localhost:8000`.

---

## 🌐 Deploying to Render

### Option A: 1-Click Blueprint Deploy (Recommended)
1. In [Render Dashboard](https://dashboard.render.com/), click **New +** -> **Blueprint**.
2. Select your `Manas-Mitra---AI-driven-Mental-Wellness-Platform` repository.
3. Render will automatically detect `render.yaml` and configure the web service.
4. Add your `GEMINI_API_KEY` under Environment Variables in the Render dashboard.
5. Click **Apply**!

### Option B: Manual Web Service Setup on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) -> **New +** -> **Web Service**.
2. Connect your GitHub repository `jayank1824/Manas-Mitra---AI-driven-Mental-Wellness-Platform`.
3. Configure the following settings:
   - **Name:** `manas-mitra`
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh` (or `pip install -r requirements.txt && python -m data.seed_data`)
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Under **Environment Variables**, add:
   - `PYTHON_VERSION`: `3.11.9`
   - `SECRET_KEY`: *(Generate a secure random string)*
   - `GEMINI_API_KEY`: *(Your Google Gemini API Key)*
5. Click **Create Web Service**.


---

## 🧪 Testing

Run the full end-to-end integration test suite:
```bash
python test_e2e.py
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
