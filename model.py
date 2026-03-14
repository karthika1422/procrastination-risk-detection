"""
model.py
Loads the trained model and provides prediction utilities.
Falls back to a rule-based heuristic if no saved model exists.
"""

import os
import json
import pickle
import numpy as np
from typing import Tuple, List, Dict

FEATURES = [
    "days_since_last_study",
    "avg_session_duration",
    "task_completion_rate",
    "deadline_proximity_avg",
    "idle_ratio",
    "sessions_this_week",
    "missed_deadlines_count",
    "self_reported_stress",
]

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "saved")


# ──────────────────────────────────────────────
# Intervention library
# ──────────────────────────────────────────────
INTERVENTIONS = {
    "low": [
        {"title": "Keep Up the Momentum", "description": "You're doing great! Try the Pomodoro technique to maintain focus during sessions.", "category": "habit", "priority": 3},
        {"title": "Reward Yourself", "description": "Set small rewards after completing tasks to reinforce positive behavior.", "category": "mindset", "priority": 3},
    ],
    "medium": [
        {"title": "Time-Block Your Day", "description": "Assign specific 45-minute study blocks to your calendar with no-phone rules.", "category": "habit", "priority": 2},
        {"title": "Reduce Your Study Environment Distractions", "description": "Use website blockers (Cold Turkey, Freedom) during study sessions.", "category": "environment", "priority": 2},
        {"title": "Two-Minute Rule", "description": "If a task takes less than 2 minutes, do it immediately. Start bigger tasks with just 2 minutes of effort.", "category": "mindset", "priority": 2},
    ],
    "high": [
        {"title": "Create a Weekly Study Contract", "description": "Write down 3 specific goals for this week with deadlines. Share with a peer for accountability.", "category": "social", "priority": 1},
        {"title": "Break Tasks into Sub-tasks", "description": "Decompose every assignment into steps of ≤30 minutes each. Track each sub-task.", "category": "habit", "priority": 1},
        {"title": "Stress Management Check-in", "description": "High stress is linked to avoidance. Try a 5-minute guided breathing exercise before each session.", "category": "mindset", "priority": 1},
        {"title": "Reduce Idle Time", "description": "Use app usage tracking (e.g., Digital Wellbeing) to identify your top distraction app and set a daily limit.", "category": "environment", "priority": 1},
    ],
    "critical": [
        {"title": "🚨 Immediate Advisor Meeting", "description": "Your behavioral patterns indicate high procrastination risk. Please schedule a meeting with your academic advisor this week.", "category": "social", "priority": 1},
        {"title": "Academic Recovery Plan", "description": "Work with your counselor to create a structured 2-week recovery plan with daily check-ins.", "category": "habit", "priority": 1},
        {"title": "Identify Root Cause", "description": "Procrastination is often driven by fear of failure or perfectionism. Consider talking to a counselor.", "category": "mindset", "priority": 1},
    ],
}


# ──────────────────────────────────────────────
# Rule-based fallback predictor
# ──────────────────────────────────────────────
def rule_based_risk_score(features: Dict) -> float:
    """
    Heuristic risk scoring when no ML model is available.
    Returns a probability (0–1).
    """
    score = 0.0
    score += min(features["days_since_last_study"] / 14, 1.0) * 0.25
    score += (1 - min(features["avg_session_duration"] / 120, 1.0)) * 0.15
    score += (1 - features["task_completion_rate"]) * 0.20
    score += (1 - min(features["deadline_proximity_avg"] / 5, 1.0)) * 0.10
    score += features["idle_ratio"] * 0.15
    score += (1 - min(features["sessions_this_week"] / 7, 1.0)) * 0.10
    score += min(features["missed_deadlines_count"] / 5, 1.0) * 0.05
    score += (features["self_reported_stress"] - 1) / 9 * 0.00  # secondary signal
    return float(np.clip(score, 0, 1))


# ──────────────────────────────────────────────
# Model loader
# ──────────────────────────────────────────────
class ProcrastinationPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_type = "rule_based"
        self._load()

    def _load(self):
        meta_path = os.path.join(MODEL_DIR, "metadata.json")
        scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")

        if not os.path.exists(meta_path):
            print("⚠️  No trained model found. Using rule-based predictor.")
            return

        with open(meta_path) as f:
            meta = json.load(f)
        self.model_type = meta.get("model_type", "rule_based")

        with open(scaler_path, "rb") as f:
            self.scaler = pickle.load(f)

        if self.model_type == "tensorflow":
            try:
                import tensorflow as tf
                model_path = os.path.join(MODEL_DIR, "model_final.keras")
                if not os.path.exists(model_path):
                    model_path = os.path.join(MODEL_DIR, "best_model.keras")
                self.model = tf.keras.models.load_model(model_path)
                print("✅ TensorFlow model loaded.")
            except Exception as e:
                print(f"⚠️  Could not load TF model: {e}. Falling back.")
                self.model_type = "rule_based"
        elif self.model_type == "sklearn":
            try:
                with open(os.path.join(MODEL_DIR, "sklearn_model.pkl"), "rb") as f:
                    self.model = pickle.load(f)
                print("✅ Sklearn model loaded.")
            except Exception as e:
                print(f"⚠️  Could not load sklearn model: {e}. Falling back.")
                self.model_type = "rule_based"

    def predict(self, feature_dict: Dict) -> Tuple[int, float, str, List[str]]:
        """
        Returns: (risk_score, probability, risk_level, risk_factors)
        """
        if self.model_type == "rule_based" or self.model is None:
            prob = rule_based_risk_score(feature_dict)
        else:
            x = np.array([[feature_dict[f] for f in FEATURES]])
            x_scaled = self.scaler.transform(x)
            if self.model_type == "tensorflow":
                prob = float(self.model.predict(x_scaled, verbose=0)[0][0])
            else:
                prob = float(self.model.predict_proba(x_scaled)[0][1])

        risk_score = int(prob * 100)
        risk_level = self._risk_level(risk_score)
        risk_factors = self._top_factors(feature_dict)
        return risk_score, prob, risk_level, risk_factors

    @staticmethod
    def _risk_level(score: int) -> str:
        if score <= 30:
            return "Low"
        elif score <= 60:
            return "Medium"
        elif score <= 80:
            return "High"
        else:
            return "Critical"

    @staticmethod
    def _top_factors(features: Dict) -> List[str]:
        """Returns human-readable top risk factors."""
        factors = []
        if features["days_since_last_study"] > 5:
            factors.append(f"No study session for {features['days_since_last_study']:.0f} days")
        if features["task_completion_rate"] < 0.5:
            factors.append(f"Low task completion ({features['task_completion_rate']*100:.0f}%)")
        if features["idle_ratio"] > 0.4:
            factors.append(f"High idle/distraction ratio ({features['idle_ratio']*100:.0f}%)")
        if features["missed_deadlines_count"] >= 3:
            factors.append(f"{features['missed_deadlines_count']} missed deadlines this semester")
        if features["sessions_this_week"] <= 2:
            factors.append(f"Only {features['sessions_this_week']} study session(s) this week")
        if features["self_reported_stress"] >= 7:
            factors.append(f"High self-reported stress ({features['self_reported_stress']:.0f}/10)")
        if features["deadline_proximity_avg"] < 1:
            factors.append("Submitting tasks very close to deadlines")
        return factors[:4] if factors else ["Behavioral patterns within normal range"]

    @staticmethod
    def get_interventions(risk_level: str) -> List[Dict]:
        level = risk_level.lower()
        return INTERVENTIONS.get(level, INTERVENTIONS["medium"])


# Singleton instance
predictor = ProcrastinationPredictor()
