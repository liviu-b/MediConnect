import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Building2, Loader2, Save, CheckCircle } from 'lucide-react';
import { api } from '../App';

const OrganizationSettings = () => {
  const { t } = useTranslation();
  const [organization, setOrganization] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const [form, setForm] = useState({
    name: '',
    legal_name: '',
    cui: '',
    registration_number: '',
    tax_registration: '',
    legal_address: '',
    phone: '',
    email: '',
    website: '',
    description: ''
  });

  useEffect(() => {
    fetchOrganization();
  }, []);

  const fetchOrganization = async () => {
    try {
      setLoading(true);
      const res = await api.get('/organizations/me');
      setOrganization(res.data);
      setForm({
        name: res.data.name || '',
        legal_name: res.data.legal_name || '',
        cui: res.data.cui || '',
        registration_number: res.data.registration_number || '',
        tax_registration: res.data.tax_registration || '',
        legal_address: res.data.legal_address || '',
        phone: res.data.phone || '',
        email: res.data.email || '',
        website: res.data.website || '',
        description: res.data.description || ''
      });
    } catch (error) {
      console.error('Error fetching organization:', error);
      setError(t('organization.errorFetching') || 'Failed to load organization details');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess(false);

    try {
      await api.put('/organizations/me', form);
      setSuccess(true);
      
      // Refresh organization data
      await fetchOrganization();

      // Hide success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <Building2 className="w-8 h-8 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">
            {t('organization.settings') || 'Organization Settings'}
          </h2>
        </div>
        <p className="text-gray-600">
          {t('organization.subtitle') || 'Manage your organization details and legal information'}
        </p>
      </div>

      {/* Success Message */}
      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg flex items-center gap-2">
          <CheckCircle className="w-5 h-5" />
          {t('organization.saveSuccess') || 'Organization details saved successfully!'}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-lg">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Information */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {t('organization.basicInfo') || 'Basic Information'}
          </h3>

          <div className="space-y-4">
            {/* Organization Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('organization.name') || 'Organization Name'} <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder={t('organization.namePlaceholder') || 'e.g., Medical Group XYZ'}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Legal Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('organization.legalName') || 'Legal Name'}
              </label>
              <input
                type="text"
                value={form.legal_name}
                onChange={(e) => setForm({ ...form, legal_name: e.target.value })}
                placeholder={t('organization.legalNamePlaceholder') || 'Official registered name'}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('organization.description') || 'Description'}
              </label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder={t('organization.descriptionPlaceholder') || 'Brief description of your organization...'}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
            </div>
          </div>
        </div>

        {/* Legal Information */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {t('organization.legalInfo') || 'Legal Information'}
          </h3>

          <div className="space-y-4">
            {/* CUI (Read-only) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.cui')} <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.cui}
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500 cursor-not-allowed"
              />
              <p className="text-xs text-gray-500 mt-1">
                {t('organization.cuiReadonly') || 'CUI cannot be changed after registration'}
              </p>
            </div>

            {/* Registration Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('organization.registrationNumber') || 'Registration Number'}
              </label>
              <input
                type="text"
                value={form.registration_number}
                onChange={(e) => setForm({ ...form, registration_number: e.target.value })}
                placeholder={t('organization.registrationNumberPlaceholder') || 'e.g., J35/1234/2020'}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Tax Registration */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('organization.taxRegistration') || 'Tax Registration'}
              </label>
              <input
                type="text"
                value={form.tax_registration}
                onChange={(e) => setForm({ ...form, tax_registration: e.target.value })}
                placeholder={t('organization.taxRegistrationPlaceholder') || 'Tax registration number'}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Legal Address */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('organization.legalAddress') || 'Legal Address'}
              </label>
              <input
                type="text"
                value={form.legal_address}
                onChange={(e) => setForm({ ...form, legal_address: e.target.value })}
                placeholder={t('organization.legalAddressPlaceholder') || 'Official registered address'}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {t('organization.contactInfo') || 'Contact Information'}
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('organization.phone') || 'Phone'}
              </label>
              <input
                type="tel"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                placeholder="+40 21 123 4567"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('organization.email') || 'Email'}
              </label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="contact@example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Website */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('organization.website') || 'Website'}
              </label>
              <input
                type="url"
                value={form.website}
                onChange={(e) => setForm({ ...form, website: e.target.value })}
                placeholder="https://www.example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {saving ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                {t('common.saving') || 'Saving...'}
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                {t('common.save')}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default OrganizationSettings;
