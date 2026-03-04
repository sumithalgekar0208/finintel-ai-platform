class AnomalyClassifier:

    def get_severity(self, score: float) -> str:
        """
        Classify anomaly severity based on score.
        More negative = more anomalous.
        """

        if score < -0.08:
            return "HIGH"
        elif score < -0.05:
            return "MEDIUM"
        else:
            return "LOW"


    def get_confidence(self, score: float) -> float:
        """
        Convert anomaly score into a confidence metric (0 to 1).
        """

        # Normalize roughly assuming score range [-0.15, 0.15]
        normalized = min(max((-score) / 0.15, 0), 1)

        return round(normalized, 2)