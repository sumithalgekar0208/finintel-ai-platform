import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from app.db.models.transaction import Transaction
from app.db.models.category  import Category, TransactionType
from app.ml.registry.model_registry import ModelRegistry
from app.ml.training.feature_builder import TransactionFeatureBuilder
from functools import lru_cache


class AnomalyInferencePipeline:

    @staticmethod
    @lru_cache(maxsize=128)
    def _get_cached_model(user_id: int):
        """
        Cache loaded models to speed up inference for active users.
        """
        return ModelRegistry.load_model(user_id)


    def predict_for_user(self, db: Session, user_id: int):
        """
        Run anomaly detection for all transactions of a user.
        """

        # Load model dynamically per user
        data = self._get_cached_model(user_id)
        model = data["model"]
        scaler = data.get("scaler")

        # Fetch transaction
        transactions = (
            db.query(Transaction)
            .join(Category, Transaction.category_id == Category.id)
            .filter(
                Transaction.created_by == user_id,
                Transaction.is_deleted == False,
                Category.type == TransactionType.EXPENSE
            )
            .all()
        )

        if not transactions:
            return []
        
        # Convert to DataFrame (same structure as training)
        df = pd.DataFrame([{
            "amount": tx.amount,
            "transaction_date": tx.transaction_date,
            "category_id": tx.category_id,
        } for tx in transactions])

        # Build features using SAME training logic
        X = TransactionFeatureBuilder.build_features(df)

        # Predict
        X_scaled = pd.DataFrame(
            scaler.transform(X),
            columns=X.columns
        )
        predictions = model.predict(X_scaled)
        scores = model.decision_function(X_scaled)

        results = []

        for tx, pred, score in zip(transactions, predictions, scores):
            results.append({
                "transaction_id": tx.id,
                "amount": float(tx.amount),
                "is_anomaly": True if pred == -1 else False,
                "anomaly_score": float(score)
            })

         
        return results