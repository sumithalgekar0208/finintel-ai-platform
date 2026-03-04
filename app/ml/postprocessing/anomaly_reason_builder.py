class AnomalyReasonBuilder:
    
    FEATURE_REASON_MAP = {
        "category_freq": "belongs to a rarely used category",
        "amount": "amount is unusual compared to your past spending.",
        "transaction_hour": "occurred at an unusual time of day",
        "transaction_day": "occurred on an unusual day of the month",
        "transaction_month": "occurred in an unusual month",
        "is_weekend": "was made on weekend which is unusual",
    }


    def build(self, explanations: list) -> str:
        """
        Convert feature deviations into a readable sentence.
        """

        if not explanations:
            return ""

        reasons = []
        for item in explanations:
            feature = item.get("feature")
            if feature in self.FEATURE_REASON_MAP:
                reasons.append(self.FEATURE_REASON_MAP[feature])

        if not reasons:
            return "This transaction deviates from your normal spending patterns" 

        if len(reasons) == 1:
            return f"This expense {reasons[0]}."
        
        return "This expense " + " and ".join(reasons) + "."