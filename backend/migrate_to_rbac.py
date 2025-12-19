"""
Migration script to update existing users with new RBAC fields.

This script:
1. Updates existing users with new permission fields
2. Assigns proper roles based on old role system
3. Sets assigned_location_ids for location-scoped users
4. Initializes cached_permissions
5. Migrates old clinic_id to organization_id where needed

Run this AFTER running init_permissions_db.py
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import db
from app.schemas.permission import ROLE_PERMISSIONS_MATRIX
from app.schemas.user import UserRole


async def migrate_user_roles():
    """
    Update user roles to new role system.
    
    Old roles -> New roles:
    - CLINIC_ADMIN -> SUPER_ADMIN (if they own the organization)
    - CLINIC_ADMIN -> LOCATION_ADMIN (if they manage a location)
    - DOCTOR -> DOCTOR
    - ASSISTANT -> ASSISTANT (or RECEPTIONIST based on context)
    - USER -> USER
    """
    print("Migrating user roles...")
    
    users = await db.users.find({}).to_list(1000)
    updated_count = 0
    
    for user in users:
        updates = {}
        
        # Map old roles to new roles
        old_role = user.get('role', 'USER')
        
        if old_role == 'CLINIC_ADMIN':
            # Check if they are the organization owner
            if user.get('organization_id'):
                org = await db.organizations.find_one({
                    "organization_id": user['organization_id']
                })
                if org and user['user_id'] in org.get('super_admin_ids', []):
                    updates['role'] = UserRole.SUPER_ADMIN
                else:
                    updates['role'] = UserRole.LOCATION_ADMIN
            else:
                # Default to LOCATION_ADMIN if no organization
                updates['role'] = UserRole.LOCATION_ADMIN
        
        elif old_role == 'DOCTOR':
            updates['role'] = UserRole.DOCTOR
        
        elif old_role == 'ASSISTANT':
            # Keep as ASSISTANT (can be manually changed to RECEPTIONIST later)
            updates['role'] = UserRole.ASSISTANT
        
        elif old_role == 'USER':
            updates['role'] = UserRole.USER
        
        else:
            # Unknown role, default to USER
            updates['role'] = UserRole.USER
        
        # Initialize new fields if they don't exist
        if 'cached_permissions' not in user:
            # Set cached permissions based on role
            role = updates.get('role', old_role)
            if role in ROLE_PERMISSIONS_MATRIX:
                updates['cached_permissions'] = list(ROLE_PERMISSIONS_MATRIX[role].keys())
                updates['permissions_updated_at'] = datetime.now(timezone.utc).isoformat()
        
        if 'metadata' not in user:
            updates['metadata'] = {}
        
        if 'is_email_verified' not in user:
            updates['is_email_verified'] = False
        
        if 'updated_at' not in user:
            updates['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Handle assigned_location_ids
        if 'assigned_location_ids' not in user:
            role = updates.get('role', old_role)
            
            if role == UserRole.SUPER_ADMIN:
                # Super admins have access to all locations (None)
                updates['assigned_location_ids'] = None
            
            elif role in [UserRole.LOCATION_ADMIN, UserRole.RECEPTIONIST, UserRole.DOCTOR, UserRole.ASSISTANT]:
                # For staff, try to get locations from organization
                if user.get('organization_id'):
                    locations = await db.locations.find({
                        "organization_id": user['organization_id'],
                        "is_active": True
                    }).to_list(100)
                    
                    if locations:
                        # Assign to all locations (can be refined later)
                        updates['assigned_location_ids'] = [loc['location_id'] for loc in locations]
                    else:
                        updates['assigned_location_ids'] = []
                else:
                    updates['assigned_location_ids'] = []
            
            else:
                # Regular users don't need location assignments
                updates['assigned_location_ids'] = None
        
        # Apply updates
        if updates:
            await db.users.update_one(
                {"user_id": user['user_id']},
                {"$set": updates}
            )
            updated_count += 1
            print(f"  ✓ Updated user: {user['email']} -> {updates.get('role', old_role)}")
    
    print(f"\nUpdated {updated_count} users")


async def migrate_clinic_to_organization():
    """
    Migrate users with clinic_id to organization_id.
    """
    print("\nMigrating clinic_id to organization_id...")
    
    # Find users with clinic_id but no organization_id
    users = await db.users.find({
        "clinic_id": {"$exists": True, "$ne": None},
        "organization_id": {"$exists": False}
    }).to_list(1000)
    
    migrated_count = 0
    
    for user in users:
        clinic_id = user.get('clinic_id')
        
        # Try to find organization for this clinic
        # First check if clinic exists in old clinics collection
        clinic = await db.clinics.find_one({"clinic_id": clinic_id})
        
        if clinic:
            # Check if organization exists for this CUI
            cui = clinic.get('cui')
            if cui:
                org = await db.organizations.find_one({"cui": cui})
                
                if org:
                    # Update user with organization_id
                    await db.users.update_one(
                        {"user_id": user['user_id']},
                        {"$set": {"organization_id": org['organization_id']}}
                    )
                    migrated_count += 1
                    print(f"  ✓ Migrated user {user['email']} to organization {org['organization_id']}")
    
    print(f"\nMigrated {migrated_count} users from clinic_id to organization_id")


async def verify_migration():
    """
    Verify that migration was successful.
    """
    print("\nVerifying migration...")
    
    # Check users without roles
    users_without_role = await db.users.count_documents({
        "$or": [
            {"role": {"$exists": False}},
            {"role": None}
        ]
    })
    print(f"  - Users without role: {users_without_role}")
    
    # Check users without cached_permissions
    users_without_perms = await db.users.count_documents({
        "$or": [
            {"cached_permissions": {"$exists": False}},
            {"cached_permissions": None}
        ]
    })
    print(f"  - Users without cached_permissions: {users_without_perms}")
    
    # Check staff without assigned_location_ids
    staff_without_locations = await db.users.count_documents({
        "role": {"$in": [UserRole.LOCATION_ADMIN, UserRole.RECEPTIONIST, UserRole.DOCTOR, UserRole.ASSISTANT]},
        "$or": [
            {"assigned_location_ids": {"$exists": False}},
            {"assigned_location_ids": None},
            {"assigned_location_ids": []}
        ]
    })
    print(f"  - Staff without assigned locations: {staff_without_locations}")
    
    # Count users by role
    print("\nUsers by role:")
    for role in UserRole.ALL_ROLES:
        count = await db.users.count_documents({"role": role})
        print(f"  - {role}: {count}")
    
    # Check super admins
    super_admins = await db.users.find({"role": UserRole.SUPER_ADMIN}).to_list(100)
    print(f"\nSuper Admins: {len(super_admins)}")
    for admin in super_admins:
        print(f"  - {admin['email']} (org: {admin.get('organization_id', 'N/A')})")


async def create_sample_receptionist():
    """
    Create a sample receptionist for testing (optional).
    """
    print("\nCreating sample receptionist...")
    
    # Find first organization
    org = await db.organizations.find_one({})
    if not org:
        print("  ⚠ No organization found. Skipping sample receptionist creation.")
        return
    
    # Find first location in organization
    location = await db.locations.find_one({"organization_id": org['organization_id']})
    if not location:
        print("  ⚠ No location found. Skipping sample receptionist creation.")
        return
    
    # Check if receptionist already exists
    existing = await db.users.find_one({
        "email": "receptionist@test.com"
    })
    
    if existing:
        print("  - Sample receptionist already exists")
        return
    
    # Create receptionist
    from app.schemas.user import User
    from app.security import hash_password
    import uuid
    
    receptionist = User(
        user_id=f"user_{uuid.uuid4().hex[:12]}",
        email="receptionist@test.com",
        name="Test Receptionist",
        password_hash=hash_password("password123"),
        role=UserRole.RECEPTIONIST,
        organization_id=org['organization_id'],
        assigned_location_ids=[location['location_id']],
        cached_permissions=list(ROLE_PERMISSIONS_MATRIX[UserRole.RECEPTIONIST].keys()),
        permissions_updated_at=datetime.now(timezone.utc),
        is_active=True,
        is_email_verified=True
    )
    
    user_doc = receptionist.model_dump()
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    user_doc['permissions_updated_at'] = user_doc['permissions_updated_at'].isoformat()
    
    await db.users.insert_one(user_doc)
    print(f"  ✓ Created sample receptionist: receptionist@test.com / password123")
    print(f"    Organization: {org.get('name', org['organization_id'])}")
    print(f"    Location: {location.get('name', location['location_id'])}")


async def main():
    """
    Run all migration tasks.
    """
    print("=" * 60)
    print("MIGRATING TO RBAC SYSTEM")
    print("=" * 60)
    
    try:
        await migrate_user_roles()
        await migrate_clinic_to_organization()
        await verify_migration()
        
        # Optional: Create sample receptionist for testing
        create_sample = input("\nCreate sample receptionist for testing? (y/n): ")
        if create_sample.lower() == 'y':
            await create_sample_receptionist()
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        print("\n✅ All users have been migrated to the new RBAC system.")
        print("\nNext steps:")
        print("1. Review user roles in the database")
        print("2. Manually adjust assigned_location_ids if needed")
        print("3. Test permission checks with different roles")
        print("4. Proceed to Phase 2 (Route Integration)")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
