"""
Permission Service - Centralized permission checking logic.

This service implements the core RBAC logic with the following critical rules:
1. SUPER_ADMIN and LOCATION_ADMIN have VIEW-ONLY access to appointments
2. Only RECEPTIONIST, DOCTOR, ASSISTANT can perform operational appointment actions
3. Location-scoped access control is enforced
4. All permission checks are logged for audit purposes
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, timezone

from ..db import db
from ..schemas.user import User, UserRole
from ..schemas.permission import (
    PermissionConstants,
    ROLE_PERMISSIONS_MATRIX,
    PermissionCheckResult
)
from ..schemas.audit_log import AuditLog, AuditActions


class PermissionService:
    """
    Centralized permission checking service.
    """
    
    @staticmethod
    async def check_permission(
        user: User,
        permission: str,
        resource_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> PermissionCheckResult:
        """
        Check if a user has a specific permission.
        
        Args:
            user: The user to check permissions for
            permission: The permission to check (e.g., "appointments:accept")
            resource_id: Optional resource ID (e.g., appointment_id, location_id)
            context: Additional context for the permission check
            
        Returns:
            PermissionCheckResult with allowed status and details
        """
        context = context or {}
        
        # Get role permissions
        role_permissions = ROLE_PERMISSIONS_MATRIX.get(user.role, {})
        
        # Check if role has this permission
        if permission not in role_permissions:
            return PermissionCheckResult(
                allowed=False,
                reason=f"Role {user.role} does not have permission {permission}",
                scope=None
            )
        
        permission_config = role_permissions[permission]
        
        # Check scope constraints
        scope = permission_config.get("scope", "location")
        
        # CRITICAL: Check view-only constraint for admins on appointments
        # But allow doctors to manage their own appointments
        if permission.startswith("appointments:") and permission != PermissionConstants.APPOINTMENTS_VIEW:
            if user.role in [UserRole.SUPER_ADMIN, UserRole.LOCATION_ADMIN]:
                # Admins cannot perform operational appointment actions
                await PermissionService._log_permission_denial(
                    user=user,
                    permission=permission,
                    resource_id=resource_id,
                    reason="Admin roles have view-only access to appointments"
                )
                return PermissionCheckResult(
                    allowed=False,
                    reason="Admin roles have view-only access to appointments. Only operational staff can perform this action.",
                    scope=scope,
                    constraints=permission_config
                )
        
        # Check location-scoped access
        if scope == "location":
            if not await PermissionService._check_location_access(user, context.get("location_id")):
                return PermissionCheckResult(
                    allowed=False,
                    reason="User does not have access to this location",
                    scope=scope
                )
        
        # Check organization-scoped access
        if scope == "organization":
            if not await PermissionService._check_organization_access(user, context.get("organization_id")):
                return PermissionCheckResult(
                    allowed=False,
                    reason="User does not have access to this organization",
                    scope=scope
                )
        
        # Check "own_appointments_only" constraint (for doctors)
        if permission_config.get("own_appointments_only"):
            if not await PermissionService._check_own_appointment(user, resource_id):
                return PermissionCheckResult(
                    allowed=False,
                    reason="You can only access your own appointments",
                    scope=scope,
                    constraints=permission_config
                )
        
        # Check "own_location_only" constraint
        if permission_config.get("own_location_only"):
            if not await PermissionService._check_own_location(user, resource_id):
                return PermissionCheckResult(
                    allowed=False,
                    reason="You can only access your assigned location",
                    scope=scope,
                    constraints=permission_config
                )
        
        # Permission granted
        return PermissionCheckResult(
            allowed=True,
            reason="Permission granted",
            scope=scope,
            constraints=permission_config
        )
    
    @staticmethod
    async def _check_location_access(user: User, location_id: Optional[str]) -> bool:
        """
        Check if user has access to a specific location.
        
        Rules:
        - SUPER_ADMIN: Access to all locations in their organization
        - Others: Access only to assigned_location_ids
        """
        if user.role == UserRole.SUPER_ADMIN:
            # Super admin has access to all locations in their organization
            if location_id and user.organization_id:
                location = await db.locations.find_one(
                    {"location_id": location_id, "organization_id": user.organization_id},
                    {"_id": 0}
                )
                return location is not None
            return True
        
        # For other roles, check assigned_location_ids
        if not user.assigned_location_ids:
            return False
        
        if location_id:
            return location_id in user.assigned_location_ids
        
        # If no specific location_id provided, allow if user has any assigned locations
        return len(user.assigned_location_ids) > 0
    
    @staticmethod
    async def _check_organization_access(user: User, organization_id: Optional[str]) -> bool:
        """
        Check if user has access to a specific organization.
        """
        if not organization_id:
            organization_id = user.organization_id
        
        return user.organization_id == organization_id
    
    @staticmethod
    async def _check_own_appointment(user: User, appointment_id: Optional[str]) -> bool:
        """
        Check if an appointment belongs to the user (for doctors).
        """
        if not appointment_id:
            return False
        
        appointment = await db.appointments.find_one(
            {"appointment_id": appointment_id},
            {"_id": 0}
        )
        
        if not appointment:
            return False
        
        # For doctors, check if they are the assigned doctor
        if user.role == UserRole.DOCTOR:
            # Find doctor record for this user
            doctor = await db.doctors.find_one(
                {"email": user.email.lower()},
                {"_id": 0}
            )
            if doctor:
                return appointment.get("doctor_id") == doctor.get("doctor_id")
        
        return False
    
    @staticmethod
    async def _check_own_location(user: User, location_id: Optional[str]) -> bool:
        """
        Check if a location is in the user's assigned locations.
        """
        if not location_id or not user.assigned_location_ids:
            return False
        
        return location_id in user.assigned_location_ids
    
    @staticmethod
    async def _log_permission_denial(
        user: User,
        permission: str,
        resource_id: Optional[str],
        reason: str
    ):
        """
        Log permission denial for audit purposes.
        """
        audit_log = AuditLog(
            user_id=user.user_id,
            user_email=user.email,
            user_role=user.role,
            action=AuditActions.PERMISSION_DENIED,
            resource_type="permission",
            resource_id=resource_id,
            organization_id=user.organization_id,
            description=f"Permission denied: {permission}",
            metadata={
                "permission": permission,
                "reason": reason
            },
            status="denied",
            severity="warning"
        )
        
        log_doc = audit_log.model_dump()
        log_doc['timestamp'] = log_doc['timestamp'].isoformat()
        await db.audit_logs.insert_one(log_doc)
    
    @staticmethod
    async def can_accept_appointments(user: User) -> bool:
        """
        Check if user can accept/reject appointments.
        
        CRITICAL RULE: Only RECEPTIONIST can accept/reject appointments.
        SUPER_ADMIN and LOCATION_ADMIN have VIEW-ONLY access.
        """
        result = await PermissionService.check_permission(
            user=user,
            permission=PermissionConstants.APPOINTMENTS_ACCEPT
        )
        return result.allowed
    
    @staticmethod
    async def can_modify_appointments(user: User, appointment_id: Optional[str] = None) -> bool:
        """
        Check if user can modify appointments.
        
        Rules:
        - RECEPTIONIST: Can modify any appointment in their location
        - DOCTOR: Can modify only their own appointments
        - SUPER_ADMIN/LOCATION_ADMIN: Cannot modify (view-only)
        """
        result = await PermissionService.check_permission(
            user=user,
            permission=PermissionConstants.APPOINTMENTS_UPDATE,
            resource_id=appointment_id
        )
        return result.allowed
    
    @staticmethod
    async def can_view_appointments(user: User, location_id: Optional[str] = None) -> bool:
        """
        Check if user can view appointments.
        
        All staff roles can view appointments, but with different scopes.
        """
        result = await PermissionService.check_permission(
            user=user,
            permission=PermissionConstants.APPOINTMENTS_VIEW,
            context={"location_id": location_id}
        )
        return result.allowed
    
    @staticmethod
    async def can_invite_users(user: User, target_role: str) -> bool:
        """
        Check if user can invite other users with a specific role.
        
        Rules:
        - SUPER_ADMIN: Can invite LOCATION_ADMIN, RECEPTIONIST, DOCTOR, ASSISTANT
        - LOCATION_ADMIN: Can invite RECEPTIONIST, DOCTOR, ASSISTANT (NOT other LOCATION_ADMINs)
        """
        if user.role == UserRole.SUPER_ADMIN:
            return target_role in [
                UserRole.LOCATION_ADMIN,
                UserRole.RECEPTIONIST,
                UserRole.DOCTOR,
                UserRole.ASSISTANT
            ]
        elif user.role == UserRole.LOCATION_ADMIN:
            return target_role in [
                UserRole.RECEPTIONIST,
                UserRole.DOCTOR,
                UserRole.ASSISTANT
            ]
        return False
    
    @staticmethod
    async def can_manage_locations(user: User) -> bool:
        """
        Check if user can manage locations (add/edit/delete).
        
        Only SUPER_ADMIN can manage locations.
        """
        result = await PermissionService.check_permission(
            user=user,
            permission=PermissionConstants.LOCATIONS_MANAGE
        )
        return result.allowed
    
    @staticmethod
    async def get_accessible_locations(user: User) -> List[str]:
        """
        Get list of location IDs the user has access to.
        
        Returns:
            List of location_ids
        """
        if user.role == UserRole.SUPER_ADMIN and user.organization_id:
            # Super admin has access to all locations in their organization
            locations = await db.locations.find(
                {"organization_id": user.organization_id, "is_active": True},
                {"_id": 0, "location_id": 1}
            ).to_list(100)
            return [loc["location_id"] for loc in locations]
        
        # For other roles, return assigned locations
        return user.assigned_location_ids or []
    
    @staticmethod
    async def log_action(
        user: User,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        status: str = "success",
        severity: str = "info"
    ):
        """
        Log a user action for audit purposes.
        """
        audit_log = AuditLog(
            user_id=user.user_id,
            user_email=user.email,
            user_role=user.role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            organization_id=user.organization_id,
            location_id=user.assigned_location_ids[0] if user.assigned_location_ids else None,
            description=description,
            metadata=metadata or {},
            status=status,
            severity=severity
        )
        
        log_doc = audit_log.model_dump()
        log_doc['timestamp'] = log_doc['timestamp'].isoformat()
        await db.audit_logs.insert_one(log_doc)


# Convenience instance
permission_service = PermissionService()
