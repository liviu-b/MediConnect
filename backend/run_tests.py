"""
Test Runner Script
Run all tests with coverage reporting
"""

import sys
import subprocess


def run_tests():
    """Run pytest with coverage"""
    print("🧪 Running MediConnect Test Suite...\n")
    
    # Run pytest with coverage
    cmd = [
        "pytest",
        "-v",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--tb=short",
        "tests/"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("\n📊 Coverage report generated:")
        print("   - HTML: htmlcov/index.html")
        print("   - XML: coverage.xml")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


def run_specific_tests(marker):
    """Run tests with specific marker"""
    print(f"🧪 Running {marker} tests...\n")
    
    cmd = [
        "pytest",
        "-v",
        "-m", marker,
        "--tb=short",
        "tests/"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"\n✅ All {marker} tests passed!")
    else:
        print(f"\n❌ Some {marker} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test category
        marker = sys.argv[1]
        run_specific_tests(marker)
    else:
        # Run all tests
        run_tests()
