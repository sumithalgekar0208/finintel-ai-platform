from app.db.session import SessionLocal
from app.ml.pipelines.anomaly_inference import AnomalyInferencePipeline


class TestAnomaly:

    def test_anomaly_inference_pipeline(self, user_id: int):
        db = SessionLocal()

        try:
            results = AnomalyInferencePipeline().predict_for_user(db, user_id)

            print(f"Total transactions: {len(results)}")

            anomalies = [r for r in results if r["is_anomaly"]]
            print(f"Anomalies detected: {len(anomalies)}")

            print("\nTop 5 anomalies:")
            for a in sorted(anomalies, key=lambda x: x["anomaly_score"])[:5]:
                #print(f"Transaction ID: {a['transaction_id']}, Amount: {a['amount']}, Score: {a['anomaly_score']}")
                print(a)
        finally:
            db.close()


if __name__ == "__main__":
    test = TestAnomaly()
    test.test_anomaly_inference_pipeline(user_id=1)