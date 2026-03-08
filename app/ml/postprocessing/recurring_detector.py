from collections import defaultdict
from statistics import median
from datetime import datetime


class RecurringDetector:

    AMOUNT_TOLERANCE_PERCENTAGE = 10
    DAY_TOLERANCE = 3
    MIN_OCCURRENCES = 3


    def detect_recurring_transactions(self, transactions):
        """
        Detect recurring monthly patterns.

        Returns:
        [
            {
                "category_id": int,
                "avg_amount": float,
                "day_of_month": int,
                "amount_tolerance": float
            }
        ]
        """

        grouped = defaultdict(list)

        # ------------------------------
        # Group transactions by category
        # ------------------------------
        for tx in transactions:
            if not isinstance(tx, dict):
                raise ValueError("Transactions must be dictionaries")
            grouped[tx["category_id"]].append(tx)

        recurring_profiles = []

        for category_id, tx_list in grouped.items():
            if len(tx_list) < self.MIN_OCCURRENCES:
                continue

            # ------------------------------
            # Sort transactions by date
            # ------------------------------
            tx_list.sort(key=lambda x: x["transaction_date"])

            amounts = [float(tx["amount"]) for tx in tx_list]

            days = [
                tx["transaction_date"].day
                if isinstance(tx["transaction_date"], datetime)
                else datetime.fromisoformat(tx["transaction_date"]).day
                for tx in tx_list
            ]

            avg_amount = median(amounts)

            # ------------------------------
            # Group days with tolerance
            # ------------------------------
            day_groups = defaultdict(int)
            for day in days:
                bucket = day // self.DAY_TOLERANCE
                day_groups[bucket] += 1

            most_common_bucket = max(day_groups,key=day_groups.get)

            if day_groups[most_common_bucket] >= self.MIN_OCCURRENCES:
                recurring_profiles.append({
                    "category_id": category_id,
                    "avg_amount": round(avg_amount, 2),
                    "day_bucket": most_common_bucket,
                    "amount_tolerance": self.AMOUNT_TOLERANCE_PERCENTAGE
                })

        return recurring_profiles
    

    def get_recurring_profiles(self, tx, recurring_profiles):
        """
        Get recurring profiles that match the transaction's category.
        """
        tx_day = (
            tx["transaction_date"].day
            if isinstance(tx["transaction_date"], datetime)
            else datetime.fromisoformat(tx["transaction_date"]).day
        )

        bucket = tx_day // self.DAY_TOLERANCE

        for profile in recurring_profiles:
            if tx["category_id"] != profile["category_id"]:
                continue

            if bucket != profile["day_bucket"]:
                continue

            return profile
        
        return None
    

    def is_recurring_transaction(self, tx, recurring_profiles):
        """
        Returns True if transaction matches recurring pattern.
        """
        profile = self.get_recurring_profiles(tx, recurring_profiles)

        if not profile:
            return False

        lower = profile["avg_amount"] * (1 - profile["amount_tolerance"] / 100)
        upper = profile["avg_amount"] * (1 + profile["amount_tolerance"] / 100)

        if not (lower <= tx["amount"] <= upper):
            return False

        return True