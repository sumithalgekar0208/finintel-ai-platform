from sklearn.ensemble import IsolationForest


class AnomalyModelTrainer:

    @staticmethod
    def train(X):
        """
        Train Isolation Forest model.
        """

        model = IsolationForest(
            n_estimators=200,
            contamination=0.02, #2% anomalies
            random_state=42,
            n_jobs=-1
        )

        model.fit(X)

        return model