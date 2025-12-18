import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import {
  Plus,
  Trash2,
  Edit2,
  Briefcase,
  Clock,
  Loader2,
  X,
  Euro,
  Coins,
  Globe
} from 'lucide-react';

const CURRENCIES = [
  { code: 'LEI', symbol: 'LEI', icon: Coins },
  { code: 'EURO', symbol: '€', icon: Euro }
];

const Services = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingService, setEditingService] = useState(null);
  const [form, setForm] = useState({ 
    name: '', 
    name_en: '', 
    name_ro: '', 
    description: '', 
    description_en: '', 
    description_ro: '', 
    duration: 30, 
    price: 0, 
    currency: 'LEI' 
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchServices();
  }, [i18n.language]);

  const fetchServices = async () => {
    try {
      const res = await api.get('/services');
      setServices(res.data);
    } catch (err) {
      console.error('Error fetching services:', err);
    } finally {
      setLoading(false);
    }
  };

  const getLocalizedName = (service) => {
    if (i18n.language === 'ro' && service.name_ro) {
      return service.name_ro;
    }
    if (i18n.language === 'en' && service.name_en) {
      return service.name_en;
    }
    // Fallback to default name
    return service.name;
  };

  const getLocalizedDescription = (service) => {
    if (i18n.language === 'ro' && service.description_ro) {
      return service.description_ro;
    }
    if (i18n.language === 'en' && service.description_en) {
      return service.description_en;
    }
    // Fallback to default description
    return service.description;
  };

  const handleOpenModal = (service = null) => {
    if (service) {
      setEditingService(service);
      setForm({
        name: service.name || '',
        name_en: service.name_en || '',
        name_ro: service.name_ro || '',
        description: service.description || '',
        description_en: service.description_en || '',
        description_ro: service.description_ro || '',
        duration: service.duration,
        price: service.price,
        currency: service.currency || 'LEI'
      });
    } else {
      setEditingService(null);
      setForm({ 
        name: '', 
        name_en: '', 
        name_ro: '', 
        description: '', 
        description_en: '', 
        description_ro: '', 
        duration: 30, 
        price: 0, 
        currency: 'LEI' 
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingService(null);
    setForm({ 
      name: '', 
      name_en: '', 
      name_ro: '', 
      description: '', 
      description_en: '', 
      description_ro: '', 
      duration: 30, 
      price: 0, 
      currency: 'LEI' 
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      // Use English name as default name if not provided
      const submitData = {
        ...form,
        name: form.name_en || form.name_ro || form.name
      };

      if (editingService) {
        await api.put(`/services/${editingService.service_id}`, submitData);
      } else {
        await api.post('/services', submitData);
      }
      handleCloseModal();
      fetchServices();
    } catch (err) {
      console.error('Error saving service:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (serviceId) => {
    if (!window.confirm(t('services.deleteConfirm'))) return;
    try {
      await api.delete(`/services/${serviceId}`);
      fetchServices();
    } catch (err) {
      console.error('Error deleting service:', err);
    }
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

  if (user?.role !== 'CLINIC_ADMIN') {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">{t('auth.noPermission')}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('services.title')}</h1>
          <p className="text-sm text-gray-500">{t('services.subtitle')}</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all"
        >
          <Plus className="w-4 h-4" />
          {t('services.addService')}
        </button>
      </div>

      {/* Services Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : services.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <Briefcase className="w-12 h-12 mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500">{t('services.noServices')}</p>
          <button
            onClick={() => handleOpenModal()}
            className="mt-3 text-blue-600 hover:underline text-sm"
          >
            {t('services.addFirst')}
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
          {services.map((service) => {
            const localizedName = getLocalizedName(service);
            const localizedDescription = getLocalizedDescription(service);

            return (
              <div key={service.service_id} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900">{localizedName}</h3>
                      {(service.name_en || service.name_ro) && (
                        <Globe className="w-3.5 h-3.5 text-blue-500" title="Multilingual" />
                      )}
                    </div>
                    {localizedDescription && (
                      <p className="text-xs text-gray-500 line-clamp-1 mt-1">{localizedDescription}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleOpenModal(service)}
                      className="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(service.service_id)}
                      className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="mt-3 flex items-center gap-4 text-sm">
                  <span className="flex items-center gap-1 text-gray-500">
                    <Clock className="w-4 h-4" />
                    {service.duration} min
                  </span>
                  <span className="text-green-600 font-medium">
                    {formatPrice(service.price, service.currency || 'LEI')}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add/Edit Service Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white">
              <div className="flex items-center gap-2">
                <h2 className="font-semibold text-gray-900">
                  {editingService ? t('services.editService') : t('services.addService')}
                </h2>
                <Globe className="w-4 h-4 text-blue-500" />
              </div>
              <button onClick={handleCloseModal} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              {/* Multilingual Service Names */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <Globe className="w-4 h-4 text-blue-600" />
                  <h3 className="text-sm font-semibold text-blue-900">{t('services.serviceName')} (Multilingual)</h3>
                </div>
                <div className="space-y-2">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      English Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={form.name_en}
                      onChange={(e) => setForm({ ...form, name_en: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                      placeholder="e.g., Cardiology"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Romanian Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={form.name_ro}
                      onChange={(e) => setForm({ ...form, name_ro: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                      placeholder="ex. Cardiologie"
                    />
                  </div>
                </div>
              </div>

              {/* Multilingual Descriptions */}
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <h3 className="text-sm font-semibold text-gray-900 mb-2">{t('services.serviceDescription')} (Optional)</h3>
                <div className="space-y-2">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">English Description</label>
                    <textarea
                      value={form.description_en}
                      onChange={(e) => setForm({ ...form, description_en: e.target.value })}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm"
                      placeholder="Description in English..."
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Romanian Description</label>
                    <textarea
                      value={form.description_ro}
                      onChange={(e) => setForm({ ...form, description_ro: e.target.value })}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm"
                      placeholder="Descriere în română..."
                    />
                  </div>
                </div>
              </div>

              {/* Duration and Price */}
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('services.serviceDuration')}</label>
                  <input
                    type="number"
                    min="5"
                    step="5"
                    value={form.duration}
                    onChange={(e) => setForm({ ...form, duration: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('services.servicePrice')}</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={form.price}
                    onChange={(e) => setForm({ ...form, price: parseFloat(e.target.value) || 0 })}
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

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleCloseModal}
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
                  {t('common.save')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Services;
