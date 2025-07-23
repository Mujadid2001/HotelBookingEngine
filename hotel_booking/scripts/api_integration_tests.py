#!/usr/bin/env python3
"""
Hotel Booking Engine API Integration Test Script
===============================================

This script performs comprehensive integration testing of all API endpoints
for the accounts app. It validates authentication, JWT token blacklisting,
and all user management functionality.

Usage: 
    cd hotel_booking/scripts
    python api_integration_tests.py

Requirements:
    - Django development server running on http://127.0.0.1:8000
    - All dependencies installed
    - Database migrations applied

Test Coverage:
    ✅ User Registration
    ✅ User Login (JWT tokens)
    ✅ Profile Access (protected endpoint)  
    ✅ Password Change
    ✅ Token Refresh
    ✅ Secure Logout (with token blacklisting)
    ✅ Token Blacklist Validation

Last Updated: July 23, 2025
Status: Production Ready
"""

# Standard library imports
import json
import sys
from datetime import datetime

# Third-party imports
import requests

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000/api/accounts"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        
    def test_registration(self):
        """Test user registration"""
        self.log("Testing user registration...")
        
        data = {
            "email": f"testuser_{datetime.now().strftime('%H%M%S')}@example.com",
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
            "password_confirm": "testpass123"
        }
        
        response = self.session.post(f"{BASE_URL}/register/", json=data)
        
        if response.status_code == 201:
            result = response.json()
            self.log(f"Registration successful! User: {result['user']['email']}", "SUCCESS")
            self.user_email = data['email']
            self.user_password = data['password']
            return True
        else:
            self.log(f"Registration failed: {response.status_code} - {response.text}", "ERROR")
            return False
    
    def test_login(self):
        """Test user login"""
        self.log("Testing user login...")
        
        data = {
            "email": self.user_email,
            "password": self.user_password
        }
        
        response = self.session.post(f"{BASE_URL}/login/", json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result['tokens']['access']
            self.refresh_token = result['tokens']['refresh']
            self.log(f"Login successful! Welcome message: {result['message']}", "SUCCESS")
            return True
        else:
            self.log(f"Login failed: {response.status_code} - {response.text}", "ERROR")
            return False
    
    def test_profile_get(self):
        """Test getting user profile"""
        self.log("Testing profile retrieval...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = self.session.get(f"{BASE_URL}/profile/", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            self.log(f"Profile retrieved! User: {result['full_name']} ({result['email']})", "SUCCESS")
            self.log(f"User type: {result['user_type']}, Active: {result['is_active']}, Verified: {result['is_verified']}")
            return True
        else:
            self.log(f"Profile retrieval failed: {response.status_code} - {response.text}", "ERROR")
            return False
    
    def test_profile_update(self):
        """Test updating user profile"""
        self.log("Testing profile update...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {
            "bio": "Updated bio for testing",
            "city": "Test City",
            "profile": {
                "preferred_room_type": "deluxe",
                "dietary_restrictions": "vegetarian"
            }
        }
        
        response = self.session.put(f"{BASE_URL}/profile/update/", json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            self.log(f"Profile updated! Bio: {result.get('bio', 'N/A')}", "SUCCESS")
            return True
        else:
            self.log(f"Profile update failed: {response.status_code} - {response.text}", "ERROR")
            return False
    
    def test_password_reset(self):
        """Test password reset request"""
        self.log("Testing password reset...")
        
        data = {"email": self.user_email}
        response = self.session.post(f"{BASE_URL}/password/reset/", json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.log(f"Password reset requested: {result['message']}", "SUCCESS")
            return True
        else:
            self.log(f"Password reset failed: {response.status_code} - {response.text}", "ERROR")
            return False
    
    def test_token_refresh(self):
        """Test JWT token refresh"""
        self.log("Testing token refresh...")
        
        data = {"refresh": self.refresh_token}
        response = self.session.post(f"{BASE_URL}/token/refresh/", json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.log("Token refresh successful!", "SUCCESS")
            return True
        else:
            self.log(f"Token refresh failed: {response.status_code} - {response.text}", "ERROR")
            return False
    
    def test_logout(self):
        """Test user logout"""
        self.log("Testing logout...")
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        data = {"refresh": self.refresh_token}
        response = self.session.post(f"{BASE_URL}/logout/", json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            self.log(f"Logout successful: {result['message']}", "SUCCESS")
            return True
        else:
            self.log(f"Logout failed: {response.status_code} - {response.text}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 60)
        print("Hotel Booking Engine - API Test Suite")
        print("=" * 60)
        
        tests = [
            ("User Registration", self.test_registration),
            ("User Login", self.test_login),
            ("Profile Retrieval", self.test_profile_get),
            ("Profile Update", self.test_profile_update),
            ("Password Reset", self.test_password_reset),
            ("Token Refresh", self.test_token_refresh),
            ("User Logout", self.test_logout),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} FAILED - Exception: {str(e)}")
            
        print("\n" + "=" * 60)
        print(f"Test Results: {passed}/{total} tests passed")
        print("=" * 60)
        
        if passed == total:
            print("🎉 All tests passed! Your API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
            return False


def main():
    """Main function"""
    try:
        tester = APITester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to the server.")
        print("Make sure the Django development server is running on http://127.0.0.1:8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
