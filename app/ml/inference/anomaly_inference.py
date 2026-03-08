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


class AnomalyInference:

    def predict_for_user(self, db: Session, user_id: int):
        """
        Run anomaly detection for all transactions of a user.
        """

        # --------------------------------    
        # Load model artifacts
        # --------------------------------
        data = ModelRegistry.load_model(user_id)

        if not data:
            raise ValueError(f"No model found for user_id {user_id}")

        model = data["model"]
        scaler = data.get("scaler")
        feature_stats = data.get("feature_stats")
        feature_columns = data.get("feature_columns")
        recurring_profiles = data.get("recurring_profiles", [])

        # --------------------------------
        # Fetch transaction
        # --------------------------------
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
        
        # --------------------------------
        # Ensure transaction are ordered
        # --------------------------------
        transactions = sorted(transactions, key=lambda x: x.transaction_date)
        
        # --------------------------------
        # Convert to dictionaries
        # --------------------------------
        tx_dicts = [{
            "transaction_id": tx.id,
            "amount": tx.amount,
            "transaction_date": tx.transaction_date,
            "category_id": tx.category_id,
        } for tx in transactions]


        # ---------------------------------
        # Convert to dataframe
        # ---------------------------------
        df = pd.DataFrame(tx_dicts)
        
        # --------------------------------
        # Build features using SAME training logic
        # --------------------------------
        X_raw = TransactionFeatureBuilder.build_features(df)

        # --------------------------------
        # Enforce same feature order as training
        # --------------------------------
        if feature_columns:
            missing_cols = set(feature_columns) - set(X_raw.columns)
            if missing_cols:
                raise ValueError(f"Missing features for inference: {missing_cols}")
            X_raw = X_raw[feature_columns]

        # --------------------------------
        # Scale features using the same scaler from training
        # --------------------------------
        if scaler:
            X_scaled = scaler.transform(X_raw)
        else:
            X_scaled = X_raw.values

        # -------------------------------
        # Run model Prediction
        # -------------------------------
        predictions = model.predict(X_scaled)
        scores = model.decision_function(X_scaled)

        # --------------------------------
        # Initialize helpers once (not inside loop)
        # --------------------------------
        explainer = AnomalyExplainer()
        classifier = AnomalyClassifier()
        reason_builder = AnomalyReasonBuilder()
        recurring_detector = RecurringDetector()
        results = []

        # --------------------------------
        # Process results
        # --------------------------------
        amount_ratio = None
        for idx, (tx, pred, score) in enumerate(zip(transactions, predictions, scores)):
            score = float(score)
            anomaly_score = round(-score, 4)

            tx_dict = tx_dicts[idx]

            # --------------------------------
            # Recurring override logic
            # --------------------------------
            profile = recurring_detector.get_recurring_profiles(tx_dict, recurring_profiles)

            # --------------------------------
            # Recurring transactions should not be anomalies
            # ---------------------------------
            if profile:
                amount_ratio = tx.amount / profile["avg_amount"] if profile["avg_amount"] else None
                is_recurring = True
                expected_amount = profile["avg_amount"]

                # --------------------------------
                # Allow +- 30% deviation
                # --------------------------------
                lower = expected_amount * 0.7
                upper = expected_amount * 1.3

                if lower <= tx.amount <= upper:
                    is_anomaly = False
                else:
                    is_anomaly = True
            else:
                is_recurring = False
                is_anomaly = pred == -1

            explanation = []
            severity = None
            confidence = None
            reason = None

            # --------------------------------
            # Generate explanation if anomaly
            # --------------------------------
            if is_anomaly:
                explanation = explainer.explain(
                    X_raw.iloc[idx].to_dict(),
                    feature_stats
                )

                severity = classifier.get_severity(score, )
                confidence = classifier.get_confidence(score)
                reason = reason_builder.build(explanation)

            # -------------------------------
            # Append results
            
            results.append({
                "amount": tx.amount,
                "anomaly_score": score,
                "category_id": tx.category_id,
                "confidence": confidence,
                "is_anomaly": is_anomaly,
                "is_recurring": is_recurring,
                "reason": reason,
                "severity": severity,
                "transaction_id": tx.id,
                "transaction_date": tx.transaction_date,
            })

         
        return results