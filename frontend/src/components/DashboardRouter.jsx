import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';

/**
 * DashboardRouter Component
 * 
 * Handles automatic routing based on user role and login response.
 * This component is used after login to redirect users to the appropriate dashboard.
 * 
 * Routing Logic:
 * - SUPER_ADMIN (multi-location) → /dashboard (global)
 * - SUPER_ADMIN (single-location) → /location/{id}/dashboard
 * - LOCATION_ADMIN → /location/{id}/dashboard
 * - DOCTOR → /doctor-dashboard (dedicated doctor interface)
 * - RECEPTIONIST/ASSISTANT → /staff-dashboard
 * - USER (patient) → /patient-dashboard
 */
const DashboardRouter = ({ user }) => {
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      // No user, redirect to login
      navigate('/login', { replace: true });
      return;
    }

    // Use redirect_to from login response if available
    if (user.redirect_to) {
      navigate(user.redirect_to, { replace: true });
      return;
    }

    // Fallback routing based on role
    const role = user.role;

    if (role === 'SUPER_ADMIN') {
      // Check location count
      if (user.location_count > 1) {
        // Multi-location: Global dashboard
        navigate('/dashboard', { replace: true });
      } else if (user.primary_location_id) {
        // Single location: Direct to location dashboard
        navigate(`/location/${user.primary_location_id}/dashboard`, { replace: true });
      } else {
        // Fallback to global dashboard
        navigate('/dashboard', { replace: true });
      }
    } else if (role === 'LOCATION_ADMIN') {
      // Location admin goes to their assigned location
      if (user.primary_location_id) {
        navigate(`/location/${user.primary_location_id}/dashboard`, { replace: true });
      } else if (user.assigned_location_ids && user.assigned_location_ids.length > 0) {
        navigate(`/location/${user.assigned_location_ids[0]}/dashboard`, { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    } else if (role === 'DOCTOR') {
      // Doctors get their own dedicated dashboard
      navigate('/doctor-dashboard', { replace: true });
    } else if (['RECEPTIONIST', 'ASSISTANT'].includes(role)) {
      // Other staff goes to staff dashboard
      navigate('/staff-dashboard', { replace: true });
    } else if (role === 'CLINIC_ADMIN') {
      // Legacy support
      navigate('/dashboard', { replace: true });
    } else {
      // Regular user (patient)
      navigate('/patient-dashboard', { replace: true });
    }
  }, [user, navigate]);

  // Show loading state while redirecting
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-3" />
        <p className="text-gray-600">Redirecting to your dashboard...</p>
      </div>
    </div>
  );
};

export default DashboardRouter;
