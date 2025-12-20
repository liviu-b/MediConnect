"""
Complete RBAC System Test Suite

Runs all tests from Phases 1-5 to verify the system is working correctly.

Run: python test_all_phases.py
"""

import asyncio
import sys
import subprocess
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")


def run_test_file(test_file, description):
    """Run a test file and return success status"""
    print_header(f"Running: {description}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print_success(f"{description} - ALL TESTS PASSED")
            return True
        else:
            print_error(f"{description} - SOME TESTS FAILED")
            if result.stderr:
                print(f"\nError output:\n{result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print_error(f"{description} - TIMEOUT (>60s)")
        return False
    except Exception as e:
        print_error(f"{description} - ERROR: {str(e)}")
        return False


def main():
    print_header("MEDICONNECT RBAC - COMPLETE TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test files to run
    tests = [
        ("test_rbac_system.py", "Phase 1 & 2: RBAC System Tests (50 tests)"),
        ("test_phase3_invitations.py", "Phase 3: Invitation System Tests (27 tests)"),
        ("test_phase4_dashboard.py", "Phase 4: Dashboard Routing Tests (20 tests)"),
    ]
    
    results = {}
    total_passed = 0
    total_failed = 0
    
    # Run each test file
    for test_file, description in tests:
        success = run_test_file(test_file, description)
        results[description] = success
        if success:
            total_passed += 1
        else:
            total_failed += 1
    
    # Print summary
    print_header("TEST SUITE SUMMARY")
    
    for description, success in results.items():
        if success:
            print_success(f"{description}")
        else:
            print_error(f"{description}")
    
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"Total Test Files: {len(tests)}")
    print(f"{GREEN}Passed: {total_passed}{RESET}")
    print(f"{RED}Failed: {total_failed}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")
    
    # Overall result
    if total_failed == 0:
        print_success("🎉 ALL TEST SUITES PASSED!")
        print(f"\n{GREEN}The RBAC system is working correctly.{RESET}")
        print(f"{GREEN}Ready to proceed with manual testing and Phase 6!{RESET}\n")
        return 0
    else:
        print_error("❌ SOME TEST SUITES FAILED")
        print(f"\n{RED}Please fix the failing tests before proceeding.{RESET}\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
