import { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../App';

/**
 * Permission Context
 * 
 * Provides permission checking functionality across the application.
 * Manages user permissions and role-based access control.
 */
const PermissionContext = createContext();

export const usePermissions = () => {
  const context = useContext(PermissionContext);
  if (!context) {
    throw new Error('usePermissions must be used within PermissionProvider');
  }
  return context;
};

export const PermissionProvider = ({ children, user }) => {
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadPermissions();
    } else {
      setPermissions([]);
      setLoading(false);
    }
  }, [user]);

  const loadPermissions = async () => {
    try {
      // Use cached permissions from user object if available
      if (user.cached_permissions && user.cached_permissions.length > 0) {
        setPermissions(user.cached_permissions);
      } else {
        // Fallback: fetch from API
        const res = await api.get('/users/me/permissions');
        setPermissions(res.data.permissions || []);
      }
    } catch (err) {
      console.error('Failed to load permissions:', err);
      // Use role-based fallback
      setPermissions(getRolePermissions(user.role));
    } finally {
      setLoading(false);
    }
  };

  /**
   * Check if user has a specific permission
   */
  const hasPermission = (permission) => {
    if (!user) return false;
    
    // Super admin has all permissions except appointment modifications
    if (user.role === 'SUPER_ADMIN') {
      // Block appointment operational actions
      if (['appointments:accept', 'appointments:reject', 'appointments:update'].includes(permission)) {
        return false;
      }
      return true;
    }

    // Location admin has view-only on appointments
    if (user.role === 'LOCATION_ADMIN') {
      if (['appointments:accept', 'appointments:reject', 'appointments:update'].includes(permission)) {
        return false;
      }
    }

    return permissions.includes(permission);
  };

  /**
   * Check if user has any of the specified permissions
   */
  const hasAnyPermission = (permissionList) => {
    return permissionList.some(permission => hasPermission(permission));
  };

  /**
   * Check if user has all of the specified permissions
   */
  const hasAllPermissions = (permissionList) => {
    return permissionList.every(permission => hasPermission(permission));
  };

  /**
   * Check if user has a specific role
   */
  const hasRole = (role) => {
    if (!user) return false;
    if (Array.isArray(role)) {
      return role.includes(user.role);
    }
    return user.role === role;
  };

  /**
   * Check if user is an admin (SUPER_ADMIN or LOCATION_ADMIN)
   */
  const isAdmin = () => {
    return hasRole(['SUPER_ADMIN', 'LOCATION_ADMIN', 'CLINIC_ADMIN']);
  };

  /**
   * Check if user is operational staff (can modify appointments)
   */
  const isOperationalStaff = () => {
    return hasRole(['RECEPTIONIST', 'DOCTOR', 'ASSISTANT']);
  };

  /**
   * Check if user can accept appointments
   */
  const canAcceptAppointments = () => {
    return hasPermission('appointments:accept');
  };

  /**
   * Check if user can modify appointments
   */
  const canModifyAppointments = () => {
    return hasPermission('appointments:update');
  };

  /**
   * Check if user can invite other users
   */
  const canInviteUsers = () => {
    return hasPermission('users:invite');
  };

  /**
   * Check if user can manage locations
   */
  const canManageLocations = () => {
    return hasPermission('locations:manage');
  };

  const value = {
    permissions,
    loading,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    isAdmin,
    isOperationalStaff,
    canAcceptAppointments,
    canModifyAppointments,
    canInviteUsers,
    canManageLocations,
    user
  };

  return (
    <PermissionContext.Provider value={value}>
      {children}
    </PermissionContext.Provider>
  );
};

/**
 * Get default permissions based on role (fallback)
 */
function getRolePermissions(role) {
  const rolePermissions = {
    'SUPER_ADMIN': [
      'appointments:view',
      'users:view',
      'users:invite',
      'locations:view',
      'locations:create',
      'locations:manage',
      'organization:view',
      'organization:update',
      'settings:view',
      'settings:update'
    ],
    'LOCATION_ADMIN': [
      'appointments:view',
      'users:view',
      'users:invite',
      'locations:view',
      'staff:view',
      'staff:create',
      'staff:invite',
      'settings:view'
    ],
    'RECEPTIONIST': [
      'appointments:view',
      'appointments:create',
      'appointments:update',
      'appointments:accept',
      'appointments:reject',
      'appointments:cancel',
      'users:view',
      'doctors:view',
      'services:view'
    ],
    'DOCTOR': [
      'appointments:view',
      'appointments:update',
      'appointments:accept',
      'appointments:reject',
      'records:view',
      'records:create',
      'records:update',
      'services:view'
    ],
    'ASSISTANT': [
      'appointments:view',
      'appointments:update',
      'records:view',
      'doctors:view',
      'services:view'
    ],
    'USER': [
      'appointments:view',
      'appointments:create',
      'appointments:cancel',
      'records:view',
      'doctors:view',
      'services:view'
    ]
  };

  return rolePermissions[role] || [];
}

export default PermissionContext;
