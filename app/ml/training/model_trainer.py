import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AnomalyModelTrainer:

    @staticmethod
    def train(X: pd.DataFrame):
        """
        Train Isolation Forest model.
        """

        # ------------------------------------
        # Handle missing values
        # ------------------------------------
        X = X.fillna(0)

        # ------------------------------------
        # Save feature order
        # ------------------------------------
        feature_columns = X.columns.tolist()

        # ------------------------------------
        # Feature statistics
        # ------------------------------------
        feature_stats = {
            "mean": X.mean().to_dict(),
            "std": X.std().replace(0, 1).to_dict()
        }

        # ------------------------------------
        # Feature scaling
        # ------------------------------------
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # ------------------------------------
        # Isolation Forest Model
        # ------------------------------------
        model = IsolationForest(
            n_estimators=200,
            contamination=0.01,
            random_state=42,
            max_samples="auto",
            bootstrap=False,
            n_jobs=-1
        )

        model.fit(X_scaled)

        # -------------------------------------
        # Model artifacts to return
        # -------------------------------------
        model_artifacts = {
            "model": model,
            "scaler": scaler,
            "feature_stats": feature_stats,
            "feature_columns": feature_columns
        }

        return model_artifacts