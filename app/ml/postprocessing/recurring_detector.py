from collections import defaultdict
from datetime import timedelta


class RecurringDetector:

    AMOUNT_TOLERANCE_PERCENTAGE = 10 
    MIN_OCCURRENCES = 3


    def detect_recurring_transactions(self, transactions):
        """
        Detect recurring transactions.
        transactions: list of dicts (must include amount, category_id, transaction_date)
        Returns set of transaction_ids that are recurring.
        """

        recurring_groups = defaultdict(list)

        # Group by category
        for tx in transactions:
            recurring_groups[tx["category_id"]].append(tx)

        recurring_ids = set()

        for category, tx_list in recurring_groups.items():
            # Sort by date
            tx_list.sort(key=lambda x: x["transaction_date"])

            for i in range(len(tx_list)):
                base = tx_list[i]
                similar_count = 1
                for j in range(i + 1, len(tx_list)):
                    compare = tx_list[j]

                    # Check amount similarity
                    lower = base["amount"] * (1 - self.AMOUNT_TOLERANCE_PERCENTAGE / 100)
                    upper = base["amount"] * (1 + self.AMOUNT_TOLERANCE_PERCENTAGE / 100)

                    if not (lower <= compare["amount"] <= upper):
                        continue

                    # Check roughly monthly gap (25–35 days)
                    delta_days = (compare["transaction_date"] - base["transaction_date"]).days

                    if 25 <= delta_days <= 35:
                        similar_count += 1

                if similar_count >= self.MIN_OCCURRENCES:
                    recurring_ids.add(base["transaction_id"])

        return recurring_ids