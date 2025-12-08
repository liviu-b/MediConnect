#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timezone, timedelta

class MediConnectAPITester:
    def __init__(self, base_url="https://healthsync-33.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session_token = None  # Will be set after login
        self.user_id = None  # Will be set after login
        self.clinic_admin_token = None  # For clinic admin tests
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()  # Use session for cookies

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, use_session=True):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if use_session:
                # Use session for cookie-based auth
                if method == 'GET':
                    response = self.session.get(url, headers=test_headers, timeout=10)
                elif method == 'POST':
                    response = self.session.post(url, json=data, headers=test_headers, timeout=10)
                elif method == 'PUT':
                    response = self.session.put(url, json=data, headers=test_headers, timeout=10)
                elif method == 'DELETE':
                    response = self.session.delete(url, headers=test_headers, timeout=10)
            else:
                # Use regular requests without session
                if method == 'GET':
                    response = requests.get(url, headers=test_headers, timeout=10)
                elif method == 'POST':
                    response = requests.post(url, json=data, headers=test_headers, timeout=10)
                elif method == 'PUT':
                    response = requests.put(url, json=data, headers=test_headers, timeout=10)
                elif method == 'DELETE':
                    response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                self.failed_tests.append({
                    'name': name,
                    'expected': expected_status,
                    'actual': response.status_code,
                    'response': response.text[:200]
                })
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")

            return success, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text

        except Exception as e:
            self.failed_tests.append({
                'name': name,
                'error': str(e)
            })
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health check"""
        return self.run_test("API Health Check", "GET", "", 200)

    def test_clinics_api(self):
        """Test clinics API"""
        success, response = self.run_test("Get Clinics", "GET", "clinics", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} clinics")
            if len(response) >= 3:
                print("✅ Expected 3+ clinics found")
            else:
                print(f"⚠️  Expected 3+ clinics, found {len(response)}")
        return success

    def test_doctors_api(self):
        """Test doctors API"""
        success, response = self.run_test("Get Doctors", "GET", "doctors", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} doctors")
            if len(response) >= 4:
                print("✅ Expected 4+ doctors found")
            else:
                print(f"⚠️  Expected 4+ doctors, found {len(response)}")
        return success

    def test_auth_me(self):
        """Test authentication with test session"""
        success, response = self.run_test("Auth Me", "GET", "auth/me", 200)
        if success and isinstance(response, dict):
            if response.get('role') == 'ADMIN':
                print("✅ Admin user authenticated successfully")
            else:
                print(f"⚠️  Expected ADMIN role, got {response.get('role')}")
        return success

    def test_stats_api(self):
        """Test stats API for dashboard"""
        success, response = self.run_test("Get Stats", "GET", "stats", 200)
        if success and isinstance(response, dict):
            expected_keys = ['total_doctors', 'total_clinics', 'total_appointments', 'upcoming_appointments']
            found_keys = [key for key in expected_keys if key in response]
            print(f"   Stats keys found: {found_keys}")
            if len(found_keys) >= 3:
                print("✅ Dashboard stats available")
            else:
                print(f"⚠️  Missing some stats keys: {set(expected_keys) - set(found_keys)}")
        return success

    def test_appointments_api(self):
        """Test appointments API"""
        success, response = self.run_test("Get Appointments", "GET", "appointments", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} appointments")
        return success

    def test_users_api(self):
        """Test users API (admin only)"""
        success, response = self.run_test("Get Users", "GET", "users", 200)
        if success and isinstance(response, list):
            print(f"   Found {len(response)} users")
        return success

    def test_doctor_availability(self):
        """Test doctor availability API"""
        # First get a doctor
        success, doctors = self.run_test("Get Doctors for Availability", "GET", "doctors", 200)
        if success and isinstance(doctors, list) and len(doctors) > 0:
            doctor_id = doctors[0]['doctor_id']
            today = datetime.now().strftime('%Y-%m-%d')
            success, response = self.run_test(
                "Get Doctor Availability", 
                "GET", 
                f"doctors/{doctor_id}/availability?date={today}", 
                200
            )
            if success and isinstance(response, dict):
                if 'available_slots' in response:
                    print(f"✅ Availability API working, found {len(response['available_slots'])} slots")
                else:
                    print("⚠️  No available_slots in response")
            return success
        else:
            print("⚠️  No doctors found to test availability")
            return False

def main():
    print("🏥 MediConnect API Testing Suite")
    print("=" * 50)
    
    tester = MediConnectAPITester()
    
    # Test sequence
    tests = [
        ("API Health Check", tester.test_health_check),
        ("Authentication", tester.test_auth_me),
        ("Clinics API", tester.test_clinics_api),
        ("Doctors API", tester.test_doctors_api),
        ("Stats API", tester.test_stats_api),
        ("Appointments API", tester.test_appointments_api),
        ("Users API", tester.test_users_api),
        ("Doctor Availability", tester.test_doctor_availability),
    ]
    
    print(f"\nRunning {len(tests)} test categories...")
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test category failed: {e}")
            tester.failed_tests.append({
                'name': test_name,
                'error': str(e)
            })
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"📊 Test Results Summary")
    print(f"{'='*50}")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "No tests run")
    
    if tester.failed_tests:
        print(f"\n❌ Failed Tests ({len(tester.failed_tests)}):")
        for i, failure in enumerate(tester.failed_tests, 1):
            print(f"{i}. {failure['name']}")
            if 'expected' in failure:
                print(f"   Expected: {failure['expected']}, Got: {failure['actual']}")
                print(f"   Response: {failure['response']}")
            elif 'error' in failure:
                print(f"   Error: {failure['error']}")
    else:
        print("\n🎉 All tests passed!")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())