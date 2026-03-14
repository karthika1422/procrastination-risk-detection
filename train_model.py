"""
train_model.py
Deep learning model for procrastination risk detection.
Architecture: MLP with Dropout regularization.
"""

import numpy as np
import pandas as pd
import os
import json
import pickle

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, mean_absolute_error
)

# Try TensorFlow/Keras; fallback to sklearn for environments without TF
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    from tensorflow.keras.optimizers import Adam
    USE_TF = True
    print("✅ TensorFlow found — using deep learning model")
except ImportError:
    from sklearn.ensemble import GradientBoostingClassifier
    USE_TF = False
    print("⚠️  TensorFlow not found — using GradientBoosting fallback")


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

TARGET = "risk_label"


def load_data():
    train = pd.read_csv("data/train.csv")
    test = pd.read_csv("data/test.csv")
    X_train = train[FEATURES].values
    y_train = train[TARGET].values
    X_test = test[FEATURES].values
    y_test = test[TARGET].values
    return X_train, y_train, X_test, y_test, train, test


def build_deep_model(input_dim):
    """Build MLP model for binary classification."""
    model = Sequential([
        Dense(128, activation="relu", input_shape=(input_dim,)),
        BatchNormalization(),
        Dropout(0.3),
        Dense(64, activation="relu"),
        BatchNormalization(),
        Dropout(0.2),
        Dense(32, activation="relu"),
        Dropout(0.2),
        Dense(16, activation="relu"),
        Dense(1, activation="sigmoid"),
    ])
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    return model


def train_tensorflow(X_train, y_train, X_test, y_test):
    os.makedirs("models/saved", exist_ok=True)

    model = build_deep_model(X_train.shape[1])
    model.summary()

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
        ModelCheckpoint("models/saved/best_model.keras", save_best_only=True),
    ]

    history = model.fit(
        X_train, y_train,
        validation_split=0.15,
        epochs=100,
        batch_size=32,
        callbacks=callbacks,
        verbose=1,
    )

    # Evaluate
    loss, acc, auc = model.evaluate(X_test, y_test, verbose=0)
    y_pred_prob = model.predict(X_test).flatten()
    y_pred = (y_pred_prob >= 0.5).astype(int)

    print(f"\n📊 Test Accuracy: {acc:.4f}")
    print(f"📊 Test AUC:      {auc:.4f}")
    print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")

    return model, y_pred_prob


def train_sklearn(X_train, y_train, X_test, y_test):
    os.makedirs("models/saved", exist_ok=True)

    model = GradientBoostingClassifier(
        n_estimators=200, max_depth=4,
        learning_rate=0.05, random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_pred_prob = model.predict_proba(X_test)[:, 1]

    acc = (y_pred == y_test).mean()
    auc = roc_auc_score(y_test, y_pred_prob)

    print(f"\n📊 Test Accuracy: {acc:.4f}")
    print(f"📊 Test AUC:      {auc:.4f}")
    print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")

    with open("models/saved/sklearn_model.pkl", "wb") as f:
        pickle.dump(model, f)

    return model, y_pred_prob


def save_scaler_and_metadata(scaler, features, use_tf):
    with open("models/saved/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    meta = {
        "features": features,
        "model_type": "tensorflow" if use_tf else "sklearn",
        "version": "1.0.0",
    }
    with open("models/saved/metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print("\n✅ Scaler and metadata saved.")


def main():
    print("🔄 Loading data...")
    X_train, y_train, X_test, y_test, train_df, test_df = load_data()

    print("🔄 Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print(f"\n🏋️ Training on {len(X_train)} samples...")
    if USE_TF:
        model, y_pred_prob = train_tensorflow(X_train_scaled, y_train, X_test_scaled, y_test)
        model.save("models/saved/model_final.keras")
    else:
        model, y_pred_prob = train_sklearn(X_train_scaled, y_train, X_test_scaled, y_test)

    save_scaler_and_metadata(scaler, FEATURES, USE_TF)

    # MAE on risk score (continuous)
    test_scores = test_df["risk_score"].values
    predicted_scores = (y_pred_prob * 100).astype(int)
    mae = mean_absolute_error(test_scores, predicted_scores)
    print(f"📊 Risk Score MAE: {mae:.2f} points")

    print("\n🎉 Training complete! Model saved to models/saved/")


if __name__ == "__main__":
    main()
