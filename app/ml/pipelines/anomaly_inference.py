import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from app.db.models.transaction import Transaction
from app.db.models.category  import Category, TransactionType
from app.ml.registry.model_registry import ModelRegistry
from app.ml.training.feature_builder import TransactionFeatureBuilder
from app.ml.explainability.anomaly_explainer import AnomalyExplainer
from app.ml.postprocessing.anomaly_classifier import AnomalyClassifier
from app.ml.postprocessing.anomaly_reason_builder import AnomalyReasonBuilder
from app.ml.postprocessing.recurring_detector import RecurringDetector
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
        feature_stats = data.get("feature_stats")

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
        
        # Prepare simplified transaction dicts
        tx_dicts = [{
            "transaction_id": tx.id,
            "amount": tx.amount,
            "transaction_date": tx.transaction_date,
            "category_id": tx.category_id,
        } for tx in transactions]
        recurring_ids = RecurringDetector().detect_recurring_transactions(tx_dicts)
        
        # Convert to DataFrame (same structure as training)
        df = pd.DataFrame([{
            "amount": tx.amount,
            "transaction_date": tx.transaction_date,
            "category_id": tx.category_id,
        } for tx in transactions])

        # Build features using SAME training logic
        X_raw = TransactionFeatureBuilder.build_features(df)

        # Predict
        X_scaled = pd.DataFrame(
            scaler.transform(X_raw),
            columns=X_raw.columns,
            index=X_raw.index
        )
        predictions = model.predict(X_scaled)
        scores = model.decision_function(X_scaled)

        results = []

        for idx, (tx, pred, score) in enumerate(zip(transactions, predictions, scores)):
            score = round(float(score), 2) if isinstance(score, (np.generic, float, int)) else score
            is_anomaly = True if pred == -1 else False
            
            is_recurring = tx.id in recurring_ids
            if is_recurring and abs(score) < 0.1:
                is_anomaly = False  # Override anomaly if it's a recurring transaction

            explanation = []
            severity = None
            confidence = None
            reason = None

            if is_anomaly:
                explanation = AnomalyExplainer().explain(
                    X_raw.iloc[idx].to_dict(),
                    feature_stats
                )

                severity = AnomalyClassifier().get_severity(score)
                confidence = AnomalyClassifier().get_confidence(score)
                reason = AnomalyReasonBuilder().build(explanation)

            results.append({
                "transaction_id": tx.id,
                "amount": tx.amount,
                "transaction_date": tx.transaction_date,
                "category_id": tx.category_id,
                "is_anomaly": is_anomaly,
                "severity": severity,
                "confidence": confidence,
                "reason": reason,
                "anomaly_score": score,
            })

         
        return results