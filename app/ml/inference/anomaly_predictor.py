import pandas as pd
from app.ml.registry.model_registry import ModelRegistry
from app.ml.training.feature_builder import TransactionFeatureBuilder


class AnomalyPredictor:

    @staticmethod
    def predict(user_id: int, transactions: list):
        model = ModelRegistry.load_model(user_id)
        df = pd.DataFrame(transactions)
        X = TransactionFeatureBuilder.build_features(df)
        predictions = model.predict(X)

        # IsolationForest returns:
        # -1 = anomaly
        #  1 = normal

        df["is_anomaly"] = predictions
        df["is_anomaly"] = df["is_anomaly"].apply(lambda x: 1 if x == -1 else 0)

        return df.to_dict(orient="records")