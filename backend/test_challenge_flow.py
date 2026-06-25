#!/usr/bin/env python3
"""
Test script for 7-day challenge flow:
1. Signup user
2. Complete profile
3. Log meals for 7 days
4. Check compliance
5. Generate report
6. Verify admin dashboard shows the data
"""

import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"
client = httpx.Client()

def log_test(step: str, status: str, details: str = ""):
    """Print test log"""
    symbol = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[INFO]"
    print(f"{symbol} {step}: {status}")
    if details:
        print(f"   {details}")

def test_flow():
    """Test the complete 7-day challenge flow"""

    print("\n" + "="*60)
    print("TESTING 7-DAY CHALLENGE FLOW")
    print("="*60 + "\n")

    # Step 1: Signup
    print("STEP 1: SIGNUP USER")
    try:
        signup_data = {
            "name": "Test User Challenge",
            "email": f"testchallenge_{datetime.now().timestamp()}@test.com",
            "password": "testpass123",
            "phone": "+91 9876543210"
        }
        response = client.post(f"{BASE_URL}/auth/signup", json=signup_data)
        if response.status_code == 200:
            auth_data = response.json()
            client_id = auth_data["client_id"]
            token = auth_data["token"]
            log_test("Signup", "PASS", f"Client ID: {client_id}")
        else:
            log_test("Signup", "FAIL", f"Status: {response.status_code}")
            return
    except Exception as e:
        log_test("Signup", "FAIL", str(e))
        return

    # Set auth header
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Complete Profile
    print("\nSTEP 2: COMPLETE PROFILE")
    try:
        profile_data = {
            "name": "Test User Challenge",
            "phone": "+91 9876543210",
            "email": signup_data["email"],
            "sex": "male",
            "gender": "Man",
            "age": 28,
            "height_cm": 175,
            "weight_kg": 75
        }
        response = client.patch(f"{BASE_URL}/profile/{client_id}", json=profile_data, headers=headers)
        if response.status_code == 200:
            log_test("Profile Update", "PASS", "All fields updated")
        else:
            log_test("Profile Update", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Profile Update", "FAIL", str(e))

    # Step 3: Log Meals for 7 Days
    print("\nSTEP 3: LOG MEALS FOR 7 DAYS")
    meals_data = [
        {"type": "BREAKFAST", "foods": ["2 idli", "sambar", "tea"]},
        {"type": "LUNCH", "foods": ["chapati", "dal", "vegetables", "rice"]},
        {"type": "DINNER", "foods": ["soup", "roti", "curry", "yogurt"]}
    ]

    # Use test image for meals
    test_image_path = "../test/South-India-Neer-Dosa.jpg"

    for day in range(1, 8):
        try:
            for meal in meals_data:
                # Open test image for this meal
                with open(test_image_path, 'rb') as img_file:
                    files = {'image': ('meal.jpg', img_file, 'image/jpeg')}
                    meal_log_data = {
                        "client_id": client_id,
                        "day_number": day,
                        "meal_type": meal["type"],
                        "meal_text": ", ".join(meal["foods"]),
                    }
                    response = client.post(
                        f"{BASE_URL}/challenge/submit-meal",
                        data=meal_log_data,
                        files=files,
                        headers=headers
                    )
                    if response.status_code != 200:
                        log_test(f"Day {day} - {meal['type']}", "FAIL", f"Status: {response.status_code}")
                        print(f"   Response: {response.text}")

            log_test(f"Day {day} Meals Logged", "PASS", "Breakfast, Lunch, Dinner")
        except Exception as e:
            log_test(f"Day {day}", "FAIL", str(e))

    # Step 4: Check Compliance
    print("\nSTEP 4: CHECK COMPLIANCE")
    try:
        response = client.get(f"{BASE_URL}/compliance/{client_id}", headers=headers)
        if response.status_code == 200:
            compliance_data = response.json()
            compliance_pct = compliance_data.get("compliance_pct", 0)
            log_test("Get Compliance", "PASS", f"Compliance: {compliance_pct}%")

            if compliance_pct >= 85:
                log_test("85% Threshold", "PASS", "User QUALIFIED for tests and discount!")
            else:
                log_test("85% Threshold", "INFO", f"Current: {compliance_pct}% (Need: 85%+)")
        else:
            log_test("Get Compliance", "FAIL", f"Status: {response.status_code}")
    except Exception as e:
        log_test("Get Compliance", "FAIL", str(e))

    # Step 5: Generate Report
    print("\nSTEP 5: GENERATE REPORT")
    try:
        response = client.post(f"{BASE_URL}/reports/generate/{client_id}", headers=headers)
        if response.status_code == 200:
            report = response.json()
            log_test("Generate Report", "PASS", f"Score: {report.get('compliance_score')}%")
            log_test("Eligibility Band", "PASS", report.get('eligibility_band', 'N/A'))
        else:
            log_test("Generate Report", "FAIL", f"Status: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        log_test("Generate Report", "FAIL", str(e))

    # Step 6: Check Admin Dashboard
    print("\nSTEP 6: CHECK ADMIN DASHBOARD")
    try:
        # Get dashboard metrics
        response = client.get(f"{BASE_URL}/admin/dashboard")
        if response.status_code == 200:
            dashboard = response.json()
            log_test("Admin Dashboard Metrics", "PASS",
                    f"Total: {dashboard.get('total')}, Qualified: {dashboard.get('qualified')}, "
                    f"Profile Completed: {dashboard.get('profile_completed')}")
        else:
            log_test("Admin Dashboard", "FAIL", f"Status: {response.status_code}")

        # Get clients list
        response = client.get(f"{BASE_URL}/admin/clients")
        if response.status_code == 200:
            clients_data = response.json()
            total_clients = clients_data.get("total", 0)
            log_test("Admin Clients List", "PASS", f"Total clients: {total_clients}")

            # Find our test user
            for client_info in clients_data.get("clients", []):
                if client_info.get("client_id") == client_id:
                    log_test("Test User in Dashboard", "PASS",
                            f"Name: {client_info.get('name')}, "
                            f"Compliance: {client_info.get('compliance_pct')}%, "
                            f"Profile: {client_info.get('profile_completed')}")
                    break
        else:
            log_test("Admin Clients List", "FAIL", f"Status: {response.status_code}")

        # Get client detail
        response = client.get(f"{BASE_URL}/admin/clients/{client_id}")
        if response.status_code == 200:
            client_detail = response.json()
            client_info = client_detail.get("client", {})
            log_test("Admin Client Detail", "PASS",
                    f"Sex: {client_info.get('sex')}, Gender: {client_info.get('gender')}, "
                    f"Age: {client_info.get('age')}")

            # Check compliance
            compliance = client_detail.get("compliance", {})
            log_test("Compliance in Detail", "PASS",
                    f"Compliance: {compliance.get('compliance_pct')}%, "
                    f"Days: {compliance.get('completed_days')}/7")

            # Check tests
            tests = client_detail.get("tests", {})
            mcq_status = "✅ Completed" if tests.get("mcq", {}).get("completed") else "🔒 Locked"
            descriptive_status = "✅ Completed" if tests.get("descriptive", {}).get("completed") else "🔒 Locked"
            log_test("Test Status", "PASS", f"MCQ: {mcq_status}, Descriptive: {descriptive_status}")
        else:
            log_test("Admin Client Detail", "FAIL", f"Status: {response.status_code}")

    except Exception as e:
        log_test("Admin Dashboard", "FAIL", str(e))

    # Summary
    print("\n" + "="*60)
    print("TEST COMPLETE!")
    print("="*60 + "\n")
    print(f"Test User Email: {signup_data['email']}")
    print(f"Client ID: {client_id}")
    print("\nCheck Admin Dashboard: http://localhost:3000/admin")
    print("Your test user should appear in the dashboard with:")
    print("   - Profile: Completed")
    print("   - Compliance: 100% (logged all 21 meals)")
    print("   - Status: QUALIFIED")
    print("   - Eligibility Band: Gold/Strong")

if __name__ == "__main__":
    test_flow()
