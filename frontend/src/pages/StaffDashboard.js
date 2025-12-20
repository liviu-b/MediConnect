import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
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
  Clock,
  LogOut,
  Menu,
  X,
  Loader2,
  CalendarDays,
  Settings,
  Save,
  CheckCircle,
  AlertCircle,
  XCircle,
  History,
  ChevronDown,
  FileText,
  Pill,
  Plus,
  User,
  Users,
  BarChart3,
  Stethoscope,
  DollarSign,
  Image as ImageIcon
} from 'lucide-react';

const DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

const specialtyKeys = [
  'anesthesiology',
  'cardiology',
  'dentistry',
  'dermatology',
  'emergencyMedicine',
  'endocrinology',
  'gastroenterology',
  'generalPractice',
  'generalSurgery',
  'geriatrics',
  'gynecology',
  'hematology',
  'immunology',
  'medicalTests',
  'infectiousDisease',
  'nephrology',
  'neurology',
  'obstetrics',
  'oncology',
  'ophthalmology',
  'orthopedics',
  'otolaryngology',
  'pediatrics',
  'plasticSurgery',
  'psychiatry',
  'pulmonology',
  'radiology',
  'rheumatology',
  'sportsMedicine',
  'urology',
];

const CURRENCIES = [
  { code: 'LEI', symbol: 'LEI' },
  { code: 'EURO', symbol: '€' }
];

const StaffDashboard = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const calendarRef = useRef(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('calendar');
  const [loading, setLoading] = useState(true);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  
  // Profile editing
  const [editingProfile, setEditingProfile] = useState(false);
  const [profileForm, setProfileForm] = useState({});
  const [savingProfile, setSavingProfile] = useState(false);

  // Doctor data
  const [doctor, setDoctor] = useState(null);
  const [clinicHours, setClinicHours] = useState(null);

  // Availability editing
  const [availability, setAvailability] = useState({});
  const [savingAvailability, setSavingAvailability] = useState(false);
  const [availabilitySaved, setAvailabilitySaved] = useState(false);

  // Appointments data
  const [appointments, setAppointments] = useState([]);
  const [appointmentsLoading, setAppointmentsLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showColleagueAppointments, setShowColleagueAppointments] = useState(true);
  const [cancelingId, setCancelingId] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelAppointment, setCancelAppointment] = useState(null);
  const [cancelReason, setCancelReason] = useState('');
  const [cancelError, setCancelError] = useState('');

  // Prescription and Medical Record states
  const [showPrescriptionModal, setShowPrescriptionModal] = useState(false);
  const [showMedicalRecordModal, setShowMedicalRecordModal] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [medications, setMedications] = useState([{ name: '', dosage: '', frequency: '', duration: '' }]);
  const [prescriptionNotes, setPrescriptionNotes] = useState('');
  const [recordType, setRecordType] = useState('RECOMMENDATION');
  const [recordTitle, setRecordTitle] = useState('');
  const [recordContent, setRecordContent] = useState('');
  const [savingDocument, setSavingDocument] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (activeTab === 'appointments') {
      fetchAppointments();
    }
  }, [activeTab]);

  // Initialize profile form when doctor data loads or tab changes to profile
  useEffect(() => {
    if (doctor && activeTab === 'profile') {
      setProfileForm({
        phone: doctor.phone || '',
        specialty: doctor.specialty || '',
        bio: doctor.bio || '',
        picture: doctor.picture || '',
        consultation_duration: doctor.consultation_duration || 30,
        consultation_fee: doctor.consultation_fee || 0,
        currency: doctor.currency || 'LEI'
      });
    }
  }, [doctor, activeTab]);

  const fetchData = async () => {
    try {
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

      // Fetch appointments for calendar
      await fetchAppointments();
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAppointments = async () => {
    setAppointmentsLoading(true);
    try {
      const res = await api.get('/appointments');
      setAppointments(res.data);
    } catch (err) {
      console.error('Error fetching appointments:', err);
    } finally {
      setAppointmentsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout');
      navigate('/auth/already-registered', { replace: true });
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/auth/already-registered', { replace: true });
    }
  };

  const getRoleLabel = (role) => {
    const roleMap = {
      'DOCTOR': t('staff.doctor'),
      'ASSISTANT': t('staff.assistant'),
      'NURSE': t('staff.nurse'),
      'RECEPTIONIST': t('staff.receptionist')
    };
    return roleMap[role] || role;
  };

  // Availability management
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

  // Profile management
  const handleSaveProfile = async () => {
    if (!doctor) return;

    setSavingProfile(true);
    try {
      await api.put(`/doctors/${doctor.doctor_id}`, profileForm);
      alert(t('doctors.profileUpdated') || 'Profile updated successfully!');
      fetchData(); // Refresh doctor data
    } catch (err) {
      console.error('Error saving profile:', err);
      alert(err.response?.data?.detail || 'Error saving profile');
    } finally {
      setSavingProfile(false);
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

  // Appointment management
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

    setCancelingId(cancelAppointment.appointment_id);
    try {
      await api.post(`/appointments/${cancelAppointment.appointment_id}/cancel`, {
        reason: cancelReason.trim()
      });
      setShowCancelModal(false);
      setCancelAppointment(null);
      fetchAppointments();
    } catch (err) {
      console.error('Error canceling appointment:', err);
      setCancelError(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setCancelingId(null);
    }
  };

  const handleAcceptAppointment = async (id) => {
    try {
      await api.put(`/appointments/${id}`, {
        status: 'CONFIRMED'
      });
      fetchAppointments();
    } catch (err) {
      console.error('Error accepting appointment:', err);
      alert(t('notifications.error'));
    }
  };

  const openPrescriptionModal = (apt) => {
    setSelectedAppointment(apt);
    setMedications([{ name: '', dosage: '', frequency: '', duration: '' }]);
    setPrescriptionNotes('');
    setShowPrescriptionModal(true);
  };

  const openMedicalRecordModal = (apt) => {
    setSelectedAppointment(apt);
    setRecordType('RECOMMENDATION');
    setRecordTitle('');
    setRecordContent('');
    setShowMedicalRecordModal(true);
  };

  const addMedication = () => {
    setMedications([...medications, { name: '', dosage: '', frequency: '', duration: '' }]);
  };

  const updateMedication = (index, field, value) => {
    const updated = [...medications];
    updated[index][field] = value;
    setMedications(updated);
  };

  const removeMedication = (index) => {
    setMedications(medications.filter((_, i) => i !== index));
  };

  const handleCreatePrescription = async () => {
    if (!selectedAppointment) return;

    const validMedications = medications.filter(m => m.name && m.dosage);
    if (validMedications.length === 0) {
      alert('Please add at least one medication');
      return;
    }

    setSavingDocument(true);
    try {
      await api.post('/prescriptions', {
        appointment_id: selectedAppointment.appointment_id,
        medications: validMedications,
        notes: prescriptionNotes || null
      });
      alert(t('appointments.prescriptionSuccess'));
      setShowPrescriptionModal(false);
      fetchAppointments();
    } catch (err) {
      console.error('Error creating prescription:', err);
      alert(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setSavingDocument(false);
    }
  };

  const handleCreateMedicalRecord = async () => {
    if (!selectedAppointment || !recordTitle || !recordContent) {
      alert('Please fill in all required fields');
      return;
    }

    setSavingDocument(true);
    try {
      await api.post('/medical-records', {
        appointment_id: selectedAppointment.appointment_id,
        record_type: recordType,
        title: recordTitle,
        content: recordContent
      });
      alert(t('appointments.recordSuccess'));
      setShowMedicalRecordModal(false);
      fetchAppointments();
    } catch (err) {
      console.error('Error creating medical record:', err);
      alert(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setSavingDocument(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'SCHEDULED': return 'bg-blue-100 text-blue-700';
      case 'CONFIRMED': return 'bg-green-100 text-green-700';
      case 'COMPLETED': return 'bg-gray-100 text-gray-700';
      case 'CANCELLED': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getRowBackground = (status, isOwnPatient) => {
    if (isOwnPatient === false) {
      // Colleague's patient
      return 'bg-gray-50 border-gray-300';
    }
    if (status === 'CONFIRMED' || status === 'ACCEPTED') {
      return 'bg-green-100 border-green-300';
    }
    return 'bg-white border-gray-200';
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const filteredAppointments = appointments.filter(apt => {
    const matchesSearch = !search ||
      apt.patient_name?.toLowerCase().includes(search.toLowerCase()) ||
      apt.doctor_name?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'all' || apt.status === statusFilter;
    const matchesColleagueFilter = showColleagueAppointments || apt.is_own_patient !== false;
    return matchesSearch && matchesStatus && matchesColleagueFilter;
  });

  const statusCounts = {
    all: appointments.length,
    SCHEDULED: appointments.filter(a => a.status === 'SCHEDULED').length,
    CONFIRMED: appointments.filter(a => a.status === 'CONFIRMED').length,
    COMPLETED: appointments.filter(a => a.status === 'COMPLETED').length,
    CANCELLED: appointments.filter(a => a.status === 'CANCELLED').length
  };

  // Calendar events with colleague appointments
  const calendarEvents = appointments
    .filter(apt => {
      if (apt.status === 'CANCELLED') return false;
      // Filter out colleague appointments if toggle is off
      if (!showColleagueAppointments && apt.is_own_patient === false) return false;
      return true;
    })
    .map(apt => {
      const isOwnPatient = apt.is_own_patient !== false; // Default to true if not set

      let bgColor = '#3B82F6'; // Default blue
      let borderColor = 'transparent';

      if (!isOwnPatient) {
        // Colleague's patient - light gray with border
        bgColor = '#E5E7EB'; // Light gray
        borderColor = '#9CA3AF'; // Gray border
      } else if (apt.status === 'CONFIRMED' || apt.status === 'ACCEPTED') {
        bgColor = '#22C55E'; // Green for confirmed
      } else if (apt.status === 'COMPLETED') {
        bgColor = '#9CA3AF'; // Gray for completed
      }

      return {
        id: apt.appointment_id,
        title: isOwnPatient ? apt.patient_name : `${apt.doctor_name.split(' ')[0]} - ${apt.patient_name}`,
        start: apt.date_time,
        backgroundColor: bgColor,
        borderColor: borderColor,
        textColor: !isOwnPatient ? '#374151' : 'white',
        extendedProps: {
          isOwnPatient,
          doctorName: apt.doctor_name,
          patientName: apt.patient_name
        }
      };
    });

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
            <Link to="/staff-dashboard" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
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
              onClick={() => setActiveTab('calendar')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${activeTab === 'calendar'
                ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              <Calendar className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('nav.calendar')}</span>
            </button>

            <button
              onClick={() => setActiveTab('appointments')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${activeTab === 'appointments'
                ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                : 'text-gray-600 hover:bg-gray-100'
                }`}
            >
              <CalendarDays className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-medium">{t('nav.appointments')}</span>
            </button>

            {user?.role === 'DOCTOR' && (
              <>
                <button
                  onClick={() => setActiveTab('profile')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${activeTab === 'profile'
                    ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                    }`}
                >
                  <User className="w-5 h-5 flex-shrink-0" />
                  <span className="text-sm font-medium">{t('doctors.profileSettings') || 'Profile Settings'}</span>
                </button>

                <button
                  onClick={() => setActiveTab('availability')}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${activeTab === 'availability'
                    ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                    }`}
                >
                  <Clock className="w-5 h-5 flex-shrink-0" />
                  <span className="text-sm font-medium">{t('staffDashboard.myAvailability')}</span>
                </button>
              </>
            )}
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
                {activeTab === 'calendar' ? t('nav.calendar') :
                  activeTab === 'appointments' ? t('nav.appointments') :
                  activeTab === 'profile' ? (t('doctors.profileSettings') || 'Profile Settings') :
                    t('staffDashboard.myAvailability')}
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
                    <p className="text-xs text-gray-500">{getRoleLabel(user?.role)}</p>
                  </div>
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                </button>

                {userDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                      <p className="text-xs text-gray-500">{user?.email}</p>
                      <p className="text-xs text-blue-600 mt-1">{getRoleLabel(user?.role)}</p>
                    </div>
                    {user?.role === 'DOCTOR' && (
                      <button
                        onClick={() => {
                          setActiveTab('profile');
                          setUserDropdownOpen(false);
                        }}
                        className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                      >
                        <User className="w-4 h-4" />
                        {t('doctors.profileSettings') || 'Profile Settings'}
                      </button>
                    )}
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
          ) : activeTab === 'calendar' ? (
            /* Calendar Tab */
            <div className="space-y-4">
              {/* Calendar Controls */}
              {user?.role === 'DOCTOR' && (
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-gray-700">
                        {t('staffDashboard.viewOptions') || 'Opțiuni Vizualizare'}
                      </span>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={showColleagueAppointments}
                          onChange={(e) => setShowColleagueAppointments(e.target.checked)}
                          className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-600">
                          {t('staffDashboard.showColleagues') || 'Arată programări colegi'}
                        </span>
                      </label>
                    </div>
                    <div className="flex items-center gap-4 text-xs">
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-green-500 rounded"></div>
                        <span className="text-gray-600">{t('staffDashboard.myPatients') || 'Pacienții mei'}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-gray-300 border-2 border-gray-400 rounded"></div>
                        <span className="text-gray-600">{t('staffDashboard.colleaguePatients') || 'Pacienți colegi'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <FullCalendar
                  ref={calendarRef}
                  plugins={[dayGridPlugin, interactionPlugin]}
                  initialView="dayGridMonth"
                  events={calendarEvents}
                  locale={i18n.language === 'ro' ? roLocale : enLocale}
                  headerToolbar={{
                    left: 'prev,next today',
                    center: 'title',
                    right: ''
                  }}
                  height="auto"
                  dayMaxEvents={3}
                  eventMouseEnter={(info) => {
                    // Tooltip on hover
                    const { extendedProps } = info.event;
                    if (extendedProps && !extendedProps.isOwnPatient) {
                      info.el.title = `Dr. ${extendedProps.doctorName} - ${extendedProps.patientName}`;
                    }
                  }}
                />
              </div>
            </div>
          ) : activeTab === 'appointments' ? (
            /* Appointments Tab */
            <div className="space-y-4">
              {/* Filters */}
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder={t('appointments.searchPlaceholder')}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="flex gap-2 overflow-x-auto pb-1">
                  {['all', 'SCHEDULED', 'CONFIRMED', 'COMPLETED', 'CANCELLED'].map((status) => (
                    <button
                      key={status}
                      onClick={() => setStatusFilter(status)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${statusFilter === status
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                    >
                      {status === 'all' ? t('appointments.all') : t(`appointments.${status.toLowerCase()}`)} ({statusCounts[status]})
                    </button>
                  ))}
                </div>
              </div>

              {/* Appointments List */}
              {appointmentsLoading ? (
                <div className="flex justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                </div>
              ) : filteredAppointments.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
                  <CalendarDays className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                  <p className="text-gray-500">{t('appointments.noAppointments')}</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredAppointments.map((apt) => (
                    <div
                      key={apt.appointment_id}
                      className={`rounded-xl border p-4 ${getRowBackground(apt.status, apt.is_own_patient)}`}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-3 min-w-0 flex-1">
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${apt.status === 'CONFIRMED' ? 'bg-green-200 text-green-700' : 'bg-blue-100 text-blue-600'
                            }`}>
                            <CalendarDays className="w-5 h-5" />
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2">
                              <p className="font-semibold text-gray-900">{apt.patient_name}</p>
                              {apt.is_own_patient === false && (
                                <span className="px-2 py-0.5 bg-gray-200 text-gray-600 text-xs rounded-full">
                                  {t('appointments.colleaguePatient')}
                                </span>
                              )}
                            </div>
                            {apt.patient_email && <p className="text-sm text-gray-500">{apt.patient_email}</p>}
                            <p className="text-sm text-blue-600">Dr. {apt.doctor_name}</p>
                            <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                              <span className="flex items-center gap-1">
                                <CalendarDays className="w-4 h-4" />
                                {formatDate(apt.date_time)}
                              </span>
                              <span className="flex items-center gap-1">
                                <Clock className="w-4 h-4" />
                                {apt.duration} min
                              </span>
                            </div>
                            {apt.notes && (
                              <p className="mt-2 text-sm text-gray-600 bg-gray-50 p-2 rounded-lg">
                                {apt.notes}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(apt.status)}`}>
                            {t(`appointments.${apt.status.toLowerCase()}`)}
                          </span>
                          <div className="flex gap-1 flex-wrap">
                            {/* Accept/Reject for SCHEDULED appointments */}
                            {apt.status === 'SCHEDULED' && (
                              <>
                                <button
                                  onClick={() => handleAcceptAppointment(apt.appointment_id)}
                                  className="p-1.5 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                                  title={t('appointments.acceptAppointment')}
                                >
                                  <CheckCircle className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => openCancelModal(apt)}
                                  className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                  title={t('appointments.rejectAppointment')}
                                >
                                  <XCircle className="w-4 h-4" />
                                </button>
                              </>
                            )}
                            {/* Add Prescription & Medical Record for CONFIRMED/COMPLETED */}
                            {(apt.status === 'CONFIRMED' || apt.status === 'COMPLETED') && user?.role === 'DOCTOR' && (
                              <>
                                <button
                                  onClick={() => openPrescriptionModal(apt)}
                                  className="p-1.5 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                                  title={t('appointments.addPrescription')}
                                >
                                  <Pill className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => openMedicalRecordModal(apt)}
                                  className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                  title={t('appointments.addMedicalRecord')}
                                >
                                  <FileText className="w-4 h-4" />
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : activeTab === 'profile' ? (
            /* Profile Settings Tab (Doctors Only) */
            <div className="space-y-4 max-w-3xl">
              <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-6">
                {/* Personal Information - Read Only */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
                    <User className="w-5 h-5 text-blue-600" />
                    {t('doctors.personalInfo') || 'Personal Information'}
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('common.name') || 'Name'}
                      </label>
                      <input
                        type="text"
                        value={user?.name || ''}
                        disabled
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('common.email') || 'Email'}
                      </label>
                      <input
                        type="email"
                        value={user?.email || ''}
                        disabled
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
                      />
                    </div>
                  </div>
                </div>

                {/* Contact Information */}
                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
                    <User className="w-5 h-5 text-blue-600" />
                    {t('doctors.contactInfo') || 'Contact Information'}
                  </h3>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('doctors.phone') || 'Phone Number'}
                    </label>
                    <input
                      type="tel"
                      value={profileForm.phone || ''}
                      onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                      placeholder="+40 XXX XXX XXX"
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Professional Information */}
                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
                    <Stethoscope className="w-5 h-5 text-blue-600" />
                    {t('doctors.professionalInfo') || 'Professional Information'}
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('doctors.specialty') || 'Specialty'}
                      </label>
                      <select
                        value={profileForm.specialty || ''}
                        onChange={(e) => setProfileForm({ ...profileForm, specialty: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">{t('doctors.selectSpecialty') || 'Select specialty'}</option>
                        {specialtyKeys.map((key) => (
                          <option key={key} value={key}>
                            {t(`specialties.${key}`) || key}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('doctors.bio') || 'Bio / Description'}
                      </label>
                      <textarea
                        value={profileForm.bio || ''}
                        onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                        rows={4}
                        placeholder={t('doctors.bioPlaceholder') || 'Tell patients about your experience, education, and approach to care...'}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        <span className="flex items-center gap-2">
                          <ImageIcon className="w-4 h-4" />
                          {t('doctors.profilePicture') || 'Profile Picture URL'}
                        </span>
                      </label>
                      <input
                        type="url"
                        value={profileForm.picture || ''}
                        onChange={(e) => setProfileForm({ ...profileForm, picture: e.target.value })}
                        placeholder="https://example.com/photo.jpg"
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                {/* Consultation Settings */}
                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
                    <Clock className="w-5 h-5 text-blue-600" />
                    {t('doctors.consultationSettings') || 'Consultation Settings'}
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('doctors.consultationDuration') || 'Duration (minutes)'}
                      </label>
                      <select
                        value={profileForm.consultation_duration || 30}
                        onChange={(e) => setProfileForm({ ...profileForm, consultation_duration: parseInt(e.target.value) })}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value={15}>15 min</option>
                        <option value={20}>20 min</option>
                        <option value={30}>30 min</option>
                        <option value={45}>45 min</option>
                        <option value={60}>60 min</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('doctors.consultationFee') || 'Consultation Fee'}
                      </label>
                      <input
                        type="number"
                        value={profileForm.consultation_fee || 0}
                        onChange={(e) => setProfileForm({ ...profileForm, consultation_fee: parseFloat(e.target.value) || 0 })}
                        min="0"
                        step="10"
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('doctors.currency') || 'Currency'}
                      </label>
                      <select
                        value={profileForm.currency || 'LEI'}
                        onChange={(e) => setProfileForm({ ...profileForm, currency: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        {CURRENCIES.map((curr) => (
                          <option key={curr.code} value={curr.code}>
                            {curr.symbol}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="border-t border-gray-200 pt-6 flex gap-3">
                  <button
                    onClick={() => {
                      // Reset form to original doctor data
                      if (doctor) {
                        setProfileForm({
                          phone: doctor.phone || '',
                          specialty: doctor.specialty || '',
                          bio: doctor.bio || '',
                          picture: doctor.picture || '',
                          consultation_duration: doctor.consultation_duration || 30,
                          consultation_fee: doctor.consultation_fee || 0,
                          currency: doctor.currency || 'LEI'
                        });
                      }
                    }}
                    className="px-6 py-2.5 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                  >
                    {t('common.cancel') || 'Cancel'}
                  </button>
                  <button
                    onClick={handleSaveProfile}
                    disabled={savingProfile}
                    className="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {savingProfile ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Save className="w-5 h-5" />
                    )}
                    {t('doctors.saveProfile') || 'Save Profile'}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* Availability Tab (Doctors Only) */
            <div className="space-y-4 max-w-2xl">
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm text-blue-800">{t('staffDashboard.availabilityInfo')}</p>
                  </div>
                </div>
              </div>

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
                                step="900"
                                pattern="[0-9]{2}:[0-9]{2}"
                                required
                              />
                              <span className="text-gray-400">-</span>
                              <input
                                type="time"
                                value={period.end || '17:00'}
                                onChange={(e) => updateAvailability(day, index, 'end', e.target.value)}
                                className="px-2 py-1 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                step="900"
                                pattern="[0-9]{2}:[0-9]{2}"
                                required
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

      {/* Prescription Modal */}
      {showPrescriptionModal && selectedAppointment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white">
              <div className="flex items-center gap-2 text-purple-600">
                <Pill className="w-5 h-5" />
                <h2 className="font-semibold">{t('appointments.createPrescription')}</h2>
              </div>
              <button onClick={() => setShowPrescriptionModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="text-sm font-medium text-gray-700">{t('appointments.patient')}: {selectedAppointment.patient_name}</p>
                <p className="text-xs text-gray-500">{formatDate(selectedAppointment.date_time)}</p>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">{t('appointments.medications')}</label>
                  <button
                    onClick={addMedication}
                    className="flex items-center gap-1 text-xs text-blue-600 hover:underline"
                  >
                    <Plus className="w-3 h-3" />
                    {t('appointments.addMedication')}
                  </button>
                </div>

                <div className="space-y-3">
                  {medications.map((med, index) => (
                    <div key={index} className="p-3 bg-gray-50 rounded-lg space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Medicament {index + 1}</span>
                        {medications.length > 1 && (
                          <button
                            onClick={() => removeMedication(index)}
                            className="text-xs text-red-600 hover:underline"
                          >
                            {t('appointments.remove')}
                          </button>
                        )}
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <input
                          type="text"
                          placeholder={t('appointments.medicationName')}
                          value={med.name}
                          onChange={(e) => updateMedication(index, 'name', e.target.value)}
                          className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        />
                        <input
                          type="text"
                          placeholder={t('appointments.dosage')}
                          value={med.dosage}
                          onChange={(e) => updateMedication(index, 'dosage', e.target.value)}
                          className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        />
                        <input
                          type="text"
                          placeholder={t('appointments.frequency')}
                          value={med.frequency}
                          onChange={(e) => updateMedication(index, 'frequency', e.target.value)}
                          className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        />
                        <input
                          type="text"
                          placeholder={t('appointments.duration')}
                          value={med.duration}
                          onChange={(e) => updateMedication(index, 'duration', e.target.value)}
                          className="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('appointments.prescriptionNotes')}</label>
                <textarea
                  value={prescriptionNotes}
                  onChange={(e) => setPrescriptionNotes(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                  placeholder="Note adiționale..."
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setShowPrescriptionModal(false)}
                  className="flex-1 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={handleCreatePrescription}
                  disabled={savingDocument}
                  className="flex-1 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {savingDocument && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t('common.save')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Medical Record Modal */}
      {showMedicalRecordModal && selectedAppointment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 animate-fadeIn">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white">
              <div className="flex items-center gap-2 text-blue-600">
                <FileText className="w-5 h-5" />
                <h2 className="font-semibold">{t('appointments.createMedicalRecord')}</h2>
              </div>
              <button onClick={() => setShowMedicalRecordModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="text-sm font-medium text-gray-700">{t('appointments.patient')}: {selectedAppointment.patient_name}</p>
                <p className="text-xs text-gray-500">{formatDate(selectedAppointment.date_time)}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('appointments.recordType')}</label>
                <select
                  value={recordType}
                  onChange={(e) => setRecordType(e.target.value)}
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
                  value={recordTitle}
                  onChange={(e) => setRecordTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="ex. Recomandare tratament, Scrisoare medicală..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('appointments.recordContent')}</label>
                <textarea
                  value={recordContent}
                  onChange={(e) => setRecordContent(e.target.value)}
                  rows={8}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  placeholder="Introduceți conținutul documentului medical..."
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setShowMedicalRecordModal(false)}
                  className="flex-1 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={handleCreateMedicalRecord}
                  disabled={savingDocument}
                  className="flex-1 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {savingDocument && <Loader2 className="w-4 h-4 animate-spin" />}
                  {t('common.save')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cancellation Modal */}
      {showCancelModal && cancelAppointment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
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
                  <span className="font-medium">{t('appointments.patient')}:</span> {cancelAppointment.patient_name}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">{t('appointments.title')}:</span> {formatDate(cancelAppointment.date_time)}
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
                  disabled={cancelingId}
                  className="flex-1 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {cancelingId && <Loader2 className="w-4 h-4 animate-spin" />}
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

export default StaffDashboard;