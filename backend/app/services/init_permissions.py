"""
Initialize permissions in the database.

This script seeds the database with predefined permissions and role-permission mappings.
Run this once during initial setup or after permission schema changes.
"""

from datetime import datetime, timezone
from typing import List, Dict

from ..db import db
from ..schemas.permission import (
    Permission,
    RolePermission,
    PermissionConstants,
    ROLE_PERMISSIONS_MATRIX
)


async def init_permissions():
    """
    Initialize all permissions in the database.
    """
    print("Initializing permissions...")
    
    # Define all permissions
    permissions_to_create = [
        # Appointment permissions
        Permission(
            name=PermissionConstants.APPOINTMENTS_VIEW,
            resource="appointments",
            action="view",
            description="View appointments"
        ),
        Permission(
            name=PermissionConstants.APPOINTMENTS_CREATE,
            resource="appointments",
            action="create",
            description="Create new appointments"
        ),
        Permission(
            name=PermissionConstants.APPOINTMENTS_UPDATE,
            resource="appointments",
            action="update",
            description="Update existing appointments"
        ),
        Permission(
            name=PermissionConstants.APPOINTMENTS_DELETE,
            resource="appointments",
            action="delete",
            description="Delete appointments"
        ),
        Permission(
            name=PermissionConstants.APPOINTMENTS_ACCEPT,
            resource="appointments",
            action="accept",
            description="Accept pending appointments"
        ),
        Permission(
            name=PermissionConstants.APPOINTMENTS_REJECT,
            resource="appointments",
            action="reject",
            description="Reject appointments"
        ),
        Permission(
            name=PermissionConstants.APPOINTMENTS_CANCEL,
            resource="appointments",
            action="cancel",
            description="Cancel appointments"
        ),
        Permission(
            name=PermissionConstants.APPOINTMENTS_RESCHEDULE,
            resource="appointments",
            action="reschedule",
            description="Reschedule appointments"
        ),
        
        # User management permissions
        Permission(
            name=PermissionConstants.USERS_VIEW,
            resource="users",
            action="view",
            description="View users"
        ),
        Permission(
            name=PermissionConstants.USERS_CREATE,
            resource="users",
            action="create",
            description="Create new users"
        ),
        Permission(
            name=PermissionConstants.USERS_UPDATE,
            resource="users",
            action="update",
            description="Update user information"
        ),
        Permission(
            name=PermissionConstants.USERS_DELETE,
            resource="users",
            action="delete",
            description="Delete users"
        ),
        Permission(
            name=PermissionConstants.USERS_INVITE,
            resource="users",
            action="invite",
            description="Invite new users"
        ),
        Permission(
            name=PermissionConstants.USERS_MANAGE_ROLES,
            resource="users",
            action="manage_roles",
            description="Manage user roles and permissions"
        ),
        
        # Location permissions
        Permission(
            name=PermissionConstants.LOCATIONS_VIEW,
            resource="locations",
            action="view",
            description="View locations"
        ),
        Permission(
            name=PermissionConstants.LOCATIONS_CREATE,
            resource="locations",
            action="create",
            description="Create new locations"
        ),
        Permission(
            name=PermissionConstants.LOCATIONS_UPDATE,
            resource="locations",
            action="update",
            description="Update location information"
        ),
        Permission(
            name=PermissionConstants.LOCATIONS_DELETE,
            resource="locations",
            action="delete",
            description="Delete locations"
        ),
        Permission(
            name=PermissionConstants.LOCATIONS_MANAGE,
            resource="locations",
            action="manage",
            description="Full location management"
        ),
        
        # Organization permissions
        Permission(
            name=PermissionConstants.ORGANIZATION_VIEW,
            resource="organization",
            action="view",
            description="View organization details"
        ),
        Permission(
            name=PermissionConstants.ORGANIZATION_UPDATE,
            resource="organization",
            action="update",
            description="Update organization information"
        ),
        Permission(
            name=PermissionConstants.ORGANIZATION_SETTINGS,
            resource="organization",
            action="settings",
            description="Manage organization settings"
        ),
        Permission(
            name=PermissionConstants.ORGANIZATION_BILLING,
            resource="organization",
            action="billing",
            description="Manage billing and payments"
        ),
        
        # Staff permissions
        Permission(
            name=PermissionConstants.STAFF_VIEW,
            resource="staff",
            action="view",
            description="View staff members"
        ),
        Permission(
            name=PermissionConstants.STAFF_CREATE,
            resource="staff",
            action="create",
            description="Create staff members"
        ),
        Permission(
            name=PermissionConstants.STAFF_UPDATE,
            resource="staff",
            action="update",
            description="Update staff information"
        ),
        Permission(
            name=PermissionConstants.STAFF_DELETE,
            resource="staff",
            action="delete",
            description="Delete staff members"
        ),
        Permission(
            name=PermissionConstants.STAFF_INVITE,
            resource="staff",
            action="invite",
            description="Invite staff members"
        ),
        
        # Doctor permissions
        Permission(
            name=PermissionConstants.DOCTORS_VIEW,
            resource="doctors",
            action="view",
            description="View doctors"
        ),
        Permission(
            name=PermissionConstants.DOCTORS_CREATE,
            resource="doctors",
            action="create",
            description="Create doctor profiles"
        ),
        Permission(
            name=PermissionConstants.DOCTORS_UPDATE,
            resource="doctors",
            action="update",
            description="Update doctor information"
        ),
        Permission(
            name=PermissionConstants.DOCTORS_DELETE,
            resource="doctors",
            action="delete",
            description="Delete doctor profiles"
        ),
        
        # Medical records permissions
        Permission(
            name=PermissionConstants.RECORDS_VIEW,
            resource="records",
            action="view",
            description="View medical records"
        ),
        Permission(
            name=PermissionConstants.RECORDS_CREATE,
            resource="records",
            action="create",
            description="Create medical records"
        ),
        Permission(
            name=PermissionConstants.RECORDS_UPDATE,
            resource="records",
            action="update",
            description="Update medical records"
        ),
        Permission(
            name=PermissionConstants.RECORDS_DELETE,
            resource="records",
            action="delete",
            description="Delete medical records"
        ),
        
        # Service permissions
        Permission(
            name=PermissionConstants.SERVICES_VIEW,
            resource="services",
            action="view",
            description="View services"
        ),
        Permission(
            name=PermissionConstants.SERVICES_CREATE,
            resource="services",
            action="create",
            description="Create services"
        ),
        Permission(
            name=PermissionConstants.SERVICES_UPDATE,
            resource="services",
            action="update",
            description="Update services"
        ),
        Permission(
            name=PermissionConstants.SERVICES_DELETE,
            resource="services",
            action="delete",
            description="Delete services"
        ),
        
        # Settings permissions
        Permission(
            name=PermissionConstants.SETTINGS_VIEW,
            resource="settings",
            action="view",
            description="View settings"
        ),
        Permission(
            name=PermissionConstants.SETTINGS_UPDATE,
            resource="settings",
            action="update",
            description="Update settings"
        ),
        
        # Access request permissions
        Permission(
            name=PermissionConstants.ACCESS_REQUESTS_VIEW,
            resource="access_requests",
            action="view",
            description="View access requests"
        ),
        Permission(
            name=PermissionConstants.ACCESS_REQUESTS_APPROVE,
            resource="access_requests",
            action="approve",
            description="Approve access requests"
        ),
        Permission(
            name=PermissionConstants.ACCESS_REQUESTS_REJECT,
            resource="access_requests",
            action="reject",
            description="Reject access requests"
        ),
    ]
    
    # Insert permissions
    for perm in permissions_to_create:
        existing = await db.permissions.find_one({"name": perm.name})
        if not existing:
            perm_doc = perm.model_dump()
            perm_doc['created_at'] = perm_doc['created_at'].isoformat()
            await db.permissions.insert_one(perm_doc)
            print(f"  ✓ Created permission: {perm.name}")
        else:
            print(f"  - Permission already exists: {perm.name}")
    
    print(f"\nTotal permissions: {len(permissions_to_create)}")


async def init_role_permissions():
    """
    Initialize role-permission mappings in the database.
    """
    print("\nInitializing role-permission mappings...")
    
    role_permissions_to_create: List[RolePermission] = []
    
    # Convert ROLE_PERMISSIONS_MATRIX to RolePermission objects
    for role, permissions in ROLE_PERMISSIONS_MATRIX.items():
        for permission_name, config in permissions.items():
            role_perm = RolePermission(
                role=role,
                permission_name=permission_name,
                scope=config.get("scope", "location"),
                constraints=config
            )
            role_permissions_to_create.append(role_perm)
    
    # Clear existing role permissions
    await db.role_permissions.delete_many({})
    print("  - Cleared existing role permissions")
    
    # Insert new role permissions
    for role_perm in role_permissions_to_create:
        role_perm_doc = role_perm.model_dump()
        role_perm_doc['created_at'] = role_perm_doc['created_at'].isoformat()
        await db.role_permissions.insert_one(role_perm_doc)
    
    print(f"  ✓ Created {len(role_permissions_to_create)} role-permission mappings")
    
    # Print summary by role
    print("\nRole-Permission Summary:")
    for role in ROLE_PERMISSIONS_MATRIX.keys():
        count = len(ROLE_PERMISSIONS_MATRIX[role])
        print(f"  - {role}: {count} permissions")


async def create_indexes():
    """
    Create database indexes for performance.
    """
    print("\nCreating database indexes...")
    
    # Permissions indexes
    await db.permissions.create_index("name", unique=True)
    await db.permissions.create_index("resource")
    print("  ✓ Created permissions indexes")
    
    # Role permissions indexes
    await db.role_permissions.create_index([("role", 1), ("permission_name", 1)])
    await db.role_permissions.create_index("role")
    print("  ✓ Created role_permissions indexes")
    
    # User permission overrides indexes
    await db.user_permission_overrides.create_index([("user_id", 1), ("permission_name", 1)])
    await db.user_permission_overrides.create_index("user_id")
    print("  ✓ Created user_permission_overrides indexes")
    
    # Audit logs indexes
    await db.audit_logs.create_index([("user_id", 1), ("timestamp", -1)])
    await db.audit_logs.create_index([("action", 1), ("timestamp", -1)])
    await db.audit_logs.create_index([("organization_id", 1), ("timestamp", -1)])
    await db.audit_logs.create_index("timestamp")
    print("  ✓ Created audit_logs indexes")
    
    # Invitations indexes
    await db.invitations.create_index("invitation_token", unique=True)
    await db.invitations.create_index([("email", 1), ("status", 1)])
    await db.invitations.create_index([("organization_id", 1), ("status", 1)])
    print("  ✓ Created invitations indexes")
    
    # Users indexes (additional)
    await db.users.create_index([("organization_id", 1), ("role", 1)])
    await db.users.create_index("assigned_location_ids")
    print("  ✓ Created additional users indexes")


async def initialize_all():
    """
    Run all initialization tasks.
    """
    print("=" * 60)
    print("INITIALIZING MEDICONNECT PERMISSION SYSTEM")
    print("=" * 60)
    
    await init_permissions()
    await init_role_permissions()
    await create_indexes()
    
    print("\n" + "=" * 60)
    print("INITIALIZATION COMPLETE")
    print("=" * 60)
    print("\nThe permission system is now ready to use.")
    print("\nKey features:")
    print("  ✓ Role-based access control (RBAC)")
    print("  ✓ Location-scoped permissions")
    print("  ✓ View-only constraint for admins on appointments")
    print("  ✓ Audit logging for all actions")
    print("  ✓ Invitation system for staff onboarding")


if __name__ == "__main__":
    import asyncio
    asyncio.run(initialize_all())
