import hashlib
import io
import csv
from typing import Dict, Any, List, Optional, Tuple
from fastapi import HTTPException, status
from app.repositories.transaction_repo import TransactionRepository
from app.ai.categorizer import categorizer_engine


class TransactionService:
    def __init__(self, txn_repo: TransactionRepository):
        self.txn_repo = txn_repo

    def _compute_import_hash(self, date: str, amount: float, title: str, payment_method: str) -> str:
        s = f"{date.strip()}-{amount:.2f}-{title.strip().lower()}-{payment_method.strip().lower()}"
        return hashlib.md5(s.encode("utf-8")).hexdigest()

    async def create_transaction(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        amount = round(float(data["amount"]), 2)
        date_val = str(data["date"]).strip()
        title_val = str(data["title"]).strip()
        method_val = str(data.get("payment_method", "UPI")).strip()

        # Generate deduplication hash
        data["import_hash"] = self._compute_import_hash(date_val, amount, title_val, method_val)

        # Automatic category suggestion if category wasn't provided or is empty
        if not data.get("category"):
            pred = categorizer_engine.predict(title=title_val, description=data.get("description", ""))
            data["category"] = pred["predicted_category"]
            data["ai_suggested_category"] = pred["predicted_category"]
            data["ai_confidence"] = pred["confidence"]
            data["is_user_confirmed"] = False

        return await self.txn_repo.create(user_id, data)

    async def update_transaction(self, user_id: str, txn_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        existing = await self.txn_repo.get_by_id(txn_id, user_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

        # If date, amount, title or payment_method is updated, recompute hash
        new_date = data.get("date", existing["date"])
        new_amt = round(float(data.get("amount", existing["amount"])), 2)
        new_title = data.get("title", existing["title"])
        new_method = data.get("payment_method", existing.get("payment_method", "UPI"))
        data["import_hash"] = self._compute_import_hash(new_date, new_amt, new_title, new_method)

        updated = await self.txn_repo.update(txn_id, user_id, data)
        return updated

    async def delete_transaction(self, user_id: str, txn_id: str) -> bool:
        existing = await self.txn_repo.get_by_id(txn_id, user_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        return await self.txn_repo.delete(txn_id, user_id)

    async def get_transaction(self, user_id: str, txn_id: str) -> Dict[str, Any]:
        doc = await self.txn_repo.get_by_id(txn_id, user_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        return doc

    async def list_transactions(
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
        return await self.txn_repo.list_paginated(
            user_id=user_id,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            category=category,
            txn_type=txn_type,
            payment_method=payment_method,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )

    async def export_transactions_csv(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        txn_type: Optional[str] = None,
        payment_method: Optional[str] = None,
        search: Optional[str] = None
    ) -> str:
        items, _ = await self.txn_repo.list_paginated(
            user_id=user_id,
            skip=0,
            limit=10000,
            start_date=start_date,
            end_date=end_date,
            category=category,
            txn_type=txn_type,
            payment_method=payment_method,
            search=search,
            sort_by="date",
            sort_order="asc"
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Date", "Title", "Amount (INR)", "Type", "Category",
            "Payment Method", "UPI Reference", "Recurring", "Description"
        ])

        for item in items:
            writer.writerow([
                item.get("date", ""),
                item.get("title", ""),
                f"{float(item.get('amount', 0)):.2f}",
                item.get("type", "").capitalize(),
                item.get("category", ""),
                item.get("payment_method", ""),
                item.get("upi_reference", ""),
                "Yes" if item.get("is_recurring") else "No",
                item.get("description", "")
            ])

        return output.getvalue()
