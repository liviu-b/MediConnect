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

    def test_user_registration(self):
        """Test user registration"""
        import time
        unique_email = f"newuser{int(time.time())}@test.com"
        data = {
            "email": unique_email,
            "password": "test123456",
            "name": "New User",
            "phone": "1234567890"
        }
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, data, use_session=False)
        if success and isinstance(response, dict):
            if 'user' in response and 'session_token' in response:
                print("✅ User registration successful with session token")
                return True
            else:
                print("⚠️  Missing user or session_token in response")
        return success

    def test_user_login(self):
        """Test user login"""
        data = {
            "email": "testuser@example.com",
            "password": "test123456"
        }
        success, response = self.run_test("User Login", "POST", "auth/login", 200, data)
        if success and isinstance(response, dict):
            if 'user' in response and 'session_token' in response:
                print("✅ User login successful")
                self.session_token = response.get('session_token')
                self.user_id = response.get('user', {}).get('user_id')
                return True
            else:
                print("⚠️  Missing user or session_token in response")
        return success

    def test_clinic_admin_login(self):
        """Test clinic admin login"""
        data = {
            "email": "jane.doe@healthcareplus.com",
            "password": "securepass123"
        }
        success, response = self.run_test("Clinic Admin Login", "POST", "auth/login", 200, data)
        if success and isinstance(response, dict):
            if 'user' in response and 'session_token' in response:
                user = response.get('user', {})
                if user.get('role') == 'CLINIC_ADMIN':
                    print("✅ Clinic admin login successful")
                    self.clinic_admin_token = response.get('session_token')
                    return True
                else:
                    print(f"⚠️  Expected CLINIC_ADMIN role, got {user.get('role')}")
            else:
                print("⚠️  Missing user or session_token in response")
        return success

    def test_validate_registration_code(self):
        """Test registration code validation"""
        success, response = self.run_test("Validate Registration Code", "POST", "auth/validate-code?code=CLINIC2025A", 200, use_session=False)
        if success and isinstance(response, dict):
            if response.get('valid') == True:
                print("✅ Registration code validation successful")
                return True
            else:
                print(f"⚠️  Code validation failed: {response.get('message')}")
        return success

    def test_clinic_registration(self):
        """Test clinic registration"""
        import time
        unique_email = f"admin{int(time.time())}@testclinic.com"
        clinic_email = f"clinic{int(time.time())}@test.com"
        data = {
            "registration_code": "CLINIC2025A",
            "clinic_name": "Test Clinic",
            "address": "123 Test St",
            "phone": "+1234567890",
            "email": clinic_email,
            "description": "Test clinic description",
            "admin_name": "Admin User",
            "admin_email": unique_email,
            "admin_password": "admin123",
            "admin_phone": "+1234567891"
        }
        success, response = self.run_test("Clinic Registration", "POST", "auth/register-clinic", 200, data, use_session=False)
        if success and isinstance(response, dict):
            if 'user' in response and 'clinic' in response and 'session_token' in response:
                print("✅ Clinic registration successful")
                return True
            else:
                print("⚠️  Missing user, clinic, or session_token in response")
        return success

    def test_auth_me(self):
        """Test get current user"""
        success, response = self.run_test("Get Current User", "GET", "auth/me", 200)
        if success and isinstance(response, dict):
            if 'user_id' in response and 'email' in response:
                print(f"✅ Current user retrieved: {response.get('email')}")
                return True
            else:
                print("⚠️  Missing user_id or email in response")
        return success

    def test_get_clinics(self):
        """Test get all clinics"""
        success, response = self.run_test("Get All Clinics", "GET", "clinics", 200, use_session=False)
        if success and isinstance(response, list):
            print(f"✅ Found {len(response)} clinics")
            return True
        return success

    def test_get_doctors(self):
        """Test get all doctors (authenticated)"""
        success, response = self.run_test("Get All Doctors", "GET", "doctors", 200)
        if success and isinstance(response, list):
            print(f"✅ Found {len(response)} doctors")
            return True
        return success

    def test_get_appointments(self):
        """Test get appointments (authenticated)"""
        success, response = self.run_test("Get Appointments", "GET", "appointments", 200)
        if success and isinstance(response, list):
            print(f"✅ Found {len(response)} appointments")
            return True
        return success

    def test_get_stats(self):
        """Test get dashboard stats (authenticated)"""
        success, response = self.run_test("Get Dashboard Stats", "GET", "stats", 200)
        if success and isinstance(response, dict):
            stats_keys = list(response.keys())
            print(f"✅ Stats retrieved with keys: {stats_keys}")
            return True
        return success

def main():
    print("🏥 MediConnect API Testing Suite")
    print("=" * 50)
    
    tester = MediConnectAPITester()
    
    # Test sequence based on review request
    tests = [
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("Validate Registration Code", tester.test_validate_registration_code),
        ("Clinic Registration", tester.test_clinic_registration),
        ("Get Current User", tester.test_auth_me),
        ("Get All Clinics", tester.test_get_clinics),
        ("Get All Doctors", tester.test_get_doctors),
        ("Get Appointments", tester.test_get_appointments),
        ("Get Dashboard Stats", tester.test_get_stats),
        ("Clinic Admin Login", tester.test_clinic_admin_login),
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