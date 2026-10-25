import requests
import sys
import uuid

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def log(msg, success=True):
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {msg}")

def run_phase_verification():
    print("=" * 60)
    print("STARTING E2E VERIFICATION: PHASES 1 THROUGH 4")
    print("=" * 60)

    # ---------------------------------------------------------
    # PHASE 1: System Health & Base Environment
    # ---------------------------------------------------------
    print("\n--- Phase 1: Environment & API Accessibility ---")
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    health_data = resp.json()
    assert health_data["status"] == "healthy"
    assert health_data["database"] == "connected"
    log("Health endpoint is healthy and database is connected.")

    docs_resp = requests.get(f"{BASE_URL}/docs")
    assert docs_resp.status_code == 200
    log("FastAPI OpenAPI documentation accessible at /docs.")

    # ---------------------------------------------------------
    # PHASE 2: Database, Secure Authentication & User Isolation
    # ---------------------------------------------------------
    print("\n--- Phase 2: Secure Authentication & Isolation ---")
    unique_suffix = str(uuid.uuid4())[:8]
    user1_email = f"user1_{unique_suffix}@example.com"
    user2_email = f"user2_{unique_suffix}@example.com"
    pwd1 = "Password123!Secure"
    pwd2 = "Password456!Secure"

    # Register User 1
    u1_reg = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": user1_email,
        "password": pwd1,
        "full_name": "Arjun Patel",
        "monthly_income": 85000.0,
        "occupation": "Software Engineer"
    })
    assert u1_reg.status_code == 201, f"User 1 registration failed: {u1_reg.text}"
    u1_token = u1_reg.json()["access_token"]
    u1_id = u1_reg.json()["user"]["id"]
    u1_headers = {"Authorization": f"Bearer {u1_token}"}
    log(f"User 1 registered successfully (ID: {u1_id}).")

    # Register User 2
    u2_reg = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": user2_email,
        "password": pwd2,
        "full_name": "Priya Sharma",
        "monthly_income": 65000.0,
        "occupation": "Product Analyst"
    })
    assert u2_reg.status_code == 201, f"User 2 registration failed: {u2_reg.text}"
    u2_token = u2_reg.json()["access_token"]
    u2_id = u2_reg.json()["user"]["id"]
    u2_headers = {"Authorization": f"Bearer {u2_token}"}
    log(f"User 2 registered successfully (ID: {u2_id}).")

    # Login User 1
    u1_login = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": user1_email,
        "password": pwd1
    })
    assert u1_login.status_code == 200
    assert "access_token" in u1_login.json()
    log("User 1 login verified with JWT token issuance.")

    # Profile verification
    me_resp = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=u1_headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == user1_email
    log("User 1 profile fetched and verified.")

    # ---------------------------------------------------------
    # PHASE 3: Transactions CRUD & Indian Payment Methods
    # ---------------------------------------------------------
    print("\n--- Phase 3: Transaction CRUD, Persistence & Data Isolation ---")
    # User 1 creates an expense with UPI and UTR reference
    txn1_payload = {
        "title": "Swiggy Biryani Dinner",
        "amount": 540.0,
        "type": "expense",
        "date": "2026-10-24",
        "category": "Food and groceries",
        "payment_method": "UPI",
        "upi_reference": "UPI987654321012",
        "description": "Weekend family meal",
        "is_recurring": False
    }
    t1_create = requests.post(f"{BASE_URL}/api/v1/transactions", json=txn1_payload, headers=u1_headers)
    assert t1_create.status_code == 201, f"Txn creation failed: {t1_create.text}"
    txn1 = t1_create.json()
    txn1_id = txn1["id"]
    log(f"Transaction 1 created: '{txn1['title']}', Amount: ₹{txn1['amount']}, UPI Ref: {txn1['upi_reference']}.")

    # User 1 creates an income transaction
    txn_income_payload = {
        "title": "Monthly Salary October",
        "amount": 85000.0,
        "type": "income",
        "date": "2026-10-01",
        "category": "Salary and income",
        "payment_method": "Bank Transfer",
        "description": "Company payroll credit"
    }
    t_inc_create = requests.post(f"{BASE_URL}/api/v1/transactions", json=txn_income_payload, headers=u1_headers)
    assert t_inc_create.status_code == 201
    log("Income transaction created: ₹85,000.00 via Bank Transfer.")

    # Database Persistence: Fetch by ID
    get_t1 = requests.get(f"{BASE_URL}/api/v1/transactions/{txn1_id}", headers=u1_headers)
    assert get_t1.status_code == 200
    assert get_t1.json()["title"] == "Swiggy Biryani Dinner"
    assert get_t1.json()["amount"] == 540.0
    log("Database persistence verified: Transaction correctly retrieved by ID.")

    # Update Transaction
    update_payload = {
        "title": "Swiggy Biryani + Gulab Jamun",
        "amount": 620.0
    }
    patch_t1 = requests.patch(f"{BASE_URL}/api/v1/transactions/{txn1_id}", json=update_payload, headers=u1_headers)
    assert patch_t1.status_code == 200
    assert patch_t1.json()["amount"] == 620.0
    assert patch_t1.json()["title"] == "Swiggy Biryani + Gulab Jamun"
    log("Transaction update verified: Amount updated to ₹620.00.")

    # Search & Filter
    search_resp = requests.get(f"{BASE_URL}/api/v1/transactions?search=Biryani", headers=u1_headers)
    assert search_resp.status_code == 200
    assert search_resp.json()["total"] == 1
    log("Keyword search verified: Found transaction by query 'Biryani'.")

    # CSV Export
    csv_resp = requests.get(f"{BASE_URL}/api/v1/transactions/export/csv", headers=u1_headers)
    assert csv_resp.status_code == 200
    assert "Date,Title,Amount (INR),Type,Category" in csv_resp.text
    assert "Swiggy Biryani + Gulab Jamun" in csv_resp.text
    log("CSV Export verified: Formatted statement generated with correct columns.")

    # User 2 creates their own transaction
    txn2_payload = {
        "title": "Uber ride to Airport",
        "amount": 890.0,
        "type": "expense",
        "date": "2026-10-25",
        "category": "Transportation",
        "payment_method": "UPI",
        "upi_reference": "UPI112233445566"
    }
    t2_create = requests.post(f"{BASE_URL}/api/v1/transactions", json=txn2_payload, headers=u2_headers)
    assert t2_create.status_code == 201
    txn2_id = t2_create.json()["id"]
    log(f"User 2 transaction created: '{txn2_payload['title']}' (ID: {txn2_id}).")

    # STRICT USER DATA ISOLATION TESTS
    print("\n--- Verifying Strict User Data Isolation ---")
    # 1. User 1 listing should NOT contain User 2's transaction
    u1_list = requests.get(f"{BASE_URL}/api/v1/transactions", headers=u1_headers).json()
    u1_txn_ids = [item["id"] for item in u1_list["items"]]
    assert txn2_id not in u1_txn_ids, "DATA ISOLATION LEAK: User 1 sees User 2's transaction!"
    log("Data Isolation: User 1 cannot see User 2's transactions in list.")

    # 2. User 2 listing should NOT contain User 1's transaction
    u2_list = requests.get(f"{BASE_URL}/api/v1/transactions", headers=u2_headers).json()
    u2_txn_ids = [item["id"] for item in u2_list["items"]]
    assert txn1_id not in u2_txn_ids, "DATA ISOLATION LEAK: User 2 sees User 1's transaction!"
    log("Data Isolation: User 2 cannot see User 1's transactions in list.")

    # 3. User 2 cannot GET User 1's transaction by ID
    u2_get_u1 = requests.get(f"{BASE_URL}/api/v1/transactions/{txn1_id}", headers=u2_headers)
    assert u2_get_u1.status_code == 404, f"Security breach: User 2 got User 1's txn: {u2_get_u1.status_code}"
    log("Data Isolation: User 2 receives 404 when attempting to access User 1's transaction.")

    # 4. User 2 cannot PATCH User 1's transaction
    u2_patch_u1 = requests.patch(f"{BASE_URL}/api/v1/transactions/{txn1_id}", json={"amount": 1.0}, headers=u2_headers)
    assert u2_patch_u1.status_code == 404, "Security breach: User 2 updated User 1's txn"
    log("Data Isolation: User 2 receives 404 when attempting to modify User 1's transaction.")

    # 5. User 2 cannot DELETE User 1's transaction
    u2_del_u1 = requests.delete(f"{BASE_URL}/api/v1/transactions/{txn1_id}", headers=u2_headers)
    assert u2_del_u1.status_code == 404, "Security breach: User 2 deleted User 1's txn"
    log("Data Isolation: User 2 receives 404 when attempting to delete User 1's transaction.")

    # Delete transaction by owner
    del_t1 = requests.delete(f"{BASE_URL}/api/v1/transactions/{txn1_id}", headers=u1_headers)
    assert del_t1.status_code == 200
    confirm_del = requests.get(f"{BASE_URL}/api/v1/transactions/{txn1_id}", headers=u1_headers)
    assert confirm_del.status_code == 404
    log("Transaction deletion verified: Owner successfully deleted transaction and record is removed.")

    # ---------------------------------------------------------
    # PHASE 4: AI-Powered Automatic Expense Categorization
    # ---------------------------------------------------------
    print("\n--- Phase 4: AI Expense Categorization Engine ---")
    test_cases = [
        ("Swiggy order for lunch", "Food and groceries"),
        ("Uber cab ride to office", "Transportation"),
        ("Amazon online purchase electronics", "Shopping"),
        ("Monthly hostel rent payment", "Rent and housing"),
        ("College tuition semester fee", "Education"),
        ("Electricity bill BESCOM payment", "Bills and utilities"),
        ("Apollo pharmacy medicines", "Healthcare"),
        ("Netflix monthly subscription", "Entertainment"),
        ("MakeMyTrip holiday hotel and resort", "Travel"),
        ("Monthly salary credit from employer", "Salary and income"),
    ]

    for title, expected_cat in test_cases:
        ai_resp = requests.post(f"{BASE_URL}/api/v1/ai/categorize", json={"title": title}, headers=u1_headers)
        assert ai_resp.status_code == 200, f"AI categorize failed for '{title}': {ai_resp.text}"
        data = ai_resp.json()
        assert data["predicted_category"] == expected_cat, f"Mismatch for '{title}': got '{data['predicted_category']}', expected '{expected_cat}'"
        assert data["confidence"] >= 0.70, f"Confidence too low for '{title}': {data['confidence']}"
        log(f"AI Categorized: '{title}' -> '{data['predicted_category']}' (Confidence: {data['confidence']*100:.1f}%, Model: {data['model_type']})")

    # Feedback loop test
    fb_resp = requests.post(f"{BASE_URL}/api/v1/ai/feedback", json={
        "title": "Local Dhaba Special Thali",
        "predicted_category": "Other",
        "confirmed_category": "Food and groceries",
        "confidence": 0.50
    }, headers=u1_headers)
    assert fb_resp.status_code == 200
    log("AI Feedback submitted successfully for continuous model improvement.")

    print("\n" + "=" * 60)
    print("ALL VERIFICATIONS FOR PHASES 1 THROUGH 4 PASSED PERFECTLY!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_phase_verification()
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
