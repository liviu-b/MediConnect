import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Building2, Loader2, Save, CheckCircle, Edit2, X, Phone, Mail, Globe } from 'lucide-react';
import { api } from '../App';

const OrganizationSettings = () => {
  const { t } = useTranslation();
  const [organization, setOrganization] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isEditingBasicInfo, setIsEditingBasicInfo] = useState(false);
  const [isEditingContactInfo, setIsEditingContactInfo] = useState(false);

  const [form, setForm] = useState({
    name: '',
    cui: '',
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
        cui: res.data.cui || '',
        phone: res.data.phone || '',
        email: res.data.email || '',
        website: res.data.website || '',
        description: res.data.description || ''
      });
      
      // Auto-enable edit mode if no data
      if (!res.data.name || !res.data.description) {
        setIsEditingBasicInfo(true);
      }
      if (!res.data.phone && !res.data.email) {
        setIsEditingContactInfo(true);
      }
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
      
      // Close edit modes
      setIsEditingBasicInfo(false);
      setIsEditingContactInfo(false);
      
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
      <div className="mb-4">
        <div className="flex items-center gap-3 mb-2">
          <Building2 className="w-8 h-8 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">
            {t('organization.settings') || 'Medical Center Settings'}
          </h2>
        </div>
        <p className="text-gray-600">
          {t('organization.subtitle') || 'Manage your organization details and contact information'}
        </p>
      </div>

      {/* Success Message */}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg flex items-center gap-2">
          <CheckCircle className="w-5 h-5" />
          {t('organization.saveSuccess') || 'Organization details saved successfully!'}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-600 rounded-lg">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Basic Information Section */}
        <div className="bg-white rounded-lg border border-gray-200">
          {/* Section Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="text-base font-semibold text-gray-900">
              {t('organization.basicInfo') || 'Basic Information'}
            </h3>
            {!isEditingBasicInfo && (
              <button
                type="button"
                onClick={() => setIsEditingBasicInfo(true)}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
              >
                <Edit2 className="w-4 h-4" />
                {t('common.edit') || 'Edit'}
              </button>
            )}
            {isEditingBasicInfo && (
              <button
                type="button"
                onClick={() => {
                  setIsEditingBasicInfo(false);
                  // Reset form to original values
                  setForm(prev => ({
                    ...prev,
                    name: organization.name || '',
                    description: organization.description || ''
                  }));
                }}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-4 h-4" />
                {t('common.cancel') || 'Cancel'}
              </button>
            )}
          </div>

          {/* Section Content */}
          <div className="p-4 space-y-4">
            {/* Organization Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('organization.name') || 'Organization Name'} <span className="text-red-500">*</span>
              </label>
              {isEditingBasicInfo ? (
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder={t('organization.namePlaceholder') || 'e.g., Medical Group XYZ'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
              ) : (
                <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-900">
                  {form.name || <span className="text-gray-400 italic">Not set</span>}
                </div>
              )}
            </div>

            {/* CUI (Always Read-only) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('auth.cui')} <span className="text-red-500">*</span>
              </label>
              <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-500 flex items-center justify-between">
                <span className="font-mono">{form.cui}</span>
                <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full">
                  {t('settings.verified') || 'Verified'}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {t('organization.cuiReadonly') || 'CUI cannot be changed after registration'}
              </p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('organization.description') || 'Description'}
              </label>
              {isEditingBasicInfo ? (
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder={t('organization.descriptionPlaceholder') || 'Brief description of your organization...'}
                  rows={6}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm resize-none"
                />
              ) : (
                <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-700 whitespace-pre-wrap">
                  {form.description || (
                    <span className="text-gray-400 italic">
                      {t('organization.noDescription') || 'No description added yet'}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Contact Information Section */}
        <div className="bg-white rounded-lg border border-gray-200">
          {/* Section Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="text-base font-semibold text-gray-900">
              {t('organization.contactInfo') || 'Contact Information'}
            </h3>
            {!isEditingContactInfo && (
              <button
                type="button"
                onClick={() => setIsEditingContactInfo(true)}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
              >
                <Edit2 className="w-4 h-4" />
                {t('common.edit') || 'Edit'}
              </button>
            )}
            {isEditingContactInfo && (
              <button
                type="button"
                onClick={() => {
                  setIsEditingContactInfo(false);
                  // Reset form to original values
                  setForm(prev => ({
                    ...prev,
                    phone: organization.phone || '',
                    email: organization.email || '',
                    website: organization.website || ''
                  }));
                }}
                className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-4 h-4" />
                {t('common.cancel') || 'Cancel'}
              </button>
            )}
          </div>

          {/* Section Content */}
          <div className="p-4 space-y-4">
            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('organization.phone') || 'Phone'}
              </label>
              {isEditingContactInfo ? (
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="tel"
                    value={form.phone}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                    placeholder="+40 21 123 4567"
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  />
                </div>
              ) : (
                <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-900">
                  <Phone className="w-4 h-4 text-gray-400" />
                  {form.phone || <span className="text-gray-400 italic">Not set</span>}
                </div>
              )}
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('organization.email') || 'Email'}
              </label>
              {isEditingContactInfo ? (
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                    placeholder="contact@example.com"
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  />
                </div>
              ) : (
                <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-900">
                  <Mail className="w-4 h-4 text-gray-400" />
                  {form.email || <span className="text-gray-400 italic">Not set</span>}
                </div>
              )}
            </div>

            {/* Website */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('organization.website') || 'Website'}
              </label>
              {isEditingContactInfo ? (
                <div className="relative">
                  <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="url"
                    value={form.website}
                    onChange={(e) => setForm({ ...form, website: e.target.value })}
                    placeholder="https://www.example.com"
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  />
                </div>
              ) : (
                <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-900">
                  <Globe className="w-4 h-4 text-gray-400" />
                  {form.website ? (
                    <a href={form.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                      {form.website}
                    </a>
                  ) : (
                    <span className="text-gray-400 italic">Not set</span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Save Button - Only show when editing */}
        {(isEditingBasicInfo || isEditingContactInfo) && (
          <button
            type="submit"
            disabled={saving}
            className="w-full py-3 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {saving ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                {t('common.saving') || 'Saving...'}
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                {t('common.saveChanges') || 'Save Changes'}
              </>
            )}
          </button>
        )}
      </form>
    </div>
  );
};

export default OrganizationSettings;
