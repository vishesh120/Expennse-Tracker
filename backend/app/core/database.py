import logging
from typing import Optional
from datetime import datetime, timezone
import uuid
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import mongomock_motor
from pymongo import ASCENDING
from app.core.config import settings

logger = logging.getLogger("expense_tracker.db")

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    is_mock: bool = False

db_instance = Database()

DEFAULT_CATEGORIES = [
    {"name": "Food and groceries", "type": "expense", "color": "#f97316", "icon": "Utensils", "is_system": True},
    {"name": "Transportation", "type": "expense", "color": "#3b82f6", "icon": "Car", "is_system": True},
    {"name": "Shopping", "type": "expense", "color": "#ec4899", "icon": "ShoppingBag", "is_system": True},
    {"name": "Education", "type": "expense", "color": "#8b5cf6", "icon": "GraduationCap", "is_system": True},
    {"name": "Rent and housing", "type": "expense", "color": "#10b981", "icon": "Home", "is_system": True},
    {"name": "Bills and utilities", "type": "expense", "color": "#eab308", "icon": "Zap", "is_system": True},
    {"name": "Healthcare", "type": "expense", "color": "#ef4444", "icon": "HeartPulse", "is_system": True},
    {"name": "Entertainment", "type": "expense", "color": "#06b6d4", "icon": "Film", "is_system": True},
    {"name": "Travel", "type": "expense", "color": "#14b8a6", "icon": "Plane", "is_system": True},
    {"name": "Salary and income", "type": "income", "color": "#22c55e", "icon": "Wallet", "is_system": True},
    {"name": "Investments and savings", "type": "both", "color": "#6366f1", "icon": "TrendingUp", "is_system": True},
    {"name": "Other", "type": "both", "color": "#64748b", "icon": "MoreHorizontal", "is_system": True},
]

async def connect_to_database():
    """Connect to MongoDB with graceful fallback to Mock MongoDB."""
    use_mock = settings.USE_MOCK_DB.lower() == "true"
    auto_mode = settings.USE_MOCK_DB.lower() == "auto"

    if not use_mock:
        try:
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
            client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000
            )
            # Test connection
            await client.admin.command('ping')
            db_instance.client = client
            db_instance.db = client[settings.DATABASE_NAME]
            db_instance.is_mock = False
            logger.info(f"Successfully connected to MongoDB database: {settings.DATABASE_NAME}")
        except Exception as e:
            if auto_mode:
                logger.warning(
                    f"Could not connect to MongoDB server ({e}). Falling back to in-memory Mock MongoDB engine."
                )
                use_mock = True
            else:
                logger.error(f"MongoDB connection failed: {e}")
                raise e

    if use_mock:
        logger.info("Initializing in-memory resilient Async MongoMock database engine...")
        client = mongomock_motor.AsyncMongoMockClient()
        db_instance.client = client
        db_instance.db = client[settings.DATABASE_NAME]
        db_instance.is_mock = True
        logger.info("Mock MongoDB initialized successfully.")

    # Initialize indexes and default system categories
    await setup_database_indexes()
    await seed_system_categories()
    await seed_initial_demo_if_empty()


async def close_database_connection():
    """Close the database client connection."""
    if db_instance.client:
        db_instance.client.close()
        logger.info("Closed MongoDB database connection.")


async def setup_database_indexes():
    """Ensure essential indexes exist for performance and constraints."""
    db = db_instance.db
    if db is None:
        return

    try:
        # Users index
        await db.users.create_index([("email", ASCENDING)], unique=True)
        # Transactions index
        await db.transactions.create_index([("user_id", ASCENDING), ("date", ASCENDING)])
        await db.transactions.create_index([("user_id", ASCENDING), ("import_hash", ASCENDING)])
        # Budgets index
        await db.budgets.create_index([("user_id", ASCENDING), ("month", ASCENDING)], unique=True)
        # Categories index
        await db.categories.create_index([("user_id", ASCENDING), ("name", ASCENDING)])
    except Exception as e:
        logger.warning(f"Index creation note: {e}")


async def seed_system_categories():
    """Seed default system categories if not already present."""
    db = db_instance.db
    if db is None:
        return

    try:
        count = await db.categories.count_documents({"is_system": True})
        if count == 0:
            for cat in DEFAULT_CATEGORIES:
                await db.categories.insert_one({
                    **cat,
                    "user_id": "system"
                })
            logger.info("Default categories seeded successfully.")
    except Exception as e:
        logger.warning(f"Seeding default categories note: {e}")


async def seed_initial_demo_if_empty():
    """Seeds the demo user account if the database is newly initialized."""
    db = db_instance.db
    if db is None:
        return
    try:
        user_count = await db.users.count_documents({})
        if user_count == 0:
            from app.core.security import hash_password
            from app.ai.synthetic_data import generate_sample_transactions

            user_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            demo_user = {
                "_id": user_id,
                "email": "demo@expensetracker.in",
                "password_hash": hash_password("DemoPassword123!"),
                "full_name": "Rohan Sharma",
                "occupation": "Working Professional",
                "monthly_income": 65000.0,
                "phone": "+91 98765 43210",
                "preferences": {
                    "dark_mode": False,
                    "currency": "INR",
                    "currency_symbol": "₹",
                    "budget_alerts_enabled": True,
                    "alert_thresholds": [50, 80, 100]
                },
                "created_at": now,
                "updated_at": now
            }
            await db.users.insert_one(demo_user)

            samples = generate_sample_transactions(user_id, days=45)
            to_insert = []
            for s in samples:
                to_insert.append({
                    "_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    **s,
                    "created_at": now,
                    "updated_at": now
                })
            if to_insert:
                await db.transactions.insert_many(to_insert)

            months = sorted(list({t["date"][:7] for t in samples}), reverse=True)
            for m in months[:2]:
                await db.budgets.insert_one({
                    "_id": str(uuid.uuid4()),
                    "user_id": user_id,
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
                    "alert_thresholds": [50, 80, 100],
                    "created_at": now,
                    "updated_at": now
                })
            logger.info("Auto-seeded initial demo user and transactions.")
    except Exception as e:
        logger.warning(f"Initial demo seeding note: {e}")


def get_db() -> AsyncIOMotorDatabase:
    """Dependency injection helper for FastAPI endpoints."""
    if db_instance.db is None:
        raise RuntimeError("Database not initialized")
    return db_instance.db
