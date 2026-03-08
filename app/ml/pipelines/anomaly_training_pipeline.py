import pandas as pd
from sqlalchemy.orm import Session

from app.db.models.transaction import Transaction
from app.db.models.category  import Category, TransactionType
from app.ml.inference.anomaly_inference import AnomalyInference
from app.ml.training.feature_builder import TransactionFeatureBuilder
from app.ml.training.model_trainer import AnomalyModelTrainer
from app.ml.registry.model_registry import ModelRegistry
from app.ml.postprocessing.recurring_detector import RecurringDetector


class AnomalyTrainingPipeline:

    @staticmethod
    def run(db: Session, user_id: int):
        # -----------------------------
        # Fetch user transactions
        # -----------------------------
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
            raise ValueError("No transactions found for training.")

        # -----------------------------
        # Detect recurring transactions
        # -----------------------------
        tx_data = [{
            "transaction_id": tx.id,
            "amount": float(tx.amount),
            "transaction_date": tx.transaction_date,
            "category_id": tx.category_id
        } for tx in transactions]
        
        recurring_detector = RecurringDetector()
        recurring_profiles = recurring_detector.detect_recurring_transactions(tx_data)
        
        # ------------------------------
        # Convert to dataframe
        # ------------------------------
        df = pd.DataFrame(tx_data)

        # ------------------------------
        # Build features
        # ------------------------------
        X = TransactionFeatureBuilder.build_features(df)

        # ------------------------------
        # Train model
        # ------------------------------
        model_artifact = AnomalyModelTrainer.train(X)

        # ------------------------------
        # Add recurring profiles to model artifact
        # ------------------------------
        model_artifact["recurring_profiles"] = recurring_profiles

        # ------------------------------
        # Save model
        # ------------------------------
        ModelRegistry.save_model(user_id, model_artifact)

        return {
                "message": "Model trained successfully",
                "records_used": len(df),
                "recurring patterns": recurring_profiles,
            }