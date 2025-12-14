import { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import LanguageSwitcher from '../components/LanguageSwitcher';
import {
  Building2,
  Calendar,
  Users,
  Clock,
  LogOut,
  Menu,
  X,
  Loader2,
  CalendarDays,
  UserCircle,
  Settings,
  Save,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

const StaffDashboard = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [stats, setStats] = useState(null);
  const [doctor, setDoctor] = useState(null);
  const [clinicHours, setClinicHours] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  // Availability editing
  const [availability, setAvailability] = useState({});
  const [savingAvailability, setSavingAvailability] = useState(false);
  const [availabilitySaved, setAvailabilitySaved] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const statsRes = await api.get('/stats/staff');
      setStats(statsRes.data);

      // If user is a doctor, fetch their doctor record and clinic hours
      if (user?.role === 'DOCTOR') {
        const doctorsRes = await api.get('/doctors');
        const myDoctor = doctorsRes.data.find(d => d.email.toLowerCase() === user.email.toLowerCase());
        if (myDoctor) {
          setDoctor(myDoctor);
          setAvailability(myDoctor.availability_schedule || {});

          // Fetch clinic hours
          const clinicRes = await api.get(`/clinics/${myDoctor.clinic_id}`);
          setClinicHours(clinicRes.data.working_hours || {});
        }
      }
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout');
      navigate('/register-clinic?tab=login', { replace: true });
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/register-clinic?tab=login', { replace: true });
    }
  };

  const getRoleLabel = (role) => {
    const roleMap = {
      'DOCTOR': t('staff.doctor'),
      'ASSISTANT': t('staff.assistant')
    };
    return roleMap[role] || role;
  };

  const updateAvailability = (day, index, field, value) => {
    setAvailability(prev => {
      const daySchedule = [...(prev[day] || [])];
      if (!daySchedule[index]) {
        daySchedule[index] = { start: '09:00', end: '17:00' };
      }
      daySchedule[index] = { ...daySchedule[index], [field]: value };
      return { ...prev, [day]: daySchedule };
    });
  };

  const addPeriod = (day) => {
    setAvailability(prev => ({
      ...prev,
      [day]: [...(prev[day] || []), { start: '09:00', end: '17:00' }]
    }));
  };

  const removePeriod = (day, index) => {
    setAvailability(prev => ({
      ...prev,
      [day]: (prev[day] || []).filter((_, i) => i !== index)
    }));
  };

  const handleSaveAvailability = async () => {
    if (!doctor) return;

    setSavingAvailability(true);
    setAvailabilitySaved(false);

    try {
      await api.put(`/doctors/${doctor.doctor_id}/availability`, {
        availability_schedule: availability
      });
      setAvailabilitySaved(true);
      setTimeout(() => setAvailabilitySaved(false), 3000);
    } catch (err) {
      console.error('Error saving availability:', err);
      alert(err.response?.data?.detail || 'Error saving availability');
    } finally {
      setSavingAvailability(false);
    }
  };

  const isClinicOpen = (day) => {
    return clinicHours && clinicHours[day] !== null;
  };

  const getClinicHoursText = (day) => {
    if (!clinicHours || clinicHours[day] === null) {
      return t('settings.closed');
    }
    return `${clinicHours[day].start} - ${clinicHours[day].end}`;
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
        className={`fixed lg:sticky top-0 h-screen bg-white border-r border-gray-200 z-50 transition-all duration-300 w-56 ${
          sidebarOpen ? 'left-0' : '-left-64 lg:left-0'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-3 border-b border-gray-200">
            <Link to="/staff-dashboard" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-teal-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <Building2 className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-teal-500 bg-clip-text text-transparent">
                MediConnect
              </span>
            </Link>
          </div>

          {/* Clinic Info */}
          {stats?.clinic_name && (
            <div className="px-3 py-2 border-b border-gray-200">
              <p className="text-xs text-gray-500 uppercase tracking-wider">{t('staffDashboard.yourClinic')}</p>
              <p className="font-medium text-gray-900 text-sm truncate">{stats.clinic_name}</p>
            </div>
          )}

          {/* Nav */}
          <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                activeTab === 'dashboard'
                  ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Calendar className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('nav.dashboard')}</span>
            </button>

            {user?.role === 'DOCTOR' && (
              <button
                onClick={() => setActiveTab('availability')}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  activeTab === 'availability'
                    ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Settings className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm font-medium">{t('staffDashboard.myAvailability')}</span>
              </button>
            )}
          </nav>

          {/* User & Logout */}
          <div className="p-2 border-t border-gray-200">
            <div className="flex items-center gap-2 px-3 py-2 mb-2">
              {user?.picture ? (
                <img src={user.picture} alt={user?.name} className="w-8 h-8 rounded-full" />
              ) : (
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-teal-500 rounded-full flex items-center justify-center text-white font-medium text-sm">
                  {user?.name?.charAt(0) || 'U'}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{user?.name}</p>
                <p className="text-xs text-gray-500">{getRoleLabel(user?.role)}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-all"
            >
              <LogOut className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('common.signOut')}</span>
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
                {activeTab === 'dashboard' ? t('staffDashboard.title') : t('staffDashboard.myAvailability')}
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <LanguageSwitcher compact />
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="p-4 page-transition">
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : activeTab === 'dashboard' ? (
            <div className="space-y-6">
              {/* Welcome */}
              <div className="bg-gradient-to-r from-blue-600 to-teal-500 rounded-xl p-6 text-white">
                <h2 className="text-2xl font-bold mb-1">
                  {t('dashboard.welcomeBack', { name: user?.name?.split(' ')[0] || 'User' })}
                </h2>
                <p className="text-white/80">{t('staffDashboard.subtitle')}</p>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white rounded-xl border border-gray-200 p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Clock className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">{stats?.today_appointments || 0}</p>
                      <p className="text-sm text-gray-500">{t('staffDashboard.todayAppointments')}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-xl border border-gray-200 p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center">
                      <CalendarDays className="w-6 h-6 text-teal-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">{stats?.upcoming_appointments || 0}</p>
                      <p className="text-sm text-gray-500">{t('staffDashboard.upcomingAppointments')}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-xl border border-gray-200 p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Users className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">{stats?.total_patients || 0}</p>
                      <p className="text-sm text-gray-500">{t('staffDashboard.totalPatients')}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Info Card */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    <UserCircle className="w-6 h-6 text-gray-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">{t('staffDashboard.yourAccount')}</h3>
                    <p className="text-sm text-gray-600 mb-2">{t('staffDashboard.accountInfo')}</p>
                    <div className="space-y-1 text-sm">
                      <p><span className="text-gray-500">{t('auth.email')}:</span> <span className="font-medium">{user?.email}</span></p>
                      <p><span className="text-gray-500">{t('staff.staffRole')}:</span> <span className="font-medium">{getRoleLabel(user?.role)}</span></p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Availability Tab */
            <div className="space-y-4 max-w-2xl">
              {/* Info Banner */}
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm text-blue-800">{t('staffDashboard.availabilityInfo')}</p>
                  </div>
                </div>
              </div>

              {/* Availability Editor */}
              <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-4">
                <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-blue-600" />
                  {t('staffDashboard.setYourSchedule')}
                </h2>

                <div className="space-y-3">
                  {DAYS_OF_WEEK.map((day) => (
                    <div key={day} className="border-b border-gray-100 pb-3 last:border-0">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <span className="font-medium text-gray-900 capitalize">{t(`days.${day}`)}</span>
                          <span className={`ml-2 text-xs ${isClinicOpen(day) ? 'text-green-600' : 'text-red-500'}`}>
                            ({t('staffDashboard.clinicHours')}: {getClinicHoursText(day)})
                          </span>
                        </div>
                        {isClinicOpen(day) && (
                          <button
                            onClick={() => addPeriod(day)}
                            className="text-xs text-blue-600 hover:underline"
                          >
                            + {t('staffDashboard.addPeriod')}
                          </button>
                        )}
                      </div>

                      {!isClinicOpen(day) ? (
                        <p className="text-sm text-gray-400 italic">{t('staffDashboard.clinicClosed')}</p>
                      ) : (availability[day] || []).length === 0 ? (
                        <p className="text-sm text-gray-400 italic">{t('staffDashboard.noPeriods')}</p>
                      ) : (
                        <div className="space-y-2">
                          {(availability[day] || []).map((period, index) => (
                            <div key={index} className="flex items-center gap-2">
                              <input
                                type="time"
                                value={period.start || '09:00'}
                                onChange={(e) => updateAvailability(day, index, 'start', e.target.value)}
                                className="px-2 py-1 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              />
                              <span className="text-gray-400">-</span>
                              <input
                                type="time"
                                value={period.end || '17:00'}
                                onChange={(e) => updateAvailability(day, index, 'end', e.target.value)}
                                className="px-2 py-1 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              />
                              <button
                                onClick={() => removePeriod(day, index)}
                                className="p-1 text-red-500 hover:bg-red-50 rounded"
                              >
                                <X className="w-4 h-4" />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                <button
                  onClick={handleSaveAvailability}
                  disabled={savingAvailability}
                  className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {savingAvailability ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : availabilitySaved ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    <Save className="w-5 h-5" />
                  )}
                  {availabilitySaved ? t('notifications.saveSuccess') : t('common.save')}
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default StaffDashboard;