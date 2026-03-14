# 🧠 Early Procrastination Risk Detection System

> Behavioral analytics + Deep Learning to detect and intervene in student procrastination early.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green) ![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange) ![React](https://img.shields.io/badge/React-18-cyan)

---

## 📌 Overview

This system uses **behavioral analytics** and a **deep learning model (LSTM + MLP)** to:
- Track student study behavior (session logs, assignment completions, idle time)
- Predict procrastination risk scores in real-time
- Recommend targeted habit-based interventions

---

## 🗂️ Project Structure

```
procrastination-detector/
├── backend/              # FastAPI REST API
│   ├── main.py           # App entry point + routes
│   ├── model.py          # ML model loader + predictor
│   ├── schemas.py        # Pydantic data models
│   └── requirements.txt
├── models/
│   └── train_model.py    # Model training script
├── data/
│   └── generate_data.py  # Synthetic dataset generator
├── frontend/             # React dashboard
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── index.css
│   └── package.json
├── notebooks/
│   └── analysis.ipynb    # EDA + model evaluation
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Setup Backend

```bash
git clone https://github.com/yourusername/procrastination-detector.git
cd procrastination-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Generate Data & Train Model

```bash
# Generate synthetic student behavioral data
python data/generate_data.py

# Train the deep learning model
python models/train_model.py
```

### 3. Start Backend API

```bash
cd backend
uvicorn main:app --reload --port 8000
```
API docs available at: `http://localhost:8000/docs`

### 4. Start Frontend

```bash
cd frontend
npm install
npm start
```
Dashboard at: `http://localhost:3000`

---

## 🧬 Features

| Feature | Description |
|---|---|
| **Risk Score** | 0–100 score predicting procrastination likelihood |
| **Behavioral Input** | Session frequency, task delays, idle time, completion rate |
| **LSTM Model** | Temporal pattern recognition over study sessions |
| **Interventions** | Rule + ML-based personalized recommendations |
| **Dashboard** | Real-time React UI with charts and alerts |

---

## 🧠 Model Architecture

```
Input Features (8) → Dense(64, ReLU) → Dropout(0.3)
                   → Dense(32, ReLU) → Dropout(0.2)
                   → Dense(16, ReLU)
                   → Output(1, Sigmoid) → Risk Score
```

Trained on synthetic behavioral data with features:
- `days_since_last_study` — recency of activity
- `avg_session_duration` — focus depth
- `task_completion_rate` — follow-through
- `deadline_proximity_avg` — urgency awareness
- `idle_ratio` — distraction index
- `sessions_this_week` — consistency
- `missed_deadlines_count` — track record
- `self_reported_stress` — subjective load

---

## 📊 Risk Levels

| Score | Level | Action |
|---|---|---|
| 0–30 | 🟢 Low | Positive reinforcement |
| 31–60 | 🟡 Medium | Study tips + reminders |
| 61–80 | 🟠 High | Structured plan + check-ins |
| 81–100 | 🔴 Critical | Immediate counselor alert |

---

## 📡 API Endpoints

```
POST /predict          → Get risk score for a student
GET  /students         → List all student records
POST /log-session      → Log a new study session
GET  /interventions    → Get recommended interventions
GET  /stats            → System-wide analytics
```

---

## 🔬 Research Inspiration

- Steel, P. (2007). *The Nature of Procrastination*
- Duhigg, C. (2012). *The Power of Habit*
- Baumeister & Heatherton (1996). *Self-regulation failure*
- Integrated behavioral loop: Cue → Routine → Reward model

---

## 📄 License

MIT License — free to use, modify, and distribute.
