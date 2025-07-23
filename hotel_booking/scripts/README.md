# Hotel Booking Engine - Utility Scripts

This directory contains utility scripts for development, testing, and deployment.

## 📁 Available Scripts

### `api_integration_tests.py`
**Purpose**: Comprehensive API testing script
**Usage**: `python api_integration_tests.py`
**Description**: Tests all API endpoints including authentication, JWT token blacklisting, and user management functionality.

**Test Coverage**:
- ✅ User Registration
- ✅ User Login (JWT tokens)
- ✅ Profile Access (protected endpoint)
- ✅ Password Change
- ✅ Token Refresh
- ✅ Secure Logout (with token blacklisting)
- ✅ Token Blacklist Validation

### `environment_checker.py`
**Purpose**: Environment validation utility
**Usage**: `python environment_checker.py`
**Description**: Validates Django configuration, database connectivity, and environment setup.

**Checks**:
- Django settings module
- Database connection
- Environment variables
- Installed packages
- Development/Production mode

## 🚀 Running Scripts

1. **Prerequisites**:
   ```bash
   # Ensure Django server is running (for API tests)
   cd ../
   python manage.py runserver
   ```

2. **Execute Scripts**:
   ```bash
   cd scripts/
   python script_name.py
   ```

## 📋 Script Requirements

- Python 3.8+
- Django development server (for API tests)
- All project dependencies installed
- Database migrations applied

## 🔒 Production Notes

- API integration tests should only be run in development
- Environment checker can be used in production for health checks
- All scripts are designed to be safe and non-destructive

## 📚 Adding New Scripts

When adding new utility scripts:
1. Place them in this directory
2. Follow the existing naming convention
3. Include comprehensive docstrings
4. Update this README with script descriptions
5. Ensure they're excluded from production deployments via .gitignore

---
**Last Updated**: July 23, 2025  
**Directory Purpose**: Development and deployment utilities
