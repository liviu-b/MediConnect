# MediConnect Test Suite

Comprehensive automated testing for the MediConnect application.

## 📋 Test Coverage

### Test Categories

| Category | Tests | Coverage |
|----------|-------|----------|
| **Authentication** | 15+ tests | Login, Registration, JWT, Permissions |
| **Doctors** | 20+ tests | CRUD, Availability, Caching |
| **Appointments** | 25+ tests | Booking, Cancellation, Recurring |
| **Clinics** | 10+ tests | CRUD, Services, Doctors |
| **Integration** | All | End-to-end workflows |

### Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.doctors` - Doctor-related tests
- `@pytest.mark.appointments` - Appointment tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.performance` - Performance tests

## 🚀 Running Tests

### Run All Tests

```bash
# Windows
cd backend
python run_tests.py

# Or directly with pytest
pytest -v

# With coverage report
pytest --cov=app --cov-report=html
```

### Run Specific Test Categories

```bash
# Authentication tests only
pytest -m auth

# Doctor tests only
pytest -m doctors

# Appointment tests only
pytest -m appointments

# Integration tests only
pytest -m integration
```

### Run Specific Test File

```bash
# Run auth tests
pytest tests/test_auth.py -v

# Run doctor tests
pytest tests/test_doctors.py -v

# Run appointment tests
pytest tests/test_appointments.py -v
```

### Run Specific Test

```bash
# Run single test
pytest tests/test_auth.py::TestUserLogin::test_login_success -v
```

## 📊 Coverage Reports

After running tests with coverage, reports are generated in:

- **HTML Report**: `htmlcov/index.html` (open in browser)
- **Terminal Report**: Displayed after test run
- **XML Report**: `coverage.xml` (for CI/CD)

### View HTML Coverage Report

```bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

## 🔧 Test Configuration

### pytest.ini

Configuration file for pytest settings:
- Test discovery patterns
- Coverage settings
- Markers
- Output options

### conftest.py

Shared fixtures for all tests:
- `client` - Test HTTP client
- `test_user` - Sample user
- `auth_headers` - Authentication headers
- `admin_user` - Admin user
- `admin_headers` - Admin authentication
- `test_clinic` - Sample clinic
- `test_doctor` - Sample doctor
- `test_appointment` - Sample appointment

## 📝 Writing New Tests

### Test Structure

```python
import pytest
from httpx import AsyncClient

@pytest.mark.your_marker
@pytest.mark.asyncio
class TestYourFeature:
    """Test your feature"""
    
    async def test_something(self, client: AsyncClient, auth_headers):
        """Test description"""
        # Arrange
        data = {"key": "value"}
        
        # Act
        response = await client.post("/api/endpoint", json=data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["key"] == "value"
```

### Best Practices

1. **Use descriptive test names**: `test_user_cannot_delete_other_users_appointment`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **One assertion per test** (when possible)
4. **Use fixtures** for common setup
5. **Test both success and failure cases**
6. **Test edge cases** and boundary conditions
7. **Mock external services** (email, payment, etc.)

### Example Test Cases to Cover

For each feature, test:
- ✅ Success case
- ❌ Failure cases (invalid input, unauthorized, etc.)
- 🔒 Permission checks
- 📊 Data validation
- 🔄 State transitions
- 🚫 Edge cases

## 🐛 Debugging Tests

### Run with verbose output

```bash
pytest -vv
```

### Run with print statements

```bash
pytest -s
```

### Run with debugger

```bash
pytest --pdb
```

### Run failed tests only

```bash
pytest --lf
```

### Run last failed first

```bash
pytest --ff
```

## 🔍 Test Database

Tests use a separate test database (`mediconnect_test`) that is:
- Created before tests
- Cleaned before each test
- Dropped after all tests

This ensures tests don't affect production data.

## 📈 Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| **Overall** | 80%+ |
| **Critical Paths** | 95%+ |
| **Auth & Security** | 100% |
| **Business Logic** | 90%+ |
| **API Endpoints** | 85%+ |

## 🚨 CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [HTTPX Testing](https://www.python-httpx.org/advanced/#testing)
- [Coverage.py](https://coverage.readthedocs.io/)

## 🤝 Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain 80%+ coverage
4. Update this README if needed

## 📞 Support

For test-related issues:
- Check test output for error messages
- Review test logs
- Check database connection
- Verify test fixtures are working

---

**Happy Testing! 🧪**
