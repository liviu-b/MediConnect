"""
Test script for Resend email implementation
Run this to verify all email templates are working correctly
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.email import (
    send_staff_invitation_email,
    send_password_reset_email,
    send_appointment_confirmation_email,
    send_appointment_reminder_email,
    send_cancellation_notification_email,
    send_welcome_email,
    send_access_request_notification_email
)
from app.config import RESEND_API_KEY, DEFAULT_FROM_EMAIL
from datetime import datetime, timedelta


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(result, email_type):
    """Print the result of an email send attempt"""
    if result.get("success"):
        email_id = result.get("email_id", "N/A")
        print(f"✅ {email_type} - SUCCESS (ID: {email_id})")
    else:
        error = result.get("error", "Unknown error")
        print(f"❌ {email_type} - FAILED: {error}")


def check_configuration():
    """Check if Resend is properly configured"""
    print_header("Configuration Check")
    
    if not RESEND_API_KEY:
        print("❌ RESEND_API_KEY is not set in .env file")
        print("   Please add: RESEND_API_KEY=your_api_key_here")
        return False
    
    print(f"✅ RESEND_API_KEY is set: {RESEND_API_KEY[:10]}...")
    print(f"✅ DEFAULT_FROM_EMAIL: {DEFAULT_FROM_EMAIL}")
    return True


def test_staff_invitation():
    """Test staff invitation email"""
    print_header("Test 1: Staff Invitation Email")
    
    result = send_staff_invitation_email(
        recipient_email="keen-cents.0t@icloud.com",
        recipient_name="Dr. John Smith",
        role="DOCTOR",
        invitation_link="https://mediconnect.com/accept-invitation?token=test_token_123",
        clinic_name="City Medical Center",
        inviter_name="Admin User"
    )
    
    print_result(result, "Staff Invitation")
    return result.get("success", False)


def test_password_reset():
    """Test password reset email"""
    print_header("Test 2: Password Reset Email")
    
    result = send_password_reset_email(
        recipient_email="keen-cents.0t@icloud.com",
        recipient_name="Jane Doe",
        reset_link="https://mediconnect.com/reset-password?token=reset_token_456",
        medical_center={"name": "City Medical Center"}
    )
    
    print_result(result, "Password Reset")
    return result.get("success", False)


def test_appointment_confirmation():
    """Test appointment confirmation email"""
    print_header("Test 3: Appointment Confirmation Email")
    
    # Create a future appointment date
    future_date = datetime.now() + timedelta(days=7)
    appointment_date = future_date.isoformat()
    
    result = send_appointment_confirmation_email(
        patient_email="keen-cents.0t@icloud.com",
        patient_name="Jane Doe",
        doctor_name="Dr. John Smith",
        clinic_name="City Medical Center",
        appointment_date=appointment_date,
        appointment_id="apt_test_123456",
        clinic_address="123 Main Street, City, State 12345"
    )
    
    print_result(result, "Appointment Confirmation")
    return result.get("success", False)


def test_appointment_reminder():
    """Test appointment reminder email"""
    print_header("Test 4: Appointment Reminder Email")
    
    # Create a tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    appointment_date = tomorrow.isoformat()
    
    result = send_appointment_reminder_email(
        patient_email="keen-cents.0t@icloud.com",
        patient_name="Jane Doe",
        doctor_name="Dr. John Smith",
        clinic_name="City Medical Center",
        appointment_date=appointment_date,
        clinic_address="123 Main Street, City, State 12345"
    )
    
    print_result(result, "Appointment Reminder")
    return result.get("success", False)


def test_cancellation_notification():
    """Test appointment cancellation email"""
    print_header("Test 5: Appointment Cancellation Email")
    
    # Create a future appointment date
    future_date = datetime.now() + timedelta(days=3)
    appointment_date = future_date.isoformat()
    
    result = send_cancellation_notification_email(
        patient_email="keen-cents.0t@icloud.com",
        patient_name="Jane Doe",
        doctor_name="Dr. John Smith",
        clinic_name="City Medical Center",
        appointment_date=appointment_date,
        cancellation_reason="Doctor is unavailable due to emergency"
    )
    
    print_result(result, "Cancellation Notification")
    return result.get("success", False)


def test_welcome_email():
    """Test welcome email"""
    print_header("Test 6: Welcome Email")
    
    result = send_welcome_email(
        recipient_email="keen-cents.0t@icloud.com",
        recipient_name="Jane Doe",
        user_role="USER"
    )
    
    print_result(result, "Welcome Email")
    return result.get("success", False)


def test_access_request_notification():
    """Test access request notification email"""
    print_header("Test 7: Access Request Notification Email")
    
    result = send_access_request_notification_email(
        admin_email="keen-cents.0t@icloud.com",
        admin_name="Admin User",
        requester_name="John Doe",
        requester_email="john.doe@example.com",
        clinic_name="City Medical Center",
        request_id="req_test_789"
    )
    
    print_result(result, "Access Request Notification")
    return result.get("success", False)


def run_all_tests():
    """Run all email tests"""
    print("\n" + "🚀" * 30)
    print("  RESEND EMAIL IMPLEMENTATION TEST SUITE")
    print("🚀" * 30)
    
    # Check configuration first
    if not check_configuration():
        print("\n❌ Configuration check failed. Please fix the issues above.")
        return
    
    print("\n📧 Starting email tests...")
    print("Note: All test emails will be sent to 'keen-cents.0t@icloud.com'")
    print("      (This is the verified email for the Resend API key)")
    
    # Run all tests
    results = []
    results.append(("Staff Invitation", test_staff_invitation()))
    results.append(("Password Reset", test_password_reset()))
    results.append(("Appointment Confirmation", test_appointment_confirmation()))
    results.append(("Appointment Reminder", test_appointment_reminder()))
    results.append(("Cancellation Notification", test_cancellation_notification()))
    results.append(("Welcome Email", test_welcome_email()))
    results.append(("Access Request Notification", test_access_request_notification()))
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    print("\nDetailed Results:")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed == total:
        print("\n🎉 All tests passed! Resend is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
    
    print("\n" + "=" * 60)
    print("💡 Tips:")
    print("  - Check Resend dashboard: https://resend.com/emails")
    print("  - Verify your API key is correct")
    print("  - For production, use a verified domain")
    print("  - Check application logs for detailed errors")
    print("=" * 60 + "\n")


def test_custom_email():
    """Test with a custom email address"""
    print_header("Custom Email Test")
    
    email = input("Enter your email address to receive a test email: ").strip()
    
    if not email or "@" not in email:
        print("❌ Invalid email address")
        return
    
    print(f"\n📧 Sending test email to: {email}")
    
    result = send_welcome_email(
        recipient_email=email,
        recipient_name="Test User",
        user_role="USER"
    )
    
    if result.get("success"):
        print(f"\n✅ Test email sent successfully!")
        print(f"   Email ID: {result.get('email_id', 'N/A')}")
        print(f"   Check your inbox at: {email}")
    else:
        print(f"\n❌ Failed to send test email")
        print(f"   Error: {result.get('error', 'Unknown error')}")


def interactive_menu():
    """Interactive menu for testing"""
    while True:
        print("\n" + "=" * 60)
        print("  RESEND EMAIL TEST MENU")
        print("=" * 60)
        print("\n1. Run all tests (test@example.com)")
        print("2. Send test email to custom address")
        print("3. Test staff invitation")
        print("4. Test password reset")
        print("5. Test appointment confirmation")
        print("6. Test appointment reminder")
        print("7. Test cancellation notification")
        print("8. Test welcome email")
        print("9. Test access request notification")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-9): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        elif choice == "1":
            run_all_tests()
        elif choice == "2":
            test_custom_email()
        elif choice == "3":
            test_staff_invitation()
        elif choice == "4":
            test_password_reset()
        elif choice == "5":
            test_appointment_confirmation()
        elif choice == "6":
            test_appointment_reminder()
        elif choice == "7":
            test_cancellation_notification()
        elif choice == "8":
            test_welcome_email()
        elif choice == "9":
            test_access_request_notification()
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            run_all_tests()
        elif sys.argv[1] == "--custom":
            test_custom_email()
        else:
            print("Usage:")
            print("  python test_resend.py           # Interactive menu")
            print("  python test_resend.py --all     # Run all tests")
            print("  python test_resend.py --custom  # Send to custom email")
    else:
        interactive_menu()
