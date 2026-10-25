from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np


class SpendingForecaster:
    def __init__(self, min_days_required: int = 5):
        self.min_days_required = min_days_required

    def forecast_spending(
        self,
        transactions: List[Dict[str, Any]],
        forecast_days: int = 30,
        monthly_budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Produce a spending forecast for the next N days (7 or 30).
        """
        # Filter only expenses
        expenses = [
            t for t in transactions
            if t.get("type", "").lower() == "expense" and float(t.get("amount", 0)) > 0
        ]

        if not expenses:
            return {
                "status": "insufficient_data",
                "has_sufficient_data": False,
                "forecast_days": forecast_days,
                "historical_days_used": 0,
                "predicted_total": 0.0,
                "predicted_daily_average": 0.0,
                "points": [],
                "influencing_factors": [
                    "No expense transactions recorded yet."
                ],
                "overspending_risk_level": "Low",
                "message": f"At least {self.min_days_required} distinct days of historical expenses are required to generate an accurate forecast."
            }

        # Build daily aggregations
        df = pd.DataFrame(expenses)
        df["date"] = pd.to_datetime(df["date"])
        daily = df.groupby(df["date"].dt.date)["amount"].sum().reset_index()
        daily = daily.sort_values("date")

        distinct_days = len(daily)
        if distinct_days < self.min_days_required:
            return {
                "status": "insufficient_data",
                "has_sufficient_data": False,
                "forecast_days": forecast_days,
                "historical_days_used": distinct_days,
                "predicted_total": 0.0,
                "predicted_daily_average": 0.0,
                "points": [],
                "influencing_factors": [
                    f"Only {distinct_days} day(s) of transactions found."
                ],
                "overspending_risk_level": "Low",
                "message": f"Found only {distinct_days} day(s) of expense history. A minimum of {self.min_days_required} days is needed to compute statistical predictions."
            }

        # Identify recurring expenses
        recurring_expenses = [t for t in expenses if t.get("is_recurring")]
        recurring_daily_rate = sum(float(t["amount"]) for t in recurring_expenses) / 30.0 if recurring_expenses else 0.0

        # Calculate historical stats
        amounts = daily["amount"].values
        mean_expense = float(np.mean(amounts))
        std_expense = float(np.std(amounts)) if len(amounts) > 1 else mean_expense * 0.25
        median_expense = float(np.median(amounts))

        # Recent trend (last 7 recorded days weight)
        recent_window = min(7, len(amounts))
        recent_mean = float(np.mean(amounts[-recent_window:]))
        trend_ratio = (recent_mean / mean_expense) if mean_expense > 0 else 1.0

        # Linear trend calculation
        x = np.arange(len(amounts))
        if len(amounts) >= 3:
            slope, intercept = np.polyfit(x, amounts, 1)
        else:
            slope, intercept = 0.0, mean_expense

        # Blend weighted baseline (60% recent average + 40% long-term median) + slight slope dampening
        base_daily = 0.6 * recent_mean + 0.4 * median_expense
        # Ensure daily baseline isn't negative
        base_daily = max(base_daily, recurring_daily_rate)

        # Standard error / uncertainty margin
        margin = max(std_expense * 0.75, base_daily * 0.2)

        # Build historical points (last 14 days)
        points: List[Dict[str, Any]] = []
        historical_subset = daily.tail(14)
        for _, row in historical_subset.iterrows():
            d_str = row["date"].strftime("%Y-%m-%d")
            val = round(float(row["amount"]), 2)
            points.append({
                "date": d_str,
                "predicted_expense": val,
                "lower_bound": val,
                "upper_bound": val,
                "is_historical": True,
                "actual_expense": val
            })

        # Generate future forecast points
        last_date = daily["date"].max()
        future_totals = 0.0
        influencing_factors = []

        if trend_ratio > 1.2:
            influencing_factors.append(f"Recent spending rate is {round((trend_ratio - 1) * 100)}% higher than your long-term daily baseline.")
        elif trend_ratio < 0.8:
            influencing_factors.append(f"Recent spending pace has reduced by {round((1 - trend_ratio) * 100)}% relative to average.")
        else:
            influencing_factors.append("Daily spending has remained relatively stable across recorded days.")

        if recurring_expenses:
            influencing_factors.append(f"{len(recurring_expenses)} recurring commitment(s) totaling ₹{round(sum(float(t['amount']) for t in recurring_expenses), 2)} factored into base projections.")

        for i in range(1, forecast_days + 1):
            target_date = last_date + timedelta(days=i)
            # Day-of-week factor: weekends (Friday, Saturday, Sunday) often see +15% higher discretionary spend
            weekday = target_date.weekday()
            dow_multiplier = 1.15 if weekday in [4, 5, 6] else 0.95

            # Forecast value with mild slope dampening
            step_slope = slope * 0.1 * i if abs(slope) < base_daily * 0.5 else 0.0
            predicted_val = max(100.0, (base_daily + step_slope) * dow_multiplier)
            predicted_val = round(predicted_val, 2)
            lower_val = max(0.0, round(predicted_val - margin, 2))
            upper_val = round(predicted_val + margin * (1 + 0.02 * i), 2)  # uncertainty widens with horizon

            future_totals += predicted_val
            points.append({
                "date": target_date.strftime("%Y-%m-%d"),
                "predicted_expense": predicted_val,
                "lower_bound": lower_val,
                "upper_bound": upper_val,
                "is_historical": False,
                "actual_expense": None
            })

        predicted_daily_avg = round(future_totals / forecast_days, 2)
        predicted_total = round(future_totals, 2)

        # Overspending risk assessment
        risk_level = "Low"
        if monthly_budget and monthly_budget > 0:
            projected_month_scale = predicted_daily_avg * 30
            if projected_month_scale > monthly_budget * 1.2:
                risk_level = "High"
                influencing_factors.append(
                    f"Warning: Projected 30-day expense (₹{round(projected_month_scale)}) exceeds your monthly budget of ₹{round(monthly_budget)} by {round(((projected_month_scale/monthly_budget)-1)*100)}%."
                )
            elif projected_month_scale > monthly_budget * 0.9:
                risk_level = "Medium"
                influencing_factors.append(
                    f"Caution: Projected spending is approaching {round((projected_month_scale/monthly_budget)*100)}% of your monthly limit."
                )
        elif trend_ratio > 1.3:
            risk_level = "Medium"
            influencing_factors.append("Moderate risk: High spending velocity in recent days may cause overspending.")

        return {
            "status": "success",
            "has_sufficient_data": True,
            "forecast_days": forecast_days,
            "historical_days_used": distinct_days,
            "predicted_total": predicted_total,
            "predicted_daily_average": predicted_daily_avg,
            "points": points,
            "influencing_factors": influencing_factors,
            "overspending_risk_level": risk_level,
            "message": f"Successfully calculated {forecast_days}-day forecast based on {distinct_days} days of historical records."
        }


spending_forecaster = SpendingForecaster()
