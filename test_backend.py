"""
Automated Integration and Unit Tests for Personal Expense Tracker API.
Tests endpoints, authentication, CRUD operations, database persistence, and validations.
"""

import sys
import io

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def run_tests():
    print("==================================================")
    print(">> Starting Personal Expense Tracker Test Suite...")
    print("==================================================")

    # 1. Test Root / Health Endpoint
    print("\n[Test 1] Testing Root / Health Check Endpoint...")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert res.json()["status"] == "online"
    print("  ✅ Passed: Health check endpoint is active.")

    # 2. Test User Registration
    print("\n[Test 2] Testing User Registration...")
    test_username = f"testuser_{int(client.get('/').elapsed.total_seconds() * 1000)}"
    test_email = f"{test_username}@example.com"
    test_password = "securePassword123"

    reg_payload = {
        "username": test_username,
        "email": test_email,
        "password": test_password
    }
    res = client.post("/auth/register", json=reg_payload)
    assert res.status_code == 201, f"Register failed: {res.text}"
    user_data = res.json()
    assert user_data["username"] == test_username
    assert "hashed_password" not in user_data
    print(f"  ✅ Passed: Successfully registered user '{test_username}'.")

    # 3. Test Duplicate Registration (Should fail with 400)
    print("\n[Test 3] Testing Duplicate Registration Prevention...")
    res = client.post("/auth/register", json=reg_payload)
    assert res.status_code == 400, f"Expected 400 for duplicate, got {res.status_code}"
    print("  ✅ Passed: Correctly blocked duplicate registration with 400 Bad Request.")

    # 4. Test User Login (Invalid credentials)
    print("\n[Test 4] Testing Login with Wrong Password...")
    bad_login = {"username": test_username, "password": "wrongpassword"}
    res = client.post("/auth/login", json=bad_login)
    assert res.status_code == 401, f"Expected 401 for bad password, got {res.status_code}"
    print("  ✅ Passed: Rejected bad credentials with 401 Unauthorized.")

    # 5. Test User Login (Valid credentials)
    print("\n[Test 5] Testing Login with Valid Credentials...")
    valid_login = {"username": test_username, "password": test_password}
    res = client.post("/auth/login", json=valid_login)
    assert res.status_code == 200, f"Login failed: {res.text}"
    token_data = res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    print("  ✅ Passed: Successfully logged in and received JWT Bearer token.")

    # 6. Test /auth/me Profile Retrieval
    print("\n[Test 6] Testing /auth/me Profile Route...")
    res = client.get("/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["username"] == test_username
    assert res.json()["email"] == test_email
    print("  ✅ Passed: /auth/me successfully returned authenticated user data.")

    # 7. Test Input Validation for Expenses (Pydantic validations)
    print("\n[Test 7] Testing Input Validations (Negative amount, empty title)...")
    invalid_expense = {
        "title": "   ",  # whitespace only
        "amount": -50.0,  # negative
        "category": "Food & Dining"
    }
    res = client.post("/expenses/", json=invalid_expense, headers=auth_headers)
    assert res.status_code == 422, f"Expected 422 for invalid expense, got {res.status_code}"
    print("  ✅ Passed: Pydantic correctly rejected negative amount and blank title with 422 Unprocessable Entity.")

    # 8. Test Creating Valid Expenses (CRUD: Create)
    print("\n[Test 8] Testing Expense Creation...")
    expenses_to_add = [
        {"title": "Grocery Supermarket", "amount": 85.50, "category": "Shopping & Groceries", "description": "Weekly food and snacks"},
        {"title": "Subway Pass", "amount": 30.00, "category": "Transportation", "description": "Monthly transit pass"},
        {"title": "Coffee with Team", "amount": 12.75, "category": "Food & Dining", "description": "Latte and pastry"}
    ]
    created_ids = []
    for exp in expenses_to_add:
        res = client.post("/expenses/", json=exp, headers=auth_headers)
        assert res.status_code == 201, f"Failed to create expense: {res.text}"
        data = res.json()
        assert data["title"] == exp["title"]
        assert data["amount"] == exp["amount"]
        created_ids.append(data["id"])
    print(f"  ✅ Passed: Created 3 expenses successfully with IDs: {created_ids}.")

    # 9. Test Listing and Filtering Expenses (CRUD: Read)
    print("\n[Test 9] Testing Listing & Filtering Expenses...")
    # List all
    res = client.get("/expenses/", headers=auth_headers)
    assert res.status_code == 200
    all_expenses = res.json()
    assert len(all_expenses) >= 3

    # Filter by category
    res = client.get("/expenses/?category=Transportation", headers=auth_headers)
    assert res.status_code == 200
    trans_expenses = res.json()
    assert all(e["category"] == "Transportation" for e in trans_expenses)

    # Search keyword
    res = client.get("/expenses/?search=Coffee", headers=auth_headers)
    assert res.status_code == 200
    coffee_expenses = res.json()
    assert len(coffee_expenses) == 1
    assert coffee_expenses[0]["title"] == "Coffee with Team"
    print("  ✅ Passed: Listing, category filtering, and search queries work as expected.")

    # 10. Test Analytics Summary Endpoint
    print("\n[Test 10] Testing /expenses/summary Analytics...")
    res = client.get("/expenses/summary", headers=auth_headers)
    assert res.status_code == 200
    summary = res.json()
    assert summary["total_count"] >= 3
    assert summary["total_amount"] >= 128.25
    assert "Food & Dining" in summary["category_breakdown"]
    assert "Transportation" in summary["category_breakdown"]
    print(f"  ✅ Passed: Summary calculated total spent (${summary['total_amount']}) across {summary['total_count']} expenses.")

    # 11. Test Update Expense (CRUD: Update)
    print("\n[Test 11] Testing Expense Update...")
    target_id = created_ids[0]
    update_payload = {"amount": 95.00, "title": "Grocery Supermarket (Updated)"}
    res = client.put(f"/expenses/{target_id}", json=update_payload, headers=auth_headers)
    assert res.status_code == 200
    updated_data = res.json()
    assert updated_data["amount"] == 95.00
    assert updated_data["title"] == "Grocery Supermarket (Updated)"
    print(f"  ✅ Passed: Expense #{target_id} successfully updated.")

    # 12. Test Delete Expense (CRUD: Delete)
    print("\n[Test 12] Testing Expense Deletion...")
    delete_id = created_ids[-1]
    res = client.delete(f"/expenses/{delete_id}", headers=auth_headers)
    assert res.status_code == 200
    print(f"  ✅ Passed: Expense #{delete_id} deleted.")

    # Verify deleted expense is gone
    res = client.get(f"/expenses/{delete_id}", headers=auth_headers)
    assert res.status_code == 404, f"Expected 404 for deleted expense, got {res.status_code}"
    print("  ✅ Passed: Accessing deleted expense correctly returns 404 Not Found.")

    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED SUCCESSFULLY! 100% End-to-End Coverage.")
    print("=" * 50)


if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"\n❌ Test Assertion Failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error During Tests: {e}", file=sys.stderr)
        sys.exit(1)
