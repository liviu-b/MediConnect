import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { MapPin, Building2, Edit, Trash2, Plus, Loader2, Phone, Mail, Star, X, AlertCircle } from 'lucide-react';
import { api } from '../App';
import { useAuth } from '../App';

const Locations = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [locations, setLocations] = useState([]);
  const [organization, setOrganization] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingLocation, setEditingLocation] = useState(null);
  const [formLoading, setFormLoading] = useState(false);
  const [error, setError] = useState('');

  // Form state
  const [form, setForm] = useState({
    name: '',
    address: '',
    city: '',
    county: '',
    phone: '',
    is_primary: false
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Fetch locations
      const locationsRes = await api.get('/locations');
      setLocations(locationsRes.data);
      
      // Fetch organization data to get email
      if (user?.organization_id) {
        const orgRes = await api.get(`/organizations/${user.organization_id}`);
        setOrganization(orgRes.data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setError(t('locations.errorFetching') || 'Failed to load locations');
    } finally {
      setLoading(false);
    }
  };

  const fetchLocations = async () => {
    try {
      const res = await api.get('/locations');
      setLocations(res.data);
    } catch (error) {
      console.error('Error fetching locations:', error);
    }
  };

  const openCreateForm = () => {
    setEditingLocation(null);
    setForm({
      name: '',
      address: '',
      city: '',
      county: '',
      phone: '',
      is_primary: false
    });
    setShowForm(true);
    setError('');
  };

  const openEditForm = (location) => {
    setEditingLocation(location);
    setForm({
      name: location.name || '',
      address: location.address || '',
      city: location.city || '',
      county: location.county || '',
      phone: location.phone || '',
      is_primary: location.is_primary || false
    });
    setShowForm(true);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormLoading(true);
    setError('');

    try {
      if (editingLocation) {
        // Update existing location
        await api.put(`/locations/${editingLocation.location_id}`, form);
      } else {
        // Create new location
        await api.post('/locations', form);
      }

      // Refresh locations
      await fetchLocations();

      // Close form
      setShowForm(false);
      setEditingLocation(null);
    } catch (err) {
      setError(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setFormLoading(false);
    }
  };

  const handleDelete = async (locationId) => {
    if (!window.confirm(t('locations.deleteConfirm') || 'Delete this location?')) {
      return;
    }

    try {
      await api.delete(`/locations/${locationId}`);
      await fetchLocations();
    } catch (err) {
      setError(err.response?.data?.detail || t('notifications.error'));
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('locations.manageLocations')}</h1>
          <p className="text-sm text-gray-500 mt-1">{t('locations.subtitle') || 'Manage your organization\'s locations'}</p>
        </div>
        <button
          onClick={openCreateForm}
          className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all"
        >
          <Plus className="w-5 h-5" />
          {t('locations.addLocation')}
        </button>
      </div>

      {/* Organization Email Info Banner */}
      {organization?.email && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <Mail className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900 mb-1">
                {t('organization.contactInfo')}
              </h3>
              <p className="text-sm text-blue-700 mb-2">
                {t('locations.emailInherited')}
              </p>
              <div className="flex items-center gap-2 text-sm">
                <span className="font-medium text-blue-900">{t('organization.email')}:</span>
                <span className="text-blue-700">{organization.email}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && !showForm && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : locations.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <MapPin className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {t('locations.noLocations')}
          </h3>
          <p className="text-gray-500 mb-6">
            {t('locations.createFirst')}
          </p>
          <button
            onClick={openCreateForm}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all"
          >
            <Plus className="w-5 h-5" />
            {t('locations.addLocation')}
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {locations.map((location) => (
            <div
              key={location.location_id}
              className="bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all duration-200 overflow-hidden group"
            >
              {/* Card Header with Gradient */}
              <div className="bg-gradient-to-br from-blue-50 to-teal-50 p-4 relative">
                {/* Primary Badge */}
                {location.is_primary && (
                  <div className="absolute top-3 right-3">
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-semibold shadow-sm">
                      <Star className="w-3.5 h-3.5 fill-current" />
                      {t('locations.primary')}
                    </span>
                  </div>
                )}

                {/* Location Icon & Name */}
                <div className="flex items-start gap-3">
                  <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center shadow-sm flex-shrink-0">
                    <Building2 className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0 pr-12">
                    <h3 className="text-lg font-bold text-gray-900 truncate">
                      {location.name}
                    </h3>
                    {location.city && (
                      <p className="text-sm text-gray-600 flex items-center gap-1 mt-1">
                        <MapPin className="w-3.5 h-3.5 flex-shrink-0" />
                        <span className="truncate">
                          {location.city}{location.county && `, ${location.county}`}
                        </span>
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Card Body */}
              <div className="p-4 space-y-3">
                {/* Address */}
                {location.address && (
                  <div className="flex items-start gap-2 text-sm text-gray-600">
                    <MapPin className="w-4 h-4 flex-shrink-0 mt-0.5 text-gray-400" />
                    <span className="line-clamp-2">{location.address}</span>
                  </div>
                )}

                {/* Phone */}
                {location.phone && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Phone className="w-4 h-4 flex-shrink-0 text-gray-400" />
                    <span>{location.phone}</span>
                  </div>
                )}

                {/* Email from Organization */}
                {organization?.email && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Mail className="w-4 h-4 flex-shrink-0 text-gray-400" />
                    <span className="truncate">{organization.email}</span>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 pt-3 border-t border-gray-100">
                  <button
                    onClick={() => openEditForm(location)}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors text-sm font-medium"
                  >
                    <Edit className="w-4 h-4" />
                    {t('common.edit')}
                  </button>
                  <button
                    onClick={() => handleDelete(location.location_id)}
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors text-sm font-medium"
                  >
                    <Trash2 className="w-4 h-4" />
                    {t('common.delete')}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create/Edit Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 sticky top-0 bg-white z-10 rounded-t-xl">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  {editingLocation ? t('locations.editLocation') : t('locations.addLocation')}
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  {editingLocation 
                    ? t('locations.editLocationDesc') || 'Update location information'
                    : t('locations.addLocationDesc') || 'Add a new location to your organization'
                  }
                </p>
              </div>
              <button 
                onClick={() => {
                  setShowForm(false);
                  setEditingLocation(null);
                  setError('');
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6">

              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Location Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('locations.locationName')} <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    placeholder={t('locations.locationNamePlaceholder') || 'e.g., Clinica Timișoara'}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {/* Address */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('locations.locationAddress')}
                  </label>
                  <input
                    type="text"
                    value={form.address}
                    onChange={(e) => setForm({ ...form, address: e.target.value })}
                    placeholder={t('locations.addressPlaceholder') || 'e.g., Str. Revolutiei 10'}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {/* City and County */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('locations.locationCity')}
                    </label>
                    <input
                      type="text"
                      value={form.city}
                      onChange={(e) => setForm({ ...form, city: e.target.value })}
                      placeholder={t('locations.cityPlaceholder') || 'e.g., Timișoara'}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('locations.locationCounty')}
                    </label>
                    <input
                      type="text"
                      value={form.county}
                      onChange={(e) => setForm({ ...form, county: e.target.value })}
                      placeholder={t('locations.countyPlaceholder') || 'e.g., Timiș'}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                {/* Phone */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {t('locations.locationPhone')}
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="tel"
                      value={form.phone}
                      onChange={(e) => setForm({ ...form, phone: e.target.value })}
                      placeholder="+40 256 123 456"
                      className="w-full pl-11 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                {/* Email Info Note */}
                <div className="bg-gradient-to-r from-blue-50 to-teal-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Mail className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-blue-900 mb-1">{t('locations.emailNote') || 'Email Contact'}</p>
                      <p className="text-sm text-blue-700 mb-2">
                        {t('locations.emailInherited') || 'Email is managed at the organization level. Update it in Medical Center Settings to apply to all locations.'}
                      </p>
                      {organization?.email && (
                        <div className="flex items-center gap-2 text-sm">
                          <span className="font-medium text-blue-900">{t('organization.email')}:</span>
                          <span className="text-blue-700">{organization.email}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Primary Location */}
                <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <input
                    type="checkbox"
                    id="is_primary"
                    checked={form.is_primary}
                    onChange={(e) => setForm({ ...form, is_primary: e.target.checked })}
                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor="is_primary" className="text-sm text-gray-700 cursor-pointer flex items-center gap-2">
                    <Star className="w-4 h-4 text-yellow-500" />
                    {t('locations.setPrimary') || 'Set as primary location'}
                  </label>
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-6 border-t border-gray-200">
                  <button
                    type="button"
                    onClick={() => {
                      setShowForm(false);
                      setEditingLocation(null);
                      setError('');
                    }}
                    disabled={formLoading}
                    className="flex-1 py-2.5 px-4 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all disabled:opacity-50"
                  >
                    {t('common.cancel')}
                  </button>
                  <button
                    type="submit"
                    disabled={formLoading}
                    className="flex-1 py-2.5 px-4 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {formLoading && <Loader2 className="w-5 h-5 animate-spin" />}
                    {editingLocation ? t('common.save') : t('common.add')}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Locations;
