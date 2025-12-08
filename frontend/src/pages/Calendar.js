import { useState, useEffect, useRef } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import listPlugin from '@fullcalendar/list';
import { useTranslation } from 'react-i18next';
import { api, useAuth } from '../App';

const Calendar = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const calendarRef = useRef(null);
  const [appointments, setAppointments] = useState([]);
  const [clinics, setClinics] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [selectedClinic, setSelectedClinic] = useState('');
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [notes, setNotes] = useState('');
  const [recurrence, setRecurrence] = useState('NONE');
  const [recurrenceEndDate, setRecurrenceEndDate] = useState('');

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (selectedClinic) {
      fetchDoctors();
    }
  }, [selectedClinic]);

  useEffect(() => {
    if (selectedDoctor && selectedSlot) {
      fetchAvailability();
    }
  }, [selectedDoctor, selectedSlot]);

  const fetchInitialData = async () => {
    try {
      const [appointmentsRes, clinicsRes] = await Promise.all([
        api.get('/appointments'),
        api.get('/clinics')
      ]);
      setAppointments(appointmentsRes.data);
      setClinics(clinicsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDoctors = async () => {
    try {
      const response = await api.get(`/doctors?clinic_id=${selectedClinic}`);
      setDoctors(response.data);
    } catch (error) {
      console.error('Error fetching doctors:', error);
    }
  };

  const fetchAvailability = async () => {
    if (!selectedDoctor || !selectedSlot) return;
    
    const dateStr = selectedSlot.toISOString().split('T')[0];
    try {
      const response = await api.get(`/doctors/${selectedDoctor}/availability?date=${dateStr}`);
      setAvailableSlots(response.data.available_slots || []);
    } catch (error) {
      console.error('Error fetching availability:', error);
      setAvailableSlots([]);
    }
  };

  const handleDateClick = (info) => {
    setSelectedSlot(info.date);
    setShowBookingModal(true);
    setAvailableSlots([]);
    setNotes('');
    setRecurrence('NONE');
    setRecurrenceEndDate('');
  };

  const handleEventClick = (info) => {
    const appointment = appointments.find(apt => apt.appointment_id === info.event.id);
    if (appointment) {
      const locale = i18n.language === 'ro' ? 'ro-RO' : 'en-US';
      alert(`${t('appointments.title')}: ${appointment.doctor_name?.startsWith('Dr.') ? appointment.doctor_name : `Dr. ${appointment.doctor_name}`}\n${t('calendar.selectedDate')}: ${new Date(appointment.date_time).toLocaleString(locale)}\nStatus: ${appointment.status}`);
    }
  };

  const handleBookAppointment = async (slotTime) => {
    if (!selectedClinic || !selectedDoctor) {
      alert(t('calendar.selectFirst'));
      return;
    }

    setBookingLoading(true);
    try {
      const appointmentData = {
        doctor_id: selectedDoctor,
        clinic_id: selectedClinic,
        date_time: slotTime,
        notes: notes || null,
        recurrence: recurrence !== 'NONE' ? {
          pattern_type: recurrence,
          interval: 1,
          end_date: recurrenceEndDate || null
        } : null
      };

      await api.post('/appointments', appointmentData);
      
      // Refresh appointments
      const response = await api.get('/appointments');
      setAppointments(response.data);
      
      setShowBookingModal(false);
      alert(t('notifications.bookingSuccess'));
    } catch (error) {
      console.error('Error booking appointment:', error);
      alert(error.response?.data?.detail || t('notifications.bookingError'));
    } finally {
      setBookingLoading(false);
    }
  };

  const calendarEvents = appointments
    .filter(apt => apt.status !== 'CANCELLED')
    .map(apt => ({
      id: apt.appointment_id,
      title: apt.doctor_name?.startsWith('Dr.') ? apt.doctor_name : `Dr. ${apt.doctor_name}`,
      start: apt.date_time,
      end: new Date(new Date(apt.date_time).getTime() + apt.duration * 60000).toISOString(),
      backgroundColor: apt.status === 'CONFIRMED' ? '#10b981' : apt.status === 'COMPLETED' ? '#6366f1' : '#3b82f6',
      borderColor: 'transparent',
      extendedProps: { appointment: apt }
    }));

  const calendarLocale = i18n.language === 'ro' ? 'ro' : 'en';

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="calendar-page">
      {/* Filters */}
      <div className="bg-white rounded-2xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('calendar.selectClinicDoctor')}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('calendar.clinic')}</label>
            <select
              value={selectedClinic}
              onChange={(e) => {
                setSelectedClinic(e.target.value);
                setSelectedDoctor('');
              }}
              data-testid="clinic-select"
              className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">{t('calendar.selectClinic')}</option>
              {clinics.map(clinic => (
                <option key={clinic.clinic_id} value={clinic.clinic_id}>
                  {clinic.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">{t('calendar.doctor')}</label>
            <select
              value={selectedDoctor}
              onChange={(e) => setSelectedDoctor(e.target.value)}
              disabled={!selectedClinic}
              data-testid="doctor-select"
              className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">{t('calendar.selectDoctor')}</option>
              {doctors.map(doctor => (
                <option key={doctor.doctor_id} value={doctor.doctor_id}>
                  {doctor.name?.startsWith('Dr.') ? doctor.name : `Dr. ${doctor.name}`} - {doctor.specialty}
                </option>
              ))}
            </select>
          </div>
        </div>
        {selectedClinic && selectedDoctor && (
          <p className="mt-4 text-sm text-blue-600">
            {t('calendar.clickToBook')}
          </p>
        )}
      </div>

      {/* Calendar */}
      <div className="bg-white rounded-2xl p-6 shadow-sm">
        <FullCalendar
          ref={calendarRef}
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin]}
          initialView="dayGridMonth"
          locale={calendarLocale}
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
          }}
          events={calendarEvents}
          dateClick={handleDateClick}
          eventClick={handleEventClick}
          selectable={true}
          selectMirror={true}
          dayMaxEvents={3}
          weekends={true}
          height="auto"
          eventTimeFormat={{
            hour: '2-digit',
            minute: '2-digit',
            meridiem: 'short'
          }}
        />
      </div>

      {/* Booking Modal */}
      {showBookingModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center modal-backdrop" data-testid="booking-modal">
          <div className="bg-white rounded-2xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto animate-fadeIn">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-gray-900">
                {t('calendar.bookAppointment')}
              </h3>
              <button
                onClick={() => setShowBookingModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div className="bg-gray-50 rounded-xl p-4">
                <p className="text-sm text-gray-500">{t('calendar.selectedDate')}</p>
                <p className="font-semibold text-gray-900">
                  {selectedSlot?.toLocaleDateString(i18n.language === 'ro' ? 'ro-RO' : 'en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>

              {!selectedClinic || !selectedDoctor ? (
                <div className="text-center py-8">
                  <p className="text-gray-500">{t('calendar.selectFirst')}</p>
                </div>
              ) : (
                <>
                  {/* Notes */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">{t('calendar.notes')}</label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder={t('calendar.notesPlaceholder')}
                      data-testid="appointment-notes"
                      className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      rows={3}
                    />
                  </div>

                  {/* Recurrence */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">{t('calendar.recurringAppointment')}</label>
                    <select
                      value={recurrence}
                      onChange={(e) => setRecurrence(e.target.value)}
                      data-testid="recurrence-select"
                      className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="NONE">{t('calendar.noRecurrence')}</option>
                      <option value="DAILY">{t('calendar.daily')}</option>
                      <option value="WEEKLY">{t('calendar.weekly')}</option>
                      <option value="MONTHLY">{t('calendar.monthly')}</option>
                    </select>
                  </div>

                  {recurrence !== 'NONE' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">{t('calendar.recurrenceEndDate')}</label>
                      <input
                        type="date"
                        value={recurrenceEndDate}
                        onChange={(e) => setRecurrenceEndDate(e.target.value)}
                        data-testid="recurrence-end-date"
                        className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  )}

                  {/* Available Slots */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">{t('calendar.availableSlots')}</label>
                    {availableSlots.length === 0 ? (
                      <p className="text-gray-500 text-sm">{t('calendar.noSlots')}</p>
                    ) : (
                      <div className="grid grid-cols-3 gap-2 max-h-48 overflow-y-auto">
                        {availableSlots.map((slot) => (
                          <button
                            key={slot.time}
                            onClick={() => handleBookAppointment(slot.datetime)}
                            disabled={bookingLoading}
                            data-testid={`slot-${slot.time}`}
                            className="px-3 py-2 rounded-lg border border-blue-200 text-blue-600 hover:bg-blue-50 hover:border-blue-400 transition-all text-sm font-medium disabled:opacity-50"
                          >
                            {slot.time}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>

            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => setShowBookingModal(false)}
                className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                {t('common.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Calendar;
