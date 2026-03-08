import pandas as pd
import numpy as np


class TransactionFeatureBuilder:

    @staticmethod
    def build_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert raw transaction dataframe into ML features.
        """

        df = df.copy()

        # -----------------------------------
        # Sort df by transaction date
        # -----------------------------------
        df = df.sort_values("transaction_date")

        # -----------------------------------
        # Basic features
        # -----------------------------------
        df["amount"] = df["amount"].astype(float)

        dt = pd.to_datetime(df["transaction_date"])

        df["transaction_hour"] = dt.dt.hour
        df["transaction_day"] = dt.dt.day
        df["transaction_month"] = dt.dt.month
        df["transaction_weekday"] = dt.dt.weekday

        # -----------------------------------
        # Spending behavior features
        # -----------------------------------
        df["is_weekend"] = (df["transaction_weekday"] >= 5).astype(int)

        # -----------------------------------
        # Day since last transaction category wise
        # -----------------------------------
        df["days_since_last_txn"] = (df.groupby("category_id")["transaction_date"].diff().dt.days.fillna(0))
        
        # -----------------------------------
        # Category Frequency Encoding
        # -----------------------------------
        category_count = df["category_id"].value_counts()
        total = len(df)
        category_freq_map = (category_count / total).to_dict()
        df["category_freq"] = df["category_id"].map(category_freq_map)

        # -----------------------------------
        # Category Behavior
        # -----------------------------------
        df["category_mean"] = df.groupby("category_id")["amount"].transform("mean")
        df["amount_vs_category_mean"] = df["amount"] / (df["category_mean"] + 1e-6)  # Avoid division by zero
        df["amount_deviation_ratio"] = (df["amount"] - df["category_mean"]) / (df["category_mean"] + 1e-6)

        # -----------------------------------
        # Rolling spending pattern per catrgory
        # -----------------------------------
        df["rolling_mean_5"] = df.groupby("category_id")["amount"].rolling(5).mean().reset_index(0, drop=True)
        df["rolling_std_5"] = df.groupby("category_id")["amount"].rolling(5).std().reset_index(0, drop=True)

        df["rolling_mean_5"] = df["rolling_mean_5"].fillna(df["amount"])
        df["rolling_std_5"] = df["rolling_std_5"].fillna(0)

        # -----------------------------------
        # Amount Z-score
        # -----------------------------------
        df["amount_zscore"] = (df["amount"] - df["category_mean"]) / (df["rolling_std_5"] + 1e-6)

        # -----------------------------------
        # User spending baseline
        # -----------------------------------
        df["user_mean_amount"] = df["amount"].mean()
        df["amount_vs_user_mean"] = df["amount"] / (df["user_mean_amount"] + 1e-6)

        # -----------------------------------
        # Log amount
        # -----------------------------------
        df["log_amount"] = np.log1p(df["amount"])

        # -----------------------------------
        # Month Progress
        # -----------------------------------
        df["month_progress"] = df["transaction_day"] / 31

        # -----------------------------------
        # Final feature set
        # -----------------------------------
        feature_columns = [
            "amount_vs_category_mean",
            "amount_deviation_ratio",
            "amount_vs_user_mean",
            "amount_zscore",
            "category_freq",
            "category_mean",
            "days_since_last_txn",
            "is_weekend",
            "log_amount",
            "month_progress",
            "rolling_mean_5",
            "rolling_std_5",
            "transaction_hour",
            "transaction_day",
            "transaction_month",
            "transaction_weekday",
            "user_mean_amount",  
        ]


        return df[feature_columns]