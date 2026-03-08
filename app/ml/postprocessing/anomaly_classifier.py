class AnomalyClassifier:


    def get_severity(self, score: float, amount_ratio: float | None = None) -> str:
        """
        Classify anomaly severity based on score.
        More negative = more anomalous.
        """

        # ----------------------------------
        # High severity if amount is very abnormal
        # -----------------------------------
        if amount_ratio and amount_ratio >= 2:
            return "HIGH" 

        if score < -0.08:
            return "HIGH"
        elif score < -0.05:
            return "MEDIUM"
        else:
            return "LOW"


    def get_confidence(self, score: float, amount_ratio: float | None = None) -> float:
        """
        Convert anomaly score into a confidence metric (0 to 1).
        """

        # --------------------------------
        # Model confidence based on score
        # --------------------------------
        model_conf = min(max((-score) / 0.15, 0), 1)

        # -------------------------------
        # Amount ratio confidence
        # -------------------------------
        if amount_ratio:
            ratio_conf = min(amount_ratio / 3, 1)
        else:
            ratio_conf = 0
        
        # --------------------------------
        # Combine model confidence and amount ratio confidence
        # --------------------------------
        confidence = max(model_conf, ratio_conf)

        # --------------------------------
        # Avoid absolute certainty
        # --------------------------------
        confidence = min(confidence, 0.95)

        return round(confidence, 2)