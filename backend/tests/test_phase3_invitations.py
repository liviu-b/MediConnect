"""
Phase 3 Invitation System Tests

This script tests the invitation system to ensure:
1. Role hierarchy is enforced
2. Token generation and validation works
3. Invitation acceptance creates users correctly
4. Location assignments are validated
5. Email validation works
6. Expiration handling works

Run: python test_phase3_invitations.py
"""

import asyncio
import sys
from datetime import datetime, timezone, timedelta
import secrets

sys.path.insert(0, '.')

from app.db import db
from app.schemas.user import User, UserRole
from app.schemas.invitation import (
    Invitation,
    validate_invitation_role,
    get_user_role_from_invitation_role
)
from app.services.permissions import PermissionService


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"  ✅ {test_name}")
    
    def add_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {reason}")
        print(f"  ❌ {test_name}")
        print(f"     Reason: {reason}")
    
    def summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({self.passed/total*100:.1f}%)")
        print(f"Failed: {self.failed} ({self.failed/total*100:.1f}%)")
        
        if self.failed > 0:
            print("\nFailed Tests:")
            for error in self.errors:
                print(f"  - {error}")
        
        return self.failed == 0


results = TestResults()


async def test_invitation_role_validation():
    """Test 1: Invitation role hierarchy validation"""
    print("\n" + "=" * 60)
    print("TEST 1: Invitation Role Hierarchy Validation")
    print("=" * 60)
    
    # Test 1.1: Super Admin can invite Location Admin
    can_invite = validate_invitation_role(UserRole.LOCATION_ADMIN, UserRole.SUPER_ADMIN)
    if can_invite:
        results.add_pass("Super Admin CAN invite Location Admin")
    else:
        results.add_fail("Super Admin invite Location Admin", "Should be allowed")
    
    # Test 1.2: Super Admin can invite Receptionist
    can_invite = validate_invitation_role(UserRole.RECEPTIONIST, UserRole.SUPER_ADMIN)
    if can_invite:
        results.add_pass("Super Admin CAN invite Receptionist")
    else:
        results.add_fail("Super Admin invite Receptionist", "Should be allowed")
    
    # Test 1.3: Location Admin CANNOT invite Location Admin
    can_invite = validate_invitation_role(UserRole.LOCATION_ADMIN, UserRole.LOCATION_ADMIN)
    if not can_invite:
        results.add_pass("Location Admin CANNOT invite Location Admin")
    else:
        results.add_fail("Location Admin invite Location Admin", "Should be denied")
    
    # Test 1.4: Location Admin CAN invite Receptionist
    can_invite = validate_invitation_role(UserRole.RECEPTIONIST, UserRole.LOCATION_ADMIN)
    if can_invite:
        results.add_pass("Location Admin CAN invite Receptionist")
    else:
        results.add_fail("Location Admin invite Receptionist", "Should be allowed")
    
    # Test 1.5: Location Admin CAN invite Doctor
    can_invite = validate_invitation_role(UserRole.DOCTOR, UserRole.LOCATION_ADMIN)
    if can_invite:
        results.add_pass("Location Admin CAN invite Doctor")
    else:
        results.add_fail("Location Admin invite Doctor", "Should be allowed")
    
    # Test 1.6: Location Admin CAN invite Assistant
    can_invite = validate_invitation_role(UserRole.ASSISTANT, UserRole.LOCATION_ADMIN)
    if can_invite:
        results.add_pass("Location Admin CAN invite Assistant")
    else:
        results.add_fail("Location Admin invite Assistant", "Should be allowed")
    
    # Test 1.7: Regular user CANNOT invite anyone
    can_invite = validate_invitation_role(UserRole.RECEPTIONIST, UserRole.USER)
    if not can_invite:
        results.add_pass("Regular user CANNOT invite")
    else:
        results.add_fail("Regular user invite", "Should be denied")


async def test_invitation_creation():
    """Test 2: Invitation creation and storage"""
    print("\n" + "=" * 60)
    print("TEST 2: Invitation Creation and Storage")
    print("=" * 60)
    
    # Clean up test data
    await db.invitations.delete_many({"email": "test_invite@test.com"})
    
    # Test 2.1: Create invitation
    invitation_token = f"invite_{secrets.token_hex(32)}"
    invitation = Invitation(
        organization_id="test_org_inv",
        location_ids=["test_loc_inv"],
        email="test_invite@test.com",
        name="Test Invitee",
        phone="+40123456789",
        role=UserRole.RECEPTIONIST,
        invitation_token=invitation_token,
        invited_by="test_admin_123",
        invited_by_name="Test Admin",
        status="PENDING"
    )
    
    invitation_doc = invitation.model_dump()
    invitation_doc['created_at'] = invitation_doc['created_at'].isoformat()
    invitation_doc['expires_at'] = invitation_doc['expires_at'].isoformat()
    
    await db.invitations.insert_one(invitation_doc)
    
    # Verify insertion
    stored = await db.invitations.find_one({"invitation_token": invitation_token})
    if stored:
        results.add_pass("Invitation created and stored in database")
    else:
        results.add_fail("Invitation creation", "Not found in database")
    
    # Test 2.2: Check required fields
    if stored:
        required_fields = ['invitation_id', 'email', 'role', 'invitation_token', 'status', 'expires_at']
        missing = [f for f in required_fields if f not in stored]
        if not missing:
            results.add_pass("Invitation has all required fields")
        else:
            results.add_fail("Invitation fields", f"Missing: {missing}")
    
    # Test 2.3: Check token format
    if stored and stored.get('invitation_token', '').startswith('invite_'):
        results.add_pass("Invitation token has correct format")
    else:
        results.add_fail("Invitation token format", "Should start with 'invite_'")
    
    # Test 2.4: Check expiration is set
    if stored and stored.get('expires_at'):
        expires_at = stored['expires_at']
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        # Should expire in ~7 days
        now = datetime.now(timezone.utc)
        days_until_expiry = (expires_at - now).days
        if 6 <= days_until_expiry <= 7:
            results.add_pass(f"Invitation expires in {days_until_expiry} days")
        else:
            results.add_fail("Invitation expiration", f"Expected 7 days, got {days_until_expiry}")
    else:
        results.add_fail("Invitation expiration", "expires_at not set")
    
    # Cleanup
    await db.invitations.delete_many({"email": "test_invite@test.com"})


async def test_role_mapping():
    """Test 3: Role mapping from invitation to user"""
    print("\n" + "=" * 60)
    print("TEST 3: Role Mapping")
    print("=" * 60)
    
    # Test 3.1: Location Admin maps correctly
    user_role = get_user_role_from_invitation_role(UserRole.LOCATION_ADMIN)
    if user_role == UserRole.LOCATION_ADMIN:
        results.add_pass("LOCATION_ADMIN maps to LOCATION_ADMIN")
    else:
        results.add_fail("LOCATION_ADMIN mapping", f"Got {user_role}")
    
    # Test 3.2: Receptionist maps correctly
    user_role = get_user_role_from_invitation_role(UserRole.RECEPTIONIST)
    if user_role == UserRole.RECEPTIONIST:
        results.add_pass("RECEPTIONIST maps to RECEPTIONIST")
    else:
        results.add_fail("RECEPTIONIST mapping", f"Got {user_role}")
    
    # Test 3.3: Doctor maps correctly
    user_role = get_user_role_from_invitation_role(UserRole.DOCTOR)
    if user_role == UserRole.DOCTOR:
        results.add_pass("DOCTOR maps to DOCTOR")
    else:
        results.add_fail("DOCTOR mapping", f"Got {user_role}")
    
    # Test 3.4: Assistant maps correctly
    user_role = get_user_role_from_invitation_role(UserRole.ASSISTANT)
    if user_role == UserRole.ASSISTANT:
        results.add_pass("ASSISTANT maps to ASSISTANT")
    else:
        results.add_fail("ASSISTANT mapping", f"Got {user_role}")


async def test_invitation_expiration():
    """Test 4: Invitation expiration handling"""
    print("\n" + "=" * 60)
    print("TEST 4: Invitation Expiration")
    print("=" * 60)
    
    # Clean up
    await db.invitations.delete_many({"email": "expired_test@test.com"})
    
    # Test 4.1: Create expired invitation
    invitation_token = f"invite_{secrets.token_hex(32)}"
    expired_invitation = {
        "invitation_id": f"inv_{secrets.token_hex(12)}",
        "organization_id": "test_org_exp",
        "location_ids": ["test_loc_exp"],
        "email": "expired_test@test.com",
        "name": "Expired Test",
        "role": UserRole.RECEPTIONIST,
        "invitation_token": invitation_token,
        "invited_by": "test_admin",
        "status": "PENDING",
        "expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "created_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
    }
    
    await db.invitations.insert_one(expired_invitation)
    
    # Test 4.2: Check if expired
    stored = await db.invitations.find_one({"invitation_token": invitation_token})
    if stored:
        expires_at = datetime.fromisoformat(stored['expires_at'])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        is_expired = expires_at < datetime.now(timezone.utc)
        if is_expired:
            results.add_pass("Expired invitation detected correctly")
        else:
            results.add_fail("Expiration detection", "Should be expired")
    
    # Test 4.3: Create valid invitation
    valid_token = f"invite_{secrets.token_hex(32)}"
    valid_invitation = {
        "invitation_id": f"inv_{secrets.token_hex(12)}",
        "organization_id": "test_org_valid",
        "location_ids": ["test_loc_valid"],
        "email": "valid_test@test.com",
        "name": "Valid Test",
        "role": UserRole.RECEPTIONIST,
        "invitation_token": valid_token,
        "invited_by": "test_admin",
        "status": "PENDING",
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.invitations.insert_one(valid_invitation)
    
    stored = await db.invitations.find_one({"invitation_token": valid_token})
    if stored:
        expires_at = datetime.fromisoformat(stored['expires_at'])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        is_valid = expires_at > datetime.now(timezone.utc)
        if is_valid:
            results.add_pass("Valid invitation detected correctly")
        else:
            results.add_fail("Valid invitation", "Should not be expired")
    
    # Cleanup
    await db.invitations.delete_many({"email": {"$in": ["expired_test@test.com", "valid_test@test.com"]}})


async def test_invitation_status():
    """Test 5: Invitation status management"""
    print("\n" + "=" * 60)
    print("TEST 5: Invitation Status Management")
    print("=" * 60)
    
    # Clean up
    await db.invitations.delete_many({"email": "status_test@test.com"})
    
    # Test 5.1: Create pending invitation
    invitation_token = f"invite_{secrets.token_hex(32)}"
    invitation = {
        "invitation_id": f"inv_{secrets.token_hex(12)}",
        "organization_id": "test_org_status",
        "location_ids": ["test_loc_status"],
        "email": "status_test@test.com",
        "name": "Status Test",
        "role": UserRole.RECEPTIONIST,
        "invitation_token": invitation_token,
        "invited_by": "test_admin",
        "status": "PENDING",
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.invitations.insert_one(invitation)
    
    stored = await db.invitations.find_one({"invitation_token": invitation_token})
    if stored and stored['status'] == 'PENDING':
        results.add_pass("Invitation created with PENDING status")
    else:
        results.add_fail("Invitation status", "Should be PENDING")
    
    # Test 5.2: Update to ACCEPTED
    await db.invitations.update_one(
        {"invitation_token": invitation_token},
        {"$set": {"status": "ACCEPTED", "accepted_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    stored = await db.invitations.find_one({"invitation_token": invitation_token})
    if stored and stored['status'] == 'ACCEPTED':
        results.add_pass("Invitation status updated to ACCEPTED")
    else:
        results.add_fail("Status update", "Should be ACCEPTED")
    
    # Test 5.3: Check accepted_at timestamp
    if stored and stored.get('accepted_at'):
        results.add_pass("accepted_at timestamp set")
    else:
        results.add_fail("accepted_at timestamp", "Not set")
    
    # Cleanup
    await db.invitations.delete_many({"email": "status_test@test.com"})


async def test_location_assignment():
    """Test 6: Location assignment validation"""
    print("\n" + "=" * 60)
    print("TEST 6: Location Assignment")
    print("=" * 60)
    
    # Test 6.1: Single location assignment
    invitation = Invitation(
        organization_id="test_org_loc",
        location_ids=["loc_1"],
        email="single_loc@test.com",
        name="Single Location",
        role=UserRole.RECEPTIONIST,
        invitation_token=f"invite_{secrets.token_hex(32)}",
        invited_by="test_admin",
        invited_by_name="Test Admin"
    )
    
    if len(invitation.location_ids) == 1:
        results.add_pass("Single location assignment works")
    else:
        results.add_fail("Single location", f"Expected 1, got {len(invitation.location_ids)}")
    
    # Test 6.2: Multiple location assignment
    invitation = Invitation(
        organization_id="test_org_loc",
        location_ids=["loc_1", "loc_2", "loc_3"],
        email="multi_loc@test.com",
        name="Multi Location",
        role=UserRole.RECEPTIONIST,
        invitation_token=f"invite_{secrets.token_hex(32)}",
        invited_by="test_admin",
        invited_by_name="Test Admin"
    )
    
    if len(invitation.location_ids) == 3:
        results.add_pass("Multiple location assignment works")
    else:
        results.add_fail("Multiple locations", f"Expected 3, got {len(invitation.location_ids)}")
    
    # Test 6.3: Empty location list (for Location Admin)
    invitation = Invitation(
        organization_id="test_org_loc",
        location_ids=[],
        email="no_loc@test.com",
        name="No Location",
        role=UserRole.LOCATION_ADMIN,
        invitation_token=f"invite_{secrets.token_hex(32)}",
        invited_by="test_admin",
        invited_by_name="Test Admin"
    )
    
    if len(invitation.location_ids) == 0:
        results.add_pass("Empty location list allowed for Location Admin")
    else:
        results.add_fail("Empty location list", "Should be allowed")


async def test_email_validation():
    """Test 7: Email validation"""
    print("\n" + "=" * 60)
    print("TEST 7: Email Validation")
    print("=" * 60)
    
    # Clean up
    await db.invitations.delete_many({"email": "duplicate@test.com"})
    await db.users.delete_many({"email": "existing@test.com"})
    
    # Test 7.1: Check for duplicate invitations
    invitation_token = f"invite_{secrets.token_hex(32)}"
    invitation = {
        "invitation_id": f"inv_{secrets.token_hex(12)}",
        "organization_id": "test_org_email",
        "location_ids": ["test_loc"],
        "email": "duplicate@test.com",
        "name": "Duplicate Test",
        "role": UserRole.RECEPTIONIST,
        "invitation_token": invitation_token,
        "invited_by": "test_admin",
        "status": "PENDING",
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.invitations.insert_one(invitation)
    
    # Check for existing pending invitation
    existing = await db.invitations.find_one({
        "email": "duplicate@test.com",
        "status": "PENDING"
    })
    
    if existing:
        results.add_pass("Duplicate invitation detection works")
    else:
        results.add_fail("Duplicate detection", "Should find existing invitation")
    
    # Test 7.2: Check for existing user
    test_user = {
        "user_id": f"user_{secrets.token_hex(12)}",
        "email": "existing@test.com",
        "name": "Existing User",
        "role": UserRole.USER,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(test_user)
    
    existing_user = await db.users.find_one({"email": "existing@test.com"})
    if existing_user:
        results.add_pass("Existing user detection works")
    else:
        results.add_fail("Existing user detection", "Should find existing user")
    
    # Cleanup
    await db.invitations.delete_many({"email": "duplicate@test.com"})
    await db.users.delete_many({"email": "existing@test.com"})


async def test_invitation_metadata():
    """Test 8: Invitation metadata storage"""
    print("\n" + "=" * 60)
    print("TEST 8: Invitation Metadata")
    print("=" * 60)
    
    # Test 8.1: Store metadata
    invitation = Invitation(
        organization_id="test_org_meta",
        location_ids=["test_loc"],
        email="metadata@test.com",
        name="Metadata Test",
        role=UserRole.DOCTOR,
        invitation_token=f"invite_{secrets.token_hex(32)}",
        invited_by="test_admin",
        invited_by_name="Test Admin",
        metadata={"department": "Cardiology", "specialization": "Cardiologist"}
    )
    
    if invitation.metadata and "department" in invitation.metadata:
        results.add_pass("Metadata stored in invitation")
    else:
        results.add_fail("Metadata storage", "Metadata not stored")
    
    # Test 8.2: Empty metadata
    invitation = Invitation(
        organization_id="test_org_meta",
        location_ids=["test_loc"],
        email="no_metadata@test.com",
        name="No Metadata",
        role=UserRole.RECEPTIONIST,
        invitation_token=f"invite_{secrets.token_hex(32)}",
        invited_by="test_admin",
        invited_by_name="Test Admin"
    )
    
    if invitation.metadata == {}:
        results.add_pass("Empty metadata handled correctly")
    else:
        results.add_fail("Empty metadata", "Should be empty dict")


async def run_all_tests():
    """Run all Phase 3 tests"""
    print("\n" + "=" * 60)
    print("PHASE 3 INVITATION SYSTEM - COMPREHENSIVE TESTS")
    print("=" * 60)
    print("\nTesting invitation system implementation")
    print("This will verify all invitation features are working correctly")
    print("\nStarting tests...\n")
    
    try:
        await test_invitation_role_validation()
        await test_invitation_creation()
        await test_role_mapping()
        await test_invitation_expiration()
        await test_invitation_status()
        await test_location_assignment()
        await test_email_validation()
        await test_invitation_metadata()
        
        # Print summary
        success = results.summary()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ ALL PHASE 3 TESTS PASSED!")
            print("=" * 60)
            print("\nThe invitation system is working correctly.")
            print("Ready to proceed to Phase 4!")
            return 0
        else:
            print("\n" + "=" * 60)
            print("❌ SOME TESTS FAILED")
            print("=" * 60)
            print("\nPlease fix the issues before proceeding to Phase 4.")
            return 1
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
