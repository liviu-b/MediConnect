import { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import roLocale from '@fullcalendar/core/locales/ro';
import enLocale from '@fullcalendar/core/locales/en-gb';
import {
  Building2,
  Stethoscope,
  Clock,
  X,
  Loader2,
  ChevronDown
} from 'lucide-react';

const CalendarPage = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const calendarRef = useRef(null);
  const [clinics, setClinics] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [selectedClinic, setSelectedClinic] = useState('');
  const [selectedDoctor, setSelectedDoctor] = useState('');
  const [selectedDate, setSelectedDate] = useState(null);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [booking, setBooking] = useState(false);
  const [notes, setNotes] = useState('');
  const [selectedSlot, setSelectedSlot] = useState(null);

  const isClinicAdmin = user?.role === 'CLINIC_ADMIN';

  useEffect(() => {
    fetchInitialData();
  }, []);

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

  useEffect(() => {
    fetchAppointments();
  }, [selectedDoctor]);

  const fetchInitialData = async () => {
    try {
      const res = await api.get('/clinics');
      setClinics(res.data);
      // Auto-select clinic for clinic admin
      if (isClinicAdmin && user?.clinic_id) {
        setSelectedClinic(user.clinic_id);
      }
    } catch (err) {
      console.error('Error fetching clinics:', err);
    } finally {
      setLoading(false);
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

  const fetchAppointments = async () => {
    if (!selectedDoctor) return;
    try {
      const res = await api.get(`/appointments?doctor_id=${selectedDoctor}`);
      setAppointments(res.data);
    } catch (err) {
      console.error('Error fetching appointments:', err);
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
      fetchAppointments();
    } catch (err) {
      console.error('Error booking appointment:', err);
      alert(err.response?.data?.detail || t('notifications.bookingError'));
    } finally {
      setBooking(false);
    }
  };

  const calendarEvents = appointments
    .filter(apt => apt.status !== 'CANCELLED')
    .map(apt => {
      // Color coding: Light green for CONFIRMED/ACCEPTED appointments
      let bgColor = '#3B82F6'; // Default blue
      if (apt.status === 'CONFIRMED' || apt.status === 'ACCEPTED') {
        bgColor = '#59bb7dff'; // Light green for confirmed
      } else if (apt.status === 'COMPLETED') {
        bgColor = '#9CA3AF'; // Gray for completed
      }

      return {
        id: apt.appointment_id,
        title: isClinicAdmin ? apt.patient_name : `Dr. ${apt.doctor_name}`,
        start: apt.date_time,
        backgroundColor: bgColor,
        borderColor: 'transparent',
        textColor: apt.status === 'CONFIRMED' || apt.status === 'ACCEPTED' ? '#166534' : 'white'
      };
    });

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
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
              disabled={isClinicAdmin}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
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
                  Dr. {doctor.name} - {t(`specialties.${doctor.specialty}`, doctor.specialty)}
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
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
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
                  {selectedDate.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
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
  );
};

export default CalendarPage;