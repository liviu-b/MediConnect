import { usePermissions } from '../contexts/PermissionContext';
import { Lock } from 'lucide-react';

/**
 * PermissionButton Component
 * 
 * A button that automatically disables/hides based on user permissions.
 * 
 * Usage:
 * <PermissionButton 
 *   permission="appointments:accept"
 *   onClick={handleAccept}
 * >
 *   Accept Appointment
 * </PermissionButton>
 * 
 * Props:
 * - permission: Required permission to enable button
 * - role: Required role to enable button
 * - hideIfNoPermission: Hide button instead of disabling (default: false)
 * - showLockIcon: Show lock icon when disabled (default: true)
 * - tooltip: Custom tooltip text when disabled
 */
const PermissionButton = ({
  children,
  permission,
  role,
  hideIfNoPermission = false,
  showLockIcon = true,
  tooltip,
  onClick,
  className = '',
  disabled = false,
  ...props
}) => {
  const { hasPermission, hasRole } = usePermissions();

  // Check permission
  let hasAccess = true;
  let denialReason = '';

  if (permission && !hasPermission(permission)) {
    hasAccess = false;
    denialReason = tooltip || 'You do not have permission to perform this action';
  }

  if (role && !hasRole(role)) {
    hasAccess = false;
    denialReason = tooltip || 'This action is restricted to specific roles';
  }

  // Hide button if no permission and hideIfNoPermission is true
  if (!hasAccess && hideIfNoPermission) {
    return null;
  }

  // Determine if button should be disabled
  const isDisabled = disabled || !hasAccess;

  // Base button classes
  const baseClasses = className || 'px-4 py-2 rounded-lg font-medium transition-all';
  
  // Add disabled styling
  const disabledClasses = isDisabled 
    ? 'opacity-50 cursor-not-allowed' 
    : 'hover:shadow-md';

  const handleClick = (e) => {
    if (isDisabled) {
      e.preventDefault();
      return;
    }
    if (onClick) {
      onClick(e);
    }
  };

  return (
    <div className="relative inline-block group">
      <button
        onClick={handleClick}
        disabled={isDisabled}
        className={`${baseClasses} ${disabledClasses}`}
        {...props}
      >
        <span className="flex items-center gap-2">
          {!hasAccess && showLockIcon && (
            <Lock className="w-4 h-4" />
          )}
          {children}
        </span>
      </button>

      {/* Tooltip on hover when disabled */}
      {!hasAccess && denialReason && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
          {denialReason}
          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900"></div>
        </div>
      )}
    </div>
  );
};

/**
 * AcceptAppointmentButton
 * Pre-configured button for accepting appointments
 */
export const AcceptAppointmentButton = ({ onClick, ...props }) => {
  return (
    <PermissionButton
      permission="appointments:accept"
      tooltip="Only receptionists can accept appointments. Admins have view-only access."
      onClick={onClick}
      className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700"
      {...props}
    >
      Accept
    </PermissionButton>
  );
};

/**
 * RejectAppointmentButton
 * Pre-configured button for rejecting appointments
 */
export const RejectAppointmentButton = ({ onClick, ...props }) => {
  return (
    <PermissionButton
      permission="appointments:reject"
      tooltip="Only receptionists and doctors can reject appointments. Admins have view-only access."
      onClick={onClick}
      className="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700"
      {...props}
    >
      Reject
    </PermissionButton>
  );
};

/**
 * InviteUserButton
 * Pre-configured button for inviting users
 */
export const InviteUserButton = ({ onClick, ...props }) => {
  return (
    <PermissionButton
      permission="users:invite"
      tooltip="You do not have permission to invite users"
      onClick={onClick}
      className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
      {...props}
    >
      Invite User
    </PermissionButton>
  );
};

/**
 * ManageLocationsButton
 * Pre-configured button for managing locations
 */
export const ManageLocationsButton = ({ onClick, ...props }) => {
  return (
    <PermissionButton
      permission="locations:manage"
      role="SUPER_ADMIN"
      tooltip="Only Super Admins can manage locations"
      onClick={onClick}
      className="px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700"
      {...props}
    >
      Manage Locations
    </PermissionButton>
  );
};

export default PermissionButton;
