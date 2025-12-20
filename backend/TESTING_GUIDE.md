# MediConnect - Testing Implementation Guide

**Status**: ✅ Testing Infrastructure Complete  
**Coverage Target**: 80%+  
**Last Updated**: December 20, 2025

---

## 📋 Overview

Comprehensive automated testing suite for MediConnect, covering all critical workflows and business logic.

### What's Implemented

✅ **Test Infrastructure**
- Pytest configuration
- Async test support
- Coverage reporting
- Test fixtures and helpers

✅ **Test Categories**
- Authentication & Authorization (15+ tests)
- Doctor Management (20+ tests)
- Appointment Workflows (25+ tests)
- Clinic Operations (10+ tests)

✅ **Test Types**
- Unit tests
- Integration tests
- End-to-end tests
- Security tests

---

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for testing
- `faker` - Test data generation

### 2. Run All Tests

```bash
# Windows
run-tests.bat

# Or directly
cd backend
pytest -v
```

### 3. View Coverage Report

```bash
# Run with coverage
pytest --cov=app --cov-report=html

# Open report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac/Linux
```

---

## 📊 Test Structure

```
backend/
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_auth.py             # Authentication tests
│   ├── test_doctors.py          # Doctor tests
│   ├── test_appointments.py     # Appointment tests
│   ├── test_clinics.py          # Clinic tests
│   └── README.md                # Test documentation
├── pytest.ini                   # Pytest configuration
└── run_tests.py                 # Test runner script
```

---

## 🧪 Test Categories

### 1. Authentication Tests (`test_auth.py`)

**Coverage**: User registration, login, JWT tokens, permissions

```python
# Example tests:
- test_register_new_user_success
- test_register_duplicate_email
- test_login_success
- test_login_wrong_password
- test_access_protected_route_without_token
- test_password_hashed_in_database
- test_regular_user_cannot_create_clinic
- test_admin_can_create_clinic
```

**Run auth tests:**
```bash
pytest -m auth
# or
run-tests.bat auth
```

### 2. Doctor Tests (`test_doctors.py`)

**Coverage**: Doctor CRUD, availability, caching

```python
# Example tests:
- test_create_doctor_as_admin
- test_create_doctor_as_regular_user_fails
- test_get_doctor_by_id
- test_get_doctor_availability
- test_availability_excludes_booked_slots
- test_update_doctor_as_admin
- test_doctor_cached_after_first_request
- test_cache_invalidated_after_update
```

**Run doctor tests:**
```bash
pytest -m doctors
# or
run-tests.bat doctors
```

### 3. Appointment Tests (`test_appointments.py`)

**Coverage**: Booking, cancellation, recurring appointments

```python
# Example tests:
- test_create_appointment_success
- test_create_appointment_past_date_fails
- test_create_appointment_duplicate_slot_fails
- test_get_my_appointments
- test_cannot_view_other_users_appointment
- test_cancel_appointment_as_patient
- test_reschedule_appointment
- test_create_recurring_appointments
- test_appointment_within_doctor_availability
```

**Run appointment tests:**
```bash
pytest -m appointments
# or
run-tests.bat appointments
```

### 4. Clinic Tests (`test_clinics.py`)

**Coverage**: Clinic CRUD, services, doctor relationships

```python
# Example tests:
- test_create_clinic_as_admin
- test_create_clinic_as_regular_user_fails
- test_get_all_clinics
- test_search_clinics_by_county
- test_update_clinic_working_hours
- test_get_clinic_doctors
- test_add_service_to_clinic
```

**Run clinic tests:**
```bash
pytest tests/test_clinics.py -v
```

---

## 🎯 Running Tests

### Run All Tests

```bash
# With coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v

# Quick run (no coverage)
pytest --tb=short
```

### Run Specific Categories

```bash
# Authentication tests
pytest -m auth

# Doctor tests
pytest -m doctors

# Appointment tests
pytest -m appointments

# Integration tests
pytest -m integration

# Security tests
pytest -m security
```

### Run Specific Test File

```bash
pytest tests/test_auth.py -v
pytest tests/test_doctors.py -v
pytest tests/test_appointments.py -v
```

### Run Specific Test

```bash
# Run single test
pytest tests/test_auth.py::TestUserLogin::test_login_success -v

# Run test class
pytest tests/test_auth.py::TestUserLogin -v
```

### Run with Different Options

```bash
# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run failed tests first
pytest --ff

# Parallel execution (requires pytest-xdist)
pytest -n auto
```

---

## 📈 Coverage Reports

### Generate Coverage Report

```bash
# HTML report (recommended)
pytest --cov=app --cov-report=html

# Terminal report
pytest --cov=app --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=app --cov-report=xml

# All formats
pytest --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml
```

### View Coverage Report

```bash
# Open HTML report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # Mac/Linux
```

### Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| **Overall** | 80%+ | TBD |
| **Auth & Security** | 100% | TBD |
| **Business Logic** | 90%+ | TBD |
| **API Endpoints** | 85%+ | TBD |
| **Critical Paths** | 95%+ | TBD |

---

## 🔧 Test Fixtures

Shared fixtures available in all tests (from `conftest.py`):

### Basic Fixtures

```python
@pytest.fixture
async def client():
    """HTTP test client"""
    # Usage: response = await client.get("/api/endpoint")

@pytest.fixture
async def test_user():
    """Regular test user"""
    # Returns: {"email": "test@example.com", "password": "...", "user_id": "..."}

@pytest.fixture
async def auth_headers():
    """Authentication headers for test user"""
    # Returns: {"Authorization": "Bearer <token>"}

@pytest.fixture
async def admin_user():
    """Admin test user"""
    # Returns: {"email": "admin@example.com", "role": "CLINIC_ADMIN", ...}

@pytest.fixture
async def admin_headers():
    """Authentication headers for admin user"""
    # Returns: {"Authorization": "Bearer <token>"}
```

### Resource Fixtures

```python
@pytest.fixture
async def test_clinic():
    """Test clinic"""
    # Returns: {"clinic_id": "...", "name": "Test Clinic", ...}

@pytest.fixture
async def test_doctor():
    """Test doctor"""
    # Returns: {"doctor_id": "...", "name": "Dr. Test", ...}

@pytest.fixture
async def test_appointment():
    """Test appointment"""
    # Returns: {"appointment_id": "...", "date_time": "...", ...}
```

### Sample Data Fixtures

```python
@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""

@pytest.fixture
def sample_doctor_data():
    """Sample doctor data for testing"""

@pytest.fixture
def sample_appointment_data():
    """Sample appointment data for testing"""
```

---

## 📝 Writing New Tests

### Test Template

```python
import pytest
from httpx import AsyncClient

@pytest.mark.your_category
@pytest.mark.asyncio
class TestYourFeature:
    """Test your feature description"""
    
    async def test_success_case(
        self,
        client: AsyncClient,
        auth_headers
    ):
        """Test successful operation"""
        # Arrange
        data = {
            "field1": "value1",
            "field2": "value2"
        }
        
        # Act
        response = await client.post(
            "/api/your-endpoint",
            json=data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        result = response.json()
        assert result["field1"] == data["field1"]
        assert "id" in result
    
    async def test_failure_case(
        self,
        client: AsyncClient,
        auth_headers
    ):
        """Test failure scenario"""
        # Arrange
        invalid_data = {"field1": ""}
        
        # Act
        response = await client.post(
            "/api/your-endpoint",
            json=invalid_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400
        assert "error" in response.json()
```

### Best Practices

1. **Use descriptive names**
   ```python
   # Good
   async def test_user_cannot_delete_other_users_appointment()
   
   # Bad
   async def test_delete()
   ```

2. **Follow AAA pattern**
   ```python
   # Arrange - Set up test data
   user_data = {"email": "test@example.com"}
   
   # Act - Perform the action
   response = await client.post("/api/users", json=user_data)
   
   # Assert - Verify the result
   assert response.status_code == 201
   ```

3. **Test one thing per test**
   ```python
   # Good - Tests one specific behavior
   async def test_login_with_wrong_password_fails()
   
   # Bad - Tests multiple things
   async def test_login_and_get_user_and_update_profile()
   ```

4. **Use fixtures for setup**
   ```python
   # Good - Uses fixture
   async def test_get_appointment(client, test_appointment):
       response = await client.get(f"/api/appointments/{test_appointment['id']}")
   
   # Bad - Creates data in test
   async def test_get_appointment(client):
       # Create appointment...
       # Create doctor...
       # Create clinic...
       response = await client.get(f"/api/appointments/{appointment_id}")
   ```

5. **Test both success and failure**
   ```python
   async def test_create_appointment_success()
   async def test_create_appointment_past_date_fails()
   async def test_create_appointment_duplicate_slot_fails()
   async def test_create_appointment_without_auth_fails()
   ```

---

## 🐛 Debugging Tests

### Verbose Output

```bash
# More verbose
pytest -v

# Even more verbose
pytest -vv
```

### Show Print Statements

```bash
pytest -s
```

### Drop into Debugger on Failure

```bash
pytest --pdb
```

### Run Specific Failed Test

```bash
# Run last failed
pytest --lf

# Run failed first, then others
pytest --ff
```

### Show Local Variables on Failure

```bash
pytest -l
```

### Detailed Traceback

```bash
pytest --tb=long
```

---

## 🚨 CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:7
        ports:
          - 27017:27017
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-report=term-missing
        env:
          MONGO_URL: mongodb://localhost:27017
          REDIS_URL: redis://localhost:6379/0
          TESTING: true
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
        with:
          file: ./backend/coverage.xml
          fail_ci_if_error: true
      
      - name: Check coverage threshold
        run: |
          cd backend
          pytest --cov=app --cov-fail-under=80
```

---

## 📊 Test Metrics

### Current Status

```
Total Tests: 70+
├── Authentication: 15 tests
├── Doctors: 20 tests
├── Appointments: 25 tests
├── Clinics: 10 tests
└── Integration: All

Coverage: TBD (Target: 80%+)
├── Auth & Security: TBD (Target: 100%)
├── Business Logic: TBD (Target: 90%+)
├── API Endpoints: TBD (Target: 85%+)
└── Critical Paths: TBD (Target: 95%+)
```

### Run Metrics

```bash
# Get test count
pytest --collect-only

# Get coverage summary
pytest --cov=app --cov-report=term-missing

# Generate detailed report
pytest --cov=app --cov-report=html
```

---

## 🎓 Testing Checklist

When adding new features, ensure:

- [ ] Unit tests for business logic
- [ ] Integration tests for API endpoints
- [ ] Success case tested
- [ ] Failure cases tested
- [ ] Permission checks tested
- [ ] Input validation tested
- [ ] Edge cases tested
- [ ] Error messages verified
- [ ] Coverage > 80%
- [ ] All tests pass
- [ ] Documentation updated

---

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [HTTPX Testing](https://www.python-httpx.org/advanced/#testing)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

## 🤝 Contributing

1. Write tests for new features
2. Ensure all tests pass
3. Maintain 80%+ coverage
4. Follow testing best practices
5. Update documentation

---

## 📞 Support

For testing issues:
- Check test output for errors
- Review test logs
- Verify database connection
- Check fixture setup
- Review test documentation

---

**Happy Testing! 🧪✅**
