from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.users

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"_id": user_id})
        if doc:
            doc["id"] = doc["_id"]
            return doc
        return None

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"email": email.lower().strip()})
        if doc:
            doc["id"] = doc["_id"]
            return doc
        return None

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        doc = {
            "_id": user_id,
            "email": user_data["email"].lower().strip(),
            "password_hash": user_data["password_hash"],
            "full_name": user_data["full_name"],
            "phone": user_data.get("phone"),
            "occupation": user_data.get("occupation", "Working Professional"),
            "monthly_income": float(user_data.get("monthly_income", 0.0)),
            "preferences": user_data.get("preferences", {
                "dark_mode": False,
                "currency": "INR",
                "currency_symbol": "₹",
                "budget_alerts_enabled": True,
                "alert_thresholds": [50, 80, 100]
            }),
            "created_at": now,
            "updated_at": now
        }
        await self.collection.insert_one(doc)
        doc["id"] = user_id
        return doc

    async def update_user(self, user_id: str, update_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        update_dict["updated_at"] = datetime.now(timezone.utc)
        await self.collection.update_one({"_id": user_id}, {"$set": update_dict})
        return await self.get_by_id(user_id)

    async def update_password(self, user_id: str, new_password_hash: str) -> bool:
        res = await self.collection.update_one(
            {"_id": user_id},
            {"$set": {"password_hash": new_password_hash, "updated_at": datetime.now(timezone.utc)}}
        )
        return res.modified_count > 0
