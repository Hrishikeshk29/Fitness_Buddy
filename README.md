# 💪 Fitness Buddy — Agentic AI Powered Health & Fitness Coach

> **Built with IBM Granite on watsonx.ai** · Flask · SQLite · Bootstrap 5 · Chart.js

Fitness Buddy is a **production-ready agentic AI web application** that acts as your personal virtual fitness coach. It uses a **multi-agent architecture** powered by **IBM Granite models** to deliver personalised workout plans, Indian meal recommendations, habit coaching, and progress tracking through a beautiful conversational interface.

---

## 🚀 Live Demo Features

| Feature | Description |
|---|---|
| 🤖 **7 AI Agents** | Orchestrator, Profile, Workout, Nutrition, Motivation, Habit, Progress |
| 💬 **ChatGPT-Style UI** | Real-time streaming chat with agent reasoning display |
| 📊 **Analytics Dashboard** | Weight trends, workout frequency, habit charts |
| 🥗 **Indian Meal Plans** | Vegetarian/Non-veg with calorie estimates |
| 👨‍👩‍👧 **Family Profiles** | Track fitness for your entire family |
| 🌙 **Dark Mode** | Full dark/light mode toggle |
| 📱 **Mobile Responsive** | Works perfectly on all devices |

---

## 🏗️ Architecture

```
fitness_buddy/
├── app.py                          # Flask application factory
├── config.py                       # Config + AGENT_INSTRUCTIONS
├── requirements.txt
├── .env.example                    # Environment variable template
│
├── agents/
│   ├── orchestrator_agent.py       # Routes requests to specialist agents
│   ├── user_profile_agent.py       # BMI, fitness profile analysis
│   ├── workout_planning_agent.py   # Personalised workout plans
│   ├── nutrition_agent.py          # Indian meal recommendations
│   ├── motivation_agent.py         # Daily motivation & accountability
│   ├── habit_tracking_agent.py     # Water, sleep, streak coaching
│   └── progress_evaluation_agent.py# Progress analysis & adaptation
│
├── models/
│   └── models.py                   # SQLAlchemy ORM models
│
├── routes/
│   ├── auth_routes.py              # Login / Register
│   ├── main_routes.py              # Dashboard, profile, logging
│   └── chat_routes.py              # AI chat API endpoints
│
├── services/
│   └── watsonx_service.py          # IBM watsonx.ai SDK wrapper
│
├── templates/
│   ├── base.html                   # Shared layout with navbar
│   ├── index.html                  # Landing page
│   ├── auth/                       # Login & Register
│   ├── dashboard/                  # Dashboard & Analytics
│   ├── chat/                       # AI Coach chat interface
│   └── profile/                    # Setup, Edit, Family profiles
│
└── static/
    ├── css/style.css               # Premium SaaS styling
    └── js/
        ├── app.js                  # Dark mode, global utilities
        ├── chat.js                 # Chat interface logic
        ├── dashboard.js            # Weight chart
        └── analytics.js            # All analytics charts
```

---

## ⚙️ Quick Start (Local Setup)

### 1. Clone and Set Up

```bash
git clone <your-repo-url>
cd fitness_buddy
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and fill in your IBM Cloud credentials:

```env
IBM_API_KEY=your_ibm_cloud_api_key_here
IBM_PROJECT_ID=your_watsonx_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=your-super-secret-key-here
```

### 5. Run the Application

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 🔑 Getting IBM API Credentials

### Step 1 — Create IBM Cloud Account
1. Visit [cloud.ibm.com](https://cloud.ibm.com) and create a free account.

### Step 2 — Create an API Key
1. Go to **Manage → Access (IAM) → API Keys**
2. Click **Create an IBM Cloud API key**
3. Copy the key and paste into `.env` as `IBM_API_KEY`

### Step 3 — Set Up watsonx.ai Project
1. Go to [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)
2. Create a new **Watson Studio** project
3. From the project settings, copy the **Project ID**
4. Paste into `.env` as `IBM_PROJECT_ID`

### Step 4 — Select Region URL
| Region | URL |
|--------|-----|
| US South (default) | `https://us-south.ml.cloud.ibm.com` |
| EU Frankfurt | `https://eu-de.ml.cloud.ibm.com` |
| Tokyo | `https://jp-tok.ml.cloud.ibm.com` |
| London | `https://eu-gb.ml.cloud.ibm.com` |

---

## 🤖 AGENT_INSTRUCTIONS Customisation

All AI behaviour is controlled by the `AGENT_INSTRUCTIONS` dictionary in [`config.py`](config.py). Edit this section to customise the coaching experience **without changing any core code**:

```python
AGENT_INSTRUCTIONS = {
    "coaching_style": "motivational",     # motivational | analytical | strict | gentle
    "motivation_tone": "positive",         # positive | challenging | calm
    "default_workout_intensity": "moderate",
    "indian_meal_recommendations": True,   # Enable Indian food suggestions
    "beginner_friendly": True,
    "family_friendly": True,
    "language_style": "simple_english",
    # ... and more
}
```

---

## 🌐 Deployment

### Render (Recommended — Free Tier)

1. Push code to GitHub
2. Create account at [render.com](https://render.com)
3. Click **New → Web Service**
4. Connect your GitHub repo
5. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Add all environment variables from `.env` in the **Environment** tab
7. Deploy!

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Add environment variables in the Railway dashboard.

### IBM Cloud (Code Engine)

```bash
# Install IBM Cloud CLI
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh

# Login
ibmcloud login --apikey $IBM_API_KEY

# Deploy as container
ibmcloud ce project create --name fitness-buddy
ibmcloud ce application create \
  --name fitness-buddy-app \
  --image icr.io/your-namespace/fitness-buddy:latest \
  --env IBM_API_KEY=$IBM_API_KEY \
  --env IBM_PROJECT_ID=$IBM_PROJECT_ID
```

### Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t fitness-buddy .
docker run -p 5000:5000 --env-file .env fitness-buddy
```

---

## 📊 Database Schema

| Table | Key Columns |
|-------|-------------|
| `users` | id, name, age, gender, height, weight, fitness_goal, fitness_level |
| `workout_logs` | user_id, workout_type, duration, calories_burned, date |
| `habit_logs` | user_id, water_intake, sleep_hours, steps_count, mood, date |
| `progress_records` | user_id, weight, bmi, waist, date |
| `ai_recommendations` | user_id, agent_name, recommendation, category |
| `chat_messages` | user_id, role, content, agent_used |

---

## 🎯 Agent Capabilities

### Orchestrator Agent
- Classifies user intent using keyword matching
- Routes to up to 2 specialist agents per query
- Synthesises outputs into one cohesive response

### User Profile Agent
- Analyses BMI, age, gender, fitness level
- Generates personalised fitness profile
- Provides profile completeness scoring

### Workout Planning Agent
- Creates daily and weekly workout plans
- Home workouts — no equipment required
- Adapts difficulty: Beginner → Intermediate → Advanced
- Supports 10–60 minute sessions

### Nutrition Agent
- Indian meal plans (vegetarian & non-vegetarian)
- Regional variety (North, South, West Indian cuisines)
- Calorie and macronutrient estimates
- Hydration recommendations

### Motivation Agent
- Daily personalised motivation
- Challenge of the day
- Quote of the day
- Accountability coaching

### Habit Tracking Agent
- Water intake analysis
- Sleep quality coaching
- Workout streak building
- Weekly habit scoring

### Progress Evaluation Agent
- Weight trend analysis
- Goal achievement scoring
- Plan adjustment recommendations
- Estimated goal timeline

---

## 🔒 Security

- IBM API credentials stored securely in `.env`
- Passwords hashed with Werkzeug PBKDF2
- Flask-Login session management
- CSRF protection via Flask-WTF
- Input validation on all forms
- Never hardcode secrets in source code

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Backend** | IBM Granite 3 8B Instruct via watsonx.ai |
| **Web Framework** | Flask 3.0 |
| **Database** | SQLite (SQLAlchemy ORM) |
| **Authentication** | Flask-Login |
| **Frontend** | Bootstrap 5, Chart.js |
| **Styling** | Custom CSS (glassmorphism + gradients) |
| **Deployment** | Gunicorn WSGI server |

---

## 📸 Application Pages

| Page | Route |
|------|-------|
| Landing Page | `/` |
| Register | `/register` |
| Login | `/login` |
| Dashboard | `/dashboard` |
| AI Coach Chat | `/chat` |
| Analytics | `/analytics` |
| Edit Profile | `/edit-profile` |
| Family Profiles | `/family` |

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## ⚕️ Health Disclaimer

Fitness Buddy provides **general fitness guidance only** and is **not a substitute for professional medical advice**. Always consult a qualified healthcare provider before starting a new exercise or nutrition programme.

---

<p align="center">Built with ❤️ using IBM Granite on watsonx.ai</p>
