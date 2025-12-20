# MediConnect - Testing Guide

**Status**: ✅ Infrastructure Complete  
**Coverage Target**: 80%+  
**Tests**: 72 automated tests

---

## 🚀 Quick Start

### Run All Tests

```bash
# Windows
run-tests.bat

# Or directly
cd backend
pytest -v
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
start htmlcov/index.html
```

---

## 📊 Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures
├── test_auth.py             # Authentication (18 tests)
├── test_doctors.py          # Doctors (20 tests)
├── test_appointments.py     # Appointments (21 tests)
└── test_clinics.py          # Clinics (10 tests)
```

---

## 🧪 Test Categories

### Run Specific Tests

```bash
# Authentication tests
pytest -m auth

# Doctor tests
pytest -m doctors

# Appointment tests
pytest -m appointments

# Specific file
pytest tests/test_auth.py -v

# Single test
pytest tests/test_auth.py::test_login_success -v
```

---

## 📈 Coverage Reports

```bash
# HTML report (recommended)
pytest --cov=app --cov-report=html

# Terminal report
pytest --cov=app --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=app --cov-report=xml
```

### Coverage Goals

| Component | Target |
|-----------|--------|
| Overall | 80%+ |
| Auth & Security | 100% |
| Business Logic | 90%+ |
| API Endpoints | 85%+ |

---

## 🔧 Available Fixtures

```python
client              # HTTP test client
test_user          # Regular user
auth_headers       # User auth headers
admin_user         # Admin user
admin_headers      # Admin auth headers
test_clinic        # Sample clinic
test_doctor        # Sample doctor
test_appointment   # Sample appointment
```

---

## 📝 Writing New Tests

### Test Template

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestYourFeature:
    async def test_success_case(
        self,
        client: AsyncClient,
        auth_headers
    ):
        # Arrange
        data = {"field": "value"}
        
        # Act
        response = await client.post(
            "/api/endpoint",
            json=data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        assert response.json()["field"] == "value"
```

---

## 🐛 Debugging Tests

```bash
# Verbose output
pytest -vv

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Drop into debugger
pytest --pdb
```

---

## 🚨 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

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
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## 📊 Current Status

**Infrastructure**: ✅ Complete  
**Tests Written**: 72 tests  
**Tests Passing**: 5 tests (framework operational)  
**Status**: Ready for development

**What Works:**
- ✅ Test infrastructure fully operational
- ✅ pytest-asyncio configured
- ✅ Fixtures working
- ✅ Rate limiting disabled for tests
- ✅ Database cleanup working

**What Needs Adjustment:**
- ⚠️ Test data validation (422 responses)
- ⚠️ Data structures need to match API schemas

---

## 🎓 Testing Checklist

When adding new features:

- [ ] Unit tests for business logic
- [ ] Integration tests for API endpoints
- [ ] Success case tested
- [ ] Failure cases tested
- [ ] Permission checks tested
- [ ] Input validation tested
- [ ] Edge cases tested
- [ ] Coverage > 80%
- [ ] All tests pass

---

## 📚 Best Practices

1. **Use descriptive names**
   ```python
   # Good
   async def test_user_cannot_delete_other_users_appointment()
   
   # Bad
   async def test_delete()
   ```

2. **Follow AAA pattern**
   - Arrange - Set up test data
   - Act - Perform the action
   - Assert - Verify the result

3. **Test one thing per test**

4. **Use fixtures for setup**

5. **Test both success and failure**

---

## 📞 Support

For testing issues:
- Check test output for errors
- Review test logs
- Verify database connection
- Check fixture setup

---

**Happy Testing! 🧪✅**
