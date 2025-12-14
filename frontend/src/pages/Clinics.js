import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuth, api } from '../App';
import {
  Building2,
  MapPin,
  Phone,
  Mail,
  Clock,
  ChevronRight,
  Loader2,
  Star,
  StarHalf
} from 'lucide-react';

const DAYS_ORDER = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

const Clinics = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [clinics, setClinics] = useState([]);
  const [clinicStats, setClinicStats] = useState({});
  const [loading, setLoading] = useState(true);

  const isClinicAdmin = user?.role === 'CLINIC_ADMIN';

  useEffect(() => {
    fetchClinics();
  }, []);

  const fetchClinics = async () => {
    try {
      const res = await api.get('/clinics');
      setClinics(res.data);
      
      // Fetch stats for each clinic
      const statsPromises = res.data.map(clinic => 
        api.get(`/clinics/${clinic.clinic_id}/stats`).catch(() => ({ data: { average_rating: 0, review_count: 0 } }))
      );
      const statsResults = await Promise.all(statsPromises);
      
      const statsMap = {};
      res.data.forEach((clinic, index) => {
        statsMap[clinic.clinic_id] = statsResults[index].data;
      });
      setClinicStats(statsMap);
    } catch (err) {
      console.error('Error fetching clinics:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatWorkingHours = (hours) => {
    if (!hours) return null;
    
    // Find today's schedule
    const today = DAYS_ORDER[new Date().getDay() === 0 ? 6 : new Date().getDay() - 1];
    const todayHours = hours[today];
    
    if (!todayHours) {
      return { today: t('settings.closed'), schedule: hours };
    }
    
    return { 
      today: `${todayHours.start} - ${todayHours.end}`,
      schedule: hours
    };
  };

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />);
    }
    if (hasHalfStar) {
      stars.push(<StarHalf key="half" className="w-4 h-4 fill-yellow-400 text-yellow-400" />);
    }
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<Star key={`empty-${i}`} className="w-4 h-4 text-gray-300" />);
    }
    
    return stars;
  };

  const handleClinicClick = (clinicId) => {
    navigate(`/clinics/${clinicId}`);
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
          {clinics.map((clinic) => {
            const stats = clinicStats[clinic.clinic_id] || { average_rating: 0, review_count: 0 };
            const workingHoursInfo = formatWorkingHours(clinic.working_hours);
            
            return (
              <div
                key={clinic.clinic_id}
                onClick={() => handleClinicClick(clinic.clinic_id)}
                className={`bg-white rounded-xl border p-4 cursor-pointer hover:shadow-lg transition-all ${
                  isClinicAdmin && clinic.clinic_id === user?.clinic_id
                    ? 'border-blue-300 ring-2 ring-blue-100'
                    : 'border-gray-200 hover:border-blue-200'
                }`}
              >
                {isClinicAdmin && clinic.clinic_id === user?.clinic_id && (
                  <span className="inline-block px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-medium rounded mb-2">
                    {t('clinics.myClinic')}
                  </span>
                )}
                
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-teal-400 flex items-center justify-center text-white flex-shrink-0">
                      <Building2 className="w-6 h-6" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900">{clinic.name}</h3>
                      {clinic.description && (
                        <p className="text-sm text-gray-500 line-clamp-1">{clinic.description}</p>
                      )}
                      
                      {/* Rating */}
                      {stats.review_count > 0 && (
                        <div className="flex items-center gap-1 mt-1">
                          <div className="flex">{renderStars(stats.average_rating)}</div>
                          <span className="text-sm text-gray-600 ml-1">
                            {stats.average_rating.toFixed(1)} ({stats.review_count} {t('clinics.reviews')})
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
                </div>
                
                <div className="mt-4 space-y-2 text-sm">
                  <p className="flex items-center gap-2 text-gray-600">
                    <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    <span className="truncate">{clinic.address}</span>
                  </p>
                  {clinic.phone && (
                    <p className="flex items-center gap-2 text-gray-600">
                      <Phone className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      {clinic.phone}
                    </p>
                  )}
                  {clinic.email && (
                    <p className="flex items-center gap-2 text-gray-600">
                      <Mail className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      {clinic.email}
                    </p>
                  )}
                  {workingHoursInfo && (
                    <p className="flex items-center gap-2 text-gray-600">
                      <Clock className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      <span>
                        {t('clinics.todayHours')}: {workingHoursInfo.today}
                      </span>
                    </p>
                  )}
                </div>

                <div className="mt-3 pt-3 border-t border-gray-100">
                  <span className="text-xs text-blue-600 font-medium">{t('clinics.viewDetails')} →</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Clinics;