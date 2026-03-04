import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.db.models import Transaction, Category, User


def generate_random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


def get_month_starts(start_date, end_date):
    """Generate first day of each month between two dates."""
    months = []
    current = start_date.replace(day=1)

    while current <= end_date:
        months.append(current)
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    return months


def seed_transactions(user_id: int, years: int = 2) -> int:
    db: Session = next(get_db())

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print("User not found")
        return

    categories = db.query(Category).all()
    if not categories:
        print("No categories found")
        return

    # Try to find specific categories by name (optional)
    salary_category = next((c for c in categories if "salary" in c.name.lower()), None)
    rent_category = next((c for c in categories if "pay-rent" in c.name.lower()), None)
    car_emi_category = next((c for c in categories if "car-emi" in c.name.lower()), None)
    exclude_keywords = ["salary", "pay-rent", "car-emi"]

    expense_categories = [
        c for c in categories
        if not any(keyword in c.name.lower() for keyword in exclude_keywords)
    ]

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)

    transactions = []

    # -------------------------
    # Monthly Salary (Fixed Income)
    # -------------------------
    if salary_category:
        month_starts = get_month_starts(start_date, end_date)

        for month in month_starts:
            salary_date = month.replace(day=1)

            transactions.append(
                Transaction(
                    amount=75000,  # fixed salary
                    transaction_date=salary_date,
                    description="Monthly Salary",
                    category_id=salary_category.id,
                    created_by=user_id,
                    updated_by=user_id,
                    user_id=user_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            )


    # -------------------------
    # Monthly Rent (Recurring)
    # -----------------------
    if rent_category:
        month_starts = get_month_starts(start_date, end_date)
        description = f"Expense - {rent_category.name}"

        for month in month_starts:
            rent_date = month.replace(day=5)
            amount = 12000

            # Inject one anomaly very hight rent
            pay_rent_anomaly_injected = False
            if month.year == start_date.year + 1 and month.month == 6 and not pay_rent_anomaly_injected:
                amount = 60000  # anomaly
                pay_rent_anomaly_injected = True

            transactions.append(
                Transaction(
                    amount=amount,
                    transaction_date=rent_date,
                    description=description,
                    category_id=rent_category.id,
                    created_by=user_id,
                    updated_by=user_id,
                    user_id=user_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            )


    # -------------------------
    # Car EMI (Recurring)
    # -----------------------
    if car_emi_category:
        month_starts = get_month_starts(start_date, end_date)
        description = f"Expense - {car_emi_category.name}"
        car_emi_anomaly_injected = False
        for month in month_starts:
            car_emi_date = month.replace(day=5)
            amount = 8500

            # Inject one anomaly very hight rent
            if month.year == start_date.year + 2 and month.month == 5 and not car_emi_anomaly_injected:
                amount = 45000  # anomaly
                car_emi_anomaly_injected = True

            transactions.append(
                Transaction(
                    amount=amount,
                    transaction_date=car_emi_date,
                    description=description,
                    category_id=car_emi_category.id,
                    created_by=user_id,
                    updated_by=user_id,
                    user_id=user_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            )


    # -------------------------
    # Yearly Bonus (One-time income per year)
    # -------------------------
    for year in range(start_date.year, end_date.year + 1):
        bonus_date = datetime(year, random.randint(1, 12), random.randint(1, 28))

        if start_date <= bonus_date <= end_date:
            if salary_category:
                transactions.append(
                    Transaction(
                        amount=random.randint(20000, 100000),
                        transaction_date=bonus_date,
                        description="Yearly Bonus",
                        category_id=salary_category.id,
                        created_by=user_id,
                        updated_by=user_id,
                        user_id=user_id,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                )

    # -------------------------
    # Random Expenses
    # -------------------------
    for _ in range(15000):
        category = random.choice(expense_categories)

        transactions.append(
            Transaction(
                amount=round(random.uniform(100, 5000), 2),
                transaction_date=generate_random_date(start_date, end_date),
                description=f"Expense - {category.name}",
                category_id=category.id,
                created_by=user_id,
                updated_by=user_id,
                user_id=user_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        )

    db.bulk_save_objects(transactions)
    db.commit()
    db.close()

    return int(len(transactions))


if __name__ == "__main__":
    transaction_count = 0
    for user_id in range(1, 6):  # Assuming you have 5 users
        transaction_count += seed_transactions(user_id=user_id, years=5)

    print(f"Total transactions inserted: {transaction_count}")