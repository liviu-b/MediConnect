import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Activity,
  Heart,
  Thermometer,
  Weight,
  Ruler,
  Droplet,
  TrendingUp,
  TrendingDown,
  Plus,
  X,
  Loader2,
  FileText,
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock,
  Download,
  Edit,
  Trash2
} from 'lucide-react';
import { api } from '../App';

const HealthStatsPage = () => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  
  // Stats data
  const [stats, setStats] = useState(null);
  const [vitals, setVitals] = useState([]);
  const [labResults, setLabResults] = useState([]);
  
  // Modals
  const [showAddVitalModal, setShowAddVitalModal] = useState(false);
  const [showLabResultModal, setShowLabResultModal] = useState(false);
  const [selectedLabResult, setSelectedLabResult] = useState(null);
  
  // Form states
  const [vitalForm, setVitalForm] = useState({
    type: 'blood_pressure',
    value: '',
    value_secondary: '',
    unit: 'mmHg',
    notes: ''
  });
  
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, vitalsRes, labsRes] = await Promise.all([
        api.get('/health/stats'),
        api.get('/health/vitals?limit=20'),
        api.get('/health/lab-results?limit=20')
      ]);
      
      setStats(statsRes.data);
      setVitals(vitalsRes.data);
      setLabResults(labsRes.data);
    } catch (error) {
      console.error('Error fetching health data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddVital = async (e) => {
    e.preventDefault();
    setSaving(true);
    
    try {
      await api.post('/health/vitals', {
        type: vitalForm.type,
        value: parseFloat(vitalForm.value),
        value_secondary: vitalForm.value_secondary ? parseFloat(vitalForm.value_secondary) : null,
        unit: vitalForm.unit,
        notes: vitalForm.notes || null
      });
      
      setShowAddVitalModal(false);
      setVitalForm({
        type: 'blood_pressure',
        value: '',
        value_secondary: '',
        unit: 'mmHg',
        notes: ''
      });
      
      await fetchData();
    } catch (error) {
      console.error('Error adding vital:', error);
      alert(t('notifications.error'));
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteVital = async (measurementId) => {
    if (!window.confirm(t('healthStats.deleteVitalConfirm'))) return;
    
    try {
      await api.delete(`/health/vitals/${measurementId}`);
      await fetchData();
    } catch (error) {
      console.error('Error deleting vital:', error);
      alert(t('notifications.error'));
    }
  };

  const getVitalIcon = (type) => {
    switch (type) {
      case 'blood_pressure': return <Heart className="w-5 h-5" />;
      case 'heart_rate': return <Activity className="w-5 h-5" />;
      case 'temperature': return <Thermometer className="w-5 h-5" />;
      case 'weight': return <Weight className="w-5 h-5" />;
      case 'height': return <Ruler className="w-5 h-5" />;
      case 'blood_sugar': return <Droplet className="w-5 h-5" />;
      default: return <Activity className="w-5 h-5" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'COMPLETED': return 'bg-green-100 text-green-700';
      case 'PENDING': return 'bg-yellow-100 text-yellow-700';
      case 'ABNORMAL': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString();
  };

  const formatDateTime = (dateStr) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const vitalTypes = [
    { value: 'blood_pressure', label: t('healthStats.bloodPressure'), unit: 'mmHg', hasSecondary: true },
    { value: 'heart_rate', label: t('healthStats.heartRate'), unit: 'bpm', hasSecondary: false },
    { value: 'temperature', label: t('healthStats.temperature'), unit: '°C', hasSecondary: false },
    { value: 'weight', label: t('healthStats.weight'), unit: 'kg', hasSecondary: false },
    { value: 'height', label: t('healthStats.height'), unit: 'cm', hasSecondary: false },
    { value: 'blood_sugar', label: t('healthStats.bloodSugar'), unit: 'mg/dL', hasSecondary: false }
  ];

  const selectedVitalType = vitalTypes.find(v => v.value === vitalForm.type);

  return (
    <div className="max-w-6xl mx-auto space-y-4">
      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-semibold text-gray-900">{t('healthStats.title')}</h3>
          </div>
          <button
            onClick={() => setShowAddVitalModal(true)}
            className="px-3 py-1.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg text-sm font-medium hover:shadow-md transition-all flex items-center gap-1"
          >
            <Plus className="w-4 h-4" />
            {t('healthStats.addMeasurement')}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-1">{t('healthStats.subtitle')}</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'overview'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          {t('healthStats.overview')}
        </button>
        <button
          onClick={() => setActiveTab('vitals')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'vitals'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          {t('healthStats.vitalSigns')} ({vitals.length})
        </button>
        <button
          onClick={() => setActiveTab('labs')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'labs'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          {t('healthStats.labResults')} ({labResults.length})
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : (
        <>
          {/* Overview Tab */}
          {activeTab === 'overview' && stats && (
            <div className="space-y-4">
              {/* Latest Vitals Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {/* Blood Pressure */}
                {stats.latest_blood_pressure && (
                  <div className="bg-gradient-to-br from-red-50 to-pink-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center text-white">
                        <Heart className="w-5 h-5" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-600">{t('healthStats.bloodPressure')}</p>
                        <p className="text-xl font-bold text-gray-900">
                          {stats.latest_blood_pressure.value}/{stats.latest_blood_pressure.value_secondary}
                        </p>
                        <p className="text-xs text-gray-500">{stats.latest_blood_pressure.unit}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Heart Rate */}
                {stats.latest_heart_rate && (
                  <div className="bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center text-white">
                        <Activity className="w-5 h-5" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-600">{t('healthStats.heartRate')}</p>
                        <p className="text-xl font-bold text-gray-900">{stats.latest_heart_rate.value}</p>
                        <p className="text-xs text-gray-500">{stats.latest_heart_rate.unit}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Weight & BMI */}
                {stats.latest_weight && (
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center text-white">
                        <Weight className="w-5 h-5" />
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-600">{t('healthStats.weight')}</p>
                        <p className="text-xl font-bold text-gray-900">{stats.latest_weight.value} kg</p>
                        {stats.latest_bmi && (
                          <p className="text-xs text-gray-500">BMI: {stats.latest_bmi}</p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Stats Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <p className="text-xs text-gray-500">{t('healthStats.totalMeasurements')}</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_vital_measurements}</p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <p className="text-xs text-gray-500">{t('healthStats.totalLabTests')}</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_lab_results}</p>
                </div>
                <div className="bg-white border border-yellow-200 rounded-lg p-4">
                  <p className="text-xs text-gray-500">{t('healthStats.pendingResults')}</p>
                  <p className="text-2xl font-bold text-yellow-600">{stats.pending_lab_results}</p>
                </div>
                <div className="bg-white border border-red-200 rounded-lg p-4">
                  <p className="text-xs text-gray-500">{t('healthStats.abnormalResults')}</p>
                  <p className="text-2xl font-bold text-red-600">{stats.abnormal_lab_results}</p>
                </div>
              </div>
            </div>
          )}

          {/* Vitals Tab */}
          {activeTab === 'vitals' && (
            <div className="space-y-3">
              {vitals.length === 0 ? (
                <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
                  <Activity className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                  <p className="text-gray-500">{t('healthStats.noVitals')}</p>
                  <button
                    onClick={() => setShowAddVitalModal(true)}
                    className="mt-4 px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-md transition-all"
                  >
                    {t('healthStats.addFirstMeasurement')}
                  </button>
                </div>
              ) : (
                vitals.map((vital) => (
                  <div key={vital.measurement_id} className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
                          {getVitalIcon(vital.type)}
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900">
                            {t(`healthStats.${vital.type}`)}
                          </h4>
                          <p className="text-2xl font-bold text-blue-600">
                            {vital.value}
                            {vital.value_secondary && `/${vital.value_secondary}`} {vital.unit}
                          </p>
                          <p className="text-sm text-gray-500">{formatDateTime(vital.measured_at)}</p>
                          {vital.notes && (
                            <p className="text-sm text-gray-600 mt-2 bg-gray-50 p-2 rounded">{vital.notes}</p>
                          )}
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteVital(vital.measurement_id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Lab Results Tab */}
          {activeTab === 'labs' && (
            <div className="space-y-3">
              {labResults.length === 0 ? (
                <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
                  <FileText className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                  <p className="text-gray-500">{t('healthStats.noLabResults')}</p>
                  <p className="text-sm text-gray-400 mt-1">{t('healthStats.noLabResultsDesc')}</p>
                </div>
              ) : (
                labResults.map((result) => (
                  <div
                    key={result.result_id}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => {
                      setSelectedLabResult(result);
                      setShowLabResultModal(true);
                    }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600">
                          <FileText className="w-5 h-5" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-semibold text-gray-900">{result.test_name}</h4>
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(result.status)}`}>
                              {t(`healthStats.status_${result.status.toLowerCase()}`)}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500">{result.test_category}</p>
                          <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                            <span className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {formatDate(result.test_date)}
                            </span>
                            {result.lab_name && (
                              <span>{result.lab_name}</span>
                            )}
                          </div>
                          {result.result_value && (
                            <div className="mt-2 p-2 bg-gray-50 rounded">
                              <span className="font-medium">{result.result_value} {result.result_unit}</span>
                              {result.reference_range && (
                                <span className="text-sm text-gray-500 ml-2">
                                  ({t('healthStats.normalRange')}: {result.reference_range})
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}

      {/* Add Vital Modal */}
      {showAddVitalModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-md">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h2 className="font-semibold text-gray-900">{t('healthStats.addMeasurement')}</h2>
              <button onClick={() => setShowAddVitalModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <form onSubmit={handleAddVital} className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('healthStats.measurementType')}
                </label>
                <select
                  value={vitalForm.type}
                  onChange={(e) => {
                    const type = vitalTypes.find(v => v.value === e.target.value);
                    setVitalForm({
                      ...vitalForm,
                      type: e.target.value,
                      unit: type.unit,
                      value_secondary: ''
                    });
                  }}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {vitalTypes.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {selectedVitalType?.hasSecondary ? t('healthStats.systolic') : t('healthStats.value')}
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={vitalForm.value}
                    onChange={(e) => setVitalForm({ ...vitalForm, value: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {selectedVitalType?.hasSecondary && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('healthStats.diastolic')}
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={vitalForm.value_secondary}
                      onChange={(e) => setVitalForm({ ...vitalForm, value_secondary: e.target.value })}
                      required
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('healthStats.notes')} ({t('common.optional')})
                </label>
                <textarea
                  value={vitalForm.notes}
                  onChange={(e) => setVitalForm({ ...vitalForm, notes: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowAddVitalModal(false)}
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

      {/* Lab Result Detail Modal */}
      {showLabResultModal && selectedLabResult && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white">
              <h2 className="font-semibold text-gray-900">{selectedLabResult.test_name}</h2>
              <button onClick={() => setShowLabResultModal(false)} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedLabResult.status)}`}>
                  {t(`healthStats.status_${selectedLabResult.status.toLowerCase()}`)}
                </span>
                <span className="text-sm text-gray-500">{selectedLabResult.test_category}</span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">{t('healthStats.testDate')}</p>
                  <p className="font-medium">{formatDate(selectedLabResult.test_date)}</p>
                </div>
                {selectedLabResult.result_date && (
                  <div>
                    <p className="text-sm text-gray-500">{t('healthStats.resultDate')}</p>
                    <p className="font-medium">{formatDate(selectedLabResult.result_date)}</p>
                  </div>
                )}
                {selectedLabResult.lab_name && (
                  <div>
                    <p className="text-sm text-gray-500">{t('healthStats.laboratory')}</p>
                    <p className="font-medium">{selectedLabResult.lab_name}</p>
                  </div>
                )}
                {selectedLabResult.ordered_by_name && (
                  <div>
                    <p className="text-sm text-gray-500">{t('healthStats.orderedBy')}</p>
                    <p className="font-medium">Dr. {selectedLabResult.ordered_by_name}</p>
                  </div>
                )}
              </div>

              {selectedLabResult.result_value && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">{t('healthStats.result')}</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {selectedLabResult.result_value} {selectedLabResult.result_unit}
                  </p>
                  {selectedLabResult.reference_range && (
                    <p className="text-sm text-gray-600 mt-1">
                      {t('healthStats.normalRange')}: {selectedLabResult.reference_range}
                    </p>
                  )}
                </div>
              )}

              {selectedLabResult.interpretation && (
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-purple-900 mb-1">{t('healthStats.interpretation')}</p>
                  <p className="text-sm text-gray-700">{selectedLabResult.interpretation}</p>
                </div>
              )}

              {selectedLabResult.notes && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-900 mb-1">{t('healthStats.notes')}</p>
                  <p className="text-sm text-gray-700">{selectedLabResult.notes}</p>
                </div>
              )}

              {selectedLabResult.file_url && (
                <a
                  href={selectedLabResult.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  {t('healthStats.downloadFile')}
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HealthStatsPage;
