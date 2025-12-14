import { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import LanguageSwitcher from '../components/LanguageSwitcher';
import {
  Building2,
  Calendar,
  User,
  Settings,
  LogOut,
  Menu,
  Loader2,
  CalendarDays,
  Clock,
  MapPin,
  Phone,
  Mail,
  Save,
  CheckCircle,
  ChevronRight,
  Star,
  Cake
} from 'lucide-react';

const PatientDashboard = () => {
  const { t } = useTranslation();
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  // Dashboard data
  const [appointments, setAppointments] = useState([]);
  const [clinics, setClinics] = useState([]);
  const [clinicStats, setClinicStats] = useState({});

  // Profile form
  const [profileForm, setProfileForm] = useState({
    name: '',
    phone: '',
    address: '',
    date_of_birth: ''
  });
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);

  useEffect(() => {
    if (user) {
      setProfileForm({
        name: user.name || '',
        phone: user.phone || '',
        address: user.address || '',
        date_of_birth: user.date_of_birth || ''
      });
    }
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      const [appointmentsRes, clinicsRes] = await Promise.all([
        api.get('/appointments'),
        api.get('/clinics')
      ]);
      setAppointments(appointmentsRes.data);
      setClinics(clinicsRes.data);

      // Fetch stats for each clinic
      const statsPromises = clinicsRes.data.map(clinic => 
        api.get(`/clinics/${clinic.clinic_id}/stats`).catch(() => ({ data: { average_rating: 0, review_count: 0 } }))
      );
      const statsResults = await Promise.all(statsPromises);

      const statsMap = {};
      clinicsRes.data.forEach((clinic, index) => {
        statsMap[clinic.clinic_id] = statsResults[index].data;
      });
      setClinicStats(statsMap);
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout');
      navigate('/login', { replace: true });
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/login', { replace: true });
    }
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileSaved(false);

    try {
      await api.put('/auth/profile', profileForm);
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 3000);
      // Refresh user data
      if (refreshUser) refreshUser();
    } catch (err) {
      console.error('Error saving profile:', err);
    } finally {
      setSavingProfile(false);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString();
  };

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    for (let i = 0; i < 5; i++) {
      stars.push(
        <Star
          key={i}
          className={`w-4 h-4 ${i < fullStars ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
        />
      );
    }
    return stars;
  };

  const upcomingAppointments = appointments
    .filter(apt => apt.status !== 'CANCELLED' && apt.status !== 'COMPLETED')
    .slice(0, 3);

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
            <Link to="/patient-dashboard" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-teal-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <Building2 className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-teal-500 bg-clip-text text-transparent">
                MediConnect
              </span>
            </Link>
          </div>

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

            <button
              onClick={() => setActiveTab('clinics')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                activeTab === 'clinics'
                  ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Building2 className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('clinics.title')}</span>
            </button>

            <button
              onClick={() => setActiveTab('profile')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                activeTab === 'profile'
                  ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Settings className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('patientDashboard.profileSettings')}</span>
            </button>
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
                <p className="text-xs text-gray-500">{t('patientDashboard.patient')}</p>
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
                {activeTab === 'dashboard' && t('patientDashboard.title')}
                {activeTab === 'clinics' && t('clinics.title')}
                {activeTab === 'profile' && t('patientDashboard.profileSettings')}
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <LanguageSwitcher compact />
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-4 page-transition">
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : activeTab === 'dashboard' ? (
            /* Dashboard Tab */
            <div className="space-y-6">
              {/* Welcome */}
              <div className="bg-gradient-to-r from-blue-600 to-teal-500 rounded-xl p-6 text-white">
                <h2 className="text-2xl font-bold mb-1">
                  {t('dashboard.welcomeBack', { name: user?.name?.split(' ')[0] || 'User' })}
                </h2>
                <p className="text-white/80">{t('patientDashboard.subtitle')}</p>
              </div>

              {/* Upcoming Appointments */}
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <CalendarDays className="w-5 h-5 text-blue-600" />
                  {t('patientDashboard.upcomingAppointments')}
                </h3>

                {upcomingAppointments.length > 0 ? (
                  <div className="space-y-3">
                    {upcomingAppointments.map((apt) => (
                      <div key={apt.appointment_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">Dr. {apt.doctor_name}</p>
                          <p className="text-sm text-gray-500">{apt.doctor_specialty}</p>
                          <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                            <CalendarDays className="w-4 h-4" />
                            {formatDate(apt.date_time)}
                            <Clock className="w-4 h-4 ml-2" />
                            {apt.duration} min
                          </div>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          apt.status === 'CONFIRMED' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                        }`}>
                          {apt.status}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">{t('patientDashboard.noUpcoming')}</p>
                )}
              </div>
            </div>
          ) : activeTab === 'clinics' ? (
            /* Clinics Tab */
            <div className="space-y-4">
              <p className="text-sm text-gray-500">{t('patientDashboard.clinicsSubtitle')}</p>

              {clinics.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
                  <Building2 className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                  <p className="text-gray-500">{t('clinics.noClinics')}</p>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 gap-4">
                  {clinics.map((clinic) => {
                    const stats = clinicStats[clinic.clinic_id] || { average_rating: 0, review_count: 0 };

                    return (
                      <div
                        key={clinic.clinic_id}
                        onClick={() => navigate(`/clinics/${clinic.clinic_id}`)}
                        className="bg-white rounded-xl border border-gray-200 p-4 cursor-pointer hover:shadow-lg hover:border-blue-200 transition-all"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex items-start gap-3 flex-1">
                            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-teal-400 flex items-center justify-center text-white flex-shrink-0">
                              <Building2 className="w-6 h-6" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <h3 className="font-semibold text-gray-900">{clinic.name}</h3>
                              {clinic.description && (
                                <p className="text-sm text-gray-500 line-clamp-1">{clinic.description}</p>
                              )}

                              {/* Rating */}
                              {stats.review_count > 0 && (
                                <div className="flex items-center gap-1 mt-1">
                                  <div className="flex">{renderStars(stats.average_rating)}</div>
                                  <span className="text-sm text-gray-600 ml-1">
                                    {stats.average_rating.toFixed(1)} ({stats.review_count})
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
                        </div>

                        <div className="mt-4 space-y-2 text-sm">
                          <p className="flex items-center gap-2 text-gray-600">
                            <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" />
                            <span className="truncate">{clinic.address}</span>
                          </p>
                          {clinic.phone && (
                            <p className="flex items-center gap-2 text-gray-600">
                              <Phone className="w-4 h-4 text-gray-400 flex-shrink-0" />
                              {clinic.phone}
                            </p>
                          )}
                        </div>

                        <div className="mt-3 pt-3 border-t border-gray-100">
                          <span className="text-xs text-blue-600 font-medium">{t('clinics.viewDetails')} →</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ) : (
            /* Profile Settings Tab */
            <div className="max-w-lg">
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <User className="w-5 h-5 text-blue-600" />
                  {t('patientDashboard.personalData')}
                </h3>

                <form onSubmit={handleSaveProfile} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('auth.name')}
                    </label>
                    <input
                      type="text"
                      value={profileForm.name}
                      onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder={t('patientDashboard.namePlaceholder')}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('auth.email')}
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="email"
                        value={user?.email || ''}
                        disabled
                        className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg bg-gray-50 cursor-not-allowed"
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{t('patientDashboard.emailCannotChange')}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('auth.phone')}
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="tel"
                        value={profileForm.phone}
                        onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                        className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder={t('auth.placeholders.phone')}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('patientDashboard.address')}
                    </label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        value={profileForm.address}
                        onChange={(e) => setProfileForm({ ...profileForm, address: e.target.value })}
                        className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder={t('patientDashboard.addressPlaceholder')}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('patientDashboard.dateOfBirth')}
                    </label>
                    <div className="relative">
                      <Cake className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="date"
                        value={profileForm.date_of_birth}
                        onChange={(e) => setProfileForm({ ...profileForm, date_of_birth: e.target.value })}
                        className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={savingProfile}
                    className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {savingProfile ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : profileSaved ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <Save className="w-5 h-5" />
                    )}
                    {profileSaved ? t('notifications.saveSuccess') : t('common.save')}
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default PatientDashboard;