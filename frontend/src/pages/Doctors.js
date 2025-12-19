import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import {
  Plus,
  Trash2,
  Edit2,
  Stethoscope,
  Mail,
  Phone,
  Clock,
  Loader2,
  X,
  Euro,
  Coins,
  UserCog
} from 'lucide-react';

// Specialty keys for translation
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

const Doctors = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState(null);
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    specialty: '',
    bio: '',
    consultation_duration: 30,
    consultation_fee: 0,
    currency: 'LEI'
  });
  const [saving, setSaving] = useState(false);

  const isClinicAdmin = user?.role === 'CLINIC_ADMIN';
  const isSuperAdmin = user?.role === 'SUPER_ADMIN';
  const canManageDoctors = isClinicAdmin || isSuperAdmin;

  useEffect(() => {
    fetchDoctors();
  }, []);

  // Listen for location changes
  useEffect(() => {
    const handleLocationChange = () => {
      fetchDoctors(); // Refresh doctors when location changes
    };
    
    window.addEventListener('locationChanged', handleLocationChange);
    return () => window.removeEventListener('locationChanged', handleLocationChange);
  }, []);

  const fetchDoctors = async () => {
    try {
      const res = await api.get('/doctors');
      setDoctors(res.data);
    } catch (err) {
      console.error('Error fetching doctors:', err);
    } finally {
      setLoading(false);
    }
  };

  const openModal = (doctor = null) => {
    if (doctor) {
      setEditingDoctor(doctor);
      setForm({
        name: doctor.name,
        email: doctor.email,
        phone: doctor.phone || '',
        specialty: doctor.specialty,
        bio: doctor.bio || '',
        consultation_duration: doctor.consultation_duration,
        consultation_fee: doctor.consultation_fee,
        currency: doctor.currency || 'LEI'
      });
    } else {
      setEditingDoctor(null);
      setForm({
        name: '',
        email: '',
        phone: '',
        specialty: '',
        bio: '',
        consultation_duration: 30,
        consultation_fee: 0,
        currency: 'LEI'
      });
    }
    setShowModal(true);
  };
  
  const getCurrencySymbol = (currency) => {
    const curr = CURRENCIES.find(c => c.code === currency);
    return curr ? curr.symbol : currency;
  };

  const formatPrice = (price, currency) => {
    const symbol = getCurrencySymbol(currency);
    if (currency === 'LEI') {
      return `${price.toFixed(2)} ${symbol}`;
    }
    return `${symbol}${price.toFixed(2)}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingDoctor) {
        await api.put(`/doctors/${editingDoctor.doctor_id}`, form);
      } else {
        await api.post('/doctors', form);
      }
      setShowModal(false);
      fetchDoctors();
    } catch (err) {
      console.error('Error saving doctor:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (doctorId) => {
    if (!window.confirm(t('doctors.deleteConfirm'))) return;
    try {
      await api.delete(`/doctors/${doctorId}`);
      fetchDoctors();
    } catch (err) {
      console.error('Error deleting doctor:', err);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('doctors.title')}</h1>
          <p className="text-sm text-gray-500">
            {t('doctors.viewSubtitle') || 'View and manage doctor profiles. To add a new doctor, go to Staff section and send an invitation.'}
          </p>
        </div>
      </div>

      {/* Info Banner */}
      {canManageDoctors && doctors.length === 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Stethoscope className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-medium text-blue-900 mb-1">
                {t('doctors.noDoctorsYet') || 'No doctors yet'}
              </h3>
              <p className="text-sm text-blue-700 mb-3">
                {t('doctors.inviteInstructions') || 'To add doctors to your medical center, go to the Staff section and invite them. They will receive an email to set up their profile.'}
              </p>
              <button
                onClick={() => navigate('/staff')}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-sm"
              >
                <UserCog className="w-4 h-4" />
                {t('doctors.goToStaff') || 'Go to Staff Section'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Doctors Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : doctors.length > 0 && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
          {doctors.map((doctor) => (
            <div key={doctor.doctor_id} className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-teal-400 flex items-center justify-center text-white font-bold text-lg">
                    {doctor.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Dr. {doctor.name}</h3>
                    <p className="text-sm text-blue-600">{t(`specialties.${doctor.specialty}`) || doctor.specialty}</p>
                  </div>
                </div>
                {canManageDoctors && (
                  <div className="flex gap-1">
                    <button
                      onClick={() => openModal(doctor)}
                      className="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(doctor.doctor_id)}
                      className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
              <div className="mt-3 space-y-1 text-sm text-gray-500">
                <p className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  {doctor.email}
                </p>
                {doctor.phone && (
                  <p className="flex items-center gap-2">
                    <Phone className="w-4 h-4" />
                    {doctor.phone}
                  </p>
                )}
              </div>
              <div className="mt-3 flex items-center gap-4 text-sm">
                <span className="flex items-center gap-1 text-gray-500">
                  <Clock className="w-4 h-4" />
                  {t('doctors.consultation', { duration: doctor.consultation_duration })}
                </span>
                <span className="text-green-600 font-medium">
                  {formatPrice(doctor.consultation_fee, doctor.currency || 'LEI')}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Doctor Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white">
              <h2 className="font-semibold text-gray-900">
                {editingDoctor ? t('doctors.editDoctor') : t('doctors.addNewDoctor')}
              </h2>
              <button onClick={() => setShowModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-4 space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('doctors.doctorName')}</label>
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.email')}</label>
                <input
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.phone')}</label>
                <input
                  type="tel"
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('doctors.specialty')}</label>
                <select
                  required
                  value={form.specialty}
                  onChange={(e) => setForm({ ...form, specialty: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">{t('doctors.selectSpecialty')}</option>
                  {specialtyKeys.map((key) => (
                    <option key={key} value={key}>{t(`specialties.${key}`)}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('doctors.consultationDuration')}</label>
                <input
                  type="number"
                  min="5"
                  step="5"
                  value={form.consultation_duration}
                  onChange={(e) => setForm({ ...form, consultation_duration: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('doctors.consultationFee')}</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={form.consultation_fee}
                    onChange={(e) => setForm({ ...form, consultation_fee: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('services.currency')}</label>
                  <select
                    value={form.currency}
                    onChange={(e) => setForm({ ...form, currency: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {CURRENCIES.map((currency) => (
                      <option key={currency.code} value={currency.code}>
                        {currency.code} ({currency.symbol})
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('doctors.bio')}</label>
                <textarea
                  value={form.bio}
                  onChange={(e) => setForm({ ...form, bio: e.target.value })}
                  rows={2}
                  placeholder={t('doctors.bioPlaceholder')}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                >
                  {t('common.cancel')}
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                  {editingDoctor ? t('doctors.updateDoctor') : t('common.save')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Doctors;