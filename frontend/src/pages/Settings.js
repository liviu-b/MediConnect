import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
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
  CheckCircle
} from 'lucide-react';

const Settings = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
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
      setForm({
        name: res.data.name || '',
        address: res.data.address || '',
        phone: res.data.phone || '',
        email: res.data.email || '',
        description: res.data.description || '',
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
      await api.put(`/clinics/${user.clinic_id}`, form);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Error updating clinic:', err);
    } finally {
      setSaving(false);
    }
  };

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
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('clinics.clinicName')}</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('clinics.address')}</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={form.address}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
                className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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

        {/* Booking Settings */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-3">
          <div className="flex items-center gap-2 text-gray-700 font-medium mb-2">
            <SettingsIcon className="w-5 h-5" />
            <span>{t('nav.settings')}</span>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">{t('clinics.allowOnlineBooking')}</p>
              <p className="text-xs text-gray-500">Allow patients to book online</p>
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
