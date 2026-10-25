import pytest
from fastapi.testclient import TestClient
from app.ai.categorizer import ExpenseCategorizer
from app.ai.forecaster import SpendingForecaster
from app.ai.insights import FinancialInsightsEngine


def test_explainable_expense_categorization():
    engine = ExpenseCategorizer()

    # 1. Rule-based with explainability
    res_swiggy = engine.predict(title="Swiggy Biryani Dinner")
    assert res_swiggy["predicted_category"] == "Food and groceries"
    assert res_swiggy["model_type"] == "rules_engine"
    assert res_swiggy["explanation"] is not None
    assert "swiggy" in res_swiggy["explanation"].lower()
    assert len(res_swiggy["explanation_factors"]) >= 2
    assert any("swiggy" in f.lower() for f in res_swiggy["explanation_factors"])

    # 2. Another rule match
    res_uber = engine.predict(title="Uber Cab Ride to Station")
    assert res_uber["predicted_category"] == "Transportation"
    assert "uber" in res_uber["explanation"].lower()

    # 3. ML Model prediction with explainability
    res_ml = engine.predict(title="Python course exam preparation books")
    assert res_ml["predicted_category"] == "Education"
    assert res_ml["explanation"] is not None
    assert len(res_ml["explanation_factors"]) >= 2

    # 4. Fallback with explainability
    res_fallback = engine.predict(title="Xyzwvk 9876 Random String")
    assert res_fallback["predicted_category"] == "Other"
    assert res_fallback["model_type"] == "fallback"
    assert "defaulting to 'Other'" in res_fallback["explanation"]
    assert len(res_fallback["explanation_factors"]) >= 1


def test_forecasting_with_insufficient_data_handling():
    forecaster = SpendingForecaster(min_days_required=5)

    # 1. Zero expenses
    res_empty = forecaster.forecast_spending([], forecast_days=30)
    assert res_empty["status"] == "insufficient_data"
    assert res_empty["has_sufficient_data"] is False
    assert res_empty["historical_days_used"] == 0
    assert "No expense transactions recorded yet" in res_empty["influencing_factors"][0]

    # 2. Insufficient distinct days (only 2 distinct dates, min 5 required)
    sparse_transactions = [
        {"type": "expense", "amount": 350.0, "date": "2026-10-01"},
        {"type": "expense", "amount": 420.0, "date": "2026-10-01"},
        {"type": "expense", "amount": 500.0, "date": "2026-10-02"},
    ]
    res_sparse = forecaster.forecast_spending(sparse_transactions, forecast_days=30)
    assert res_sparse["status"] == "insufficient_data"
    assert res_sparse["has_sufficient_data"] is False
    assert res_sparse["historical_days_used"] == 2
    assert "minimum of 5 days" in res_sparse["message"]

    # 3. Sufficient distinct days (6 distinct dates)
    sufficient_transactions = [
        {"type": "expense", "amount": 300.0, "date": "2026-10-01"},
        {"type": "expense", "amount": 450.0, "date": "2026-10-02"},
        {"type": "expense", "amount": 250.0, "date": "2026-10-03"},
        {"type": "expense", "amount": 600.0, "date": "2026-10-04"},
        {"type": "expense", "amount": 400.0, "date": "2026-10-05"},
        {"type": "expense", "amount": 500.0, "date": "2026-10-06"},
    ]
    res_good = forecaster.forecast_spending(sufficient_transactions, forecast_days=7)
    assert res_good["status"] == "success"
    assert res_good["has_sufficient_data"] is True
    assert res_good["historical_days_used"] == 6
    assert res_good["predicted_total"] > 0
    assert res_good["predicted_daily_average"] > 0
    assert len(res_good["points"]) > 6
    # Check that bounds are mathematically sound: lower_bound <= predicted <= upper_bound
    for pt in res_good["points"]:
        if not pt["is_historical"]:
            assert pt["lower_bound"] <= pt["predicted_expense"]
            assert pt["predicted_expense"] <= pt["upper_bound"]


def test_database_driven_dashboard_analytics_calculations(client: TestClient):
    # Register test user
    reg = client.post("/api/v1/auth/register", json={
        "email": "analytics_user@test.in",
        "password": "Password123!",
        "full_name": "Analytics Test User",
        "monthly_income": 60000.0
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify zero transaction state
    s0 = client.get("/api/v1/dashboard/summary?period=this_month", headers=headers).json()
    assert s0["total_expenses"] == 0.0
    assert s0["net_savings"] == 60000.0  # profile income fallback
    assert s0["savings_rate"] == 100.0

    # Insert controlled income and expenses for current month
    client.post("/api/v1/transactions", json={
        "title": "Monthly Salary",
        "amount": 50000.0,
        "type": "income",
        "date": "2026-10-01",
        "category": "Salary and income",
        "payment_method": "Bank Transfer"
    }, headers=headers)

    client.post("/api/v1/transactions", json={
        "title": "Grocery Supermarket",
        "amount": 8000.0,
        "type": "expense",
        "date": "2026-10-02",
        "category": "Food and groceries",
        "payment_method": "UPI"
    }, headers=headers)

    client.post("/api/v1/transactions", json={
        "title": "Fuel Petrol",
        "amount": 4000.0,
        "type": "expense",
        "date": "2026-10-03",
        "category": "Transportation",
        "payment_method": "Credit Card"
    }, headers=headers)

    client.post("/api/v1/transactions", json={
        "title": "Clothes Store",
        "amount": 3000.0,
        "type": "expense",
        "date": "2026-10-04",
        "category": "Shopping",
        "payment_method": "UPI"
    }, headers=headers)

    # Fetch dashboard summary
    res = client.get("/api/v1/dashboard/summary?period=this_month", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Exact mathematical verifications:
    # Income: 50,000, Expenses: 15,000
    assert data["total_income"] == 50000.0
    assert data["total_expenses"] == 15000.0
    # Net savings = 50,000 - 15,000 = 35,000
    assert data["net_savings"] == 35000.0
    # Savings rate = (35000 / 50000) * 100 = 70.0%
    assert data["savings_rate"] == 70.0

    # Highest expense category
    assert data["highest_expense_category"] == "Food and groceries"
    assert data["highest_category_amount"] == 8000.0

    # Category percentages:
    # Food: (8000 / 15000) * 100 = 53.3%
    # Transport: (4000 / 15000) * 100 = 26.7%
    # Shopping: (3000 / 15000) * 100 = 20.0%
    cat_dict = {c["category"]: c for c in data["category_breakdown"]}
    assert cat_dict["Food and groceries"]["amount"] == 8000.0
    assert cat_dict["Food and groceries"]["percentage"] == 53.3
    assert cat_dict["Transportation"]["amount"] == 4000.0
    assert cat_dict["Transportation"]["percentage"] == 26.7
    assert cat_dict["Shopping"]["amount"] == 3000.0
    assert cat_dict["Shopping"]["percentage"] == 20.0

    # Payment method breakdown:
    # UPI: 8000 + 3000 = 11,000 (73.3%)
    # Credit Card: 4000 (26.7%)
    pm_dict = {p["method"]: p for p in data["payment_method_breakdown"]}
    assert pm_dict["UPI"]["amount"] == 11000.0
    assert pm_dict["UPI"]["percentage"] == 73.3
    assert pm_dict["Credit Card"]["amount"] == 4000.0
    assert pm_dict["Credit Card"]["percentage"] == 26.7


def test_category_budgets_and_alert_thresholds(client: TestClient):
    reg = client.post("/api/v1/auth/register", json={
        "email": "budget_calc_user@test.in",
        "password": "Password123!",
        "full_name": "Budget User"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Set overall budget of 20,000 and Food budget of 10,000
    b_resp = client.post("/api/v1/budgets", json={
        "month": "2026-10",
        "overall_budget": 20000.0,
        "category_budgets": {
            "Food and groceries": 10000.0,
            "Shopping": 5000.0
        },
        "alert_thresholds": [50, 80, 100]
    }, headers=headers)
    assert b_resp.status_code == 201

    # 1. Spend 5,500 on Food (55% utilization -> crosses 50% threshold)
    client.post("/api/v1/transactions", json={
        "title": "Grocery run 1",
        "amount": 5500.0,
        "type": "expense",
        "date": "2026-10-05",
        "category": "Food and groceries"
    }, headers=headers)

    s1 = client.get("/api/v1/budgets/2026-10", headers=headers).json()
    food_s1 = next(c for c in s1["category_statuses"] if c["category"] == "Food and groceries")
    assert food_s1["spent"] == 5500.0
    assert food_s1["budgeted"] == 10000.0
    assert food_s1["remaining"] == 4500.0
    assert food_s1["percentage_used"] == 55.0
    assert food_s1["status"] == "ok"  # under 80%
    # Alert for 50% should exist
    assert any(a["threshold"] == 50 and a.get("category") == "Food and groceries" for a in s1["alerts"])

    # 2. Spend an additional 3,000 on Food (total 8,500 = 85% -> warning)
    client.post("/api/v1/transactions", json={
        "title": "Grocery run 2",
        "amount": 3000.0,
        "type": "expense",
        "date": "2026-10-10",
        "category": "Food and groceries"
    }, headers=headers)

    s2 = client.get("/api/v1/budgets/2026-10", headers=headers).json()
    food_s2 = next(c for c in s2["category_statuses"] if c["category"] == "Food and groceries")
    assert food_s2["spent"] == 8500.0
    assert food_s2["remaining"] == 1500.0
    assert food_s2["percentage_used"] == 85.0
    assert food_s2["status"] == "warning"
    assert any(a["threshold"] == 80 and a.get("category") == "Food and groceries" for a in s2["alerts"])

    # 3. Spend an additional 2,000 on Food (total 10,500 = 105% -> exceeded)
    client.post("/api/v1/transactions", json={
        "title": "Grocery run 3",
        "amount": 2000.0,
        "type": "expense",
        "date": "2026-10-15",
        "category": "Food and groceries"
    }, headers=headers)

    s3 = client.get("/api/v1/budgets/2026-10", headers=headers).json()
    food_s3 = next(c for c in s3["category_statuses"] if c["category"] == "Food and groceries")
    assert food_s3["spent"] == 10500.0
    assert food_s3["remaining"] == 0.0  # remaining doesn't go below 0
    assert food_s3["percentage_used"] == 105.0
    assert food_s3["status"] == "exceeded"
    assert any(a["threshold"] == 100 and a.get("category") == "Food and groceries" for a in s3["alerts"])


def test_personalized_insights_calculation_integrity():
    engine = FinancialInsightsEngine()

    current_txns = [
        {"type": "expense", "amount": 400.0, "category": "Food and groceries", "date": "2026-10-01", "title": "Lunch"},
        {"type": "expense", "amount": 500.0, "category": "Food and groceries", "date": "2026-10-02", "title": "Dinner"},
        {"type": "expense", "amount": 350.0, "category": "Food and groceries", "date": "2026-10-03", "title": "Snacks"},
        {"type": "expense", "amount": 450.0, "category": "Transportation", "date": "2026-10-04", "title": "Cab"},
        {"type": "expense", "amount": 25000.0, "category": "Shopping", "date": "2026-10-05", "title": "High-end Smartphone"}, # Outlier
    ]
    previous_txns = [
        {"type": "expense", "amount": 8000.0, "category": "Food and groceries"},
        {"type": "expense", "amount": 2000.0, "category": "Transportation"}
    ]

    res = engine.generate_insights(
        current_transactions=current_txns,
        previous_transactions=previous_txns,
        budget={"overall_budget": 30000.0},
        monthly_income=50000.0
    )

    # Mathematical checks
    summary = res["monthly_summary"]
    assert summary["total_spent"] == 26700.0
    assert summary["total_income"] == 50000.0
    assert summary["net_savings"] == 23300.0
    # Savings rate = (23300 / 50000) * 100 = 46.6%
    assert summary["savings_rate_percent"] == 46.6

    # Verify outlier anomaly was detected
    insights = res["insights"]
    anomaly = next((i for i in insights if i["category_type"] == "anomaly"), None)
    assert anomaly is not None
    assert "High-end Smartphone" in anomaly["title"]
    assert anomaly["impact_amount"] == 25000.0

    # Verify Discretionary savings potential calculation (annual = monthly * 12)
    assert res["savings_potential_annual"] == res["savings_potential_monthly"] * 12
