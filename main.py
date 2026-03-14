"""
main.py
FastAPI backend for the Procrastination Risk Detection System.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random
import uuid

from schemas import (
    BehavioralInput, PredictionResponse, SessionLog,
    StudentRecord, StatsResponse, Intervention
)
from model import predictor, FEATURES

app = FastAPI(
    title="Procrastination Risk Detection API",
    description="Early detection of student procrastination risk using behavioral analytics and ML.",
    version="1.0.0",
)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory store (replace with a DB in production) ──────────────────────
_student_db: dict = {}
_session_logs: list = []


def _seed_demo_students():
    """Pre-populate with demo student data."""
    demo_students = [
        {"id": "STU0001", "name": "Arjun Sharma", "days_since_last_study": 7.0, "avg_session_duration": 35.0, "task_completion_rate": 0.40, "deadline_proximity_avg": 0.5, "idle_ratio": 0.55, "sessions_this_week": 1, "missed_deadlines_count": 4, "self_reported_stress": 8.5},
        {"id": "STU0002", "name": "Priya Patel",   "days_since_last_study": 1.0, "avg_session_duration": 110.0, "task_completion_rate": 0.90, "deadline_proximity_avg": 3.5, "idle_ratio": 0.15, "sessions_this_week": 6, "missed_deadlines_count": 0, "self_reported_stress": 3.0},
        {"id": "STU0003", "name": "Rahul Verma",   "days_since_last_study": 4.5, "avg_session_duration": 55.0, "task_completion_rate": 0.60, "deadline_proximity_avg": 1.5, "idle_ratio": 0.38, "sessions_this_week": 3, "missed_deadlines_count": 2, "self_reported_stress": 6.5},
        {"id": "STU0004", "name": "Sneha Reddy",   "days_since_last_study": 9.0, "avg_session_duration": 20.0, "task_completion_rate": 0.25, "deadline_proximity_avg": 0.3, "idle_ratio": 0.70, "sessions_this_week": 0, "missed_deadlines_count": 6, "self_reported_stress": 9.0},
        {"id": "STU0005", "name": "Kiran Rao",     "days_since_last_study": 2.0, "avg_session_duration": 90.0, "task_completion_rate": 0.80, "deadline_proximity_avg": 4.0, "idle_ratio": 0.20, "sessions_this_week": 5, "missed_deadlines_count": 1, "self_reported_stress": 4.0},
    ]
    for s in demo_students:
        feat = {k: s[k] for k in FEATURES}
        score, prob, level, factors = predictor.predict(feat)
        _student_db[s["id"]] = {
            "student_id": s["id"],
            "name": s["name"],
            "risk_score": score,
            "risk_level": level,
            "last_updated": datetime.now().isoformat(),
            "features": feat,
        }

_seed_demo_students()


# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Procrastination Risk Detection API v1.0"}


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_risk(data: BehavioralInput):
    """
    Predict procrastination risk score and return interventions.
    """
    feature_dict = {
        "days_since_last_study": data.days_since_last_study,
        "avg_session_duration": data.avg_session_duration,
        "task_completion_rate": data.task_completion_rate,
        "deadline_proximity_avg": data.deadline_proximity_avg,
        "idle_ratio": data.idle_ratio,
        "sessions_this_week": data.sessions_this_week,
        "missed_deadlines_count": data.missed_deadlines_count,
        "self_reported_stress": data.self_reported_stress,
    }

    risk_score, prob, risk_level, risk_factors = predictor.predict(feature_dict)
    raw_interventions = predictor.get_interventions(risk_level)
    interventions = [Intervention(**iv) for iv in raw_interventions]

    student_id = data.student_id or f"STU{uuid.uuid4().hex[:6].upper()}"

    # Save/update student record
    _student_db[student_id] = {
        "student_id": student_id,
        "name": None,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "last_updated": datetime.now().isoformat(),
        "features": feature_dict,
    }

    return PredictionResponse(
        student_id=student_id,
        risk_score=risk_score,
        risk_level=risk_level,
        risk_probability=round(prob, 4),
        top_risk_factors=risk_factors,
        interventions=interventions,
        timestamp=datetime.now().isoformat(),
    )


@app.get("/students", response_model=list[StudentRecord], tags=["Students"])
def list_students():
    """Return all student risk records."""
    return [
        StudentRecord(
            student_id=s["student_id"],
            name=s.get("name"),
            risk_score=s["risk_score"],
            risk_level=s["risk_level"],
            last_updated=s["last_updated"],
        )
        for s in _student_db.values()
    ]


@app.get("/students/{student_id}", tags=["Students"])
def get_student(student_id: str):
    """Get a specific student's risk profile."""
    if student_id not in _student_db:
        raise HTTPException(status_code=404, detail="Student not found")
    return _student_db[student_id]


@app.post("/log-session", tags=["Sessions"])
def log_session(session: SessionLog):
    """Log a new study session for a student and recompute risk."""
    ts = session.timestamp or datetime.now().isoformat()
    _session_logs.append({**session.dict(), "timestamp": ts})

    # Update student record if exists
    if session.student_id in _student_db:
        stu = _student_db[session.student_id]
        feats = stu.get("features", {})
        # Simple feature update based on new session
        if feats:
            feats["days_since_last_study"] = 0.0
            feats["avg_session_duration"] = session.duration_minutes
            feats["task_completion_rate"] = (
                session.tasks_completed / session.tasks_total
                if session.tasks_total > 0 else feats["task_completion_rate"]
            )
            feats["idle_ratio"] = min(session.idle_minutes / session.duration_minutes, 1.0) if session.duration_minutes > 0 else feats["idle_ratio"]
            feats["sessions_this_week"] = min(feats.get("sessions_this_week", 0) + 1, 21)

            score, prob, level, _ = predictor.predict(feats)
            stu.update({"risk_score": score, "risk_level": level, "last_updated": ts, "features": feats})

    return {"message": "Session logged successfully", "timestamp": ts}


@app.get("/interventions", tags=["Interventions"])
def get_interventions(risk_level: str = "medium"):
    """Get recommended interventions for a risk level."""
    valid = ["low", "medium", "high", "critical"]
    if risk_level.lower() not in valid:
        raise HTTPException(status_code=400, detail=f"risk_level must be one of {valid}")
    return predictor.get_interventions(risk_level.capitalize())


@app.get("/stats", response_model=StatsResponse, tags=["Analytics"])
def get_stats():
    """Aggregate statistics across all students."""
    if not _student_db:
        return StatsResponse(total_students=0, avg_risk_score=0, risk_distribution={}, high_risk_count=0)

    scores = [s["risk_score"] for s in _student_db.values()]
    levels = [s["risk_level"] for s in _student_db.values()]
    dist = {}
    for lv in ["Low", "Medium", "High", "Critical"]:
        dist[lv] = levels.count(lv)

    return StatsResponse(
        total_students=len(_student_db),
        avg_risk_score=round(sum(scores) / len(scores), 1),
        risk_distribution=dist,
        high_risk_count=dist.get("High", 0) + dist.get("Critical", 0),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
