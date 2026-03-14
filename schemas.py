"""
schemas.py
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BehavioralInput(BaseModel):
    student_id: Optional[str] = Field(default=None, example="STU0042")
    days_since_last_study: float = Field(..., ge=0, le=30, example=3.5,
        description="Days since the student last had a study session")
    avg_session_duration: float = Field(..., ge=0, le=480, example=75.0,
        description="Average study session duration in minutes")
    task_completion_rate: float = Field(..., ge=0, le=1, example=0.65,
        description="Proportion of assigned tasks completed (0–1)")
    deadline_proximity_avg: float = Field(..., ge=0, le=14, example=1.5,
        description="Average days before deadline when tasks are submitted")
    idle_ratio: float = Field(..., ge=0, le=1, example=0.35,
        description="Ratio of idle/distracted time during study sessions (0–1)")
    sessions_this_week: int = Field(..., ge=0, le=21, example=3,
        description="Number of study sessions this week")
    missed_deadlines_count: int = Field(..., ge=0, le=20, example=2,
        description="Total missed deadlines this semester")
    self_reported_stress: float = Field(..., ge=1, le=10, example=7.0,
        description="Self-reported stress level (1=low, 10=high)")

    class Config:
        schema_extra = {
            "example": {
                "student_id": "STU0042",
                "days_since_last_study": 4.0,
                "avg_session_duration": 50.0,
                "task_completion_rate": 0.55,
                "deadline_proximity_avg": 1.0,
                "idle_ratio": 0.45,
                "sessions_this_week": 2,
                "missed_deadlines_count": 3,
                "self_reported_stress": 7.5
            }
        }


class Intervention(BaseModel):
    title: str
    description: str
    category: str  # "habit", "environment", "mindset", "social"
    priority: int  # 1=high, 2=medium, 3=low


class PredictionResponse(BaseModel):
    student_id: Optional[str]
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str  # "Low", "Medium", "High", "Critical"
    risk_probability: float
    top_risk_factors: List[str]
    interventions: List[Intervention]
    timestamp: str


class SessionLog(BaseModel):
    student_id: str
    duration_minutes: float
    tasks_completed: int
    tasks_total: int
    idle_minutes: float
    timestamp: Optional[str] = None


class StudentRecord(BaseModel):
    student_id: str
    name: Optional[str] = None
    risk_score: int
    risk_level: str
    last_updated: str


class StatsResponse(BaseModel):
    total_students: int
    avg_risk_score: float
    risk_distribution: dict
    high_risk_count: int
