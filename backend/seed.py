import asyncio
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import connect_to_database, close_database_connection, get_db
from app.repositories.user_repo import UserRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.budget_repo import BudgetRepository
from app.core.security import hash_password
from app.ai.synthetic_data import generate_sample_transactions


async def main():
    print("Connecting to database...")
    await connect_to_database()
    db = get_db()

    user_repo = UserRepository(db)
    txn_repo = TransactionRepository(db)
    budget_repo = BudgetRepository(db)

    email = "demo@expensetracker.in"
    password = "DemoPassword123!"

    print(f"Checking if demo user '{email}' exists...")
    user = await user_repo.get_by_email(email)

    if not user:
        print("Creating demo user...")
        user = await user_repo.create_user({
            "email": email,
            "password_hash": hash_password(password),
            "full_name": "Rohan Sharma",
            "occupation": "Working Professional",
            "monthly_income": 65000.0,
            "phone": "+91 98765 43210"
        })
        print(f"Created demo user with ID: {user['id']}")
    else:
        print(f"Found existing demo user: {user['id']}")

    user_id = user["id"]

    # Generate sample transactions spanning the past 45 days
    print("Generating 45 days of realistic Indian expense and salary data...")
    samples = generate_sample_transactions(user_id, days=45)
    
    # Check duplicates and insert
    hashes = [s["import_hash"] for s in samples if s.get("import_hash")]
    existing_hashes = await txn_repo.check_duplicates(user_id, hashes)
    
    to_insert = [s for s in samples if s.get("import_hash") not in existing_hashes]
    if to_insert:
        created = await txn_repo.create_many(user_id, to_insert)
        print(f"Successfully inserted {len(created)} transactions.")
    else:
        print("Transactions already present, skipping duplicate insertions.")

    # Configure budgets for current and previous month
    months = sorted(list({t["date"][:7] for t in samples}), reverse=True)
    for m in months[:2]:
        await budget_repo.upsert(user_id, {
            "month": m,
            "overall_budget": 35000.0,
            "category_budgets": {
                "Food and groceries": 10000.0,
                "Transportation": 4000.0,
                "Rent and housing": 18000.0,
                "Shopping": 5000.0,
                "Bills and utilities": 3000.0,
                "Entertainment": 2000.0
            },
            "alert_thresholds": [50, 80, 100]
        })
        print(f"Configured budget for month: {m}")

    await close_database_connection()
    print("\n--- SEED COMPLETE ---")
    print(f"Email:    {email}")
    print(f"Password: {password}")
    print("You can now login and explore all dashboards, charts, and forecasts immediately!\n")


if __name__ == "__main__":
    asyncio.run(main())
