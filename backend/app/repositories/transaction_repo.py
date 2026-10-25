from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
import re


class TransactionRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.transactions

    async def create(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        txn_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        doc = {
            "_id": txn_id,
            "user_id": user_id,
            "title": data["title"].strip(),
            "amount": round(float(data["amount"]), 2),
            "type": data["type"].lower().strip(),
            "date": data["date"],  # YYYY-MM-DD
            "category": data["category"].strip(),
            "payment_method": data.get("payment_method", "UPI"),
            "upi_reference": data.get("upi_reference"),
            "description": data.get("description"),
            "is_recurring": bool(data.get("is_recurring", False)),
            "recurring_frequency": data.get("recurring_frequency"),
            "ai_suggested_category": data.get("ai_suggested_category"),
            "ai_confidence": data.get("ai_confidence"),
            "is_user_confirmed": bool(data.get("is_user_confirmed", True)),
            "import_hash": data.get("import_hash"),
            "created_at": now,
            "updated_at": now
        }
        await self.collection.insert_one(doc)
        doc["id"] = txn_id
        return doc

    async def create_many(self, user_id: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        docs = []
        for item in items:
            txn_id = str(uuid.uuid4())
            doc = {
                "_id": txn_id,
                "user_id": user_id,
                "title": item["title"].strip(),
                "amount": round(float(item["amount"]), 2),
                "type": item["type"].lower().strip(),
                "date": item["date"],
                "category": item["category"].strip(),
                "payment_method": item.get("payment_method", "UPI"),
                "upi_reference": item.get("upi_reference"),
                "description": item.get("description"),
                "is_recurring": bool(item.get("is_recurring", False)),
                "recurring_frequency": item.get("recurring_frequency"),
                "ai_suggested_category": item.get("ai_suggested_category"),
                "ai_confidence": item.get("ai_confidence"),
                "is_user_confirmed": bool(item.get("is_user_confirmed", True)),
                "import_hash": item.get("import_hash"),
                "created_at": now,
                "updated_at": now
            }
            docs.append(doc)
        if docs:
            await self.collection.insert_many(docs)
            for d in docs:
                d["id"] = d["_id"]
        return docs

    async def get_by_id(self, txn_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.collection.find_one({"_id": txn_id, "user_id": user_id})
        if doc:
            doc["id"] = doc["_id"]
            return doc
        return None

    async def update(self, txn_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        clean_update = {k: v for k, v in update_data.items() if v is not None}
        if "amount" in clean_update:
            clean_update["amount"] = round(float(clean_update["amount"]), 2)
        if "type" in clean_update:
            clean_update["type"] = clean_update["type"].lower().strip()
        clean_update["updated_at"] = datetime.now(timezone.utc)

        await self.collection.update_one(
            {"_id": txn_id, "user_id": user_id},
            {"$set": clean_update}
        )
        return await self.get_by_id(txn_id, user_id)

    async def delete(self, txn_id: str, user_id: str) -> bool:
        res = await self.collection.delete_one({"_id": txn_id, "user_id": user_id})
        return res.deleted_count > 0

    async def list_paginated(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        txn_type: Optional[str] = None,
        payment_method: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "date",
        sort_order: str = "desc"
    ) -> Tuple[List[Dict[str, Any]], int]:
        query: Dict[str, Any] = {"user_id": user_id}

        if start_date and end_date:
            query["date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["date"] = {"$gte": start_date}
        elif end_date:
            query["date"] = {"$lte": end_date}

        if category:
            query["category"] = category
        if txn_type:
            query["type"] = txn_type.lower()
        if payment_method:
            query["payment_method"] = payment_method

        if search:
            # Case-insensitive substring match in title or description or upi_reference
            regex = {"$regex": re.escape(search), "$options": "i"}
            query["$or"] = [
                {"title": regex},
                {"description": regex},
                {"upi_reference": regex},
                {"category": regex}
            ]

        total = await self.collection.count_documents(query)
        direction = DESCENDING if sort_order.lower() == "desc" else ASCENDING
        sort_field = sort_by if sort_by in ["date", "amount", "title", "created_at"] else "date"

        cursor = self.collection.find(query).sort([(sort_field, direction), ("_id", direction)]).skip(skip).limit(limit)
        items = []
        async for doc in cursor:
            doc["id"] = doc["_id"]
            items.append(doc)

        return items, total

    async def get_transactions_in_range(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        txn_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"user_id": user_id}
        if start_date and end_date:
            query["date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["date"] = {"$gte": start_date}
        elif end_date:
            query["date"] = {"$lte": end_date}

        if txn_type:
            query["type"] = txn_type.lower()

        cursor = self.collection.find(query).sort([("date", ASCENDING)])
        items = []
        async for doc in cursor:
            doc["id"] = doc["_id"]
            items.append(doc)
        return items

    async def check_duplicates(self, user_id: str, import_hashes: List[str]) -> set:
        """Find which hashes already exist for this user."""
        if not import_hashes:
            return set()
        cursor = self.collection.find(
            {"user_id": user_id, "import_hash": {"$in": import_hashes}},
            {"import_hash": 1}
        )
        existing = set()
        async for doc in cursor:
            if doc.get("import_hash"):
                existing.add(doc["import_hash"])
        return existing
