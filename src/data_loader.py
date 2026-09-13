"""
data_loader.py
Utility functions for loading and lightly validating the Netflix churn dataset.
"""

import pandas as pd
from pathlib import Path

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "netflix_customer_churn.csv"


def load_data(path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """
    Load the Netflix customer churn dataset from disk.

    Parameters
    ----------
    path : str or Path
        Path to the CSV file. Defaults to data/netflix_customer_churn.csv.

    Returns
    -------
    pd.DataFrame
        The raw dataset.
    """
    df = pd.read_csv(path)
    return df


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a small set of derived features used throughout the analysis:
      - age_group: binned age bracket
      - engagement_level: Low/Medium/High based on avg_watch_time_per_day tertiles
      - recency_flag: whether a customer is "at risk" (no login in 21+ days)
      - revenue_at_risk: monthly_fee for churned customers (helper for revenue calcs)

    Parameters
    ----------
    df : pd.DataFrame
        Raw dataframe as returned by load_data().

    Returns
    -------
    pd.DataFrame
        Dataframe with additional engineered columns.
    """
    df = df.copy()

    df["age_group"] = pd.cut(
        df["age"],
        bins=[0, 25, 35, 45, 55, 100],
        labels=["18-25", "26-35", "36-45", "46-55", "56+"],
    )

    df["engagement_level"] = pd.qcut(
        df["avg_watch_time_per_day"],
        q=3,
        labels=["Low", "Medium", "High"],
    )

    df["recency_flag"] = (df["last_login_days"] >= 21).map({True: "At Risk", False: "Active"})

    df["revenue_at_risk"] = df["monthly_fee"].where(df["churned"] == 1, 0)

    return df


if __name__ == "__main__":
    data = load_data()
    data = add_engineered_features(data)
    print(data.head())
    print(f"\nLoaded {len(data):,} rows, {data.shape[1]} columns.")
