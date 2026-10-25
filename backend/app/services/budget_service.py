from typing import Dict, Any, List, Optional
import calendar
from datetime import datetime
from fastapi import HTTPException, status
from app.repositories.budget_repo import BudgetRepository
from app.repositories.transaction_repo import TransactionRepository


class BudgetService:
    def __init__(self, budget_repo: BudgetRepository, txn_repo: TransactionRepository):
        self.budget_repo = budget_repo
        self.txn_repo = txn_repo

    async def upsert_budget(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        budget = await self.budget_repo.upsert(user_id, data)
        return await self.calculate_budget_status(user_id, budget["month"])

    async def calculate_budget_status(self, user_id: str, month: str) -> Dict[str, Any]:
        budget = await self.budget_repo.get_by_month(user_id, month)
        if not budget:
            # Default empty budget for this month
            budget = {
                "id": "",
                "user_id": user_id,
                "month": month,
                "overall_budget": 0.0,
                "category_budgets": {},
                "alert_thresholds": [50, 80, 100]
            }

        # Calculate month date range
        year, m = map(int, month.split("-"))
        _, last_day = calendar.monthrange(year, m)
        start_date = f"{month}-01"
        end_date = f"{month}-{last_day:02d}"

        # Fetch actual transactions in month
        txns = await self.txn_repo.get_transactions_in_range(user_id, start_date, end_date, txn_type="expense")

        total_spent = sum(float(t["amount"]) for t in txns)
        category_spending: Dict[str, float] = {}
        for t in txns:
            cat = t.get("category", "Other")
            category_spending[cat] = category_spending.get(cat, 0.0) + float(t["amount"])

        overall_budget = float(budget.get("overall_budget", 0.0))
        overall_remaining = max(0.0, overall_budget - total_spent)
        overall_pct = round((total_spent / overall_budget * 100), 1) if overall_budget > 0 else 0.0

        thresholds = budget.get("alert_thresholds", [50, 80, 100])
        alerts = []

        # Overall alerts
        if overall_budget > 0:
            for th in sorted(thresholds, reverse=True):
                if overall_pct >= th:
                    alerts.append({
                        "id": f"overall-{th}",
                        "type": "overall",
                        "category": None,
                        "threshold": th,
                        "message": f"Overall monthly budget has crossed {th}% ({overall_pct}% spent of ₹{round(overall_budget, 2)}).",
                        "current_percentage": overall_pct,
                        "spent": round(total_spent, 2),
                        "budget": round(overall_budget, 2)
                    })
                    break  # show highest threshold crossed

        # Category statuses & alerts
        category_statuses = []
        cat_budgets = budget.get("category_budgets", {})
        
        # Merge categories present in budget and categories with actual spending
        all_cats = set(cat_budgets.keys()) | set(category_spending.keys())
        for cat in sorted(all_cats):
            budgeted = float(cat_budgets.get(cat, 0.0))
            spent = round(float(category_spending.get(cat, 0.0)), 2)
            remaining = max(0.0, budgeted - spent)
            pct = round((spent / budgeted * 100), 1) if budgeted > 0 else 0.0

            if pct >= 100:
                cat_status = "exceeded"
            elif pct >= 80:
                cat_status = "warning"
            else:
                cat_status = "ok"

            category_statuses.append({
                "category": cat,
                "budgeted": budgeted,
                "spent": spent,
                "remaining": remaining,
                "percentage_used": pct,
                "status": cat_status
            })

            if budgeted > 0:
                for th in sorted(thresholds, reverse=True):
                    if pct >= th:
                        alerts.append({
                            "id": f"cat-{cat}-{th}",
                            "type": "category",
                            "category": cat,
                            "threshold": th,
                            "message": f"{cat} budget has reached {pct}% (₹{spent} of ₹{budgeted}).",
                            "current_percentage": pct,
                            "spent": spent,
                            "budget": budgeted
                        })
                        break

        return {
            "id": budget.get("id", ""),
            "user_id": user_id,
            "month": month,
            "overall_budget": overall_budget,
            "category_budgets": cat_budgets,
            "alert_thresholds": thresholds,
            "total_spent": round(total_spent, 2),
            "overall_remaining": round(overall_remaining, 2),
            "overall_percentage": overall_pct,
            "category_statuses": category_statuses,
            "alerts": alerts
        }

    async def list_budgets_history(self, user_id: str) -> List[Dict[str, Any]]:
        raw_budgets = await self.budget_repo.list_budgets(user_id)
        history = []
        for b in raw_budgets:
            status_item = await self.calculate_budget_status(user_id, b["month"])
            history.append(status_item)
        return history

    async def delete_budget(self, user_id: str, budget_id: str) -> bool:
        return await self.budget_repo.delete(user_id, budget_id)
