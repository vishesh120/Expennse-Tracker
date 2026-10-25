from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase


class BudgetRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.budgets

    async def get_by_month(self, user_id: str, month: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"user_id": user_id, "month": month})
        if doc:
            doc["id"] = doc["_id"]
            return doc
        return None

    async def get_by_id(self, user_id: str, budget_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"_id": budget_id, "user_id": user_id})
        if doc:
            doc["id"] = doc["_id"]
            return doc
        return None

    async def upsert(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        month = data["month"]
        existing = await self.get_by_month(user_id, month)
        now = datetime.now(timezone.utc)

        if existing:
            update_data = {
                "overall_budget": round(float(data["overall_budget"]), 2),
                "category_budgets": {k: round(float(v), 2) for k, v in data.get("category_budgets", {}).items()},
                "alert_thresholds": data.get("alert_thresholds", [50, 80, 100]),
                "updated_at": now
            }
            await self.collection.update_one({"_id": existing["_id"]}, {"$set": update_data})
            return await self.get_by_id(user_id, existing["_id"])
        else:
            budget_id = str(uuid.uuid4())
            doc = {
                "_id": budget_id,
                "user_id": user_id,
                "month": month,
                "overall_budget": round(float(data["overall_budget"]), 2),
                "category_budgets": {k: round(float(v), 2) for k, v in data.get("category_budgets", {}).items()},
                "alert_thresholds": data.get("alert_thresholds", [50, 80, 100]),
                "created_at": now,
                "updated_at": now
            }
            await self.collection.insert_one(doc)
            doc["id"] = budget_id
            return doc

    async def update(self, user_id: str, budget_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        update_data = {k: v for k, v in data.items() if v is not None}
        if "overall_budget" in update_data:
            update_data["overall_budget"] = round(float(update_data["overall_budget"]), 2)
        if "category_budgets" in update_data:
            update_data["category_budgets"] = {k: round(float(v), 2) for k, v in update_data["category_budgets"].items()}
        update_data["updated_at"] = datetime.now(timezone.utc)

        await self.collection.update_one({"_id": budget_id, "user_id": user_id}, {"$set": update_data})
        return await self.get_by_id(user_id, budget_id)

    async def list_budgets(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"user_id": user_id}).sort([("month", -1)])
        items = []
        async for doc in cursor:
            doc["id"] = doc["_id"]
            items.append(doc)
        return items

    async def delete(self, user_id: str, budget_id: str) -> bool:
        res = await self.collection.delete_one({"_id": budget_id, "user_id": user_id})
        return res.deleted_count > 0
