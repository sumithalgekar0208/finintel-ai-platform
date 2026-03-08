class AnomalyReasonBuilder:

    def build(self, explanations: list) -> str:
        """
        Build natural explanations using feature values.
        """

        if not explanations:
            return "This transaction looks unusual compared to your normal spending patterns."

        reasons = []

        for item in explanations:
            feature = item.get("feature")
            value = item.get("value")

            if feature == "amount_deviation_ratio" and value:
                if value > 3:
                    reasons.append(f"The amount is about {round(value,1)}× higher than your usual spending")

            elif feature == "amount_vs_category_mean" and value:
                if value > 2:
                    reasons.append(f"The amount is much higher than what you typically spend in this category")

            elif feature == "amount_zscore" and value:
                if abs(value) > 2:
                    reasons.append("The amount is significantly different from your normal spending pattern")

            elif feature == "category_freq":
                reasons.append("You rarely spend in this category")

            elif feature == "days_since_last_txn" and value:
                if value > 20:
                    reasons.append("It occurred after an unusually long gap since your last transaction")

            elif feature == "transaction_hour":
                reasons.append("It happened at an unusual time of day")

            elif feature == "is_weekend":
                reasons.append("It was made during the weekend, which is uncommon for you")

            elif feature == "rolling_mean_5":
                reasons.append("The amount differs from your recent spending trend")

        reasons = list(dict.fromkeys(reasons))[:3]

        if not reasons:
            return "This transaction deviates from your usual spending behavior."

        if len(reasons) == 1:
            return f"This transaction looks unusual because {reasons[0]}."

        if len(reasons) == 2:
            return f"This transaction looks unusual because {reasons[0]} and {reasons[1]}."

        return f"This transaction looks unusual because {reasons[0]}, {reasons[1]}, and {reasons[2]}."