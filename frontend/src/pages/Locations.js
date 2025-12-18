import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { MapPin, Building2, Edit, Trash2, Plus, Loader2, Phone, Mail, Star } from 'lucide-react';
import { api } from '../App';
import { useAuth } from '../App';

const Locations = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [locations, setLocations] = useState([]);
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
    email: '',
    is_primary: false
  });

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      setLoading(true);
      const res = await api.get('/locations');
      setLocations(res.data);
    } catch (error) {
      console.error('Error fetching locations:', error);
      setError(t('locations.errorFetching') || 'Failed to load locations');
    } finally {
      setLoading(false);
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
      email: '',
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
      email: location.email || '',
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
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <MapPin className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">{t('locations.manageLocations')}</h1>
          </div>
          <button
            onClick={openCreateForm}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            {t('locations.addLocation')}
          </button>
        </div>
        <p className="text-gray-600">{t('locations.subtitle') || 'Manage your organization\'s locations'}</p>
      </div>

      {/* Error Message */}
      {error && !showForm && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-600 rounded-lg">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : locations.length === 0 ? (
        /* Empty State */
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <MapPin className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {t('locations.noLocations')}
          </h3>
          <p className="text-gray-500 mb-4">
            {t('locations.createFirst')}
          </p>
          <button
            onClick={openCreateForm}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            {t('locations.addLocation')}
          </button>
        </div>
      ) : (
        /* Location Cards */
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {locations.map((location) => (
            <div
              key={location.location_id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow relative"
            >
              {/* Primary Badge */}
              {location.is_primary && (
                <div className="absolute top-4 right-4">
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">
                    <Star className="w-3 h-3 fill-current" />
                    {t('locations.primary')}
                  </span>
                </div>
              )}

              {/* Location Icon */}
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Building2 className="w-6 h-6 text-blue-600" />
              </div>

              {/* Location Name */}
              <h3 className="text-lg font-semibold text-gray-900 mb-2 pr-16">
                {location.name}
              </h3>

              {/* Location Details */}
              <div className="space-y-2 mb-4">
                {location.city && (
                  <div className="flex items-start gap-2 text-sm text-gray-600">
                    <MapPin className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    <span>
                      {location.city}
                      {location.county && `, ${location.county}`}
                    </span>
                  </div>
                )}
                {location.address && (
                  <p className="text-sm text-gray-600 ml-6">{location.address}</p>
                )}
                {location.phone && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Phone className="w-4 h-4 flex-shrink-0" />
                    <span>{location.phone}</span>
                  </div>
                )}
                {location.email && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Mail className="w-4 h-4 flex-shrink-0" />
                    <span>{location.email}</span>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t border-gray-100">
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
          ))}
        </div>
      )}

      {/* Create/Edit Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                {editingLocation ? t('locations.editLocation') : t('locations.addLocation')}
              </h2>

              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Location Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('locations.locationName')} <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    placeholder={t('locations.locationNamePlaceholder') || 'e.g., Clinica Timișoara'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Address */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('locations.locationAddress')}
                  </label>
                  <input
                    type="text"
                    value={form.address}
                    onChange={(e) => setForm({ ...form, address: e.target.value })}
                    placeholder={t('locations.addressPlaceholder') || 'e.g., Str. Revolutiei 10'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* City and County */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('locations.locationCity')}
                    </label>
                    <input
                      type="text"
                      value={form.city}
                      onChange={(e) => setForm({ ...form, city: e.target.value })}
                      placeholder={t('locations.cityPlaceholder') || 'e.g., Timișoara'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('locations.locationCounty')}
                    </label>
                    <input
                      type="text"
                      value={form.county}
                      onChange={(e) => setForm({ ...form, county: e.target.value })}
                      placeholder={t('locations.countyPlaceholder') || 'e.g., Timiș'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Phone and Email */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('locations.locationPhone')}
                    </label>
                    <input
                      type="tel"
                      value={form.phone}
                      onChange={(e) => setForm({ ...form, phone: e.target.value })}
                      placeholder="+40 256 123 456"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('locations.locationEmail')}
                    </label>
                    <input
                      type="email"
                      value={form.email}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                      placeholder="location@example.com"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                {/* Primary Location */}
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_primary"
                    checked={form.is_primary}
                    onChange={(e) => setForm({ ...form, is_primary: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor="is_primary" className="text-sm text-gray-700 cursor-pointer">
                    {t('locations.setPrimary') || 'Set as primary location'}
                  </label>
                </div>

                {/* Actions */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowForm(false);
                      setEditingLocation(null);
                      setError('');
                    }}
                    disabled={formLoading}
                    className="flex-1 py-2 px-4 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
                  >
                    {t('common.cancel')}
                  </button>
                  <button
                    type="submit"
                    disabled={formLoading}
                    className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {formLoading && <Loader2 className="w-4 h-4 animate-spin" />}
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
