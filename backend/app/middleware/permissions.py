"""
Permission Middleware and Decorators

This module provides decorators and middleware for enforcing permissions
on FastAPI routes with the critical business rules:
1. SUPER_ADMIN and LOCATION_ADMIN have VIEW-ONLY access to appointments
2. Only operational staff can accept/reject/modify appointments
3. Location-scoped access is enforced
"""

from functools import wraps
from typing import List, Optional, Callable
from fastapi import HTTPException, Request

from ..schemas.user import User, UserRole
from ..schemas.permission import PermissionConstants
from ..schemas.audit_log import AuditActions
from ..services.permissions import PermissionService
from ..security import require_auth


def require_permission(permission: str, resource_id_param: Optional[str] = None):
    """
    Decorator to require a specific permission for a route.
    
    Args:
        permission: Permission name (e.g., "appointments:accept")
        resource_id_param: Name of the parameter containing the resource ID
        
    Usage:
        @router.post("/appointments/{appointment_id}/accept")
        @require_permission("appointments:accept", resource_id_param="appointment_id")
        async def accept_appointment(appointment_id: str, request: Request):
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs
            request = kwargs.get('request')
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            # Get current user
            user = await require_auth(request)
            
            # Get resource ID if specified
            resource_id = kwargs.get(resource_id_param) if resource_id_param else None
            
            # Get location_id from query params or body if available
            location_id = None
            if hasattr(request, 'query_params'):
                location_id = request.query_params.get('location_id')
            
            # Check permission
            result = await PermissionService.check_permission(
                user=user,
                permission=permission,
                resource_id=resource_id,
                context={"location_id": location_id}
            )
            
            if not result.allowed:
                # Log the denial
                await PermissionService.log_action(
                    user=user,
                    action=AuditActions.PERMISSION_DENIED,
                    resource_type=permission.split(':')[0],
                    resource_id=resource_id,
                    description=f"Permission denied: {permission}",
                    metadata={"permission": permission, "reason": result.reason},
                    status="denied",
                    severity="warning"
                )
                
                raise HTTPException(status_code=403, detail=result.reason)
            
            # Permission granted, execute the function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(*allowed_roles: str):
    """
    Decorator to require specific roles for a route.
    
    Args:
        allowed_roles: One or more role names
        
    Usage:
        @router.post("/locations")
        @require_role(UserRole.SUPER_ADMIN)
        async def create_location(request: Request):
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            user = await require_auth(request)
            
            if user.role not in allowed_roles:
                await PermissionService.log_action(
                    user=user,
                    action=AuditActions.PERMISSION_DENIED,
                    resource_type="role_check",
                    description=f"Role check failed. Required: {allowed_roles}, Has: {user.role}",
                    status="denied",
                    severity="warning"
                )
                
                raise HTTPException(
                    status_code=403,
                    detail=f"This action requires one of these roles: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_location_access(location_id_param: str = "location_id"):
    """
    Decorator to ensure user has access to a specific location.
    
    Args:
        location_id_param: Name of the parameter containing the location ID
        
    Usage:
        @router.get("/locations/{location_id}/appointments")
        @require_location_access(location_id_param="location_id")
        async def get_location_appointments(location_id: str, request: Request):
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            user = await require_auth(request)
            
            # Get location_id from kwargs
            location_id = kwargs.get(location_id_param)
            if not location_id:
                raise HTTPException(status_code=400, detail="Location ID is required")
            
            # Check location access
            accessible_locations = await PermissionService.get_accessible_locations(user)
            
            if location_id not in accessible_locations:
                await PermissionService.log_action(
                    user=user,
                    action=AuditActions.PERMISSION_DENIED,
                    resource_type="location",
                    resource_id=location_id,
                    description=f"Location access denied: {location_id}",
                    status="denied",
                    severity="warning"
                )
                
                raise HTTPException(
                    status_code=403,
                    detail="You do not have access to this location"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def block_admin_appointment_modification():
    """
    Decorator to explicitly block admin roles from modifying appointments.
    This is a safety check in addition to permission checks.
    
    Usage:
        @router.post("/appointments/{appointment_id}/accept")
        @block_admin_appointment_modification()
        async def accept_appointment(appointment_id: str, request: Request):
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            user = await require_auth(request)
            
            # CRITICAL: Block admin roles from appointment modifications
            if user.role in [UserRole.SUPER_ADMIN, UserRole.LOCATION_ADMIN]:
                await PermissionService.log_action(
                    user=user,
                    action=AuditActions.APPOINTMENT_MODIFY_DENIED,
                    resource_type="appointment",
                    resource_id=kwargs.get('appointment_id'),
                    description="Admin attempted to modify appointment (blocked by decorator)",
                    metadata={"attempted_action": func.__name__},
                    status="denied",
                    severity="warning"
                )
                
                raise HTTPException(
                    status_code=403,
                    detail="Admin roles have view-only access to appointments. Only operational staff (Receptionist, Doctor) can perform this action."
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


async def check_appointment_access(user: User, appointment_id: str) -> bool:
    """
    Check if user has access to a specific appointment.
    
    Rules:
    - SUPER_ADMIN: Can view all appointments in organization
    - LOCATION_ADMIN: Can view appointments in assigned locations
    - RECEPTIONIST: Can view/modify appointments in assigned locations
    - DOCTOR: Can view/modify only own appointments
    - ASSISTANT: Can view appointments in assigned locations
    - USER: Can view only own appointments
    """
    from ..db import db
    
    appointment = await db.appointments.find_one(
        {"appointment_id": appointment_id},
        {"_id": 0}
    )
    
    if not appointment:
        return False
    
    # Check based on role
    if user.role == UserRole.USER:
        # Patients can only access their own appointments
        return appointment.get("patient_id") == user.user_id
    
    elif user.role == UserRole.DOCTOR:
        # Doctors can only access their own appointments
        doctor = await db.doctors.find_one(
            {"email": user.email.lower()},
            {"_id": 0}
        )
        if doctor:
            return appointment.get("doctor_id") == doctor.get("doctor_id")
        return False
    
    elif user.role in [UserRole.SUPER_ADMIN, UserRole.LOCATION_ADMIN, UserRole.RECEPTIONIST, UserRole.ASSISTANT]:
        # Staff can access appointments in their locations
        appointment_location = appointment.get("location_id")
        if not appointment_location:
            # Legacy: check clinic_id
            appointment_location = appointment.get("clinic_id")
        
        accessible_locations = await PermissionService.get_accessible_locations(user)
        return appointment_location in accessible_locations
    
    return False


async def check_location_access(user: User, location_id: str) -> bool:
    """
    Check if user has access to a specific location.
    """
    accessible_locations = await PermissionService.get_accessible_locations(user)
    return location_id in accessible_locations


async def check_organization_access(user: User, organization_id: str) -> bool:
    """
    Check if user has access to a specific organization.
    """
    return user.organization_id == organization_id


async def get_user_permissions(user_id: str) -> List[str]:
    """
    Get all permissions for a user.
    Returns cached permissions if available, otherwise computes them.
    """
    from ..db import db
    from ..schemas.permission import ROLE_PERMISSIONS_MATRIX
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        return []
    
    # Check if cached permissions are available and recent
    if user.get('cached_permissions'):
        return user['cached_permissions']
    
    # Compute permissions from role
    role = user.get('role', UserRole.USER)
    if role in ROLE_PERMISSIONS_MATRIX:
        permissions = list(ROLE_PERMISSIONS_MATRIX[role].keys())
        
        # Update cache
        from datetime import datetime, timezone
        await db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "cached_permissions": permissions,
                    "permissions_updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return permissions
    
    return []


async def refresh_user_permissions(user_id: str) -> List[str]:
    """
    Force refresh of user permissions cache.
    """
    from ..db import db
    from ..schemas.permission import ROLE_PERMISSIONS_MATRIX
    from datetime import datetime, timezone
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        return []
    
    role = user.get('role', UserRole.USER)
    permissions = []
    
    if role in ROLE_PERMISSIONS_MATRIX:
        permissions = list(ROLE_PERMISSIONS_MATRIX[role].keys())
    
    # Update cache
    await db.users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "cached_permissions": permissions,
                "permissions_updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return permissions
