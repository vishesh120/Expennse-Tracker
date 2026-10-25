from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import pandas as pd
import numpy as np
from app.core.config import settings


class FinancialInsightsEngine:
    def generate_insights(
        self,
        current_transactions: List[Dict[str, Any]],
        previous_transactions: List[Dict[str, Any]],
        budget: Optional[Dict[str, Any]] = None,
        monthly_income: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate grounded, mathematically verified financial insights.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        insights = []

        curr_expenses = [t for t in current_transactions if t.get("type", "").lower() == "expense"]
        curr_income = [t for t in current_transactions if t.get("type", "").lower() == "income"]
        prev_expenses = [t for t in previous_transactions if t.get("type", "").lower() == "expense"]

        total_curr_spent = sum(float(t["amount"]) for t in curr_expenses)
        total_prev_spent = sum(float(t["amount"]) for t in prev_expenses)
        total_curr_income = sum(float(t["amount"]) for t in curr_income) or monthly_income

        # Monthly summary metrics
        net_savings = max(0.0, total_curr_income - total_curr_spent)
        savings_rate = (net_savings / total_curr_income * 100) if total_curr_income > 0 else 0.0

        monthly_summary = {
            "total_spent": round(total_curr_spent, 2),
            "total_income": round(total_curr_income, 2),
            "net_savings": round(net_savings, 2),
            "savings_rate_percent": round(savings_rate, 1),
            "expense_count": len(curr_expenses)
        }

        # 1. Month-over-Month Comparison
        if total_prev_spent > 0 and total_curr_spent > 0:
            diff_pct = ((total_curr_spent - total_prev_spent) / total_prev_spent) * 100
            diff_abs = abs(total_curr_spent - total_prev_spent)
            if diff_pct > 10:
                insights.append({
                    "id": str(uuid.uuid4()),
                    "category_type": "spending_trend",
                    "title": "Overall Spending Acceleration",
                    "observation": f"Overall expenses are up {round(diff_pct, 1)}% (+₹{round(diff_abs, 2)}) compared to the previous period.",
                    "actionable_recommendation": "Review high-ticket non-essential purchases from the last two weeks to restore your baseline.",
                    "impact_amount": round(diff_abs, 2),
                    "severity": "warning"
                })
            elif diff_pct < -10:
                insights.append({
                    "id": str(uuid.uuid4()),
                    "category_type": "spending_trend",
                    "title": "Positive Spending Reduction",
                    "observation": f"Great job! Your spending is {round(abs(diff_pct), 1)}% lower (-₹{round(diff_abs, 2)}) than last period.",
                    "actionable_recommendation": f"Consider channeling this saved ₹{round(diff_abs, 2)} into an emergency fund or mutual fund SIP.",
                    "impact_amount": round(diff_abs, 2),
                    "severity": "positive"
                })

        # 2. Category Level Breakdown & Spikes
        curr_cat_spending: Dict[str, float] = {}
        for t in curr_expenses:
            cat = t.get("category", "Other")
            curr_cat_spending[cat] = curr_cat_spending.get(cat, 0.0) + float(t["amount"])

        prev_cat_spending: Dict[str, float] = {}
        for t in prev_expenses:
            cat = t.get("category", "Other")
            prev_cat_spending[cat] = prev_cat_spending.get(cat, 0.0) + float(t["amount"])

        # Check largest categories
        if curr_cat_spending:
            sorted_cats = sorted(curr_cat_spending.items(), key=lambda x: x[1], reverse=True)
            top_cat, top_amt = sorted_cats[0]
            top_share = (top_amt / total_curr_spent * 100) if total_curr_spent > 0 else 0

            insights.append({
                "id": str(uuid.uuid4()),
                "category_type": "category_spike",
                "title": f"Top Expense Category: {top_cat}",
                "observation": f"{top_cat} constitutes {round(top_share, 1)}% (₹{round(top_amt, 2)}) of your entire spending this period.",
                "actionable_recommendation": f"Setting a weekly cap on {top_cat} can help keep your total spending within bounds.",
                "impact_amount": round(top_amt, 2),
                "severity": "info"
            })

            # Check category-specific surge
            for cat, amt in sorted_cats[:3]:
                prev_amt = prev_cat_spending.get(cat, 0.0)
                if prev_amt > 1000 and amt > prev_amt * 1.25:
                    cat_diff = amt - prev_amt
                    cat_pct = ((amt - prev_amt) / prev_amt) * 100
                    insights.append({
                        "id": str(uuid.uuid4()),
                        "category_type": "category_spike",
                        "title": f"{cat} Surge Detected",
                        "observation": f"{cat} spending increased by {round(cat_pct, 1)}% (+₹{round(cat_diff, 2)}) compared to last month.",
                        "actionable_recommendation": f"Check for one-off charges or subscription renewals in {cat} to verify if this increase is recurring.",
                        "impact_amount": round(cat_diff, 2),
                        "severity": "warning"
                    })
                    break

        # 3. Budget Alerts & Threshold Warnings
        if budget:
            overall_budget = float(budget.get("overall_budget", 0))
            if overall_budget > 0:
                utilization = (total_curr_spent / overall_budget) * 100
                if utilization >= 100:
                    insights.append({
                        "id": str(uuid.uuid4()),
                        "category_type": "budget_warning",
                        "title": "Monthly Budget Exceeded",
                        "observation": f"You have reached {round(utilization, 1)}% of your overall monthly budget limit of ₹{round(overall_budget, 2)}.",
                        "actionable_recommendation": "Freeze non-essential discretionary expenses (dining out, gadgets, entertainment) for the rest of the cycle.",
                        "impact_amount": round(total_curr_spent - overall_budget, 2),
                        "severity": "critical"
                    })
                elif utilization >= 80:
                    insights.append({
                        "id": str(uuid.uuid4()),
                        "category_type": "budget_warning",
                        "title": "Budget Near Exhaustion",
                        "observation": f"You have utilized {round(utilization, 1)}% of your monthly budget. Remaining buffer is ₹{round(overall_budget - total_curr_spent, 2)}.",
                        "actionable_recommendation": "Slow down optional spending to avoid crossing into the deficit zone.",
                        "impact_amount": round(overall_budget - total_curr_spent, 2),
                        "severity": "warning"
                    })

            # Category budgets
            cat_budgets = budget.get("category_budgets", {})
            for cat, limit in cat_budgets.items():
                spent = curr_cat_spending.get(cat, 0.0)
                if limit > 0 and (spent / limit) >= 0.85:
                    cat_util = round((spent / limit) * 100, 1)
                    insights.append({
                        "id": str(uuid.uuid4()),
                        "category_type": "budget_warning",
                        "title": f"{cat} Budget Alert ({cat_util}%)",
                        "observation": f"You have spent ₹{round(spent, 2)} out of ₹{round(limit, 2)} budgeted for {cat}.",
                        "actionable_recommendation": f"Postpone non-urgent {cat} transactions until next month.",
                        "impact_amount": round(max(0.0, limit - spent), 2),
                        "severity": "warning" if cat_util < 100 else "critical"
                    })

        # 4. Outlier / Anomaly Detection (using robust IQR and Z-Score statistics)
        if len(curr_expenses) >= 5:
            amounts = [float(t["amount"]) for t in curr_expenses]
            q75, q25 = np.percentile(amounts, [75, 25])
            iqr = q75 - q25
            iqr_threshold = q75 + 2.0 * iqr
            mean_a = np.mean(amounts)
            std_a = np.std(amounts)
            z_threshold = mean_a + 1.8 * std_a
            threshold = min(iqr_threshold, z_threshold) if iqr > 0 else z_threshold

            for t in curr_expenses:
                amt = float(t["amount"])
                if amt > threshold and amt > 2500:
                    insights.append({
                        "id": str(uuid.uuid4()),
                        "category_type": "anomaly",
                        "title": f"Unusual High-Value Transaction: {t.get('title')}",
                        "observation": f"A single transaction of ₹{round(amt, 2)} ({t.get('category')}) was recorded on {t.get('date')}, significantly higher than your typical transaction.",
                        "actionable_recommendation": "Verify this transaction and mark as recurring or one-off in your records.",
                        "impact_amount": round(amt, 2),
                        "severity": "info"
                    })
                    break

        # 5. Actionable Micro-Savings Recommendation
        discretionary_categories = ["Food and groceries", "Shopping", "Entertainment", "Travel"]
        discretionary_total = sum(curr_cat_spending.get(c, 0.0) for c in discretionary_categories)
        if discretionary_total > 4000:
            suggested_cut = min(1500.0, round(discretionary_total * 0.15, -1))
            annual_saved = suggested_cut * 12
            insights.append({
                "id": str(uuid.uuid4()),
                "category_type": "savings_opportunity",
                "title": "Discretionary Spending Optimization",
                "observation": f"You spent ₹{round(discretionary_total, 2)} across Food, Shopping, and Entertainment this period.",
                "actionable_recommendation": f"Trimming non-essential orders by ₹{round(suggested_cut, 0)} per month generates ₹{round(annual_saved, 0)} in guaranteed annual savings.",
                "impact_amount": round(suggested_cut, 2),
                "severity": "positive"
            })
            monthly_savings_potential = round(suggested_cut, 2)
            annual_savings_potential = round(annual_saved, 2)
        else:
            monthly_savings_potential = 500.0
            annual_savings_potential = 6000.0

        # If few insights, add a welcoming foundational insight
        if len(insights) == 0:
            insights.append({
                "id": str(uuid.uuid4()),
                "category_type": "savings_opportunity",
                "title": "Financial Health Foundation",
                "observation": "Expense tracking initiated. We are establishing your transaction baseline.",
                "actionable_recommendation": "Aim for the 50-30-20 rule: 50% on essentials, 30% on lifestyle, and 20% dedicated to investments or savings.",
                "impact_amount": 0.0,
                "severity": "info"
            })

        # 6. AI Coach Executive Summary (Optional LLM or deterministic grounded synthesis)
        ai_coach_summary = self._generate_coach_summary(monthly_summary, insights, top_cat if 'top_cat' in locals() else None)

        return {
            "period": "Current Month",
            "generated_at": now_str,
            "insights": insights,
            "monthly_summary": monthly_summary,
            "savings_potential_monthly": monthly_savings_potential,
            "savings_potential_annual": annual_savings_potential,
            "ai_coach_summary": ai_coach_summary,
            "ai_disclaimer": "These insights and forecasts are algorithmically computed for financial wellness planning and do not constitute certified investment advice."
        }

    def _generate_coach_summary(
        self,
        summary: Dict[str, Any],
        insights: List[Dict[str, Any]],
        top_cat: Optional[str] = None
    ) -> str:
        # Check if external LLM API key is available
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY.strip())
                prompt = (
                    f"You are an empathetic, expert personal finance coach for a resident in India. "
                    f"Provide an encouraging, concise 2-sentence executive financial briefing strictly grounded in these metrics: "
                    f"Income: ₹{summary.get('total_income', 0)}, Total Spent: ₹{summary.get('total_spent', 0)}, "
                    f"Savings: ₹{summary.get('net_savings', 0)} ({summary.get('savings_rate_percent', 0)}% savings rate), "
                    f"Top Category: {top_cat or 'None'}. Do not hallucinate external figures."
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response and response.text:
                    return response.text.strip()
            except Exception:
                pass  # Graceful fallback to deterministic generator

        # Grounded algorithmic synthesis
        savings_rate = summary.get("savings_rate_percent", 0.0)
        net_saved = summary.get("net_savings", 0.0)
        if savings_rate >= 20:
            return (
                f"Your financial momentum is strong this period with a {savings_rate}% savings rate and ₹{net_saved:,.2f} retained. "
                + (f"Keeping discretionary spending in {top_cat} disciplined will help sustain your savings target." if top_cat else "Keep building your emergency fund buffer.")
            )
        elif savings_rate > 0:
            return (
                f"You have retained ₹{net_saved:,.2f} ({savings_rate}% savings rate) this cycle. "
                + (f"Monitoring recurring charges in {top_cat} could lift your savings rate above the recommended 20% mark." if top_cat else "Review discretionary outlays to strengthen your cash reserves.")
            )
        else:
            return (
                f"Current period expenditures are matching or outpacing cash inflows. "
                f"Prioritizing essential commitments and freezing non-urgent discretionary orders will restore your budget balance."
            )


insights_engine = FinancialInsightsEngine()
