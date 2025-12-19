import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import {
  CalendarDays,
  Users,
  Stethoscope,
  Building2,
  Clock,
  CalendarPlus,
  UserCog,
  Briefcase,
  ClipboardList,
  Settings,
  User,
  Phone,
  Mail,
  Save,
  CheckCircle,
  Loader2,
  AlertCircle,
  MapPin
} from 'lucide-react';

const Dashboard = () => {
  const { t } = useTranslation();
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isFetching, setIsFetching] = useState(false);
  const [currentLocation, setCurrentLocation] = useState(null);

  // Profile form
  const [profileForm, setProfileForm] = useState({
    name: '',
    phone: '',
    email: ''
  });
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);

  useEffect(() => {
    let isMounted = true;
    
    if (user) {
      setProfileForm({
        name: user.name || '',
        phone: user.phone || '',
        email: user.email || ''
      });
    }
    
    // Only fetch if mounted and user exists
    if (isMounted && user) {
      fetchData();
    }
    
    return () => {
      isMounted = false;
    };
  }, [user?.user_id]); // Only re-run when user ID changes, not on every user object change

  // Listen for location changes - only if user exists
  useEffect(() => {
    if (!user) return;
    
    const handleLocationChange = () => {
      // Only fetch if not already fetching
      if (!isFetching) {
        fetchData();
      }
    };
    
    window.addEventListener('locationChanged', handleLocationChange);
    return () => window.removeEventListener('locationChanged', handleLocationChange);
  }, [user, isFetching]);

  const fetchData = async () => {
    // Prevent duplicate calls if already fetching
    if (isFetching) return;
    
    setIsFetching(true);
    try {
      // Fetch current location if user has organization
      let locationData = null;
      if (user?.organization_id) {
        try {
          const activeLocationId = localStorage.getItem('active_location_id');
          if (activeLocationId) {
            const locRes = await api.get(`/locations/${activeLocationId}`);
            locationData = locRes.data;
          }
        } catch (err) {
          console.error('Error fetching location:', err);
        }
      }
      setCurrentLocation(locationData);

      const [statsRes, aptsRes] = await Promise.all([
        api.get('/stats'),
        api.get('/appointments')
      ]);
      setStats(statsRes.data);
      // Sort and get upcoming appointments
      const now = new Date();
      const upcoming = aptsRes.data
        .filter(a => new Date(a.date_time) >= now && a.status !== 'CANCELLED')
        .sort((a, b) => new Date(a.date_time) - new Date(b.date_time))
        .slice(0, 5);
      setAppointments(upcoming);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
      setIsFetching(false);
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileSaved(false);

    try {
      const response = await api.put('/auth/profile', profileForm);
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 3000);
      // Refresh user data from response
      if (refreshUser) {
        await refreshUser();
      }
    } catch (err) {
      console.error('Error saving profile:', err);
      alert(t('notifications.error'));
    } finally {
      setSavingProfile(false);
    }
  };

  const isClinicAdmin = user?.role === 'CLINIC_ADMIN';

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
  };

  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'dashboard'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          {t('nav.dashboard')}
        </button>
        <button
          onClick={() => setActiveTab('profile')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'profile'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          {t('patientDashboard.profileSettings')}
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'dashboard' ? (
        /* Dashboard Tab */
        <div className="space-y-4">
          {/* Welcome Header */}
          <div className="bg-gradient-to-r from-blue-600 to-teal-500 rounded-xl p-4 text-white">
            <h1 className="text-xl font-bold">{t('dashboard.welcomeBack', { name: user?.name?.split(' ')[0] })}</h1>
            <p className="text-white/80 text-sm">
              {isClinicAdmin ? t('dashboard.adminSubtitle') : t('dashboard.patientSubtitle')}
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {isClinicAdmin ? (
              <>
                <StatCard icon={CalendarDays} label={t('dashboard.stats.todayAppointments')} value={stats?.today_appointments || 0} color="blue" />
                <StatCard icon={Clock} label={t('dashboard.stats.upcoming')} value={stats?.upcoming_appointments || 0} color="teal" />
                <StatCard icon={Stethoscope} label={t('dashboard.stats.totalDoctors')} value={stats?.total_doctors || 0} color="purple" />
                <StatCard icon={Users} label={t('dashboard.stats.totalPatients')} value={stats?.total_patients || 0} color="orange" />
              </>
            ) : (
              <>
                <StatCard icon={CalendarDays} label={t('dashboard.stats.totalAppointments')} value={stats?.total_appointments || 0} color="blue" />
                <StatCard icon={Clock} label={t('dashboard.stats.upcoming')} value={stats?.upcoming_appointments || 0} color="teal" />
              </>
            )}
          </div>

          {/* Quick Actions & Upcoming */}
          <div className="grid md:grid-cols-2 gap-4">
            {/* Quick Actions */}
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <h2 className="font-semibold text-gray-900 mb-3">{t('dashboard.quickActions')}</h2>
              <div className="grid grid-cols-2 gap-2">
                {isClinicAdmin ? (
                  <>
                    <ActionButton icon={CalendarDays} label={t('dashboard.viewAllAppointments')} onClick={() => navigate('/appointments')} />
                    <ActionButton icon={Stethoscope} label={t('dashboard.manageDoctors')} onClick={() => navigate('/doctors')} />
                    <ActionButton icon={UserCog} label={t('dashboard.manageStaff')} onClick={() => navigate('/staff')} />
                    <ActionButton icon={Briefcase} label={t('dashboard.manageServices')} onClick={() => navigate('/services')} />
                  </>
                ) : (
                  <>
                    <ActionButton icon={CalendarPlus} label={t('dashboard.bookAppointment')} onClick={() => navigate('/calendar')} />
                    <ActionButton icon={CalendarDays} label={t('dashboard.viewAllAppointments')} onClick={() => navigate('/appointments')} />
                    <ActionButton icon={Building2} label={t('dashboard.browseClinics')} onClick={() => navigate('/clinics')} />
                  </>
                )}
              </div>
            </div>

            {/* Upcoming Appointments */}
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <h2 className="font-semibold text-gray-900 mb-3">
                {isClinicAdmin ? t('dashboard.todaySchedule') : t('dashboard.upcomingAppointments')}
              </h2>
              {appointments.length === 0 ? (
                <div className="text-center py-6 text-gray-500">
                  <CalendarDays className="w-10 h-10 mx-auto mb-2 text-gray-300" />
                  <p className="text-sm">{t('dashboard.noUpcoming')}</p>
                  {!isClinicAdmin && (
                    <button
                      onClick={() => navigate('/calendar')}
                      className="mt-2 text-sm text-blue-600 hover:underline"
                    >
                      {t('dashboard.bookFirst')}
                    </button>
                  )}
                </div>
              ) : (
                <div className="space-y-2">
                  {appointments.map((apt) => (
                    <div
                      key={apt.appointment_id}
                      className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                      onClick={() => navigate('/appointments')}
                    >
                      <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600 flex-shrink-0">
                        <Clock className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 text-sm truncate">
                          {isClinicAdmin ? apt.patient_name : `Dr. ${apt.doctor_name}`}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatDate(apt.date_time)} • {formatTime(apt.date_time)}
                        </p>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        apt.status === 'SCHEDULED' ? 'bg-blue-100 text-blue-700' :
                        apt.status === 'CONFIRMED' ? 'bg-green-100 text-green-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {t(`appointments.${apt.status.toLowerCase()}`)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Clinic Admin Extra Stats */}
          {isClinicAdmin && (
            <div className="grid grid-cols-3 gap-3">
              <StatCard icon={UserCog} label={t('dashboard.stats.totalStaff')} value={stats?.total_staff || 0} color="indigo" small />
              <StatCard icon={Briefcase} label={t('dashboard.stats.totalServices')} value={stats?.total_services || 0} color="pink" small />
              <StatCard icon={ClipboardList} label={t('dashboard.stats.totalAppointments')} value={stats?.total_appointments || 0} color="cyan" small />
            </div>
          )}
        </div>
      ) : (
        /* Profile Settings Tab - High density full-width layout */
        <div className="mx-auto">
          {/* Header strip */}
          <div className="bg-white border border-gray-200 rounded-lg px-4 py-2 mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Settings className="w-4 h-4 text-blue-600" />
              <h3 className="text-sm font-semibold text-gray-900">{t('patientDashboard.personalData')}</h3>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <User className="w-3.5 h-3.5 text-gray-400" />
              <span>{user?.email}</span>
            </div>
          </div>

          {/* Dense form container */}
          <form onSubmit={handleSaveProfile} className="bg-white border border-gray-200 rounded-lg p-3">
            {/* Identity row */}
            <div className="grid grid-cols-12 gap-3">
              <div className="col-span-12 md:col-span-6">
                <label className="block text-xs font-medium text-gray-600 mb-1">{t('auth.name')}</label>
                <input
                  type="text"
                  value={profileForm.name}
                  onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                  className="w-full px-2.5 py-2 border border-gray-200 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder={t('patientDashboard.namePlaceholder')}
                />
              </div>
              <div className="col-span-12 md:col-span-6">
                <label className="block text-xs font-medium text-gray-600 mb-1">{t('auth.phone')}</label>
                <div className="relative">
                  <Phone className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="tel"
                    value={profileForm.phone}
                    onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                    className="w-full pl-8 pr-2.5 py-2 border border-gray-200 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm"
                    placeholder={t('auth.placeholders.phone')}
                  />
                </div>
              </div>
            </div>

            {/* Account row */}
            <div className="grid grid-cols-12 gap-3 mt-3">
              <div className="col-span-12 md:col-span-6">
                <label className="block text-xs font-medium text-gray-600 mb-1">{t('auth.email')}</label>
                <div className="relative">
                  <Mail className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="w-full pl-8 pr-2.5 py-2 border border-gray-200 rounded-md bg-gray-50 text-gray-500 text-sm"
                  />
                </div>
                <p className="text-[11px] text-gray-500 mt-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {t('patientDashboard.emailCannotChange')}
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-2 mt-4">
              <button
                type="button"
                onClick={() => setProfileForm({
                  name: user?.name || '',
                  phone: user?.phone || '',
                  email: user?.email || ''
                })}
                className="sm:w-40 w-full py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50"
              >
                {t('common.cancel')}
              </button>
              <button
                type="submit"
                disabled={savingProfile}
                className="sm:w-48 w-full py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-md text-sm font-semibold hover:shadow-md disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {savingProfile ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : profileSaved ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                {profileSaved ? t('notifications.saveSuccess') : t('common.save')}
              </button>

              {profileSaved && (
                <div className="flex-1 py-2 px-3 bg-green-50 border border-green-200 text-green-700 rounded-md text-xs flex items-center gap-2">
                  <CheckCircle className="w-3.5 h-3.5" />
                  {t('notifications.profileUpdated')}
                </div>
              )}
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

const StatCard = ({ icon: Icon, label, value, color, small = false }) => {
  const colors = {
    blue: 'bg-blue-50 text-blue-600',
    teal: 'bg-teal-50 text-teal-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
    indigo: 'bg-indigo-50 text-indigo-600',
    pink: 'bg-pink-50 text-pink-600',
    cyan: 'bg-cyan-50 text-cyan-600'
  };

  return (
    <div className={`bg-white rounded-xl border border-gray-200 ${small ? 'p-3' : 'p-4'}`}>
      <div className="flex items-center gap-3">
        <div className={`${small ? 'w-8 h-8' : 'w-10 h-10'} rounded-lg ${colors[color]} flex items-center justify-center`}>
          <Icon className={small ? 'w-4 h-4' : 'w-5 h-5'} />
        </div>
        <div>
          <p className={`${small ? 'text-lg' : 'text-2xl'} font-bold text-gray-900`}>{value}</p>
          <p className="text-xs text-gray-500 truncate">{label}</p>
        </div>
      </div>
    </div>
  );
};

const ActionButton = ({ icon: Icon, label, onClick }) => (
  <button
    onClick={onClick}
    className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-all text-left group"
  >
    <Icon className="w-5 h-5 text-gray-400 group-hover:text-blue-500" />
    <span className="text-sm font-medium truncate">{label}</span>
  </button>
);

export default Dashboard;
