"""
generate_data.py
Generates synthetic student behavioral dataset for training the procrastination detection model.
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)


def generate_student_data(n_students=500):
    """
    Generates realistic synthetic behavioral data for students.
    Returns a DataFrame with features and procrastination labels.
    """
    data = []

    for i in range(n_students):
        # Randomly assign a base procrastination tendency (latent variable)
        proc_tendency = np.random.beta(2, 2)  # 0 to 1

        # Feature generation correlated with procrastination tendency
        days_since_last_study = np.clip(
            np.random.normal(proc_tendency * 7, 1.5), 0, 14
        )
        avg_session_duration = np.clip(
            np.random.normal(120 - proc_tendency * 90, 20), 10, 180
        )  # minutes
        task_completion_rate = np.clip(
            np.random.normal(1 - proc_tendency * 0.7, 0.1), 0, 1
        )
        deadline_proximity_avg = np.clip(
            np.random.normal(proc_tendency * 2 + 0.5, 0.5), 0, 5
        )  # days before deadline
        idle_ratio = np.clip(
            np.random.normal(proc_tendency * 0.6, 0.1), 0, 1
        )
        sessions_this_week = np.clip(
            int(np.random.normal(7 - proc_tendency * 5, 1)), 0, 14
        )
        missed_deadlines_count = np.clip(
            int(np.random.normal(proc_tendency * 5, 1)), 0, 10
        )
        self_reported_stress = np.clip(
            np.random.normal(proc_tendency * 8 + 1, 1.5), 1, 10
        )

        # Compute risk label: 1 = procrastinator (tendency > 0.55)
        noise = np.random.normal(0, 0.05)
        risk_label = 1 if (proc_tendency + noise) > 0.55 else 0

        # Risk score (continuous, 0–100)
        risk_score = int(np.clip((proc_tendency + noise) * 100, 0, 100))

        data.append({
            "student_id": f"STU{i+1:04d}",
            "days_since_last_study": round(days_since_last_study, 2),
            "avg_session_duration": round(avg_session_duration, 2),
            "task_completion_rate": round(task_completion_rate, 4),
            "deadline_proximity_avg": round(deadline_proximity_avg, 2),
            "idle_ratio": round(idle_ratio, 4),
            "sessions_this_week": sessions_this_week,
            "missed_deadlines_count": missed_deadlines_count,
            "self_reported_stress": round(self_reported_stress, 1),
            "risk_label": risk_label,
            "risk_score": risk_score,
        })

    return pd.DataFrame(data)


def main():
    os.makedirs("data", exist_ok=True)
    df = generate_student_data(n_students=1000)

    # Save full dataset
    df.to_csv("data/student_behavior.csv", index=False)

    # Train/test split
    train = df.sample(frac=0.8, random_state=42)
    test = df.drop(train.index)
    train.to_csv("data/train.csv", index=False)
    test.to_csv("data/test.csv", index=False)

    print(f"✅ Generated {len(df)} student records")
    print(f"   Train: {len(train)} | Test: {len(test)}")
    print(f"   Procrastinators: {df['risk_label'].sum()} ({df['risk_label'].mean()*100:.1f}%)")
    print(f"\nSample data:")
    print(df.head(3).to_string())
    print(f"\nFiles saved to data/")


if __name__ == "__main__":
    main()
