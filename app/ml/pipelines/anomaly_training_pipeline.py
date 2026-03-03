import pandas as pd
from sqlalchemy.orm import Session

from app.db.models.transaction import Transaction
from app.db.models.category  import Category, TransactionType
from app.ml.pipelines.anomaly_inference import AnomalyInferencePipeline
from app.ml.training.feature_builder import TransactionFeatureBuilder
from app.ml.training.model_trainer import AnomalyModelTrainer
from app.ml.registry.model_registry import ModelRegistry


class AnomalyTrainingPipeline:

    @staticmethod
    def run(db: Session, user_id: int):
        # Fetch user transactions
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
        
        # Convert to dataframe
        df = pd.DataFrame([{
            "amount": t.amount,
            "transaction_date": t.transaction_date,
            "category_id": t.category_id
        } for t in transactions])

        # Build features
        X = TransactionFeatureBuilder.build_features(df)

        # Train model
        model, scaler = AnomalyModelTrainer.train(X)

        # Save model
        ModelRegistry.save_model(user_id, model, scaler)

        # Clear inference cache
        AnomalyInferencePipeline._get_cached_model.cache_clear()

        return {"message": "Model trained successfully", "records_used": len(df)}