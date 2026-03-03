import pandas as pd


class TransactionFeatureBuilder:

    @staticmethod
    def build_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert raw transaction dataframe into ML features.
        """

        df = df.copy()

        # Basic features
        df["amount"] = df["amount"].astype(float)
        df["category_id"] = df["category_id"].astype(int)

        df["transaction_hour"] = pd.to_datetime(df["transaction_date"]).dt.hour
        df["transaction_day"] = pd.to_datetime(df["transaction_date"]).dt.day
        df["transaction_month"] = pd.to_datetime(df["transaction_date"]).dt.month
        df["transaction_weekday"] = pd.to_datetime(df["transaction_date"]).dt.weekday

        # Spending behavior features
        df["is_weekend"] = df["transaction_weekday"].apply(lambda x: 1 if x >= 5 else 0)
        # You can expand this later:
        # rolling averages, category encoding, etc.

        feature_columns = [
            "amount",
            "category_id",
            "transaction_hour",
            "transaction_day",
            "transaction_month",
            "transaction_weekday",
            "is_weekend"
        ]


        return df[feature_columns]