"""
Audit Logging Service
Logs critical security and business events for compliance and security monitoring
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging
from enum import Enum

from app.db import db

logger = logging.getLogger("mediconnect")


class AuditAction(str, Enum):
    """Audit action types."""
    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    
    # User Management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ROLE_CHANGED = "role_changed"
    
    # Data Access
    RECORD_VIEWED = "record_viewed"
    RECORD_CREATED = "record_created"
    RECORD_UPDATED = "record_updated"
    RECORD_DELETED = "record_deleted"
    
    # Appointments
    APPOINTMENT_CREATED = "appointment_created"
    APPOINTMENT_UPDATED = "appointment_updated"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    
    # Security Events
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # System Events
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    BACKUP_CREATED = "backup_created"
    DATA_EXPORT = "data_export"


class AuditLevel(str, Enum):
    """Audit log severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLogger:
    """
    Service for logging audit events.
    
    Logs are stored in MongoDB for:
    - Compliance (HIPAA, GDPR)
    - Security monitoring
    - Forensic analysis
    - User activity tracking
    """
    
    def __init__(self):
        self.collection = db.audit_logs
    
    async def log(
        self,
        action: AuditAction,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        level: AuditLevel = AuditLevel.INFO,
        success: bool = True
    ):
        """
        Log an audit event.
        
        Args:
            action: Type of action performed
            user_id: ID of user performing action
            user_email: Email of user
            resource_type: Type of resource affected (user, appointment, etc.)
            resource_id: ID of affected resource
            details: Additional details about the action
            ip_address: IP address of request
            user_agent: User agent string
            level: Severity level
            success: Whether action was successful
        """
        try:
            audit_entry = {
                "action": action.value,
                "user_id": user_id,
                "user_email": user_email,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details or {},
                "ip_address": ip_address,
                "user_agent": user_agent,
                "level": level.value,
                "success": success,
                "timestamp": datetime.now(timezone.utc)
            }
            
            # Store in database
            await self.collection.insert_one(audit_entry)
            
            # Also log to application logger for immediate visibility
            log_message = (
                f"AUDIT: {action.value} | "
                f"User: {user_email or user_id or 'anonymous'} | "
                f"Resource: {resource_type}:{resource_id} | "
                f"Success: {success}"
            )
            
            if level == AuditLevel.CRITICAL:
                logger.critical(log_message, extra=audit_entry)
            elif level == AuditLevel.ERROR:
                logger.error(log_message, extra=audit_entry)
            elif level == AuditLevel.WARNING:
                logger.warning(log_message, extra=audit_entry)
            else:
                logger.info(log_message, extra=audit_entry)
                
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    async def log_login_success(
        self,
        user_id: str,
        user_email: str,
        ip_address: str,
        user_agent: str
    ):
        """Log successful login."""
        await self.log(
            action=AuditAction.LOGIN_SUCCESS,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            level=AuditLevel.INFO
        )
    
    async def log_login_failed(
        self,
        email: str,
        ip_address: str,
        user_agent: str,
        reason: str
    ):
        """Log failed login attempt."""
        await self.log(
            action=AuditAction.LOGIN_FAILED,
            user_email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"reason": reason},
            level=AuditLevel.WARNING,
            success=False
        )
    
    async def log_unauthorized_access(
        self,
        user_id: Optional[str],
        user_email: Optional[str],
        resource_type: str,
        resource_id: str,
        ip_address: str,
        attempted_action: str
    ):
        """Log unauthorized access attempt."""
        await self.log(
            action=AuditAction.UNAUTHORIZED_ACCESS,
            user_id=user_id,
            user_email=user_email,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            details={"attempted_action": attempted_action},
            level=AuditLevel.WARNING,
            success=False
        )
    
    async def log_data_access(
        self,
        user_id: str,
        user_email: str,
        resource_type: str,
        resource_id: str,
        action: str,
        ip_address: str
    ):
        """Log data access for compliance."""
        audit_action = {
            "view": AuditAction.RECORD_VIEWED,
            "create": AuditAction.RECORD_CREATED,
            "update": AuditAction.RECORD_UPDATED,
            "delete": AuditAction.RECORD_DELETED,
        }.get(action, AuditAction.RECORD_VIEWED)
        
        await self.log(
            action=audit_action,
            user_id=user_id,
            user_email=user_email,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            level=AuditLevel.INFO
        )
    
    async def log_suspicious_activity(
        self,
        user_id: Optional[str],
        user_email: Optional[str],
        ip_address: str,
        activity_type: str,
        details: Dict[str, Any]
    ):
        """Log suspicious activity for security monitoring."""
        await self.log(
            action=AuditAction.SUSPICIOUS_ACTIVITY,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            details={
                "activity_type": activity_type,
                **details
            },
            level=AuditLevel.CRITICAL,
            success=False
        )
    
    async def get_user_activity(
        self,
        user_id: str,
        limit: int = 100
    ) -> list:
        """
        Get recent activity for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of entries
            
        Returns:
            List of audit log entries
        """
        try:
            cursor = self.collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Failed to retrieve user activity: {e}")
            return []
    
    async def get_failed_logins(
        self,
        email: Optional[str] = None,
        ip_address: Optional[str] = None,
        hours: int = 24
    ) -> int:
        """
        Count failed login attempts.
        
        Args:
            email: Email to check
            ip_address: IP address to check
            hours: Time window in hours
            
        Returns:
            Number of failed attempts
        """
        try:
            from datetime import timedelta
            
            since = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            query = {
                "action": AuditAction.LOGIN_FAILED.value,
                "timestamp": {"$gte": since}
            }
            
            if email:
                query["user_email"] = email
            if ip_address:
                query["ip_address"] = ip_address
            
            count = await self.collection.count_documents(query)
            return count
            
        except Exception as e:
            logger.error(f"Failed to count failed logins: {e}")
            return 0
    
    async def create_indexes(self):
        """Create indexes for efficient querying."""
        try:
            # Index on user_id and timestamp
            await self.collection.create_index([
                ("user_id", 1),
                ("timestamp", -1)
            ])
            
            # Index on action and timestamp
            await self.collection.create_index([
                ("action", 1),
                ("timestamp", -1)
            ])
            
            # Index on IP address for security monitoring
            await self.collection.create_index("ip_address")
            
            # Index on resource for compliance queries
            await self.collection.create_index([
                ("resource_type", 1),
                ("resource_id", 1)
            ])
            
            logger.info("✅ Audit log indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create audit log indexes: {e}")


# Global audit logger instance
audit_logger = AuditLogger()
