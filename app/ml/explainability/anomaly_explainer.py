class AnomalyExplainer:
    
    def explain(self, transaction_row: dict, feature_stats: dict) -> list:
        """
        Generate a simple explanation for why a transaction is anomalous.
        """

        explanations = []
        for col in feature_stats["mean"].keys():
            mean = feature_stats["mean"][col]
            std = feature_stats["std"][col]

            value = transaction_row[col]

            z_score = abs((value - mean) / std if std > 0 else 0)
            explanations.append((col, z_score))

        # Sort by highest deviation
        explanations.sort(key=lambda x: x[1], reverse=True)

        # Top 2 features
        top_features = explanations[:2]

        return [
            {
                "feature": feature,
                "deviation": round(score, 2)
            }
            for feature, score in top_features
        ]