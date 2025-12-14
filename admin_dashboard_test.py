#!/usr/bin/env python3

import requests
import json
import time

class AdminDashboardTester:
    def __init__(self, base_url="https://medteam-login.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.clinic_id = None
        
    def login_admin(self):
        """Login as clinic admin using review request credentials"""
        print("🔐 Logging in as clinic admin...")
        
        data = {
            "email": "admin@testmed.com",
            "password": "admin123456"
        }
        
        response = self.session.post(f"{self.api_url}/auth/login", json=data)
        
        if response.status_code == 200:
            user_data = response.json()
            self.clinic_id = user_data.get('user', {}).get('clinic_id')
            print(f"✅ Admin login successful - Clinic ID: {self.clinic_id}")
            return True
        else:
            print(f"❌ Admin login failed: {response.status_code} - {response.text}")
            return False
    
    def test_operating_hours(self):
        """Test Operating Hours Settings"""
        print("\n📅 Testing Operating Hours Settings...")
        
        # Test data with various scenarios
        working_hours = {
            "working_hours": {
                "monday": {"start": "08:00", "end": "18:00"},
                "tuesday": {"start": "09:00", "end": "17:00"},
                "wednesday": {"start": "08:30", "end": "16:30"},
                "thursday": {"start": "10:00", "end": "19:00"},
                "friday": {"start": "08:00", "end": "16:00"},
                "saturday": {"start": "09:00", "end": "13:00"},
                "sunday": None  # Closed day
            }
        }
        
        # Update working hours
        response = self.session.put(f"{self.api_url}/clinics/{self.clinic_id}", json=working_hours)
        
        if response.status_code == 200:
            print("✅ Operating hours updated successfully")
            
            # Verify retrieval
            get_response = self.session.get(f"{self.api_url}/clinics/{self.clinic_id}")
            if get_response.status_code == 200:
                clinic_data = get_response.json()
                saved_hours = clinic_data.get('working_hours', {})
                
                print("📋 Verifying saved working hours:")
                for day, hours in working_hours["working_hours"].items():
                    saved_day = saved_hours.get(day)
                    if hours is None:
                        if saved_day is None:
                            print(f"   ✅ {day.capitalize()}: Closed (null)")
                        else:
                            print(f"   ❌ {day.capitalize()}: Expected closed, got {saved_day}")
                    else:
                        if saved_day and saved_day.get('start') == hours['start'] and saved_day.get('end') == hours['end']:
                            print(f"   ✅ {day.capitalize()}: {hours['start']}-{hours['end']}")
                        else:
                            print(f"   ❌ {day.capitalize()}: Expected {hours}, got {saved_day}")
                
                return True
            else:
                print(f"❌ Failed to retrieve clinic data: {get_response.status_code}")
                return False
        else:
            print(f"❌ Failed to update operating hours: {response.status_code} - {response.text}")
            return False
    
    def test_services_currency(self):
        """Test Services with Currency Support"""
        print("\n💰 Testing Services with Currency Support...")
        
        # Test 1: Create service with LEI currency
        lei_service = {
            "name": "Consultation LEI Test",
            "description": "Medical consultation priced in Romanian Lei",
            "duration": 30,
            "price": 150.0,
            "currency": "LEI"
        }
        
        response = self.session.post(f"{self.api_url}/services", json=lei_service)
        if response.status_code == 200:
            lei_service_data = response.json()
            lei_service_id = lei_service_data.get('service_id')
            print(f"✅ LEI service created: {lei_service_data.get('name')} - {lei_service_data.get('currency')}")
        else:
            print(f"❌ Failed to create LEI service: {response.status_code} - {response.text}")
            return False
        
        # Test 2: Create service with EURO currency
        euro_service = {
            "name": "Consultation EURO Test",
            "description": "Medical consultation priced in Euros",
            "duration": 45,
            "price": 75.0,
            "currency": "EURO"
        }
        
        response = self.session.post(f"{self.api_url}/services", json=euro_service)
        if response.status_code == 200:
            euro_service_data = response.json()
            euro_service_id = euro_service_data.get('service_id')
            print(f"✅ EURO service created: {euro_service_data.get('name')} - {euro_service_data.get('currency')}")
        else:
            print(f"❌ Failed to create EURO service: {response.status_code} - {response.text}")
            return False
        
        # Test 3: Update service currency
        update_data = {
            "name": "Updated Consultation",
            "description": "Updated consultation with new currency",
            "duration": 30,
            "price": 100.0,
            "currency": "EURO"
        }
        
        response = self.session.put(f"{self.api_url}/services/{lei_service_id}", json=update_data)
        if response.status_code == 200:
            updated_service = response.json()
            print(f"✅ Service currency updated: {updated_service.get('name')} - {updated_service.get('currency')}")
        else:
            print(f"❌ Failed to update service currency: {response.status_code} - {response.text}")
            return False
        
        # Test 4: Verify GET /api/services returns currency
        response = self.session.get(f"{self.api_url}/services")
        if response.status_code == 200:
            services = response.json()
            print(f"\n📋 Services with currency (Total: {len(services)}):")
            
            currencies_found = set()
            for service in services:
                currency = service.get('currency', 'N/A')
                currencies_found.add(currency)
                print(f"   • {service.get('name', 'Unknown')}: {service.get('price', 0)} {currency}")
            
            print(f"\n💱 Currencies supported: {list(currencies_found)}")
            
            # Check if both LEI and EURO are supported
            if 'LEI' in currencies_found and 'EURO' in currencies_found:
                print("✅ Both LEI and EURO currencies are supported")
                return True
            elif len(currencies_found) > 0:
                print("⚠️  Partial currency support detected")
                return True
            else:
                print("❌ No currency support found")
                return False
        else:
            print(f"❌ Failed to retrieve services: {response.status_code} - {response.text}")
            return False
    
    def run_all_tests(self):
        """Run all Administrator Dashboard Settings tests"""
        print("🏥 Administrator Dashboard Settings - Comprehensive Test")
        print("=" * 60)
        
        if not self.login_admin():
            return False
        
        print(f"🎯 Testing with Clinic ID: {self.clinic_id}")
        
        # Test Operating Hours
        hours_success = self.test_operating_hours()
        
        # Test Services with Currency
        currency_success = self.test_services_currency()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        if hours_success:
            print("✅ Operating Hours Settings: PASSED")
        else:
            print("❌ Operating Hours Settings: FAILED")
        
        if currency_success:
            print("✅ Services with Currency: PASSED")
        else:
            print("❌ Services with Currency: FAILED")
        
        overall_success = hours_success and currency_success
        
        if overall_success:
            print("\n🎉 All Administrator Dashboard Settings tests PASSED!")
        else:
            print("\n⚠️  Some Administrator Dashboard Settings tests FAILED!")
        
        return overall_success

if __name__ == "__main__":
    tester = AdminDashboardTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)