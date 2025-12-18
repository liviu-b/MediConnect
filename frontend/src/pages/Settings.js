import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useAuth, api } from '../App';
import {
  Building2,
  MapPin,
  Phone,
  Mail,
  Clock,
  Settings as SettingsIcon,
  Loader2,
  Save,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const DAYS_OF_WEEK = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

const Settings = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const location = useLocation();
  const isNewClinic = location.state?.isNewClinic;
  const [clinic, setClinic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState({
    name: '',
    address: '',
    phone: '',
    email: '',
    description: '',
    working_hours: {
      monday: { start: '09:00', end: '17:00', closed: false },
      tuesday: { start: '09:00', end: '17:00', closed: false },
      wednesday: { start: '09:00', end: '17:00', closed: false },
      thursday: { start: '09:00', end: '17:00', closed: false },
      friday: { start: '09:00', end: '17:00', closed: false },
      saturday: { start: '10:00', end: '14:00', closed: false },
      sunday: { start: '10:00', end: '14:00', closed: true }
    },
    settings: {
      allow_online_booking: true,
      booking_advance_days: 30,
      cancellation_hours: 24
    }
  });

  useEffect(() => {
    if (user?.clinic_id) {
      fetchClinic();
    }
  }, [user]);

  const fetchClinic = async () => {
    try {
      const res = await api.get(`/clinics/${user.clinic_id}`);
      setClinic(res.data);
      
      // Parse working hours from backend format
      const workingHours = {};
      DAYS_OF_WEEK.forEach(day => {
        const dayData = res.data.working_hours?.[day];
        if (dayData === null || dayData === undefined) {
          workingHours[day] = { start: '09:00', end: '17:00', closed: true };
        } else {
          workingHours[day] = {
            start: dayData.start || '09:00',
            end: dayData.end || '17:00',
            closed: false
          };
        }
      });
      
      setForm({
        name: res.data.name || '',
        address: res.data.address || '',
        phone: res.data.phone || '',
        email: res.data.email || '',
        description: res.data.description || '',
        working_hours: workingHours,
        settings: res.data.settings || {
          allow_online_booking: true,
          booking_advance_days: 30,
          cancellation_hours: 24
        }
      });
    } catch (err) {
      console.error('Error fetching clinic:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    try {
      // Convert working hours to backend format (null for closed days)
      const workingHoursForBackend = {};
      DAYS_OF_WEEK.forEach(day => {
        if (form.working_hours[day].closed) {
          workingHoursForBackend[day] = null;
        } else {
          workingHoursForBackend[day] = {
            start: form.working_hours[day].start,
            end: form.working_hours[day].end
          };
        }
      });
      
      const payload = {
        ...form,
        working_hours: workingHoursForBackend
      };
      
      const res = await api.put(`/clinics/${user.clinic_id}`, payload);
      setClinic(res.data);
      setSaved(true);
      // Keep the success message visible for 3 seconds
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Error updating clinic:', err);
      alert(t('notifications.error'));
    } finally {
      setSaving(false);
    }
  };

  const updateWorkingHours = (day, field, value) => {
    setForm(prev => ({
      ...prev,
      working_hours: {
        ...prev.working_hours,
        [day]: {
          ...prev.working_hours[day],
          [field]: value
        }
      }
    }));
  };

  const isProfileIncomplete = !clinic?.name || !clinic?.address;

  if (user?.role !== 'CLINIC_ADMIN') {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">{t('auth.noPermission')}</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-4 max-w-2xl">
      {/* Welcome Banner for New Clinics */}
      {(isNewClinic || isProfileIncomplete) && (
        <div className="bg-gradient-to-r from-teal-500 to-blue-500 rounded-xl p-4 text-white">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 flex-shrink-0 mt-0.5" />
            <div>
              <h2 className="font-bold text-lg">{t('settings.welcomeTitle')}</h2>
              <p className="text-white/90 text-sm mt-1">{t('settings.welcomeMessage')}</p>
            </div>
          </div>
        </div>
      )}

      {/* CUI Display */}
      {clinic?.cui && (
        <div className="bg-gray-50 rounded-xl border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">{t('auth.cui')}</p>
              <p className="text-lg font-mono font-bold text-gray-900">{clinic.cui}</p>
            </div>
            <div className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
              {t('settings.verified')}
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-gray-900">{t('clinics.clinicSettings')}</h1>
        <p className="text-sm text-gray-500">{t('clinics.myClinic')}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Clinic Info */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
          <div className="flex items-center gap-2 text-gray-700 font-medium mb-2">
            <Building2 className="w-5 h-5" />
            <span>{t('clinics.title')}</span>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('clinics.clinicName')} <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                !form.name && isProfileIncomplete ? 'border-orange-300 bg-orange-50' : 'border-gray-200'
              }`}
              placeholder={t('settings.enterClinicName')}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('clinics.address')} <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                required
                value={form.address}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
                className={`w-full pl-9 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  !form.address && isProfileIncomplete ? 'border-orange-300 bg-orange-50' : 'border-gray-200'
                }`}
                placeholder={t('settings.enterAddress')}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('clinics.phone')}</label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="tel"
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('clinics.email')}</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('clinics.description')}</label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={2}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>
        </div>

        {/* Operating Hours */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
          <div className="flex items-center gap-2 text-gray-700 font-medium mb-2">
            <Clock className="w-5 h-5" />
            <span>{t('settings.operatingHours')}</span>
          </div>
          <p className="text-xs text-gray-500 mb-3">{t('settings.operatingHoursHelp')}</p>
          
          <div className="space-y-2">
            {DAYS_OF_WEEK.map((day) => (
              <div key={day} className="flex items-center gap-3 py-2 border-b border-gray-100 last:border-0">
                <div className="w-24 flex-shrink-0">
                  <span className="text-sm font-medium text-gray-700 capitalize">{t(`days.${day}`)}</span>
                </div>
                <div className="flex items-center gap-2 flex-1">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.working_hours[day].closed}
                      onChange={(e) => updateWorkingHours(day, 'closed', e.target.checked)}
                      className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-500">{t('settings.closed')}</span>
                  </label>
                </div>
                {!form.working_hours[day].closed && (
                  <div className="flex items-center gap-2">
                    <input
                      type="time"
                      value={form.working_hours[day].start}
                      onChange={(e) => updateWorkingHours(day, 'start', e.target.value)}
                      className="px-2 py-1 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <span className="text-gray-400">-</span>
                    <input
                      type="time"
                      value={form.working_hours[day].end}
                      onChange={(e) => updateWorkingHours(day, 'end', e.target.value)}
                      className="px-2 py-1 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                )}
                {form.working_hours[day].closed && (
                  <span className="text-sm text-gray-400 italic">{t('settings.closedDay')}</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Booking Settings */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
          <div className="flex items-center gap-2 text-gray-700 font-medium mb-2">
            <SettingsIcon className="w-5 h-5" />
            <span>{t('nav.settings')}</span>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">{t('clinics.allowOnlineBooking')}</p>
              <p className="text-xs text-gray-500">{t('settings.allowBookingHelp')}</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={form.settings.allow_online_booking}
                onChange={(e) => setForm({
                  ...form,
                  settings: { ...form.settings, allow_online_booking: e.target.checked }
                })}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('clinics.bookingAdvanceDays')}</label>
              <input
                type="number"
                min="1"
                max="365"
                value={form.settings.booking_advance_days}
                onChange={(e) => setForm({
                  ...form,
                  settings: { ...form.settings, booking_advance_days: parseInt(e.target.value) }
                })}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('clinics.cancellationHours')}</label>
              <input
                type="number"
                min="0"
                max="168"
                value={form.settings.cancellation_hours}
                onChange={(e) => setForm({
                  ...form,
                  settings: { ...form.settings, cancellation_hours: parseInt(e.target.value) }
                })}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Success Message */}
        {saved && (
          <div className="p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            {t('settings.changesSavedSuccessfully')}
          </div>
        )}

        {/* Save Button */}
        <button
          type="submit"
          disabled={saving}
          className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {saving ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : saved ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <Save className="w-5 h-5" />
          )}
          {saved ? t('notifications.saveSuccess') : t('common.save')}
        </button>
      </form>
    </div>
  );
};

export default Settings;