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
    <div className="w-full">
      {/* Header */}
      <div className="mb-3">
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

      <form onSubmit={handleSubmit} className="space-y-3">
        {/* 2-Column Grid: Left = Basic Info, Right = Legal Info + Contact Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* LEFT COLUMN: Basic Information */}
          <div className="bg-white rounded-lg border border-gray-200 p-3">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              {t('organization.basicInfo') || 'Basic Information'}
            </h3>

            <div className="space-y-3">
              {/* Organization Name */}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  {t('organization.name') || 'Organization Name'} <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder={t('organization.namePlaceholder') || 'e.g., Medical Group XYZ'}
                  className="w-full px-2.5 py-1.5 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
              </div>

              {/* Description - Increased height */}
              <div className="flex-1">
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  {t('organization.description') || 'Description'}
                </label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder={t('organization.descriptionPlaceholder') || 'Brief description of your organization...'}
                  rows={12}
                  className="w-full px-2.5 py-1.5 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm resize-none"
                />
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: Legal Information + Contact Information */}
          <div className="space-y-3">
            {/* Legal Information */}
            <div className="bg-white rounded-lg border border-gray-200 p-3">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">
                {t('organization.legalInfo') || 'Legal Information'}
              </h3>

              <div className="space-y-3">
                {/* CUI (Read-only) */}
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    {t('auth.cui')} <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={form.cui}
                    disabled
                    className="w-full px-2.5 py-1.5 border border-gray-300 rounded-md bg-gray-50 text-gray-500 cursor-not-allowed text-sm"
                  />
                  <p className="text-[10px] text-gray-500 mt-1">
                    {t('organization.cuiReadonly') || 'CUI cannot be changed after registration'}
                  </p>
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div className="bg-white rounded-lg border border-gray-200 p-3">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">
                {t('organization.contactInfo') || 'Contact Information'}
              </h3>

              <div className="space-y-3">
                {/* Phone */}
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    {t('organization.phone') || 'Phone'}
                  </label>
                  <input
                    type="tel"
                    value={form.phone}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                    placeholder="+40 21 123 4567"
                    className="w-full px-2.5 py-1.5 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                </div>

                {/* Email */}
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    {t('organization.email') || 'Email'}
                  </label>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    placeholder="contact@example.com"
                    className="w-full px-2.5 py-1.5 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                </div>

                {/* Website */}
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">
                    {t('organization.website') || 'Website'}
                  </label>
                  <input
                    type="url"
                    value={form.website}
                    onChange={(e) => setForm({ ...form, website: e.target.value })}
                    placeholder="https://www.example.com"
                    className="w-full px-2.5 py-1.5 border border-gray-300 rounded-md focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Success Message */}
        {success && (
          <div className="p-2.5 bg-green-50 border border-green-200 text-green-700 rounded-lg text-xs flex items-center gap-2">
            <CheckCircle className="w-3.5 h-3.5" />
            {t('settings.changesSavedSuccessfully')}
          </div>
        )}

        {/* Save Button */}
        <button
          type="submit"
          disabled={saving}
          className="w-full py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-semibold hover:shadow-md transition-all disabled:opacity-50 flex items-center justify-center gap-2 text-sm"
        >
          {saving ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : success ? (
            <CheckCircle className="w-4 h-4" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          {success ? t('notifications.saveSuccess') : t('common.save')}
        </button>
      </form>
    </div>
  );
};

export default OrganizationSettings;
