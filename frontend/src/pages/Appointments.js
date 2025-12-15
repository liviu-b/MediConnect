import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import {
  CalendarDays,
  Clock,
  Search,
  X,
  CheckCircle,
  XCircle,
  Loader2,
  FileText,
  User,
  AlertTriangle,
  History,
  Pill,
  FileEdit
} from 'lucide-react';

const Appointments = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [cancelingId, setCancelingId] = useState(null);

  // Cancellation modal state
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelAppointment, setCancelAppointment] = useState(null);
  const [cancelReason, setCancelReason] = useState('');
  const [cancelError, setCancelError] = useState('');

  // Patient history modal state
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [patientHistory, setPatientHistory] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [selectedAppointmentForHistory, setSelectedAppointmentForHistory] = useState(null);

  const isClinicAdmin = user?.role === 'CLINIC_ADMIN';
  const isDoctor = user?.role === 'DOCTOR';
  const isStaff = isClinicAdmin || isDoctor || user?.role === 'ASSISTANT';

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const res = await api.get('/appointments');
      setAppointments(res.data);
    } catch (err) {
      console.error('Error fetching appointments:', err);
    } finally {
      setLoading(false);
    }
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

  const handlePatientCancel = async (id) => {
    // Patients can cancel without reason
    setCancelingId(id);
    try {
      await api.delete(`/appointments/${id}`);
      fetchAppointments();
    } catch (err) {
      console.error('Error canceling appointment:', err);
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
  const viewPatientHistory = async (apt) => {
    setSelectedAppointmentForHistory(apt);
    setHistoryLoading(true);
    setShowHistoryModal(true);

    try {
      const res = await api.get(`/patients/${apt.patient_id}/history`);
      setPatientHistory(res.data);
    } catch (err) {
      console.error('Error fetching patient history:', err);
      setPatientHistory(null);
    } finally {
      setHistoryLoading(false);
    }
  };

  const closeHistoryModal = () => {
    setShowHistoryModal(false);
    setPatientHistory(null);
    setSelectedAppointmentForHistory(null);
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

  const getRowBackground = (status) => {
    if (status === 'CONFIRMED' || status === 'ACCEPTED') {
      return 'bg-green-50 border-green-200';
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
    return matchesSearch && matchesStatus;
  });

  const statusCounts = {
    all: appointments.length,
    SCHEDULED: appointments.filter(a => a.status === 'SCHEDULED').length,
    CONFIRMED: appointments.filter(a => a.status === 'CONFIRMED').length,
    COMPLETED: appointments.filter(a => a.status === 'COMPLETED').length,
    CANCELLED: appointments.filter(a => a.status === 'CANCELLED').length
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-gray-900">{t('appointments.title')}</h1>
        <p className="text-sm text-gray-500">{t('nav.appointments')}</p>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('appointments.searchPlaceholder')}
            className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
      {loading ? (
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
              className={`rounded-xl border p-4 ${getRowBackground(apt.status)}`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 min-w-0">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${apt.status === 'CONFIRMED' ? 'bg-green-200 text-green-700' : 'bg-blue-100 text-blue-600'
                    }`}>
                    <CalendarDays className="w-5 h-5" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-gray-900">
                        {isClinicAdmin || apt.is_own_patient ? apt.patient_name : `${apt.patient_name} (${t('appointments.colleaguePatient')})`}
                      </p>
                      {!apt.is_own_patient && (isDoctor || user?.role === 'ASSISTANT') && (
                        <span className="text-xs px-2 py-0.5 bg-gray-200 text-gray-600 rounded-full">{t('appointments.limitedView')}</span>
                      )}
                    </div>
                    {(isClinicAdmin || apt.is_own_patient) && apt.patient_email && (
                      <p className="text-sm text-gray-500">{apt.patient_email}</p>
                    )}
                    <p className="text-sm text-blue-600">{apt.doctor_specialty} - Dr. {apt.doctor_name}</p>
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
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(apt.status)}`}>
                    {t(`appointments.${apt.status.toLowerCase()}`)}
                  </span>
                  <div className="flex gap-1">
                    {/* Admin actions - Accept/Reject for SCHEDULED appointments */}
                    {isClinicAdmin && apt.status === 'SCHEDULED' && (
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

                    {/* View Patient History - Only for completed appointments and staff */}
                    {apt.status === 'COMPLETED' && (isClinicAdmin || (isDoctor && apt.is_own_patient)) && (
                      <button
                        onClick={() => viewPatientHistory(apt)}
                        className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title={t('appointments.viewHistory')}
                      >
                        <History className="w-4 h-4" />
                      </button>
                    )}
                    {!isClinicAdmin && apt.status !== 'CANCELLED' && apt.status !== 'COMPLETED' && (
                      <button
                        onClick={() => isStaff ? openCancelModal(apt) : handlePatientCancel(apt.appointment_id)}
                        disabled={cancelingId === apt.appointment_id}
                        className="p-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                        title={t('appointments.cancelAppointment')}
                      >
                        {cancelingId === apt.appointment_id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <XCircle className="w-4 h-4" />
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </div>
              {apt.notes && (isClinicAdmin || apt.is_own_patient) && (
                <p className="mt-3 text-sm text-gray-600 bg-gray-50 p-2 rounded-lg">
                  {apt.notes}
                </p>
              )}
              {apt.cancellation_reason && (
                <div className="mt-3 text-sm text-red-600 bg-red-50 p-2 rounded-lg flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-medium">{t('appointments.cancellationReason')}:</span> {apt.cancellation_reason}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Cancellation Modal with Reason (for Staff) */}
      {showCancelModal && cancelAppointment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-md">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center gap-2 text-red-600">
                <AlertTriangle className="w-5 h-5" />
                <h2 className="font-semibold">{t('appointments.cancelAppointment')}</h2>
              </div>
              <button onClick={() => setShowCancelModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              {/* Appointment Info */}
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">{t('appointments.patient')}:</span> {cancelAppointment.patient_name}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">{t('doctors.title')}:</span> Dr. {cancelAppointment.doctor_name}
                </p>
                <p className="text-sm text-gray-600">
                  <span className="font-medium">{t('appointments.title')}:</span> {formatDate(cancelAppointment.date_time)}
                </p>
              </div>

              {/* Reason Input */}
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

      {/* Patient History Modal */}
      {showHistoryModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center gap-2">
                <User className="w-5 h-5 text-blue-600" />
                <h2 className="font-semibold text-gray-900">{t('appointments.patientHistory')}</h2>
              </div>
              <button onClick={closeHistoryModal} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {historyLoading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                </div>
              ) : patientHistory ? (
                <>
                  {/* Patient Info */}
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h3 className="font-semibold text-blue-900">{patientHistory.patient?.name}</h3>
                    <p className="text-sm text-blue-700">{patientHistory.patient?.email}</p>
                    {patientHistory.patient?.phone && (
                      <p className="text-sm text-blue-700">{patientHistory.patient.phone}</p>
                    )}
                  </div>

                  {/* Previous Appointments */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                      <CalendarDays className="w-4 h-4 text-blue-600" />
                      {t('appointments.previousAppointments')} ({patientHistory.appointments?.length || 0})
                    </h3>
                    {patientHistory.appointments?.length > 0 ? (
                      <div className="space-y-2">
                        {patientHistory.appointments.map((apt) => (
                          <div key={apt.appointment_id} className="bg-gray-50 rounded-lg p-3">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium text-gray-900">{formatDate(apt.date_time)}</p>
                                <p className="text-sm text-gray-600">Dr. {apt.doctor_name} - {apt.doctor_specialty}</p>
                              </div>
                              <span className={`px-2 py-0.5 rounded-full text-xs ${getStatusColor(apt.status)}`}>
                                {apt.status}
                              </span>
                            </div>
                            {apt.notes && <p className="text-sm text-gray-500 mt-2">{apt.notes}</p>}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">{t('appointments.noHistory')}</p>
                    )}
                  </div>

                  {/* Prescriptions */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                      <Pill className="w-4 h-4 text-green-600" />
                      {t('appointments.prescriptions')} ({patientHistory.prescriptions?.length || 0})
                    </h3>
                    {patientHistory.prescriptions?.length > 0 ? (
                      <div className="space-y-2">
                        {patientHistory.prescriptions.map((presc) => (
                          <div key={presc.prescription_id} className="bg-green-50 rounded-lg p-3">
                            <p className="text-sm text-gray-600 mb-2">
                              {new Date(presc.created_at).toLocaleDateString()}
                            </p>
                            {presc.medications?.map((med, idx) => (
                              <div key={idx} className="text-sm">
                                <span className="font-medium">{med.name}</span>
                                {med.dosage && <span> - {med.dosage}</span>}
                                {med.frequency && <span> ({med.frequency})</span>}
                              </div>
                            ))}
                            {presc.notes && <p className="text-sm text-gray-500 mt-2 italic">{presc.notes}</p>}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm">{t('appointments.noPrescriptions')}</p>
                    )}
                  </div>

                  {/* Medical Records */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                      <FileEdit className="w-4 h-4 text-purple-600" />
                      {t('appointments.medicalRecords')} ({patientHistory.medical_records?.length || 0})
                    </h3>
                    {patientHistory.medical_records?.length > 0 ? (
                      <div className="space-y-2">
                        {patientHistory.medical_records.map((record) => (
                          <div key={record.record_id} className="bg-purple-50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="font-medium text-purple-900">{record.title}</span>
                              <span className="text-xs text-purple-600">{record.record_type}</span>
                            </div>
                            <p className="text-sm text-gray-600">{record.content}</p>
                            <p className="text-xs text-gray-400 mt-1">
                              {new Date(record.created_at).toLocaleDateString()}
                            </p>
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

            <div className="p-4 border-t border-gray-200">
              <button
                onClick={closeHistoryModal}
                className="w-full py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
              >
                {t('common.close')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Appointments;