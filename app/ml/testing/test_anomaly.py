from app.db.session import SessionLocal
from app.ml.pipelines.anomaly_inference import AnomalyInferencePipeline
import pandas as pd
import os

class TestAnomaly:

    def test_anomaly_inference_pipeline(self, user_id: int):
        db = SessionLocal()

        try:
            results = AnomalyInferencePipeline().predict_for_user(db, user_id)
            print(f"Total transactions: {len(results)}")

            # Convert to dataframe
            df = pd.DataFrame(results)

            # -------------------------
            # Ensure uploads directory exists
            # -------------------------
            base_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(base_dir, '../../../'))
            uploads_dir = os.path.join(project_root, "app", "uploads")

            # Ensure uploads directory exists
            os.makedirs(uploads_dir, exist_ok=True)

            # --------------------------
            # Anomaly path
            # --------------------------
            anomaly_path = os.path.join(uploads_dir, f"user_{user_id}_anomalies.csv")

            # Save anomalies to csv
            anomalies_df = df[df['is_anomaly'] == True]
            anomalies_df.to_csv(anomaly_path, index=False)
            print(f"Anomalies saved to {anomaly_path}: {len(anomalies_df)}")
        finally:
            db.close()


if __name__ == "__main__":
    test = TestAnomaly()
    test.test_anomaly_inference_pipeline(user_id=1)