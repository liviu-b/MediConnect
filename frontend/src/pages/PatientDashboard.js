import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import LanguageSwitcher from '../components/LanguageSwitcher';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import roLocale from '@fullcalendar/core/locales/ro';
import enLocale from '@fullcalendar/core/locales/en-gb';
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
  Cake,
  History,
  FileText,
  Pill,
  Download,
  X,
  Stethoscope,
  ChevronDown,
  ChevronUp,
  AlertCircle
} from 'lucide-react';

const PatientDashboard = () => {
  const { t, i18n } = useTranslation();
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const calendarRef = useRef(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  // Helper to capitalize first letter (for Romanian months)
  const formatDateCapitalized = (date) => {
    const formatted = date.toLocaleDateString(i18n.language === 'ro' ? 'ro-RO' : 'en-GB', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
    // Capitalize first letter of the string
    return formatted.charAt(0).toUpperCase() + formatted.slice(1);
  };

  // Dashboard data
  const [appointments, setAppointments] = useState([]);
  const [clinics, setClinics] = useState([]);
  const [clinicStats, setClinicStats] = useState({});

  // History data
  const [historyLoading, setHistoryLoading] = useState(false);
  const [prescriptions, setPrescriptions] = useState([]);
  const [medicalRecords, setMedicalRecords] = useState([]);
  const [expandedPrescription, setExpandedPrescription] = useState(null);
  const [expandedRecord, setExpandedRecord] = useState(null);

  // Cancellation modal
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelAppointment, setCancelAppointment] = useState(null);
  const [cancelReason, setCancelReason] = useState('');
  const [cancelError, setCancelError] = useState('');
  const [canceling, setCanceling] = useState(false);

  // Profile form
  const [profileForm, setProfileForm] = useState({
    name: '',
    phone: '',
    address: '',
    date_of_birth: ''
  });
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);

  // Calendar states
  const [selectedClinic, setSelectedClinic] = useState('');
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [doctors, setDoctors] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [booking, setBooking] = useState(false);
  const [notes, setNotes] = useState('');
  const [selectedSlot, setSelectedSlot] = useState(null);

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

  useEffect(() => {
    if (activeTab === 'history' && user) {
      fetchHistory();
    }
  }, [activeTab, user]);

  useEffect(() => {
    if (selectedClinic) {
      fetchDoctors(selectedClinic);
    } else {
      setDoctors([]);
      setSelectedDoctor('');
    }
  }, [selectedClinic]);

  useEffect(() => {
    if (selectedDoctor && selectedDate) {
      fetchAvailability();
    }
  }, [selectedDoctor, selectedDate]);

  const fetchData = async () => {
    try {
      const [appointmentsRes, clinicsRes] = await Promise.all([
        api.get('/appointments'),
        api.get('/clinics')
      ]);
      // Filter to show ONLY patient's own appointments
      const myAppointments = appointmentsRes.data.filter(apt => apt.patient_id === user?.user_id);
      setAppointments(myAppointments);
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

  const fetchHistory = async () => {
    if (!user?.user_id) return;
    setHistoryLoading(true);
    try {
      const res = await api.get(`/patients/${user.user_id}/history`);
      setPrescriptions(res.data.prescriptions || []);
      setMedicalRecords(res.data.medical_records || []);
    } catch (err) {
      console.error('Error fetching history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const fetchDoctors = async (clinicId) => {
    try {
      const res = await api.get(`/doctors?clinic_id=${clinicId}`);
      setDoctors(res.data);
    } catch (err) {
      console.error('Error fetching doctors:', err);
    }
  };

  const fetchAvailability = async () => {
    setLoadingSlots(true);
    try {
      const dateStr = selectedDate.toISOString().split('T')[0];
      const res = await api.get(`/doctors/${selectedDoctor}/availability?date=${dateStr}`);
      setAvailableSlots(res.data.available_slots || []);
    } catch (err) {
      console.error('Error fetching availability:', err);
      setAvailableSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  };

  const handleDateClick = (info) => {
    const clickedDate = new Date(info.dateStr);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (clickedDate < today) return;

    setSelectedDate(clickedDate);
    setSelectedSlot(null);
    if (selectedClinic && selectedDoctor) {
      setShowBookingModal(true);
    }
  };

  const handleBook = async () => {
    if (!selectedSlot) return;
    setBooking(true);
    try {
      await api.post('/appointments', {
        doctor_id: selectedDoctor,
        clinic_id: selectedClinic,
        date_time: selectedSlot.datetime,
        notes: notes || null
      });
      setShowBookingModal(false);
      setNotes('');
      setSelectedSlot(null);
      fetchData();
    } catch (err) {
      console.error('Error booking appointment:', err);
      alert(err.response?.data?.detail || t('notifications.bookingError'));
    } finally {
      setBooking(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout');
      navigate('/auth/login', { replace: true }); // Patient goes to login page
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/auth/login', { replace: true });
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

  const formatDateTime = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const openCancelModal = (apt) => {
    setCancelAppointment(apt);
    setCancelReason('');
    setCancelError('');
    setShowCancelModal(true);
  };

  const handleCancelWithReason = async () => {
    if (!cancelReason.trim() || cancelReason.trim().length < 3) {
      setCancelError(t('appointments.cancelReasonRequired'));
      return;
    }

    setCanceling(true);
    try {
      await api.post(`/appointments/${cancelAppointment.appointment_id}/cancel`, {
        reason: cancelReason.trim()
      });
      setShowCancelModal(false);
      setCancelAppointment(null);
      fetchData();
      alert(t('notifications.cancelSuccess'));
    } catch (err) {
      console.error('Error canceling appointment:', err);
      setCancelError(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setCanceling(false);
    }
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

  const completedAppointments = appointments
    .filter(apt => apt.status === 'COMPLETED');

  // Calendar events with color coding - GREEN for confirmed
  const calendarEvents = appointments
    .filter(apt => apt.status !== 'CANCELLED')
    .map(apt => {
      // Color coding: Stronger green for CONFIRMED appointments (better visibility)
      let bgColor = '#3B82F6'; // Default blue for scheduled
      let textColor = 'white';

      if (apt.status === 'CONFIRMED' || apt.status === 'ACCEPTED') {
        bgColor = '#22C55E'; // Stronger green for confirmed (better visibility)
        textColor = 'white';
      } else if (apt.status === 'COMPLETED') {
        bgColor = '#9CA3AF'; // Gray for completed
        textColor = 'white';
      }

      return {
        id: apt.appointment_id,
        title: `Dr. ${apt.doctor_name}`,
        start: apt.date_time,
        backgroundColor: bgColor,
        borderColor: 'transparent',
        textColor: textColor,
        extendedProps: {
          status: apt.status,
          specialty: apt.doctor_specialty
        }
      };
    });

  const generatePrescriptionPDF = (prescription) => {
    // Create a simple HTML representation for printing/downloading
    const doc = appointments.find(a => a.appointment_id === prescription.appointment_id);
    const doctorName = doc?.doctor_name || 'Doctor';

    const content = `
      <html>
        <head>
          <title>Prescription - ${formatDate(prescription.created_at)}</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 40px; }
            h1 { color: #0d9488; border-bottom: 2px solid #0d9488; padding-bottom: 10px; }
            .header { margin-bottom: 20px; }
            .med-item { background: #f3f4f6; padding: 15px; margin: 10px 0; border-radius: 8px; }
            .label { color: #6b7280; font-size: 12px; }
            .value { font-weight: bold; }
            .notes { margin-top: 20px; padding: 15px; background: #fef3c7; border-radius: 8px; }
          </style>
        </head>
        <body>
          <h1>Medical Prescription</h1>
          <div class="header">
            <p><span class="label">Date:</span> <span class="value">${formatDate(prescription.created_at)}</span></p>
            <p><span class="label">Doctor:</span> <span class="value">Dr. ${doctorName}</span></p>
          </div>
          <h2>Medications</h2>
          ${prescription.medications.map(med => `
            <div class="med-item">
              <p><span class="label">Medication:</span> <span class="value">${med.name}</span></p>
              <p><span class="label">Dosage:</span> ${med.dosage}</p>
              <p><span class="label">Frequency:</span> ${med.frequency}</p>
              <p><span class="label">Duration:</span> ${med.duration}</p>
            </div>
          `).join('')}
          ${prescription.notes ? `<div class="notes"><strong>Notes:</strong> ${prescription.notes}</div>` : ''}
        </body>
      </html>
    `;

    const blob = new Blob([content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `prescription_${prescription.prescription_id}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const generateRecordPDF = (record) => {
    const doc = appointments.find(a => a.appointment_id === record.appointment_id);
    const doctorName = doc?.doctor_name || 'Doctor';

    const content = `
      <html>
        <head>
          <title>${record.title} - ${formatDate(record.created_at)}</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 40px; }
            h1 { color: #0d9488; border-bottom: 2px solid #0d9488; padding-bottom: 10px; }
            .type { display: inline-block; background: #dbeafe; color: #1d4ed8; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin-bottom: 20px; }
            .header { margin-bottom: 20px; }
            .label { color: #6b7280; font-size: 12px; }
            .value { font-weight: bold; }
            .content { background: #f9fafb; padding: 20px; border-radius: 8px; white-space: pre-wrap; line-height: 1.6; }
          </style>
        </head>
        <body>
          <h1>${record.title}</h1>
          <span class="type">${record.record_type}</span>
          <div class="header">
            <p><span class="label">Date:</span> <span class="value">${formatDate(record.created_at)}</span></p>
            <p><span class="label">Doctor:</span> <span class="value">Dr. ${doctorName}</span></p>
          </div>
          <div class="content">${record.content}</div>
        </body>
      </html>
    `;

    const blob = new Blob([content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${record.record_type.toLowerCase()}_${record.record_id}.html`;
    a.click();
    URL.revokeObjectURL(url);
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
        className={`fixed lg:sticky top-0 h-screen bg-white border-r border-gray-200 z-50 transition-all duration-300 w-56 ${sidebarOpen ? 'left-0' : '-left-64 lg:left-0'
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
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${activeTab === 'dashboard'
                ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              <Calendar className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('nav.dashboard')}</span>
            </button>

            <button
              onClick={() => setActiveTab('calendar')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${activeTab === 'calendar'
                ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              <CalendarDays className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('patientDashboard.myCalendar')}</span>
            </button>

            <button
              onClick={() => setActiveTab('clinics')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${activeTab === 'clinics'
                ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              <Building2 className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('clinics.title')}</span>
            </button>

            <button
              onClick={() => setActiveTab('history')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${activeTab === 'history'
                ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              <History className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('patientDashboard.myHistory')}</span>
            </button>

            <button
              onClick={() => setActiveTab('profile')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${activeTab === 'profile'
                ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              <Settings className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('patientDashboard.profileSettings')}</span>
            </button>
          </nav>

          {/* Logout button only - profile moved to header */}
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
                {activeTab === 'dashboard' && t('patientDashboard.title')}
                {activeTab === 'calendar' && t('patientDashboard.myCalendar')}
                {activeTab === 'clinics' && t('clinics.title')}
                {activeTab === 'history' && t('patientDashboard.myHistory')}
                {activeTab === 'profile' && t('patientDashboard.profileSettings')}
              </h1>
            </div>
            <div className="flex items-center gap-3">
              <LanguageSwitcher compact />

              {/* User Profile - Always visible in top right */}
              <div className="relative">
                <button
                  onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                  className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  {user?.picture ? (
                    <img src={user.picture} alt={user?.name} className="w-8 h-8 rounded-full" />
                  ) : (
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-teal-500 rounded-full flex items-center justify-center text-white font-medium text-sm">
                      {user?.name?.charAt(0) || 'U'}
                    </div>
                  )}
                  <div className="hidden sm:block text-left">
                    <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                    <p className="text-xs text-gray-500">{t('patientDashboard.patient')}</p>
                  </div>
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                </button>

                {userDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                      <p className="text-xs text-gray-500">{user?.email}</p>
                      <p className="text-xs text-blue-600 mt-1">{t('patientDashboard.patient')}</p>
                    </div>
                    <button
                      onClick={() => setActiveTab('profile')}
                      className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      <Settings className="w-4 h-4" />
                      {t('patientDashboard.profileSettings')}
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
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">Dr. {apt.doctor_name}</p>
                          <p className="text-sm text-gray-500">{apt.doctor_specialty}</p>
                          <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                            <CalendarDays className="w-4 h-4" />
                            {formatDate(apt.date_time)}
                            <Clock className="w-4 h-4 ml-2" />
                            {apt.duration} min
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${apt.status === 'CONFIRMED' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                            }`}>
                            {apt.status === 'CONFIRMED' ? t('patientDashboard.confirmedAppointment') : t('patientDashboard.scheduledAppointment')}
                          </span>
                          {apt.status !== 'CANCELLED' && apt.status !== 'COMPLETED' && (
                            <button
                              onClick={() => openCancelModal(apt)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title={t('appointments.cancelAppointment')}
                            >
                              <X className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">{t('patientDashboard.noUpcoming')}</p>
                )}
              </div>
            </div>
          ) : activeTab === 'calendar' ? (
            /* Calendar Tab */
            <div className="space-y-4">
              {/* Filters */}
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <h2 className="font-medium text-gray-700 mb-3">{t('calendar.selectClinicDoctor')}</h2>
                <div className="grid sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">{t('calendar.clinic')}</label>
                    <select
                      value={selectedClinic}
                      onChange={(e) => setSelectedClinic(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">{t('calendar.selectClinic')}</option>
                      {clinics.map((clinic) => (
                        <option key={clinic.clinic_id} value={clinic.clinic_id}>
                          {clinic.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-500 mb-1">{t('calendar.doctor')}</label>
                    <select
                      value={selectedDoctor}
                      onChange={(e) => setSelectedDoctor(e.target.value)}
                      disabled={!selectedClinic}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                    >
                      <option value="">{t('calendar.selectDoctor')}</option>
                      {doctors.map((doctor) => (
                        <option key={doctor.doctor_id} value={doctor.doctor_id}>
                          Dr. {doctor.name} - {doctor.specialty}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                {!selectedClinic && (
                  <p className="mt-3 text-sm text-gray-500">{t('calendar.selectFirst')}</p>
                )}
                {selectedClinic && selectedDoctor && (
                  <p className="mt-3 text-sm text-blue-600">{t('calendar.clickToBook')}</p>
                )}
              </div>

              {/* Legend */}
              <div className="bg-white rounded-xl border border-gray-200 p-3">
                <div className="flex flex-wrap gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-green-500"></div>
                    <span className="text-gray-600">{t('patientDashboard.confirmedAppointment')}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-blue-500"></div>
                    <span className="text-gray-600">{t('patientDashboard.scheduledAppointment')}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-gray-400"></div>
                    <span className="text-gray-600">{t('appointments.completed')}</span>
                  </div>
                </div>
              </div>

              {/* Calendar */}
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <FullCalendar
                  ref={calendarRef}
                  plugins={[dayGridPlugin, interactionPlugin]}
                  initialView="dayGridMonth"
                  events={calendarEvents}
                  dateClick={handleDateClick}
                  locale={i18n.language === 'ro' ? roLocale : enLocale}
                  headerToolbar={{
                    left: 'prev,next today',
                    center: 'title',
                    right: ''
                  }}
                  height="auto"
                  dayMaxEvents={3}
                />
              </div>

              {/* Booking Modal */}
              {showBookingModal && selectedDate && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 animate-fadeIn">
                  <div className="bg-white rounded-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
                    <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white">
                      <h2 className="font-semibold text-gray-900">{t('calendar.bookAppointment')}</h2>
                      <button onClick={() => setShowBookingModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                        <X className="w-5 h-5 text-gray-500" />
                      </button>
                    </div>
                    <div className="p-4 space-y-4">
                      <div className="text-center py-3 bg-blue-50 rounded-lg">
                        <p className="text-sm text-gray-500">{t('calendar.selectedDate')}</p>
                        <p className="text-lg font-semibold text-blue-600">
                          {formatDateCapitalized(selectedDate)}
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">{t('calendar.availableSlots')}</label>
                        {loadingSlots ? (
                          <div className="flex justify-center py-4">
                            <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                          </div>
                        ) : availableSlots.length === 0 ? (
                          <p className="text-center py-4 text-gray-500">{t('calendar.noSlots')}</p>
                        ) : (
                          <div className="grid grid-cols-3 gap-2">
                            {availableSlots.map((slot) => (
                              <button
                                key={slot.time}
                                onClick={() => setSelectedSlot(slot)}
                                className={`py-2 px-3 rounded-lg text-sm font-medium transition-all ${selectedSlot?.time === slot.time
                                  ? 'bg-blue-600 text-white'
                                  : 'bg-gray-100 text-gray-700 hover:bg-blue-50 hover:text-blue-600'
                                  }`}
                              >
                                {slot.time}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">{t('calendar.notes')}</label>
                        <textarea
                          value={notes}
                          onChange={(e) => setNotes(e.target.value)}
                          rows={2}
                          placeholder={t('calendar.notesPlaceholder')}
                          className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        />
                      </div>

                      <div className="flex gap-3">
                        <button
                          onClick={() => setShowBookingModal(false)}
                          className="flex-1 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                        >
                          {t('common.cancel')}
                        </button>
                        <button
                          onClick={handleBook}
                          disabled={!selectedSlot || booking}
                          className="flex-1 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                          {booking && <Loader2 className="w-4 h-4 animate-spin" />}
                          {t('calendar.bookAppointment')}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
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
          ) : activeTab === 'history' ? (
            /* History Tab */
            <div className="space-y-6">
              <p className="text-sm text-gray-500">{t('patientDashboard.historySubtitle')}</p>

              {historyLoading ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                </div>
              ) : (
                <>
                  {/* Completed Appointments */}
                  <div className="bg-white rounded-xl border border-gray-200 p-4">
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      {t('patientDashboard.completedAppointments')}
                    </h3>

                    {completedAppointments.length > 0 ? (
                      <div className="space-y-3">
                        {completedAppointments.map((apt) => (
                          <div key={apt.appointment_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                                <Stethoscope className="w-5 h-5 text-green-600" />
                              </div>
                              <div>
                                <p className="font-medium text-gray-900">Dr. {apt.doctor_name}</p>
                                <p className="text-sm text-gray-500">{apt.doctor_specialty}</p>
                                <p className="text-xs text-gray-400">{formatDateTime(apt.date_time)}</p>
                              </div>
                            </div>
                            <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                              {t('appointments.completed')}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">{t('patientDashboard.noCompletedAppointments')}</p>
                    )}
                  </div>

                  {/* Prescriptions */}
                  <div className="bg-white rounded-xl border border-gray-200 p-4">
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Pill className="w-5 h-5 text-purple-600" />
                      {t('patientDashboard.prescriptionsReceived')}
                    </h3>

                    {prescriptions.length > 0 ? (
                      <div className="space-y-3">
                        {prescriptions.map((prescription) => {
                          const isExpanded = expandedPrescription === prescription.prescription_id;
                          const apt = appointments.find(a => a.appointment_id === prescription.appointment_id);

                          return (
                            <div key={prescription.prescription_id} className="border border-gray-200 rounded-lg overflow-hidden">
                              <button
                                onClick={() => setExpandedPrescription(isExpanded ? null : prescription.prescription_id)}
                                className="w-full flex items-center justify-between p-3 bg-purple-50 hover:bg-purple-100 transition-colors"
                              >
                                <div className="flex items-center gap-3">
                                  <FileText className="w-5 h-5 text-purple-600" />
                                  <div className="text-left">
                                    <p className="font-medium text-gray-900">
                                      {prescription.medications.length} {t('patientDashboard.medication')}(s)
                                    </p>
                                    <p className="text-sm text-gray-500">{formatDate(prescription.created_at)}</p>
                                  </div>
                                </div>
                                {isExpanded ? <ChevronUp className="w-5 h-5 text-gray-500" /> : <ChevronDown className="w-5 h-5 text-gray-500" />}
                              </button>

                              {isExpanded && (
                                <div className="p-4 space-y-3 bg-white">
                                  {apt && (
                                    <p className="text-sm text-gray-500">
                                      Dr. {apt.doctor_name} - {apt.doctor_specialty}
                                    </p>
                                  )}

                                  {prescription.medications.map((med, idx) => (
                                    <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                                      <p className="font-medium text-gray-900">{med.name}</p>
                                      <div className="grid grid-cols-3 gap-2 mt-2 text-sm">
                                        <div>
                                          <span className="text-gray-500">{t('patientDashboard.dosage')}:</span>
                                          <p className="font-medium">{med.dosage}</p>
                                        </div>
                                        <div>
                                          <span className="text-gray-500">{t('patientDashboard.frequency')}:</span>
                                          <p className="font-medium">{med.frequency}</p>
                                        </div>
                                        <div>
                                          <span className="text-gray-500">{t('patientDashboard.duration')}:</span>
                                          <p className="font-medium">{med.duration}</p>
                                        </div>
                                      </div>
                                    </div>
                                  ))}

                                  {prescription.notes && (
                                    <div className="p-3 bg-yellow-50 rounded-lg text-sm">
                                      <p className="text-gray-700">{prescription.notes}</p>
                                    </div>
                                  )}

                                  <button
                                    onClick={() => generatePrescriptionPDF(prescription)}
                                    className="flex items-center gap-2 px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                  >
                                    <Download className="w-4 h-4" />
                                    {t('patientDashboard.downloadPdf')}
                                  </button>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">{t('patientDashboard.noPrescriptions')}</p>
                    )}
                  </div>

                  {/* Medical Records / Recommendations */}
                  <div className="bg-white rounded-xl border border-gray-200 p-4">
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <FileText className="w-5 h-5 text-teal-600" />
                      {t('patientDashboard.recommendationsReceived')}
                    </h3>

                    {medicalRecords.length > 0 ? (
                      <div className="space-y-3">
                        {medicalRecords.map((record) => {
                          const isExpanded = expandedRecord === record.record_id;
                          const apt = appointments.find(a => a.appointment_id === record.appointment_id);

                          const typeColor = {
                            'RECOMMENDATION': 'bg-teal-50 text-teal-700',
                            'LETTER': 'bg-blue-50 text-blue-700',
                            'NOTE': 'bg-gray-100 text-gray-700'
                          }[record.record_type] || 'bg-gray-100 text-gray-700';

                          return (
                            <div key={record.record_id} className="border border-gray-200 rounded-lg overflow-hidden">
                              <button
                                onClick={() => setExpandedRecord(isExpanded ? null : record.record_id)}
                                className="w-full flex items-center justify-between p-3 bg-teal-50 hover:bg-teal-100 transition-colors"
                              >
                                <div className="flex items-center gap-3">
                                  <FileText className="w-5 h-5 text-teal-600" />
                                  <div className="text-left">
                                    <p className="font-medium text-gray-900">{record.title}</p>
                                    <div className="flex items-center gap-2 mt-1">
                                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${typeColor}`}>
                                        {record.record_type}
                                      </span>
                                      <span className="text-sm text-gray-500">{formatDate(record.created_at)}</span>
                                    </div>
                                  </div>
                                </div>
                                {isExpanded ? <ChevronUp className="w-5 h-5 text-gray-500" /> : <ChevronDown className="w-5 h-5 text-gray-500" />}
                              </button>

                              {isExpanded && (
                                <div className="p-4 space-y-3 bg-white">
                                  {apt && (
                                    <p className="text-sm text-gray-500">
                                      Dr. {apt.doctor_name} - {apt.doctor_specialty}
                                    </p>
                                  )}

                                  <div className="p-3 bg-gray-50 rounded-lg">
                                    <p className="text-gray-700 whitespace-pre-wrap">{record.content}</p>
                                  </div>

                                  <button
                                    onClick={() => generateRecordPDF(record)}
                                    className="flex items-center gap-2 px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                  >
                                    <Download className="w-4 h-4" />
                                    {t('patientDashboard.downloadPdf')}
                                  </button>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">{t('patientDashboard.noRecommendations')}</p>
                    )}
                  </div>
                </>
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

      {/* Cancellation Modal */}
      {showCancelModal && cancelAppointment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-white rounded-xl w-full max-w-md">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center gap-2 text-red-600">
                <AlertCircle className="w-5 h-5" />
                <h2 className="font-semibold">{t('appointments.cancelAppointment')}</h2>
              </div>
              <button onClick={() => setShowCancelModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">{t('calendar.doctor')}:</span> Dr. {cancelAppointment.doctor_name}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">{t('calendar.selectedDate')}:</span> {formatDateTime(cancelAppointment.date_time)}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('appointments.cancellationReason')} <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={cancelReason}
                  onChange={(e) => setCancelReason(e.target.value)}
                  rows={3}
                  placeholder={t('appointments.reasonPlaceholder')}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
                />
                <p className="text-xs text-gray-500 mt-1">{t('appointments.reasonHelp')}</p>
              </div>

              {cancelError && (
                <div className="p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                  {cancelError}
                </div>
              )}

              <div className="flex gap-3">
                <button
                  onClick={() => setShowCancelModal(false)}
                  className="flex-1 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                >
                  {t('appointments.keepAppointment')}
                </button>
                <button
                  onClick={handleCancelWithReason}
                  disabled={canceling}
                  className="flex-1 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {canceling && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t('appointments.yesCancel')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatientDashboard;