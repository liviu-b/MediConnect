import { useState, useEffect, useRef, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation, Link } from "react-router-dom";
import axios from "axios";
import { useTranslation } from "react-i18next";
import "./i18n";
import LanguageSwitcher from "./components/LanguageSwitcher";
import LocationSwitcher from "./components/LocationSwitcher";
import {
  Home,
  Calendar,
  ClipboardList,
  Building2,
  Stethoscope,
  UserCog,
  Briefcase,
  Settings,
  LogOut,
  Menu,
  X,
  UserPlus,
  MapPin
} from "lucide-react";
import { ChevronDown } from 'lucide-react';

// Configure axios defaults
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

axios.defaults.withCredentials = true;

// In-memory/session storage for bearer fallback
const TOKEN_STORAGE_KEY = 'session_token';

// Attach Authorization header and Location context if available
axios.interceptors.request.use((config) => {
  try {
    const token = sessionStorage.getItem(TOKEN_STORAGE_KEY) || localStorage.getItem(TOKEN_STORAGE_KEY);
    if (token && !config.headers?.Authorization) {
      config.headers = { ...(config.headers || {}), Authorization: `Bearer ${token}` };
    }
    
    // Add active location context to API calls
    const activeLocationId = localStorage.getItem('active_location_id');
    if (activeLocationId && !config.headers?.['X-Location-ID']) {
      config.headers = { ...(config.headers || {}), 'X-Location-ID': activeLocationId };
    }
  } catch (_) {}
  config.withCredentials = true;
  return config;
});

// Extract and store session_token from auth responses
axios.interceptors.response.use((response) => {
  try {
    const data = response?.data;
    if (data && typeof data === 'object' && data.session_token) {
      sessionStorage.setItem(TOKEN_STORAGE_KEY, data.session_token);
    }
  } catch (_) {}
  return response;
});

// API helper
const api = {
  get: (url, config = {}) => axios.get(`${API}${url}`, { ...config, withCredentials: true }),
  post: (url, data, config = {}) => axios.post(`${API}${url}`, data, { ...config, withCredentials: true }),
  put: (url, data, config = {}) => axios.put(`${API}${url}`, data, { ...config, withCredentials: true }),
  delete: (url, config = {}) => axios.delete(`${API}${url}`, { ...config, withCredentials: true })
};

// Auth Context
const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

// Landing Page Component
const LandingPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50 page-fade">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3">
          <div className="flex justify-between items-center">
            <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <div className="w-9 h-9 bg-gradient-to-br from-blue-600 to-teal-500 rounded-lg flex items-center justify-center">
                <Building2 className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-teal-500 bg-clip-text text-transparent">
                MediConnect
              </span>
            </Link>
            <div className="flex items-center gap-3">
              <LanguageSwitcher />
              <button
                onClick={() => navigate('/login')}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all text-sm"
              >
                {t('common.signIn')}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
            {t('landing.title')}
            <span className="block bg-gradient-to-r from-blue-600 to-teal-500 bg-clip-text text-transparent pb-2 leading-normal">
              {t('landing.subtitle')}
            </span>
          </h1>
          <p className="text-lg text-gray-600 mb-8 max-w-xl mx-auto">
            {t('landing.description')}
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => navigate('/register')}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-semibold hover:shadow-xl transition-all"
            >
              {t('common.getStarted')}
            </button>
            <button
              onClick={() => navigate('/register-clinic')}
              className="px-6 py-3 border-2 border-teal-500 text-teal-600 rounded-lg font-semibold hover:bg-teal-50 transition-all"
            >
              {t('auth.registerAsClinic')}
            </button>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">{t('landing.whyChoose')}</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { icon: Calendar, titleKey: 'easyScheduling' },
            { icon: ClipboardList, titleKey: 'noDoubleBooking' },
            { icon: Building2, titleKey: 'multiClinic' }
          ].map((feature, i) => (
            <div key={i} className="bg-white p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-teal-100 rounded-lg flex items-center justify-center text-blue-600 mb-4">
                <feature.icon className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {t(`landing.features.${feature.titleKey}.title`)}
              </h3>
              <p className="text-gray-600 text-sm">
                {t(`landing.features.${feature.titleKey}.desc`)}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-8">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-3">
            <Building2 className="w-6 h-6 text-white" />
            <span className="text-lg font-bold text-white">MediConnect</span>
          </div>
          <p className="text-sm">© 2025 MediConnect. {t('landing.footer')}</p>
          <p className="text-sm mt-1">(Powered by ACL-Smart Software)</p>
        </div>
      </footer>
    </div>
  );
};

// Auth Callback Component
const AuthCallback = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const processedRef = useRef(false);

  useEffect(() => {
    if (processedRef.current) return;
    processedRef.current = true;

    const processAuth = async () => {
      const hash = location.hash;
      const sessionIdMatch = hash.match(/session_id=([^&]+)/);

      if (sessionIdMatch) {
        const sessionId = sessionIdMatch[1];
        try {
          const response = await api.post('/auth/session', {}, {
            headers: { 'X-Session-ID': sessionId }
          });
          // Persist token from response just in case cookie is blocked
          if (response?.data?.session_token) {
            sessionStorage.setItem('session_token', response.data.session_token);
          }

          sessionStorage.setItem('just_authenticated', 'true');

          // Redirect based on role
          const role = response.data.user?.role;
          let redirectPath = '/dashboard';
          if (role === 'USER') {
            redirectPath = '/patient-dashboard';
          } else if (role === 'DOCTOR' || role === 'ASSISTANT') {
            redirectPath = '/staff-dashboard';
          }

          navigate(redirectPath, { replace: true, state: { user: response.data.user } });
        } catch (error) {
          console.error('Auth error:', error);
          navigate('/login', { replace: true });
        }
      } else {
        navigate('/login', { replace: true });
      }
    };

    processAuth();
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <p className="text-gray-600">{t('auth.signingIn')}</p>
      </div>
    </div>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [user, setUser] = useState(null);
  const location = useLocation();

  const refreshUser = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.error('Error refreshing user:', error);
      throw error;
    }
  };

  useEffect(() => {
    let isMounted = true;

    const checkAuth = async () => {
      // Check if user is passed via location state
      if (location.state?.user) {
        if (isMounted) {
          setUser(location.state.user);
          setIsAuthenticated(true);
        }
        return;
      }

      const justAuth = sessionStorage.getItem('just_authenticated');
      if (!justAuth) {
        await new Promise(r => setTimeout(r, 150));
      } else {
        sessionStorage.removeItem('just_authenticated');
      }

      try {
        const response = await api.get('/auth/me');
        if (isMounted) {
          setUser(response.data);
          setIsAuthenticated(true);
        }
      } catch (error) {
        if (isMounted) {
          setIsAuthenticated(false);
        }
      }
    };

    checkAuth();

    return () => {
      isMounted = false;
    };
  }, [location.pathname, location.state]);

  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <AuthContext.Provider value={{ user, setUser, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

// Layout Component
const Layout = ({ children }) => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false); // <--- FIXED: Added this line

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout');
      // Redirect to "Already Registered" login page for clinic staff
      navigate('/register-clinic?tab=login', { replace: true });
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/register-clinic?tab=login', { replace: true });
    }
  };

  const handleLogoClick = (e) => {
    e.preventDefault();
    // Navigate to appropriate dashboard based on role - using replace for absolute navigation
    const dashboardPath = user?.role === 'DOCTOR' || user?.role === 'ASSISTANT'
      ? '/staff-dashboard'
      : '/dashboard';
    if (location.pathname !== dashboardPath) {
      navigate(dashboardPath, { replace: true });
    }
    setSidebarOpen(false);
  };

  const isClinicAdmin = user?.role === 'CLINIC_ADMIN';
  const isSuperAdmin = user?.role === 'SUPER_ADMIN';

  const navItems = [
    { path: '/calendar', labelKey: 'nav.calendar', icon: Calendar },
    { path: '/appointments', labelKey: 'nav.appointments', icon: ClipboardList },
    { path: '/clinics', labelKey: 'nav.clinics', icon: Building2 },
  ];

  // Add Super Admin specific items
  if (isSuperAdmin) {
    navItems.push(
      { path: '/locations', labelKey: 'locations.manageLocations', icon: MapPin },
      { path: '/access-requests', labelKey: 'Access Requests', icon: UserPlus }
    );
  }

  if (isClinicAdmin || isSuperAdmin) {
    navItems.push(
      { path: '/doctors', labelKey: 'nav.doctors', icon: Stethoscope },
      { path: '/staff', labelKey: 'nav.staff', icon: UserCog },
      { path: '/services', labelKey: 'nav.services', icon: Briefcase },
      { path: '/settings', labelKey: 'settings.medicalCenterSettings', icon: Settings }
    );
  }

  const renderNavItem = (item) => {
    const isActive = location.pathname === item.path;
    const Icon = item.icon;
    return (
      <button
        key={item.path}
        onClick={() => {
          navigate(item.path);
          setSidebarOpen(false);
        }}
        className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${isActive
          ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
          : 'text-gray-600 hover:bg-gray-100'
          }`}
      >
        <Icon className="w-5 h-5 flex-shrink-0" />
        {!sidebarCollapsed && <span className="text-sm font-medium text-left leading-tight">{t(item.labelKey)}</span>}
      </button>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:sticky top-0 h-screen bg-white border-r border-gray-200 z-50 transition-all duration-300 ${sidebarOpen ? 'left-0' : '-left-64 lg:left-0'
          } ${sidebarCollapsed ? 'w-16' : 'w-56'}`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-3 border-b border-gray-200">
            <a href="#" onClick={handleLogoClick} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-teal-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <Building2 className="w-5 h-5 text-white" />
              </div>
              {!sidebarCollapsed && (
                <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-teal-500 bg-clip-text text-transparent">
                  MediConnect
                </span>
              )}
            </a>
          </div>

          {/* Nav */}
          <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
            {/* Home Button - Uses replace to skip history */}
            <button
              onClick={() => {
                // Always navigate to role-specific dashboard
                let dashboardPath = '/dashboard';
                if (user?.role === 'USER') {
                  dashboardPath = '/patient-dashboard';
                } else if (user?.role === 'DOCTOR' || user?.role === 'ASSISTANT') {
                  dashboardPath = '/staff-dashboard';
                } else if (user?.role === 'CLINIC_ADMIN') {
                  dashboardPath = '/dashboard';
                }
                navigate(dashboardPath, { replace: true });
                setSidebarOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${
                location.pathname === '/dashboard' || location.pathname === '/staff-dashboard' || location.pathname === '/patient-dashboard'
                  ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Home className="w-5 h-5 flex-shrink-0" />
              {!sidebarCollapsed && <span className="text-sm font-medium text-left leading-tight">{t('nav.dashboard')}</span>}
            </button>
            
            {/* Separator */}
            {!sidebarCollapsed && <div className="border-t border-gray-200 my-2"></div>}
            
            {navItems.map(renderNavItem)}
          </nav>

          {/* User & Collapse */}
          <div className="p-2 border-t border-gray-200">
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="hidden lg:flex w-full items-center justify-center p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg mb-2"
            >
              <Menu className="w-5 h-5" />
            </button>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-all"
            >
              <LogOut className="w-5 h-5 flex-shrink-0" />
              {!sidebarCollapsed && <span className="text-sm font-medium">{t('common.signOut')}</span>}
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 min-w-0">
        {/* Top Bar */}
        <header className="bg-white border-b border-gray-200 px-4 py-3 sticky top-0 z-30">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
              >
                <Menu className="w-5 h-5" />
              </button>
              <h1 className="text-lg font-bold text-gray-900">
                {t(navItems.find(item => item.path === location.pathname)?.labelKey || 'nav.dashboard')}
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <LanguageSwitcher compact />

              {/* User Profile Dropdown - Always visible */}
              <div className="relative">
                <button
                  onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                  className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  {user?.picture ? (
                    <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                  ) : (
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-teal-500 rounded-full flex items-center justify-center text-white font-medium text-sm">
                      {user?.name?.charAt(0) || 'U'}
                    </div>
                  )}
                  <div className="hidden sm:block text-left">
                    <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                    <p className="text-xs text-gray-500">
                      {isClinicAdmin ? t('users.clinicAdmin') : isSuperAdmin ? t('users.superAdmin') : t('users.patient')}
                    </p>
                  </div>
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                </button>

                {userDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                      <p className="text-xs text-gray-500">{user?.email}</p>
                      <p className="text-xs text-blue-600 mt-1">
                        {isClinicAdmin ? t('users.clinicAdmin') : t('users.patient')}
                      </p>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      {t('common.signOut')}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-4 page-transition">
          {children}
        </div>
      </main>
    </div>
  );
};

// Import pages
import Dashboard from "./pages/Dashboard";
import CalendarPage from "./pages/Calendar";
import Appointments from "./pages/Appointments";
import Clinics from "./pages/Clinics";
import ClinicDetail from "./pages/ClinicDetail";
import Doctors from "./pages/Doctors";
import Users from "./pages/Users";
import Staff from "./pages/Staff";
import Services from "./pages/Services";
import SettingsPage from "./pages/Settings";
import Login from "./pages/Login";
import RegisterUser from "./pages/RegisterUser";
import RegisterClinic from "./pages/RegisterClinic";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import AcceptInvitation from "./pages/AcceptInvitation";
import StaffDashboard from "./pages/StaffDashboard";
import PatientDashboard from "./pages/PatientDashboard";
import AccessRequestSent from "./pages/AccessRequestSent";
import AccessRequests from "./pages/AccessRequests";
import Locations from "./pages/Locations";

// App Router
function AppRouter() {
  const location = useLocation();

  // Handle session_id synchronously during render
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<RegisterUser />} />
      <Route path="/register-clinic" element={<RegisterClinic />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/accept-invitation" element={<AcceptInvitation />} />
      <Route path="/access-request-sent" element={<AccessRequestSent />} />
      <Route
        path="/staff-dashboard"
        element={
          <ProtectedRoute>
            <StaffDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/patient-dashboard"
        element={
          <ProtectedRoute>
            <PatientDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Layout><Dashboard /></Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/calendar"
        element={
          <ProtectedRoute>
            <Layout><CalendarPage /></Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/appointments"
        element={
          <ProtectedRoute>
            <Layout><Appointments /></Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/clinics"
        element={
          <ProtectedRoute>
            <Layout><Clinics /></Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/clinics/:clinicId"
        element={
          <ProtectedRoute>
            <Layout><ClinicDetail /></Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/doctors"
        element={
          <ProtectedRoute>
            <Layout><Doctors /></Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/users"
        element={
          <ProtectedRoute>
            <Layout><Users /></Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/staff"
        element={
          <ProtectedRoute>
            <Layout><Staff /></Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/services"
        element={
          <ProtectedRoute>
            <Layout><Services /></Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Layout><SettingsPage /></Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/access-requests"
        element={
          <ProtectedRoute>
            <Layout><AccessRequests /></Layout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/locations"
        element={
          <ProtectedRoute>
            <Layout><Locations /></Layout>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppRouter />
    </BrowserRouter>
  );
}

export default App;

// Export api and useAuth for use in other components
export { api, API };