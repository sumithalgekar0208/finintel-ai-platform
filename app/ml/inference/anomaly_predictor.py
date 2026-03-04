import pandas as pd
from app.ml.registry.model_registry import ModelRegistry
from app.ml.training.feature_builder import TransactionFeatureBuilder
from app.ml.explainability.anomaly_explainer import AnomalyExplainer


class AnomalyPredictor:

    @staticmethod
    def predict(user_id: int, transactions: list):
        # --------------------------------------------------
        # Load Model Bundle
        # --------------------------------------------------
        bundle = ModelRegistry.load_model(user_id)

        if bundle is None:
            raise ValueError(f"No trained model found for user_id: {user_id}")

        model = bundle["model"]
        scaler = bundle["scaler"]
        feature_stats = bundle["feature_stats"]

        # --------------------------------------------------
        # Convert Transactions to DataFrame
        # --------------------------------------------------
        df = pd.DataFrame(transactions)

        if df.empty:
            return []

        # --------------------------------------------------
        # Build RAW Features (for explanation)
        # --------------------------------------------------
        X_raw = TransactionFeatureBuilder.build_features(df)
        
        # --------------------------------------------------
        # Scale Features (for prediction)
        # --------------------------------------------------
        X_scaled = pd.DataFrame(
            scaler.transform(X_raw),
            columns=X_raw.columns,
            index=X_raw.index
        )

        # --------------------------------------------------
        # Predict Anomalies
        # --------------------------------------------------
        predictions = model.predict(X_scaled)
        scores = model.decision_function(X_scaled)

        # IsolationForest:
        # -1 = anomaly
        #  1 = normal

        # --------------------------------------------------
        # Build Final Response
        # --------------------------------------------------
        results = []
        for idx in range(len(df)):
            is_anomaly = 1 if predictions[idx] == -1 else 0

            explanation = []
            if is_anomaly:
                explanation = AnomalyExplainer().explain(
                    X_raw.iloc[idx].to_dict(),
                    feature_stats
                )

            results.append({
                "transaction_id": df.iloc[idx].get("id"),
                "amount": df.iloc[idx].get("amount"),
                "is_anomaly": is_anomaly,
                "anomaly_score": round(scores[idx], 2),
                "explanation": explanation
            })

        return results