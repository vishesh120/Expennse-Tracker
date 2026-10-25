import io
import pytest
from fastapi.testclient import TestClient


def test_input_validation_rejections(client: TestClient, auth_headers):
    # 1. Invalid date (non-existent calendar day)
    bad_date_resp = client.post("/api/v1/transactions", json={
        "title": "Invalid Date Txn",
        "amount": 500.0,
        "type": "expense",
        "date": "2026-02-31",  # Feb 31 does not exist
        "category": "Food and groceries"
    }, headers=auth_headers)
    assert bad_date_resp.status_code == 422
    assert "detail" in bad_date_resp.json()

    # 2. Negative amount
    neg_amt_resp = client.post("/api/v1/transactions", json={
        "title": "Negative Amount Txn",
        "amount": -50.0,
        "type": "expense",
        "date": "2026-10-10",
        "category": "Food and groceries"
    }, headers=auth_headers)
    assert neg_amt_resp.status_code == 422

    # 3. Zero amount
    zero_amt_resp = client.post("/api/v1/transactions", json={
        "title": "Zero Amount Txn",
        "amount": 0.0,
        "type": "expense",
        "date": "2026-10-10",
        "category": "Food and groceries"
    }, headers=auth_headers)
    assert zero_amt_resp.status_code == 422

    # 4. Invalid transaction type (must be 'expense' or 'income')
    bad_type_resp = client.post("/api/v1/transactions", json={
        "title": "Bad Type Txn",
        "amount": 100.0,
        "type": "transfer",
        "date": "2026-10-10",
        "category": "Food and groceries"
    }, headers=auth_headers)
    assert bad_type_resp.status_code == 422

    # 5. Negative category budget
    bad_cat_budget = client.post("/api/v1/budgets", json={
        "month": "2026-10",
        "overall_budget": 10000.0,
        "category_budgets": {
            "Food and groceries": -500.0
        }
    }, headers=auth_headers)
    assert bad_cat_budget.status_code == 422

    # 6. Invalid category type (must be 'expense', 'income', or 'both')
    bad_cat_type = client.post("/api/v1/categories", json={
        "name": "Custom Bad Category",
        "type": "cryptocurrency"
    }, headers=auth_headers)
    assert bad_cat_type.status_code == 422


def test_token_security_and_authorization(client: TestClient):
    # 1. Unauthenticated request to protected route
    no_auth = client.get("/api/v1/transactions")
    assert no_auth.status_code == 401

    # 2. Forged / invalid bearer token
    bad_token = client.get("/api/v1/transactions", headers={"Authorization": "Bearer forged_jwt_token_12345"})
    assert bad_token.status_code == 401

    # 3. Register user and obtain both tokens
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": "token_audit@test.in",
        "password": "Password123!",
        "full_name": "Token Auditor"
    })
    tokens = reg_resp.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # 4. Using refresh token on access-protected route should fail (cryptographic key separation)
    refresh_as_access = client.get("/api/v1/transactions", headers={"Authorization": f"Bearer {refresh_token}"})
    assert refresh_as_access.status_code == 401

    # 5. Using access token on refresh endpoint should fail (cryptographic key separation)
    access_as_refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert access_as_refresh.status_code == 401

    # 6. Valid refresh token successfully rotates tokens
    valid_refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert valid_refresh.status_code == 200
    new_tokens = valid_refresh.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens


def test_cross_user_isolation_categories_and_budgets(client: TestClient):
    # Register User 1
    u1 = client.post("/api/v1/auth/register", json={
        "email": "iso_user1@test.in",
        "password": "Password123!",
        "full_name": "Isolation User One"
    }).json()
    h1 = {"Authorization": f"Bearer {u1['access_token']}"}

    # Register User 2
    u2 = client.post("/api/v1/auth/register", json={
        "email": "iso_user2@test.in",
        "password": "Password123!",
        "full_name": "Isolation User Two"
    }).json()
    h2 = {"Authorization": f"Bearer {u2['access_token']}"}

    # User 1 creates custom category
    cat_resp = client.post("/api/v1/categories", json={
        "name": "Custom Hobby",
        "type": "expense",
        "color": "#10b981"
    }, headers=h1)
    assert cat_resp.status_code == 201
    cat1_id = cat_resp.json()["id"]

    # User 2 attempts to delete User 1's custom category -> 404
    u2_del_cat = client.delete(f"/api/v1/categories/{cat1_id}", headers=h2)
    assert u2_del_cat.status_code == 404

    # Any user attempting to delete a system category -> 404
    sys_cats = client.get("/api/v1/categories", headers=h1).json()
    sys_cat = next(c for c in sys_cats if c.get("is_system"))
    del_sys = client.delete(f"/api/v1/categories/{sys_cat['id']}", headers=h1)
    assert del_sys.status_code == 404

    # User 1 creates a monthly budget
    b_resp = client.post("/api/v1/budgets", json={
        "month": "2026-11",
        "overall_budget": 45000.0,
        "category_budgets": {"Food and groceries": 15000.0}
    }, headers=h1)
    assert b_resp.status_code == 201
    b1_id = b_resp.json()["id"]

    # User 2 cannot delete User 1's budget -> 404
    u2_del_b = client.delete(f"/api/v1/budgets/{b1_id}", headers=h2)
    assert u2_del_b.status_code == 404

    # User 2 cannot see User 1's budget in list
    u2_budgets = client.get("/api/v1/budgets", headers=h2).json()
    assert all(b["id"] != b1_id for b in u2_budgets)


def test_csv_import_security_and_formats(client: TestClient, auth_headers):
    # 1. Non-CSV file extension rejection
    fake_txt = io.BytesIO(b"Date,Title,Amount\n2026-10-01,Test,100")
    txt_resp = client.post(
        "/api/v1/imports/csv",
        files={"file": ("transactions.txt", fake_txt, "text/plain")},
        headers=auth_headers
    )
    assert txt_resp.status_code == 400
    assert "Only .csv files are supported" in txt_resp.json()["detail"]

    # 2. Empty CSV rejection
    empty_csv = io.BytesIO(b"")
    empty_resp = client.post(
        "/api/v1/imports/csv",
        files={"file": ("empty.csv", empty_csv, "text/csv")},
        headers=auth_headers
    )
    assert empty_resp.status_code == 400

    # 3. Missing mandatory columns rejection
    bad_header_csv = io.BytesIO(b"RandomColumn1,RandomColumn2\nVal1,Val2\n")
    bad_h_resp = client.post(
        "/api/v1/imports/csv",
        files={"file": ("bad_headers.csv", bad_header_csv, "text/csv")},
        headers=auth_headers
    )
    assert bad_h_resp.status_code == 400

    # 4. Valid CSV with various Indian date formats and amount formatting
    valid_csv_content = (
        "Date,Description,Amount,Payment Mode,Reference\n"
        "24/10/2026,Swiggy Lunch Order,Rs. 450.00,UPI,UPI123456789\n"
        "25-10-2026,Uber Office Commute,INR 320.50,UPI,UPI987654321\n"
        "2026-10-26,Amazon Electronics,2500.00,Credit Card,TXN55443322\n"
    ).encode("utf-8")

    csv_file = io.BytesIO(valid_csv_content)
    import_resp = client.post(
        "/api/v1/imports/csv",
        files={"file": ("statement.csv", csv_file, "text/csv")},
        headers=auth_headers
    )
    assert import_resp.status_code == 200
    data = import_resp.json()
    assert data["imported_count"] == 3
    assert data["duplicate_count"] == 0

    # 5. Re-importing identical statement verifies cryptographic deduplication
    csv_file_dup = io.BytesIO(valid_csv_content)
    reimport_resp = client.post(
        "/api/v1/imports/csv",
        files={"file": ("statement.csv", csv_file_dup, "text/csv")},
        headers=auth_headers
    )
    assert reimport_resp.status_code == 200
    dup_data = reimport_resp.json()
    assert dup_data["imported_count"] == 0
    assert dup_data["duplicate_count"] == 3
    assert dup_data["status"] == "duplicates_only"
