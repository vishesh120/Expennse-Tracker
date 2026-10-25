from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase


class AIRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.ai_feedback

    async def save_feedback(self, user_id: str, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        doc_id = str(uuid.uuid4())
        doc = {
            "_id": doc_id,
            "user_id": user_id,
            "title": feedback_data["title"].strip(),
            "predicted_category": feedback_data["predicted_category"],
            "confirmed_category": feedback_data["confirmed_category"],
            "confidence": feedback_data.get("confidence", 0.0),
            "created_at": datetime.now(timezone.utc)
        }
        await self.collection.insert_one(doc)
        doc["id"] = doc_id
        return doc

    async def get_all_training_samples(self) -> List[Dict[str, Any]]:
        cursor = self.collection.find()
        items = []
        async for doc in cursor:
            items.append({
                "text": doc["title"],
                "category": doc["confirmed_category"]
            })
        return items
