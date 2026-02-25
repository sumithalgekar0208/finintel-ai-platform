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


def seed_transactions(user_id: int, years: int = 2):
    db: Session = next(get_db())

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print("User not found")
        return

    categories = db.query(Category).filter(Category.created_by == user_id).all()
    if not categories:
        print("No categories found")
        return

    # Try to find specific categories by name (optional)
    salary_category = next((c for c in categories if "salary" in c.name.lower()), None)
    expense_categories = [c for c in categories if "salary" not in c.name.lower()]

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)

    transactions = []

    # -------------------------
    # 1️⃣ Monthly Salary (Fixed Income)
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
    # 2️⃣ Yearly Bonus (One-time income per year)
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
    # 3️⃣ Random Expenses
    # -------------------------
    for _ in range(2500):
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

    print(f"Inserted {len(transactions)} realistic transactions.")


if __name__ == "__main__":
    seed_transactions(user_id=1, years=2)