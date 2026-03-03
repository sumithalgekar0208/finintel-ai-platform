import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AnomalyModelTrainer:

    @staticmethod
    def train(X):
        """
        Train Isolation Forest model.
        """

        scaler = StandardScaler()
        X_scaled = pd.DataFrame(
            scaler.fit_transform(X),
            columns=X.columns,
            index=X.index
        )

        model = IsolationForest(
            n_estimators=200,
            contamination=0.02, #2% anomalies
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_scaled)

        return model, scaler