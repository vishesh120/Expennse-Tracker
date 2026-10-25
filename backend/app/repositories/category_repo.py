from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase


class CategoryRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.categories

    async def list_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"$or": [{"is_system": True}, {"user_id": user_id}]}).sort([("name", 1)])
        items = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            items.append(doc)
        return items

    async def create_custom(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        cat_id = str(uuid.uuid4())
        doc = {
            "_id": cat_id,
            "user_id": user_id,
            "name": data["name"].strip(),
            "type": data.get("type", "expense"),
            "color": data.get("color", "#6366f1"),
            "icon": data.get("icon", "Tag"),
            "is_system": False,
            "created_at": datetime.now(timezone.utc)
        }
        await self.collection.insert_one(doc)
        doc["id"] = cat_id
        return doc

    async def delete_custom(self, user_id: str, category_id: str) -> bool:
        res = await self.collection.delete_one({"_id": category_id, "user_id": user_id, "is_system": False})
        return res.deleted_count > 0
