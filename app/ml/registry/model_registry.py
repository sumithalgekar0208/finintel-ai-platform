import os
import joblib

MODEL_DIR = "app/ml/models"

class ModelRegistry:

    @staticmethod
    def get_model_path(user_id: int):
        return os.path.join(MODEL_DIR, f"user_{user_id}_anomaly.pkl")
    

    @staticmethod
    def save_model(user_id: int, model, scaler=None):
        os.makedirs(MODEL_DIR, exist_ok=True)
        path = ModelRegistry.get_model_path(user_id)
        joblib.dump({"model": model, "scaler": scaler}, path)


    @staticmethod
    def load_model(user_id: int):
        path = ModelRegistry.get_model_path(user_id)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Model not found user {user_id}")
        
        return joblib.load(path)