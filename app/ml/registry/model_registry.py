from pathlib import Path
import joblib
from functools import lru_cache

MODEL_DIR = Path("app/ml/models")


class ModelRegistry:

    @staticmethod
    def get_model_path(user_id: int) -> Path:
        return MODEL_DIR / f"user_{user_id}_anomaly.pkl"
    

    @staticmethod
    def save_model(user_id: int, model_artifacts: dict):
        required_keys = ["model", "scaler", "feature_stats", "feature_columns", "recurring_profiles"]
        for key in required_keys:
            if key not in model_artifacts:
                raise ValueError(f"Missing required key in model artifacts: {key}")

        # ----------------------------
        # Save trained model
        # ----------------------------
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        path = ModelRegistry.get_model_path(user_id)
        joblib.dump(model_artifacts, path)

        # ---------------------------
        # Clear cache
        # ---------------------------
        ModelRegistry.clear_cache()


    @staticmethod
    @lru_cache(maxsize=32)
    def load_model(user_id: int):
        # ----------------------------
        # Load model artifact for user
        # ----------------------------
        path = ModelRegistry.get_model_path(user_id)

        if not path.exists():
            raise FileNotFoundError(f"Model not found user {user_id}")
        
        return joblib.load(path)
    

    @staticmethod
    def clear_cache():
        ModelRegistry.load_model.cache_clear()