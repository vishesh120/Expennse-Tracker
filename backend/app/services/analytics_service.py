import calendar
from datetime import datetime, timedelta, timezone, date
from typing import Dict, Any, List, Optional
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.budget_repo import BudgetRepository


class AnalyticsService:
    def __init__(self, txn_repo: TransactionRepository, budget_repo: BudgetRepository):
        self.txn_repo = txn_repo
        self.budget_repo = budget_repo

    def _resolve_date_range(
        self,
        period: str,
        custom_start: Optional[str] = None,
        custom_end: Optional[str] = None
    ) -> tuple[str, str, str, str]:
        """
        Returns (current_start, current_end, prev_start, prev_end)
        """
        today = datetime.now(timezone.utc).date()
        
        if period == "last_month":
            first_of_curr = today.replace(day=1)
            prev_last = first_of_curr - timedelta(days=1)
            prev_first = prev_last.replace(day=1)
            start_date = prev_first.strftime("%Y-%m-%d")
            end_date = prev_last.strftime("%Y-%m-%d")
            
            # comparison: month before last
            comp_last = prev_first - timedelta(days=1)
            comp_first = comp_last.replace(day=1)
            p_start = comp_first.strftime("%Y-%m-%d")
            p_end = comp_last.strftime("%Y-%m-%d")
            return start_date, end_date, p_start, p_end

        elif period == "last_30_days":
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")
            p_start = (today - timedelta(days=60)).strftime("%Y-%m-%d")
            p_end = (today - timedelta(days=31)).strftime("%Y-%m-%d")
            return start_date, end_date, p_start, p_end

        elif period == "custom" and custom_start and custom_end:
            start_date = custom_start
            end_date = custom_end
            s_d = datetime.strptime(start_date, "%Y-%m-%d").date()
            e_d = datetime.strptime(end_date, "%Y-%m-%d").date()
            days_span = (e_d - s_d).days + 1
            p_end = (s_d - timedelta(days=1)).strftime("%Y-%m-%d")
            p_start = (s_d - timedelta(days=days_span)).strftime("%Y-%m-%d")
            return start_date, end_date, p_start, p_end

        else:  # default: "this_month"
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
            _, last_day = calendar.monthrange(today.year, today.month)
            end_date = today.replace(day=last_day).strftime("%Y-%m-%d")

            first_of_curr = today.replace(day=1)
            prev_last = first_of_curr - timedelta(days=1)
            prev_first = prev_last.replace(day=1)
            p_start = prev_first.strftime("%Y-%m-%d")
            p_end = prev_last.strftime("%Y-%m-%d")
            return start_date, end_date, p_start, p_end

    async def get_dashboard_summary(
        self,
        user_id: str,
        period: str = "this_month",
        custom_start: Optional[str] = None,
        custom_end: Optional[str] = None,
        user_income: float = 0.0
    ) -> Dict[str, Any]:
        curr_start, curr_end, prev_start, prev_end = self._resolve_date_range(period, custom_start, custom_end)

        # Fetch current period txns
        curr_txns = await self.txn_repo.get_transactions_in_range(user_id, curr_start, curr_end)
        prev_txns = await self.txn_repo.get_transactions_in_range(user_id, prev_start, prev_end, txn_type="expense")

        total_income = sum(float(t["amount"]) for t in curr_txns if t.get("type", "").lower() == "income")
        total_expenses = sum(float(t["amount"]) for t in curr_txns if t.get("type", "").lower() == "expense")
        prev_expenses = sum(float(t["amount"]) for t in prev_txns)

        # If user has set a monthly_income profile attribute and no income transactions logged yet this period
        effective_income = total_income if total_income > 0 else user_income
        net_savings = max(0.0, effective_income - total_expenses)
        savings_rate = round((net_savings / effective_income * 100), 1) if effective_income > 0 else 0.0

        # MoM Expense Change
        if prev_expenses > 0:
            mom_change = round(((total_expenses - prev_expenses) / prev_expenses) * 100, 1)
        elif total_expenses > 0 and prev_expenses == 0:
            mom_change = 100.0
        else:
            mom_change = 0.0

        # Category spending breakdown
        cat_map: Dict[str, Dict[str, Any]] = {}
        pay_map: Dict[str, Dict[str, Any]] = {}
        daily_map: Dict[str, Dict[str, float]] = {}

        for t in curr_txns:
            amt = float(t["amount"])
            t_type = t.get("type", "").lower()
            d_str = t.get("date")

            if d_str not in daily_map:
                daily_map[d_str] = {"income": 0.0, "expense": 0.0}

            if t_type == "expense":
                daily_map[d_str]["expense"] += amt
                cat = t.get("category", "Other")
                if cat not in cat_map:
                    cat_map[cat] = {"amount": 0.0, "count": 0}
                cat_map[cat]["amount"] += amt
                cat_map[cat]["count"] += 1

                pm = t.get("payment_method", "Other")
                if pm not in pay_map:
                    pay_map[pm] = {"amount": 0.0, "count": 0}
                pay_map[pm]["amount"] += amt
                pay_map[pm]["count"] += 1
            else:
                daily_map[d_str]["income"] += amt

        # Format Category Breakdown
        category_breakdown = []
        highest_cat = None
        highest_amt = 0.0

        for cat, data in sorted(cat_map.items(), key=lambda x: x[1]["amount"], reverse=True):
            cat_amt = round(data["amount"], 2)
            pct = round((cat_amt / total_expenses * 100), 1) if total_expenses > 0 else 0.0
            category_breakdown.append({
                "category": cat,
                "amount": cat_amt,
                "percentage": pct,
                "count": data["count"]
            })
            if cat_amt > highest_amt:
                highest_amt = cat_amt
                highest_cat = cat

        # Format Payment Method Breakdown
        payment_breakdown = []
        for pm, data in sorted(pay_map.items(), key=lambda x: x[1]["amount"], reverse=True):
            pm_amt = round(data["amount"], 2)
            pct = round((pm_amt / total_expenses * 100), 1) if total_expenses > 0 else 0.0
            payment_breakdown.append({
                "method": pm,
                "amount": pm_amt,
                "percentage": pct,
                "count": data["count"]
            })

        # Format Daily Trends
        daily_trends = []
        for d_key in sorted(daily_map.keys()):
            inc = round(daily_map[d_key]["income"], 2)
            exp = round(daily_map[d_key]["expense"], 2)
            daily_trends.append({
                "date": d_key,
                "income": inc,
                "expense": exp,
                "net": round(inc - exp, 2)
            })

        # Check Active Budget for month
        curr_month_str = curr_start[:7]
        budget = await self.budget_repo.get_by_month(user_id, curr_month_str)
        active_budget = float(budget["overall_budget"]) if budget else None
        budget_utilization = round((total_expenses / active_budget * 100), 1) if active_budget and active_budget > 0 else None

        # Recent transactions (latest 5)
        recent = sorted(curr_txns, key=lambda x: (x.get("date", ""), str(x.get("_id", ""))), reverse=True)[:5]
        for r in recent:
            r["id"] = r["_id"]

        # Monthly Spending & Income History (Last 6 Months)
        all_user_txns = await self.txn_repo.get_transactions_in_range(user_id)
        month_group: Dict[str, Dict[str, float]] = {}
        for t in all_user_txns:
            d_val = str(t.get("date", ""))
            if len(d_val) >= 7:
                m_key = d_val[:7]
                if m_key not in month_group:
                    month_group[m_key] = {"income": 0.0, "expense": 0.0}
                t_amt = float(t.get("amount", 0.0))
                if t.get("type", "").lower() == "income":
                    month_group[m_key]["income"] += t_amt
                else:
                    month_group[m_key]["expense"] += t_amt

        monthly_history = [
            {
                "month": m,
                "income": round(data["income"], 2),
                "expense": round(data["expense"], 2),
                "savings": round(max(0.0, data["income"] - data["expense"]), 2)
            }
            for m, data in sorted(month_group.items())[-6:]
        ]

        # Budget vs Actual Breakdown for Active Month
        budget_vs_actual = []
        if budget and budget.get("category_budgets"):
            for cat, budgeted in budget["category_budgets"].items():
                spent = round(cat_map.get(cat, {}).get("amount", 0.0), 2)
                budget_vs_actual.append({
                    "category": cat,
                    "budgeted": round(float(budgeted), 2),
                    "actual": spent,
                    "remaining": round(max(0.0, float(budgeted) - spent), 2)
                })

        return {
            "period": period,
            "start_date": curr_start,
            "end_date": curr_end,
            "total_income": round(effective_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_savings": round(net_savings, 2),
            "savings_rate": savings_rate,
            "mom_expense_change_percent": mom_change,
            "highest_expense_category": highest_cat,
            "highest_category_amount": round(highest_amt, 2) if highest_amt > 0 else None,
            "active_budget": active_budget,
            "budget_spent": round(total_expenses, 2) if active_budget else None,
            "budget_utilization_percent": budget_utilization,
            "transaction_count": len(curr_txns),
            "recent_transactions": recent,
            "category_breakdown": category_breakdown,
            "daily_trends": daily_trends,
            "payment_method_breakdown": payment_breakdown,
            "monthly_history": monthly_history,
            "budget_vs_actual": budget_vs_actual
        }
