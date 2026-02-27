import pandas as pd
from sqlalchemy.orm import Session

from app.db.models.transaction import Transaction
from app.ml.training.feature_builder import TransactionFeatureBuilder
from app.ml.training.model_trainer import AnomalyModelTrainer
from app.ml.registry.model_registry import ModelRegistry


class AnomalyTrainingPipeline:

    @staticmethod
    def run(db: Session, user_id: int):
        # Fetch user transactions
        transactions = (
            db.query(Transaction)
            .filter(
                Transaction.created_by == user_id,
                Transaction.is_deleted == False
            )
            .all()
        )

        if not transactions:
            raise ValueError("No transactions found for training.")
        
        # Convert to dataframe
        df = pd.DataFrame([{
            "amount": t.amount,
            "transaction_date": t.transaction_date
        } for t in transactions])

        # Build features
        X = TransactionFeatureBuilder.build_features(df)

        # Train model
        model = AnomalyModelTrainer.train(X)

        # Save model
        ModelRegistry.save_model(user_id, model)

        return {"message": "Model trained successfully", "records_used": len(df)}