from app.db.session import SessionLocal
from app.ml.pipelines.anomaly_training_pipeline import AnomalyTrainingPipeline


def train_for_user(user_id: int):
    db = SessionLocal()
    try:
        result = AnomalyTrainingPipeline.run(db, user_id)
        print(result)
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 -m app.ml.training.train_anomaly.py <user_id>")

    user_id = int(sys.argv[1])
    train_for_user(user_id)