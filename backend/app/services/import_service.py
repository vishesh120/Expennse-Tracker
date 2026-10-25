import csv
import io
import hashlib
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from app.repositories.transaction_repo import TransactionRepository
from app.ai.categorizer import categorizer_engine


class ImportService:
    def __init__(self, txn_repo: TransactionRepository):
        self.txn_repo = txn_repo

    def _normalize_date(self, raw_date: str) -> Optional[str]:
        raw = raw_date.strip()
        # Common formats in India: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, DD/MM/YY
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y", "%d %b %Y", "%d-%b-%Y"]:
            try:
                dt = datetime.strptime(raw, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        # ISO format prefix
        if len(raw) >= 10 and re.match(r'^\d{4}-\d{2}-\d{2}', raw):
            return raw[:10]
        return None

    def _normalize_amount(self, raw_amt: Any) -> Optional[float]:
        if raw_amt is None:
            return None
        # Remove currency symbols (₹, INR, Rs, ,)
        clean = str(raw_amt).replace("₹", "").replace("INR", "").replace("Rs.", "").replace("Rs", "").replace(",", "").strip()
        try:
            val = float(clean)
            return abs(round(val, 2))
        except ValueError:
            return None

    def _compute_hash(self, date_str: str, amount: float, title: str, method: str) -> str:
        s = f"{date_str.strip()}-{amount:.2f}-{title.strip().lower()}-{method.strip().lower()}"
        return hashlib.md5(s.encode("utf-8")).hexdigest()

    async def process_csv_upload(
        self,
        user_id: str,
        csv_content: str,
        column_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Parses CSV, maps columns, deduplicates, auto-categorizes, and imports transactions.
        """
        f = io.StringIO(csv_content)
        reader = csv.reader(f)
        try:
            header_row = next(reader)
        except StopIteration:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file is empty.")

        # Clean header strings
        headers = [h.strip().lower().replace("_", " ").replace("-", " ") for h in header_row]

        # Automatic column detection if mapping is not explicitly provided
        col_map = column_mapping or {}
        if not col_map:
            for idx, h in enumerate(headers):
                if any(k in h for k in ["date", "txn date", "transaction date", "value date"]):
                    col_map.setdefault("date", idx)
                elif any(k in h for k in ["title", "description", "narration", "particulars", "remarks", "merchant"]):
                    col_map.setdefault("title", idx)
                elif any(k in h for k in ["amount", "txn amount", "debit", "withdrawal"]):
                    col_map.setdefault("amount", idx)
                elif any(k in h for k in ["type", "cr/dr", "d/c"]):
                    col_map.setdefault("type", idx)
                elif any(k in h for k in ["category"]):
                    col_map.setdefault("category", idx)
                elif any(k in h for k in ["payment method", "mode", "channel"]):
                    col_map.setdefault("payment_method", idx)
                elif any(k in h for k in ["upi", "ref", "utr", "reference no", "chq/ref no"]):
                    col_map.setdefault("upi_reference", idx)

        # Validate minimum required columns
        if "date" not in col_map or "title" not in col_map or "amount" not in col_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not automatically detect Date, Title, or Amount columns in CSV headers: {header_row}. Please provide standard headers or column mapping."
            )

        parsed_items = []
        hashes = []
        failed_count = 0

        for row_num, row in enumerate(reader, start=2):
            if not row or all(c.strip() == "" for c in row):
                continue

            try:
                raw_date = row[int(col_map["date"])] if int(col_map["date"]) < len(row) else ""
                clean_date = self._normalize_date(raw_date)

                raw_amt = row[int(col_map["amount"])] if int(col_map["amount"]) < len(row) else ""
                clean_amt = self._normalize_amount(raw_amt)

                raw_title = row[int(col_map["title"])] if int(col_map["title"]) < len(row) else ""
                clean_title = raw_title.strip()

                if not clean_date or clean_amt is None or clean_amt <= 0 or not clean_title:
                    failed_count += 1
                    continue

                # Determine transaction type
                raw_type = row[int(col_map["type"])].strip().lower() if "type" in col_map and int(col_map["type"]) < len(row) else ""
                if "cr" in raw_type or "credit" in raw_type or "deposit" in raw_type or "income" in raw_type:
                    txn_type = "income"
                else:
                    txn_type = "expense"

                # Payment method & UPI reference
                payment_method = "UPI"
                if "payment_method" in col_map and int(col_map["payment_method"]) < len(row):
                    pm = row[int(col_map["payment_method"])].strip()
                    if pm:
                        payment_method = pm

                upi_ref = None
                if "upi_reference" in col_map and int(col_map["upi_reference"]) < len(row):
                    ref = row[int(col_map["upi_reference"])].strip()
                    if ref:
                        upi_ref = ref

                # Category
                category = None
                if "category" in col_map and int(col_map["category"]) < len(row):
                    cat_val = row[int(col_map["category"])].strip()
                    if cat_val:
                        category = cat_val

                # Auto-predict category if not specified
                ai_suggested = None
                ai_conf = None
                is_confirmed = True

                if not category:
                    pred = categorizer_engine.predict(title=clean_title)
                    category = pred["predicted_category"]
                    ai_suggested = pred["predicted_category"]
                    ai_conf = pred["confidence"]
                    is_confirmed = False

                item_hash = self._compute_hash(clean_date, clean_amt, clean_title, payment_method)
                hashes.append(item_hash)

                parsed_items.append({
                    "title": clean_title,
                    "amount": clean_amt,
                    "type": txn_type,
                    "date": clean_date,
                    "category": category,
                    "payment_method": payment_method,
                    "upi_reference": upi_ref,
                    "description": f"Imported from CSV row {row_num}",
                    "is_recurring": False,
                    "ai_suggested_category": ai_suggested,
                    "ai_confidence": ai_conf,
                    "is_user_confirmed": is_confirmed,
                    "import_hash": item_hash
                })
            except Exception:
                failed_count += 1

        # Duplicate checking
        existing_hashes = await self.txn_repo.check_duplicates(user_id, hashes)
        valid_items = []
        duplicate_count = 0

        for item in parsed_items:
            if item["import_hash"] in existing_hashes:
                duplicate_count += 1
            else:
                valid_items.append(item)
                existing_hashes.add(item["import_hash"])  # avoid duplicates within the same batch

        # Bulk insert valid items
        created = []
        if valid_items:
            created = await self.txn_repo.create_many(user_id, valid_items)

        return {
            "total_rows_processed": len(parsed_items) + failed_count,
            "imported_count": len(created),
            "duplicate_count": duplicate_count,
            "failed_count": failed_count,
            "status": "completed" if len(created) > 0 else ("duplicates_only" if duplicate_count > 0 else "failed")
        }
