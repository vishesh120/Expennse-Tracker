import io
from fastapi.testclient import TestClient


def test_auth_and_profile(client: TestClient):
    # 1. Register
    reg_data = {
        "email": "freshuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Rohan Sharma",
        "monthly_income": 45000.0,
        "occupation": "Fresher / First Job"
    }
    reg_resp = client.post("/api/v1/auth/register", json=reg_data)
    assert reg_resp.status_code == 201
    reg_json = reg_resp.json()
    assert "access_token" in reg_json
    assert "user" in reg_json
    assert reg_json["user"]["email"] == "freshuser@example.com"
    token = reg_json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Profile
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["full_name"] == "Rohan Sharma"

    # 3. Invalid Login
    bad_login = client.post("/api/v1/auth/login", json={
        "email": "freshuser@example.com",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # 4. Valid Login
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "freshuser@example.com",
        "password": "SecurePassword123!"
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()


def test_transaction_crud_and_isolation(client: TestClient):
    # Register User 1
    u1_resp = client.post("/api/v1/auth/register", json={
        "email": "user1@example.com",
        "password": "Password123!",
        "full_name": "User One",
        "monthly_income": 60000.0
    })
    u1_token = u1_resp.json()["access_token"]
    u1_headers = {"Authorization": f"Bearer {u1_token}"}

    # Register User 2
    u2_resp = client.post("/api/v1/auth/register", json={
        "email": "user2@example.com",
        "password": "Password123!",
        "full_name": "User Two",
        "monthly_income": 70000.0
    })
    u2_token = u2_resp.json()["access_token"]
    u2_headers = {"Authorization": f"Bearer {u2_token}"}

    # User 1 creates transaction
    txn_data = {
        "title": "Swiggy Pizza Order",
        "amount": 450.0,
        "type": "expense",
        "date": "2026-10-10",
        "category": "Food and groceries",
        "payment_method": "UPI",
        "upi_reference": "423456789012",
        "description": "Weekend dinner"
    }
    create_resp = client.post("/api/v1/transactions", json=txn_data, headers=u1_headers)
    assert create_resp.status_code == 201
    created_txn = create_resp.json()
    txn_id = created_txn["id"]
    assert created_txn["amount"] == 450.0

    # User 2 tries to access User 1's transaction (Data Isolation test)
    u2_get = client.get(f"/api/v1/transactions/{txn_id}", headers=u2_headers)
    assert u2_get.status_code == 404

    # User 1 updates transaction
    update_resp = client.patch(
        f"/api/v1/transactions/{txn_id}",
        json={"amount": 500.0, "title": "Swiggy Pizza and Drink"},
        headers=u1_headers
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["amount"] == 500.0
    assert update_resp.json()["title"] == "Swiggy Pizza and Drink"

    # User 1 lists transactions
    list_resp = client.get("/api/v1/transactions", headers=u1_headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] == 1

    # User 1 deletes transaction
    del_resp = client.delete(f"/api/v1/transactions/{txn_id}", headers=u1_headers)
    assert del_resp.status_code == 200

    # Verify deleted
    get_del = client.get(f"/api/v1/transactions/{txn_id}", headers=u1_headers)
    assert get_del.status_code == 404


def test_ai_categorizer_and_feedback(client: TestClient, auth_headers):
    # Rule match: Swiggy
    resp1 = client.post("/api/v1/ai/categorize", json={"title": "Swiggy Gourmet Dinner"}, headers=auth_headers)
    assert resp1.status_code == 200
    assert resp1.json()["predicted_category"] == "Food and groceries"
    assert resp1.json()["confidence"] >= 0.85

    # Rule match: Uber ride
    resp2 = client.post("/api/v1/ai/categorize", json={"title": "Uber Trip to Office"}, headers=auth_headers)
    assert resp2.status_code == 200
    assert resp2.json()["predicted_category"] == "Transportation"

    # Feedback submission
    fb_resp = client.post("/api/v1/ai/feedback", json={
        "title": "Unusual Custom Merchant Name",
        "predicted_category": "Other",
        "confirmed_category": "Shopping"
    }, headers=auth_headers)
    assert fb_resp.status_code == 200


def test_budget_and_alerts(client: TestClient, auth_headers):
    # Create Budget
    budget_data = {
        "month": "2026-10",
        "overall_budget": 1000.0,
        "category_budgets": {
            "Food and groceries": 500.0
        },
        "alert_thresholds": [50, 80, 100]
    }
    b_resp = client.post("/api/v1/budgets", json=budget_data, headers=auth_headers)
    assert b_resp.status_code == 201
    assert b_resp.json()["overall_budget"] == 1000.0

    # Add transaction exceeding 80% of food budget (e.g. 450 of 500 = 90%)
    client.post("/api/v1/transactions", json={
        "title": "Grocery Shopping",
        "amount": 450.0,
        "type": "expense",
        "date": "2026-10-05",
        "category": "Food and groceries",
        "payment_method": "UPI"
    }, headers=auth_headers)

    # Check budget alerts
    status_resp = client.get("/api/v1/budgets/2026-10", headers=auth_headers)
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["total_spent"] == 450.0
    alerts = data["alerts"]
    assert any("Food and groceries" in a["message"] for a in alerts)


def test_seed_samples_forecast_and_insights(client: TestClient, auth_headers):
    # 1. Seed synthetic realistic dataset
    seed_resp = client.post("/api/v1/ai/seed-samples?days=30", headers=auth_headers)
    assert seed_resp.status_code == 201
    assert seed_resp.json()["count"] > 20

    # 2. Check forecast
    fc_after = client.get("/api/v1/ai/forecast?days=30", headers=auth_headers)
    assert fc_after.status_code == 200
    assert fc_after.json()["status"] == "success"
    assert len(fc_after.json()["points"]) > 30
    assert fc_after.json()["predicted_total"] > 0

    # 3. Check AI Insights
    insights_resp = client.get("/api/v1/ai/insights", headers=auth_headers)
    assert insights_resp.status_code == 200
    insights_data = insights_resp.json()
    assert len(insights_data["insights"]) > 0
    assert "savings_potential_annual" in insights_data


def test_csv_import_and_deduplication(client: TestClient, auth_headers):
    csv_content = """Date,Title,Amount,Type,Category,Payment Method,UPI Reference
2026-10-01,Zomato Delivery,320.00,expense,Food and groceries,UPI,423456789001
2026-10-02,Uber Commute,150.00,expense,Transportation,UPI,423456789002
2026-10-03,Freelance Design Project,12000.00,income,Salary and income,Net Banking,
"""
    files = {"file": ("statement.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    import_resp = client.post("/api/v1/imports/csv", files=files, headers=auth_headers)
    assert import_resp.status_code == 200
    res = import_resp.json()
    assert res["imported_count"] == 3
    assert res["duplicate_count"] == 0

    # Second import with same file should detect duplicates
    files_again = {"file": ("statement.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    reimport_resp = client.post("/api/v1/imports/csv", files=files_again, headers=auth_headers)
    assert reimport_resp.status_code == 200
    re_res = reimport_resp.json()
    assert re_res["imported_count"] == 0
    assert re_res["duplicate_count"] == 3


def test_rate_limiter_protection(client: TestClient):
    from app.core.rate_limiter import auth_rate_limiter
    # Temporarily set limit to 3 for quick unit verification
    original_max = auth_rate_limiter.max_requests
    auth_rate_limiter.max_requests = 3
    auth_rate_limiter.clients.clear()

    try:
        for _ in range(3):
            r = client.post("/api/v1/auth/login", json={"email": "wrong@example.com", "password": "pass"})
            assert r.status_code in [401, 200]
        # 4th request should exceed limit and yield 429
        blocked = client.post("/api/v1/auth/login", json={"email": "wrong@example.com", "password": "pass"})
        assert blocked.status_code == 429
        assert "Too many authentication attempts" in blocked.json()["detail"]
    finally:
        auth_rate_limiter.max_requests = original_max
        auth_rate_limiter.clients.clear()

