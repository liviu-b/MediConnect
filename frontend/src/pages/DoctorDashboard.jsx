import { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import LanguageSwitcher from '../components/LanguageSwitcher';
import NotificationBell from '../components/NotificationBell';
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
  CheckCircle,
  XCircle,
  History,
  FileText,
  Pill,
  Plus,
  X,
  AlertTriangle,
  Stethoscope,
  ChevronDown,
  Activity,
  Users,
  TrendingUp,
  Save
} from 'lucide-react';

const DoctorDashboard = () => {
  const { t, i18n } = useTranslation();
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const getInitialTab = () => {
    const params = new URLSearchParams(location.search);
    return params.get('tab') || 'dashboard';
  };
  
  const [activeTab, setActiveTab] = useState(getInitialTab());
  const [loading, setLoading] = useState(true);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  // Dashboard data
  const [appointments, setAppointments] = useState([]);
  const [stats, setStats] = useState({
    today: 0,
    upcoming: 0,
    completed: 0,
    totalPatients: 0
  });

  // Profile form
  const [profileForm, setProfileForm] = useState({
    name: '',
    phone: '',
    specialty: '',
    bio: '',
    consultation_duration: '',
    consultation_fee: ''
  });
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);

  // Add Prescription Modal
  const [showPrescriptionModal, setShowPrescriptionModal] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [prescriptionForm, setPrescriptionForm] = useState({
    medications: [{ name: '', dosage: '', frequency: '', duration: '' }],
    notes: ''
  });
  const [savingPrescription, setSavingPrescription] = useState(false);

  // Add Medical Record Modal
  const [showRecordModal, setShowRecordModal] = useState(false);
  const [recordForm, setRecordForm] = useState({
    record_type: 'RECOMMENDATION',
    title: '',
    content: ''
  });
  const [savingRecord, setSavingRecord] = useState(false);

  // Add Lab Result Modal
  const [showLabResultModal, setShowLabResultModal] = useState(false);
  const [labResultForm, setLabResultForm] = useState({
    test_name: '',
    test_category: 'blood_test',
    result_value: '',
    result_unit: '',
    reference_range: '',
    status: 'COMPLETED',
    notes: '',
    interpretation: '',
    lab_name: '',
    test_date: new Date().toISOString().split('T')[0]
  });
  const [savingLabResult, setSavingLabResult] = useState(false);

  // Patient History Modal
  const [showPatientHistoryModal, setShowPatientHistoryModal] = useState(false);
  const [patientHistory, setPatientHistory] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  const changeTab = (tab) => {
    setActiveTab(tab);
    navigate(`/doctor-dashboard?tab=${tab}`, { replace: true });
  };

  useEffect(() => {
    if (user) {
      setProfileForm({
        name: user.name || '',
        phone: user.phone || '',
        specialty: user.specialty || '',
        bio: user.bio || '',
        consultation_duration: user.consultation_duration || '',
        consultation_fee: user.consultation_fee || ''
      });
      fetchData();
    }
  }, [user?.user_id]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await api.get('/appointments');
      // Filter appointments for this doctor
      const myAppointments = res.data.filter(apt => apt.doctor_id === user?.user_id);
      setAppointments(myAppointments);

      // Calculate stats
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);

      const todayCount = myAppointments.filter(apt => {
        const aptDate = new Date(apt.date_time);
        return aptDate >= today && aptDate < tomorrow && apt.status !== 'CANCELLED';
      }).length;

      const upcomingCount = myAppointments.filter(apt => {
        const aptDate = new Date(apt.date_time);
        return aptDate >= today && apt.status !== 'CANCELLED' && apt.status !== 'COMPLETED';
      }).length;

      const completedCount = myAppointments.filter(apt => apt.status === 'COMPLETED').length;

      // Count unique patients
      const uniquePatients = new Set(myAppointments.map(apt => apt.patient_id));

      setStats({
        today: todayCount,
        upcoming: upcomingCount,
        completed: completedCount,
        totalPatients: uniquePatients.size
      });
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

  const handleCompleteAppointment = async (appointmentId) => {
    try {
      await api.post(`/appointments/${appointmentId}/complete`);
      fetchData();
    } catch (err) {
      console.error('Error completing appointment:', err);
      alert(t('notifications.error'));
    }
  };

  const openPrescriptionModal = (appointment) => {
    setSelectedPatient(appointment);
    setPrescriptionForm({
      medications: [{ name: '', dosage: '', frequency: '', duration: '' }],
      notes: ''
    });
    setShowPrescriptionModal(true);
  };

  const openRecordModal = (appointment) => {
    setSelectedPatient(appointment);
    setRecordForm({
      record_type: 'RECOMMENDATION',
      title: '',
      content: ''
    });
    setShowRecordModal(true);
  };

  const openLabResultModal = (appointment) => {
    setSelectedPatient(appointment);
    setLabResultForm({
      test_name: '',
      test_category: 'blood_test',
      result_value: '',
      result_unit: '',
      reference_range: '',
      status: 'COMPLETED',
      notes: '',
      interpretation: '',
      lab_name: '',
      test_date: new Date().toISOString().split('T')[0]
    });
    setShowLabResultModal(true);
  };

  const handleAddMedication = () => {
    setPrescriptionForm({
      ...prescriptionForm,
      medications: [...prescriptionForm.medications, { name: '', dosage: '', frequency: '', duration: '' }]
    });
  };

  const handleRemoveMedication = (index) => {
    const newMedications = prescriptionForm.medications.filter((_, i) => i !== index);
    setPrescriptionForm({ ...prescriptionForm, medications: newMedications });
  };

  const handleMedicationChange = (index, field, value) => {
    const newMedications = [...prescriptionForm.medications];
    newMedications[index][field] = value;
    setPrescriptionForm({ ...prescriptionForm, medications: newMedications });
  };

  const handleSavePrescription = async () => {
    setSavingPrescription(true);
    try {
      await api.post(`/appointments/${selectedPatient.appointment_id}/prescription`, prescriptionForm);
      setShowPrescriptionModal(false);
      alert(t('appointments.prescriptionSuccess'));
      fetchData();
    } catch (err) {
      console.error('Error saving prescription:', err);
      alert(t('notifications.error'));
    } finally {
      setSavingPrescription(false);
    }
  };

  const handleSaveRecord = async () => {
    setSavingRecord(true);
    try {
      await api.post(`/appointments/${selectedPatient.appointment_id}/medical-record`, recordForm);
      setShowRecordModal(false);
      alert(t('appointments.recordSuccess'));
      fetchData();
    } catch (err) {
      console.error('Error saving record:', err);
      alert(t('notifications.error'));
    } finally {
      setSavingRecord(false);
    }
  };

  const handleSaveLabResult = async () => {
    setSavingLabResult(true);
    try {
      await api.post(`/health/lab-results/${selectedPatient.patient_id}`, {
        ...labResultForm,
        test_date: new Date(labResultForm.test_date).toISOString()
      });
      setShowLabResultModal(false);
      alert('Lab result added successfully!');
      fetchData();
    } catch (err) {
      console.error('Error saving lab result:', err);
      alert(t('notifications.error'));
    } finally {
      setSavingLabResult(false);
    }
  };

  const viewPatientHistory = async (appointment) => {
    setSelectedPatient(appointment);
    setHistoryLoading(true);
    setShowPatientHistoryModal(true);

    try {
      const res = await api.get(`/patients/${appointment.patient_id}/history`);
      setPatientHistory(res.data);
    } catch (err) {
      console.error('Error fetching patient history:', err);
      setPatientHistory(null);
    } finally {
      setHistoryLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString();
  };

  const formatDateTime = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const todayAppointments = appointments.filter(apt => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const aptDate = new Date(apt.date_time);
    return aptDate >= today && aptDate < tomorrow && apt.status !== 'CANCELLED';
  });

  const upcomingAppointments = appointments.filter(apt => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const aptDate = new Date(apt.date_time);
    return aptDate >= today && apt.status !== 'CANCELLED' && apt.status !== 'COMPLETED';
  }).slice(0, 5);

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
            <Link to="/doctor-dashboard" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
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
              onClick={() => {
                navigate('/doctor-dashboard', { replace: true });
                setActiveTab('dashboard');
                setSidebarOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                activeTab === 'dashboard'
                  ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Calendar className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('nav.dashboard')}</span>
            </button>

            <div className="border-t border-gray-200 my-2"></div>

            <button
              onClick={() => changeTab('appointments')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                activeTab === 'appointments'
                  ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <CalendarDays className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('nav.appointments')}</span>
            </button>

            <button
              onClick={() => changeTab('patients')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                activeTab === 'patients'
                  ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Users className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('doctorDashboard.myPatients')}</span>
            </button>

            <button
              onClick={() => changeTab('profile')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                activeTab === 'profile'
                  ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Settings className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('doctors.profileSettings')}</span>
            </button>
          </nav>

          {/* Logout */}
          <div className="p-2 border-t border-gray-200">
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
                {activeTab === 'dashboard' && t('doctorDashboard.title')}
                {activeTab === 'appointments' && t('nav.appointments')}
                {activeTab === 'patients' && t('doctorDashboard.myPatients')}
                {activeTab === 'profile' && t('doctors.profileSettings')}
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <LanguageSwitcher compact />
              <NotificationBell />

              {/* User Profile */}
              <div className="relative">
                <button
                  onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                  className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-teal-500 rounded-full flex items-center justify-center text-white font-medium text-sm">
                    {user?.name?.charAt(0) || 'D'}
                  </div>
                  <div className="hidden sm:block text-left">
                    <p className="text-sm font-medium text-gray-900">Dr. {user?.name}</p>
                    <p className="text-xs text-gray-500">{user?.specialty}</p>
                  </div>
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                </button>

                {userDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-900">Dr. {user?.name}</p>
                      <p className="text-xs text-gray-500">{user?.email}</p>
                      <p className="text-xs text-blue-600 mt-1">{user?.specialty}</p>
                    </div>
                    <button
                      onClick={() => {
                        changeTab('profile');
                        setUserDropdownOpen(false);
                      }}
                      className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      <Settings className="w-4 h-4" />
                      {t('doctors.profileSettings')}
                    </button>
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

        {/* Content */}
        <div className="p-4">
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : activeTab === 'dashboard' ? (
            /* Dashboard Tab */
            <div className="space-y-6 max-w-6xl mx-auto">
              {/* Welcome */}
              <div className="bg-gradient-to-r from-blue-600 to-teal-500 rounded-xl p-6 text-white">
                <h2 className="text-2xl font-bold mb-1">
                  {t('dashboard.welcomeBack', { name: 'Dr. ' + (user?.name?.split(' ')[0] || 'Doctor') })}
                </h2>
                <p className="text-white/80">{t('doctorDashboard.subtitle')}</p>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Calendar className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">{t('doctorDashboard.todayAppointments')}</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.today}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <CalendarDays className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">{t('doctorDashboard.upcomingAppointments')}</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.upcoming}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <CheckCircle className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">{t('doctorDashboard.completedTotal')}</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-teal-100 rounded-lg flex items-center justify-center">
                      <Users className="w-5 h-5 text-teal-600" />
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">{t('doctorDashboard.totalPatients')}</p>
                      <p className="text-2xl font-bold text-gray-900">{stats.totalPatients}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Today's Appointments */}
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-blue-600" />
                  {t('doctorDashboard.todaySchedule')}
                </h3>

                {todayAppointments.length > 0 ? (
                  <div className="space-y-3">
                    {todayAppointments.map((apt) => (
                      <div key={apt.appointment_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{apt.patient_name}</p>
                          <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                            <Clock className="w-4 h-4" />
                            {formatDateTime(apt.date_time)}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            apt.status === 'CONFIRMED' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                          }`}>
                            {apt.status}
                          </span>
                          {apt.status === 'CONFIRMED' && (
                            <button
                              onClick={() => handleCompleteAppointment(apt.appointment_id)}
                              className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title={t('appointments.complete')}
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">{t('doctorDashboard.noAppointmentsToday')}</p>
                )}
              </div>
            </div>
          ) : activeTab === 'appointments' ? (
            /* Appointments Tab */
            <div className="space-y-4 max-w-6xl mx-auto">
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <h3 className="font-semibold text-gray-900 mb-3">{t('doctorDashboard.upcomingAppointments')}</h3>
                
                {upcomingAppointments.length > 0 ? (
                  <div className="space-y-3">
                    {upcomingAppointments.map((apt) => (
                      <div key={apt.appointment_id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <p className="font-semibold text-gray-900">{apt.patient_name}</p>
                              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                                apt.status === 'CONFIRMED' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                              }`}>
                                {apt.status}
                              </span>
                            </div>
                            <p className="text-sm text-gray-500 mt-1">{apt.patient_email}</p>
                            {apt.patient_phone && (
                              <p className="text-sm text-gray-500 flex items-center gap-1">
                                📞 {apt.patient_phone}
                              </p>
                            )}
                            <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                              <span className="flex items-center gap-1">
                                <CalendarDays className="w-4 h-4" />
                                {formatDateTime(apt.date_time)}
                              </span>
                              <span className="flex items-center gap-1">
                                <Clock className="w-4 h-4" />
                                {apt.duration} min
                              </span>
                            </div>
                            {apt.notes && (
                              <p className="mt-2 text-sm text-gray-600 bg-yellow-50 p-2 rounded">{apt.notes}</p>
                            )}
                          </div>
                          
                          <div className="flex flex-col gap-2">
                            <button
                              onClick={() => viewPatientHistory(apt)}
                              className="px-3 py-1.5 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors flex items-center gap-1"
                            >
                              <History className="w-4 h-4" />
                              {t('appointments.viewHistory')}
                            </button>
                            
                            {apt.status === 'CONFIRMED' && (
                              <>
                                <button
                                  onClick={() => openPrescriptionModal(apt)}
                                  className="px-3 py-1.5 text-sm bg-purple-50 text-purple-600 rounded-lg hover:bg-purple-100 transition-colors flex items-center gap-1"
                                >
                                  <Pill className="w-4 h-4" />
                                  {t('appointments.addPrescription')}
                                </button>
                                
                                <button
                                  onClick={() => openRecordModal(apt)}
                                  className="px-3 py-1.5 text-sm bg-teal-50 text-teal-600 rounded-lg hover:bg-teal-100 transition-colors flex items-center gap-1"
                                >
                                  <FileText className="w-4 h-4" />
                                  {t('appointments.addMedicalRecord')}
                                </button>

                                <button
                                  onClick={() => openLabResultModal(apt)}
                                  className="px-3 py-1.5 text-sm bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors flex items-center gap-1"
                                >
                                  <Activity className="w-4 h-4" />
                                  {t('doctorDashboard.addLabResult')}
                                </button>
                                
                                <button
                                  onClick={() => handleCompleteAppointment(apt.appointment_id)}
                                  className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-1"
                                >
                                  <CheckCircle className="w-4 h-4" />
                                  {t('appointments.complete')}
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">{t('appointments.noAppointments')}</p>
                )}
              </div>
            </div>
          ) : activeTab === 'patients' ? (
            /* Patients Tab */
            <div className="space-y-4 max-w-6xl mx-auto">
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <h3 className="font-semibold text-gray-900 mb-3">{t('doctorDashboard.myPatients')}</h3>
                
                {/* Get unique patients */}
                {(() => {
                  const uniquePatients = Array.from(
                    new Map(appointments.map(apt => [apt.patient_id, apt])).values()
                  );
                  
                  return uniquePatients.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {uniquePatients.map((patient) => {
                        const patientAppointments = appointments.filter(apt => apt.patient_id === patient.patient_id);
                        const completedCount = patientAppointments.filter(apt => apt.status === 'COMPLETED').length;
                        
                        return (
                          <div key={patient.patient_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <p className="font-semibold text-gray-900">{patient.patient_name}</p>
                                <p className="text-sm text-gray-500">{patient.patient_email}</p>
                                {patient.patient_phone && (
                                  <p className="text-sm text-gray-500">📞 {patient.patient_phone}</p>
                                )}
                                <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
                                  <span>{completedCount} {t('appointments.completed')}</span>
                                  <span>{patientAppointments.length} {t('doctorDashboard.totalVisits')}</span>
                                </div>
                              </div>
                              <button
                                onClick={() => viewPatientHistory(patient)}
                                className="px-3 py-1.5 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                              >
                                {t('appointments.viewHistory')}
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">{t('doctorDashboard.noPatients')}</p>
                  );
                })()}
              </div>
            </div>
          ) : (
            /* Profile Tab */
            <div className="max-w-2xl mx-auto space-y-4">
              <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
                <h3 className="text-base font-semibold text-gray-900">{t('doctors.profileSettings')}</h3>
              </div>

              <form onSubmit={handleSaveProfile} className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.name')}</label>
                    <input
                      type="text"
                      value={profileForm.name}
                      onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.phone')}</label>
                    <input
                      type="tel"
                      value={profileForm.phone}
                      onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('doctors.specialty')}</label>
                    <input
                      type="text"
                      value={profileForm.specialty}
                      onChange={(e) => setProfileForm({ ...profileForm, specialty: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('doctors.consultationDuration')}</label>
                    <input
                      type="number"
                      value={profileForm.consultation_duration}
                      onChange={(e) => setProfileForm({ ...profileForm, consultation_duration: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('doctors.consultationFee')}</label>
                    <input
                      type="number"
                      value={profileForm.consultation_fee}
                      onChange={(e) => setProfileForm({ ...profileForm, consultation_fee: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('doctors.bio')}</label>
                  <textarea
                    value={profileForm.bio}
                    onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  />
                </div>

                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={savingProfile}
                    className="px-6 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center gap-2"
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
                </div>
              </form>
            </div>
          )}
        </div>
      </main>

      {/* Add Prescription Modal */}
      {showPrescriptionModal && selectedPatient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white">
              <h2 className="font-semibold text-gray-900">{t('appointments.createPrescription')}</h2>
              <button onClick={() => setShowPrescriptionModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="font-medium text-blue-900">{selectedPatient.patient_name}</p>
                <p className="text-sm text-blue-700">{formatDateTime(selectedPatient.date_time)}</p>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">{t('appointments.medications')}</label>
                  <button
                    onClick={handleAddMedication}
                    className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                  >
                    <Plus className="w-4 h-4" />
                    {t('appointments.addMedication')}
                  </button>
                </div>

                {prescriptionForm.medications.map((med, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-3 mb-3">
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Medication {index + 1}</span>
                      {prescriptionForm.medications.length > 1 && (
                        <button
                          onClick={() => handleRemoveMedication(index)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="text"
                        placeholder={t('appointments.medicationName')}
                        value={med.name}
                        onChange={(e) => handleMedicationChange(index, 'name', e.target.value)}
                        className="col-span-2 px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <input
                        type="text"
                        placeholder={t('appointments.dosage')}
                        value={med.dosage}
                        onChange={(e) => handleMedicationChange(index, 'dosage', e.target.value)}
                        className="px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <input
                        type="text"
                        placeholder={t('appointments.frequency')}
                        value={med.frequency}
                        onChange={(e) => handleMedicationChange(index, 'frequency', e.target.value)}
                        className="px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <input
                        type="text"
                        placeholder={t('appointments.duration')}
                        value={med.duration}
                        onChange={(e) => handleMedicationChange(index, 'duration', e.target.value)}
                        className="col-span-2 px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('appointments.prescriptionNotes')}</label>
                <textarea
                  value={prescriptionForm.notes}
                  onChange={(e) => setPrescriptionForm({ ...prescriptionForm, notes: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowPrescriptionModal(false)}
                  className="flex-1 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={handleSavePrescription}
                  disabled={savingPrescription}
                  className="flex-1 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {savingPrescription && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t('common.save')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Medical Record Modal */}
      {showRecordModal && selectedPatient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white">
              <h2 className="font-semibold text-gray-900">{t('appointments.createMedicalRecord')}</h2>
              <button onClick={() => setShowRecordModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="font-medium text-blue-900">{selectedPatient.patient_name}</p>
                <p className="text-sm text-blue-700">{formatDateTime(selectedPatient.date_time)}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('appointments.recordType')}</label>
                <select
                  value={recordForm.record_type}
                  onChange={(e) => setRecordForm({ ...recordForm, record_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="RECOMMENDATION">{t('appointments.recommendation')}</option>
                  <option value="LETTER">{t('appointments.letter')}</option>
                  <option value="NOTE">{t('appointments.note')}</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('appointments.recordTitle')}</label>
                <input
                  type="text"
                  value={recordForm.title}
                  onChange={(e) => setRecordForm({ ...recordForm, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('appointments.recordContent')}</label>
                <textarea
                  value={recordForm.content}
                  onChange={(e) => setRecordForm({ ...recordForm, content: e.target.value })}
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowRecordModal(false)}
                  className="flex-1 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={handleSaveRecord}
                  disabled={savingRecord}
                  className="flex-1 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {savingRecord && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t('common.save')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add Lab Result Modal */}
      {showLabResultModal && selectedPatient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white">
              <h2 className="font-semibold text-gray-900">{t('doctorDashboard.addLabResult')}</h2>
              <button onClick={() => setShowLabResultModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="font-medium text-blue-900">{selectedPatient.patient_name}</p>
                <p className="text-sm text-blue-700">{selectedPatient.patient_email}</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('doctorDashboard.testName')}</label>
                  <input
                    type="text"
                    value={labResultForm.test_name}
                    onChange={(e) => setLabResultForm({ ...labResultForm, test_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('doctorDashboard.testCategory')}</label>
                  <select
                    value={labResultForm.test_category}
                    onChange={(e) => setLabResultForm({ ...labResultForm, test_category: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="blood_test">Blood Test</option>
                    <option value="urine_test">Urine Test</option>
                    <option value="imaging">Imaging</option>
                    <option value="biopsy">Biopsy</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('healthStats.result')}</label>
                  <input
                    type="text"
                    value={labResultForm.result_value}
                    onChange={(e) => setLabResultForm({ ...labResultForm, result_value: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
                  <input
                    type="text"
                    value={labResultForm.result_unit}
                    onChange={(e) => setLabResultForm({ ...labResultForm, result_unit: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('healthStats.normalRange')}</label>
                  <input
                    type="text"
                    value={labResultForm.reference_range}
                    onChange={(e) => setLabResultForm({ ...labResultForm, reference_range: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select
                    value={labResultForm.status}
                    onChange={(e) => setLabResultForm({ ...labResultForm, status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="PENDING">Pending</option>
                    <option value="COMPLETED">Completed</option>
                    <option value="ABNORMAL">Abnormal</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('healthStats.laboratory')}</label>
                  <input
                    type="text"
                    value={labResultForm.lab_name}
                    onChange={(e) => setLabResultForm({ ...labResultForm, lab_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('healthStats.testDate')}</label>
                  <input
                    type="date"
                    value={labResultForm.test_date}
                    onChange={(e) => setLabResultForm({ ...labResultForm, test_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('healthStats.interpretation')}</label>
                <textarea
                  value={labResultForm.interpretation}
                  onChange={(e) => setLabResultForm({ ...labResultForm, interpretation: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('healthStats.notes')}</label>
                <textarea
                  value={labResultForm.notes}
                  onChange={(e) => setLabResultForm({ ...labResultForm, notes: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowLabResultModal(false)}
                  className="flex-1 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={handleSaveLabResult}
                  disabled={savingLabResult}
                  className="flex-1 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {savingLabResult && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t('common.save')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Patient History Modal */}
      {showPatientHistoryModal && selectedPatient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white">
              <h2 className="font-semibold text-gray-900">{t('appointments.patientHistory')}</h2>
              <button onClick={() => setShowPatientHistoryModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              {historyLoading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                </div>
              ) : patientHistory ? (
                <>
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h3 className="font-semibold text-blue-900">{patientHistory.patient?.name}</h3>
                    <p className="text-sm text-blue-700">{patientHistory.patient?.email}</p>
                    {patientHistory.patient?.phone && (
                      <p className="text-sm text-blue-700">📞 {patientHistory.patient.phone}</p>
                    )}
                  </div>

                  {/* Previous Appointments */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">{t('appointments.previousAppointments')}</h3>
                    {patientHistory.appointments?.length > 0 ? (
                      <div className="space-y-2">
                        {patientHistory.appointments.map((apt) => (
                          <div key={apt.appointment_id} className="bg-gray-50 rounded-lg p-3">
                            <p className="font-medium text-gray-900">{formatDateTime(apt.date_time)}</p>
                            <p className="text-sm text-gray-600">Dr. {apt.doctor_name} - {apt.doctor_specialty}</p>
                            {apt.notes && <p className="text-sm text-gray-500 mt-1">{apt.notes}</p>}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">{t('appointments.noHistory')}</p>
                    )}
                  </div>

                  {/* Prescriptions */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">{t('appointments.prescriptions')}</h3>
                    {patientHistory.prescriptions?.length > 0 ? (
                      <div className="space-y-2">
                        {patientHistory.prescriptions.map((presc) => (
                          <div key={presc.prescription_id} className="bg-purple-50 rounded-lg p-3">
                            <p className="text-sm text-gray-600 mb-2">{formatDate(presc.created_at)}</p>
                            {presc.medications?.map((med, idx) => (
                              <div key={idx} className="text-sm">
                                <span className="font-medium">{med.name}</span> - {med.dosage} ({med.frequency})
                              </div>
                            ))}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">{t('appointments.noPrescriptions')}</p>
                    )}
                  </div>

                  {/* Medical Records */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">{t('appointments.medicalRecords')}</h3>
                    {patientHistory.medical_records?.length > 0 ? (
                      <div className="space-y-2">
                        {patientHistory.medical_records.map((record) => (
                          <div key={record.record_id} className="bg-teal-50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium text-teal-900">{record.title}</span>
                              <span className="text-xs text-teal-600">{record.record_type}</span>
                            </div>
                            <p className="text-sm text-gray-600">{record.content}</p>
                            <p className="text-xs text-gray-400 mt-1">{formatDate(record.created_at)}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">{t('appointments.noRecords')}</p>
                    )}
                  </div>
                </>
              ) : (
                <p className="text-gray-500 text-center py-8">{t('appointments.historyError')}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DoctorDashboard;
