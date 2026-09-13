"""
churn_model.py
Trains and evaluates churn-prediction models (Logistic Regression baseline
and Random Forest) on the Netflix churn dataset.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, classification_report
)

NUMERIC_FEATURES = [
    "age", "watch_hours", "last_login_days", "monthly_fee",
    "number_of_profiles", "avg_watch_time_per_day",
]
CATEGORICAL_FEATURES = [
    "gender", "subscription_type", "region", "device",
    "payment_method", "favorite_genre",
]
TARGET = "churned"


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), CATEGORICAL_FEATURES),
        ]
    )


def get_train_test_split(df: pd.DataFrame, test_size=0.2, random_state=42):
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET]
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


def train_logistic_regression(X_train, y_train) -> Pipeline:
    pipe = Pipeline(steps=[
        ("preprocess", build_preprocessor()),
        ("model", LogisticRegression(max_iter=1000, random_state=42)),
    ])
    pipe.fit(X_train, y_train)
    return pipe


def train_random_forest(X_train, y_train) -> Pipeline:
    pipe = Pipeline(steps=[
        ("preprocess", build_preprocessor()),
        ("model", RandomForestClassifier(
            n_estimators=300, max_depth=8, min_samples_leaf=5,
            random_state=42, n_jobs=-1
        )),
    ])
    pipe.fit(X_train, y_train)
    return pipe


def evaluate_model(pipe: Pipeline, X_test, y_test) -> dict:
    y_pred = pipe.predict(X_test)
    y_proba = pipe.predict_proba(X_test)[:, 1]
    return {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_proba), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, output_dict=False),
    }


def get_feature_importance(pipe: Pipeline) -> pd.Series:
    """Extract feature importances from a fitted RandomForest pipeline."""
    ohe = pipe.named_steps["preprocess"].named_transformers_["cat"]
    cat_names = list(ohe.get_feature_names_out(CATEGORICAL_FEATURES))
    feature_names = NUMERIC_FEATURES + cat_names
    importances = pipe.named_steps["model"].feature_importances_
    return pd.Series(importances, index=feature_names).sort_values(ascending=False)


if __name__ == "__main__":
    from data_loader import load_data, add_engineered_features

    df = add_engineered_features(load_data())
    X_train, X_test, y_train, y_test = get_train_test_split(df)

    rf_pipe = train_random_forest(X_train, y_train)
    metrics = evaluate_model(rf_pipe, X_test, y_test)
    print("Random Forest performance:")
    for k, v in metrics.items():
        if k != "classification_report":
            print(f"  {k}: {v}")

    print("\nTop 10 feature importances:")
    print(get_feature_importance(rf_pipe).head(10))
