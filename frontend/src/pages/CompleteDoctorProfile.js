import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import {
  Stethoscope,
  Loader2,
  Clock,
  DollarSign,
  FileText,
  Image as ImageIcon,
  CheckCircle,
  Calendar
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

const CompleteDoctorProfile = () => {
  const { t } = useTranslation();
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [locationInfo, setLocationInfo] = useState(null);
  const [form, setForm] = useState({
    specialty: '',
    consultation_duration: 30,
    consultation_fee: 0,
    currency: 'LEI',
    bio: '',
    picture: ''
  });

  useEffect(() => {
    checkProfileStatus();
  }, []);

  const checkProfileStatus = async () => {
    try {
      // Check if user is a doctor
      if (user?.role !== 'DOCTOR') {
        navigate('/dashboard', { replace: true });
        return;
      }

      // Check if doctor profile already exists
      const doctorsRes = await api.get('/doctors');
      const existingProfile = doctorsRes.data.find(
        doc => doc.email?.toLowerCase() === user.email?.toLowerCase()
      );

      if (existingProfile) {
        // Profile already complete, redirect to dashboard
        navigate('/staff-dashboard', { replace: true });
        return;
      }

      // Get location information
      if (user.assigned_location_ids && user.assigned_location_ids.length > 0) {
        const locationRes = await api.get(`/locations/${user.assigned_location_ids[0]}`);
        setLocationInfo(locationRes.data);
      }

      setLoading(false);
    } catch (err) {
      console.error('Error checking profile status:', err);
      setError('Failed to load profile information');
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      // Create doctor profile
      await api.post('/doctors', {
        name: user.name,
        email: user.email,
        phone: user.phone || '',
        specialty: form.specialty,
        bio: form.bio,
        picture: form.picture,
        consultation_duration: parseInt(form.consultation_duration),
        consultation_fee: parseFloat(form.consultation_fee),
        currency: form.currency
      });

      // Refresh user data
      if (refreshUser) {
        await refreshUser();
      }

      // Redirect to staff dashboard
      navigate('/staff-dashboard', { replace: true });
    } catch (err) {
      console.error('Error creating doctor profile:', err);
      setError(err.response?.data?.detail || 'Failed to create profile. Please try again.');
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-teal-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-3" />
          <p className="text-gray-600">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-teal-400 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
            <Stethoscope className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {t('doctors.completeProfile') || 'Complete Your Doctor Profile'}
          </h1>
          <p className="text-gray-600">
            {t('doctors.completeProfileSubtitle') || 'Set up your profile so patients can book appointments with you'}
          </p>
          {locationInfo && (
            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg">
              <CheckCircle className="w-5 h-5" />
              <span className="font-medium">{locationInfo.name}</span>
            </div>
          )}
        </div>

        {/* Profile Form */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 md:p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Personal Info (Read-only) */}
            <div className="pb-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                {t('doctors.personalInfo') || 'Personal Information'}
              </h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('doctors.doctorName')}
                  </label>
                  <input
                    type="text"
                    value={user.name}
                    disabled
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('auth.email')}
                  </label>
                  <input
                    type="email"
                    value={user.email}
                    disabled
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-600"
                  />
                </div>
              </div>
            </div>

            {/* Professional Info */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Stethoscope className="w-5 h-5 text-blue-600" />
                {t('doctors.professionalInfo') || 'Professional Information'}
              </h2>
              
              <div className="space-y-4">
                {/* Specialty */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('doctors.specialty')} <span className="text-red-500">*</span>
                  </label>
                  <select
                    required
                    value={form.specialty}
                    onChange={(e) => setForm({ ...form, specialty: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">{t('doctors.selectSpecialty')}</option>
                    {specialtyKeys.map((key) => (
                      <option key={key} value={key}>
                        {t(`specialties.${key}`)}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Consultation Duration and Fee */}
                <div className="grid md:grid-cols-3 gap-4">
                  <div>
                    <label className="flex items-center gap-1 text-sm font-medium text-gray-700 mb-1">
                      <Clock className="w-4 h-4" />
                      {t('doctors.consultationDuration')}
                    </label>
                    <select
                      value={form.consultation_duration}
                      onChange={(e) => setForm({ ...form, consultation_duration: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="15">15 min</option>
                      <option value="20">20 min</option>
                      <option value="30">30 min</option>
                      <option value="45">45 min</option>
                      <option value="60">60 min</option>
                    </select>
                  </div>
                  <div>
                    <label className="flex items-center gap-1 text-sm font-medium text-gray-700 mb-1">
                      <DollarSign className="w-4 h-4" />
                      {t('doctors.consultationFee')}
                    </label>
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
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('services.currency')}
                    </label>
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

                {/* Bio */}
                <div>
                  <label className="flex items-center gap-1 text-sm font-medium text-gray-700 mb-1">
                    <FileText className="w-4 h-4" />
                    {t('doctors.bio')}
                  </label>
                  <textarea
                    value={form.bio}
                    onChange={(e) => setForm({ ...form, bio: e.target.value })}
                    rows={4}
                    placeholder={t('doctors.bioPlaceholder') || 'Tell patients about your experience, education, and approach to care...'}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {t('doctors.bioHelp') || 'This will be visible to patients when they book appointments'}
                  </p>
                </div>

                {/* Profile Picture URL (optional) */}
                <div>
                  <label className="flex items-center gap-1 text-sm font-medium text-gray-700 mb-1">
                    <ImageIcon className="w-4 h-4" />
                    {t('doctors.profilePicture') || 'Profile Picture URL'} ({t('common.optional')})
                  </label>
                  <input
                    type="url"
                    value={form.picture}
                    onChange={(e) => setForm({ ...form, picture: e.target.value })}
                    placeholder="https://example.com/photo.jpg"
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {t('doctors.pictureHelp') || 'You can add a profile picture URL or skip for now'}
                  </p>
                </div>
              </div>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex gap-3">
                <Calendar className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-blue-800">
                  <p className="font-medium mb-1">
                    {t('doctors.availabilityNote') || 'About Your Availability'}
                  </p>
                  <p>
                    {t('doctors.availabilityNoteText') || 'After completing your profile, you can set your working hours and availability schedule from your dashboard.'}
                  </p>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={saving || !form.specialty}
                className="flex-1 py-3 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    {t('doctors.creatingProfile') || 'Creating Profile...'}
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    {t('doctors.completeProfileButton') || 'Complete Profile & Continue'}
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Footer Note */}
        <p className="text-center text-sm text-gray-500 mt-6">
          {t('doctors.profileEditNote') || 'You can edit your profile information anytime from your dashboard'}
        </p>
      </div>
    </div>
  );
};

export default CompleteDoctorProfile;
