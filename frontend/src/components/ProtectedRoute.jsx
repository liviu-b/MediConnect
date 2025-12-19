import { Navigate } from 'react-router-dom';
import { usePermissions } from '../contexts/PermissionContext';
import { AlertCircle } from 'lucide-react';

/**
 * ProtectedRoute Component
 * 
 * Wraps routes that require specific permissions or roles.
 * Redirects unauthorized users to appropriate pages.
 * 
 * Usage:
 * <ProtectedRoute requiredRole="SUPER_ADMIN">
 *   <AdminPanel />
 * </ProtectedRoute>
 * 
 * <ProtectedRoute requiredPermission="appointments:accept">
 *   <AcceptAppointmentButton />
 * </ProtectedRoute>
 */
const ProtectedRoute = ({ 
  children, 
  requiredRole, 
  requiredPermission,
  requiredAnyPermission,
  fallback = null,
  redirectTo = '/dashboard'
}) => {
  const { user, hasRole, hasPermission, hasAnyPermission, loading } = usePermissions();

  // Wait for permissions to load
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
          <p className="text-sm text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }

  // Check if user is authenticated
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Check role requirement
  if (requiredRole) {
    if (!hasRole(requiredRole)) {
      if (fallback) {
        return fallback;
      }
      return <Navigate to={redirectTo} replace />;
    }
  }

  // Check single permission requirement
  if (requiredPermission) {
    if (!hasPermission(requiredPermission)) {
      if (fallback) {
        return fallback;
      }
      return (
        <div className="flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Access Denied
            </h3>
            <p className="text-gray-600">
              You don't have permission to access this feature.
            </p>
          </div>
        </div>
      );
    }
  }

  // Check any permission requirement (user needs at least one)
  if (requiredAnyPermission && requiredAnyPermission.length > 0) {
    if (!hasAnyPermission(requiredAnyPermission)) {
      if (fallback) {
        return fallback;
      }
      return (
        <div className="flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Access Denied
            </h3>
            <p className="text-gray-600">
              You don't have permission to access this feature.
            </p>
          </div>
        </div>
      );
    }
  }

  // All checks passed, render children
  return children;
};

/**
 * AdminOnly Component
 * Shorthand for protecting admin-only routes
 */
export const AdminOnly = ({ children, fallback, redirectTo }) => {
  return (
    <ProtectedRoute 
      requiredRole={['SUPER_ADMIN', 'LOCATION_ADMIN', 'CLINIC_ADMIN']}
      fallback={fallback}
      redirectTo={redirectTo}
    >
      {children}
    </ProtectedRoute>
  );
};

/**
 * SuperAdminOnly Component
 * Shorthand for protecting super admin-only routes
 */
export const SuperAdminOnly = ({ children, fallback, redirectTo }) => {
  return (
    <ProtectedRoute 
      requiredRole="SUPER_ADMIN"
      fallback={fallback}
      redirectTo={redirectTo}
    >
      {children}
    </ProtectedRoute>
  );
};

/**
 * StaffOnly Component
 * Shorthand for protecting staff-only routes
 */
export const StaffOnly = ({ children, fallback, redirectTo }) => {
  return (
    <ProtectedRoute 
      requiredRole={['RECEPTIONIST', 'DOCTOR', 'ASSISTANT', 'SUPER_ADMIN', 'LOCATION_ADMIN', 'CLINIC_ADMIN']}
      fallback={fallback}
      redirectTo={redirectTo}
    >
      {children}
    </ProtectedRoute>
  );
};

export default ProtectedRoute;
