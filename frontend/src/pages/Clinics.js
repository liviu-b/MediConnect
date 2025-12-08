import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import {
  Building2,
  MapPin,
  Phone,
  Mail,
  Clock,
  ChevronRight,
  Loader2
} from 'lucide-react';

const Clinics = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [clinics, setClinics] = useState([]);
  const [loading, setLoading] = useState(true);

  const isClinicAdmin = user?.role === 'CLINIC_ADMIN';

  useEffect(() => {
    fetchClinics();
  }, []);

  const fetchClinics = async () => {
    try {
      const res = await api.get('/clinics');
      setClinics(res.data);
    } catch (err) {
      console.error('Error fetching clinics:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatHours = (hours) => {
    if (!hours) return '';
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
    const firstDay = hours[days[0]];
    if (!firstDay) return '';
    return `${firstDay.start} - ${firstDay.end}`;
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-gray-900">{t('clinics.title')}</h1>
        <p className="text-sm text-gray-500">{t('clinics.subtitle')}</p>
      </div>

      {/* Clinics Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : clinics.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <Building2 className="w-12 h-12 mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500">{t('clinics.noClinics')}</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4">
          {clinics.map((clinic) => (
            <div
              key={clinic.clinic_id}
              className={`bg-white rounded-xl border p-4 ${
                isClinicAdmin && clinic.clinic_id === user?.clinic_id
                  ? 'border-blue-300 ring-2 ring-blue-100'
                  : 'border-gray-200'
              }`}
            >
              {isClinicAdmin && clinic.clinic_id === user?.clinic_id && (
                <span className="inline-block px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-medium rounded mb-2">
                  {t('clinics.myClinic')}
                </span>
              )}
              <div className="flex items-start gap-3">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-teal-400 flex items-center justify-center text-white flex-shrink-0">
                  <Building2 className="w-6 h-6" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900">{clinic.name}</h3>
                  {clinic.description && (
                    <p className="text-sm text-gray-500 line-clamp-1">{clinic.description}</p>
                  )}
                </div>
              </div>
              <div className="mt-4 space-y-2 text-sm">
                <p className="flex items-center gap-2 text-gray-600">
                  <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <span className="truncate">{clinic.address}</span>
                </p>
                <p className="flex items-center gap-2 text-gray-600">
                  <Phone className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  {clinic.phone}
                </p>
                <p className="flex items-center gap-2 text-gray-600">
                  <Mail className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  {clinic.email}
                </p>
                {clinic.working_hours && (
                  <p className="flex items-center gap-2 text-gray-600">
                    <Clock className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    {formatHours(clinic.working_hours)}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Clinics;
