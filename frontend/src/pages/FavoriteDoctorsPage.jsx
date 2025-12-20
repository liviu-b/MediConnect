import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import {
  Star,
  Loader2,
  Calendar,
  Clock,
  MapPin,
  Trash2,
  Heart,
  Stethoscope,
  Phone,
  Mail,
  Building2,
  CalendarDays,
  TrendingUp
} from 'lucide-react';
import { api } from '../App';

const FavoriteDoctorsPage = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [removing, setRemoving] = useState(null);

  useEffect(() => {
    fetchFavorites();
    fetchStats();
  }, []);

  const fetchFavorites = async () => {
    setLoading(true);
    try {
      const response = await api.get('/favorites/doctors');
      setFavorites(response.data);
    } catch (error) {
      console.error('Error fetching favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/favorites/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const removeFavorite = async (favoriteId) => {
    if (!window.confirm(t('favorites.removeConfirm') || 'Remove this doctor from favorites?')) {
      return;
    }

    setRemoving(favoriteId);
    try {
      await api.delete(`/favorites/doctors/${favoriteId}`);
      await fetchFavorites();
      await fetchStats();
    } catch (error) {
      console.error('Error removing favorite:', error);
      alert(t('notifications.error'));
    } finally {
      setRemoving(null);
    }
  };

  const bookAppointment = (doctor) => {
    // Navigate to calendar with pre-selected doctor
    navigate(`/patient-dashboard?tab=calendar&clinic=${doctor.doctor_clinic_id}&doctor=${doctor.doctor_id}`);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return t('favorites.neverVisited') || 'Never visited';
    const date = new Date(dateStr);
    return date.toLocaleDateString();
  };

  const renderStars = (count) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < count ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <div className="max-w-6xl mx-auto space-y-4">
      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
        <div className="flex items-center gap-2">
          <Heart className="w-5 h-5 text-red-500 fill-red-500" />
          <h3 className="text-base font-semibold text-gray-900">{t('favorites.myFavoriteDoctors')}</h3>
        </div>
        <p className="text-xs text-gray-500 mt-1">{t('favorites.subtitle')}</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="bg-gradient-to-br from-red-50 to-pink-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center">
                <Heart className="w-5 h-5 text-white fill-white" />
              </div>
              <div>
                <p className="text-xs text-gray-600">{t('favorites.totalFavorites')}</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_favorites}</p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                <CalendarDays className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs text-gray-600">{t('favorites.totalAppointments')}</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_appointments}</p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs text-gray-600">{t('favorites.lastVisit')}</p>
                <p className="text-sm font-semibold text-gray-900">
                  {stats.last_visit ? formatDate(stats.last_visit) : t('favorites.noVisits')}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Favorites List */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : favorites.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-4">
            <Heart className="w-16 h-16 text-gray-300 mb-3" />
            <p className="text-gray-500 font-medium">{t('favorites.noFavorites')}</p>
            <p className="text-sm text-gray-400 text-center mt-1">
              {t('favorites.noFavoritesDesc')}
            </p>
            <button
              onClick={() => navigate('/patient-dashboard?tab=clinics')}
              className="mt-4 px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-md transition-all"
            >
              {t('favorites.browseDoctors')}
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {favorites.map((favorite) => (
              <div
                key={favorite.favorite_id}
                className="p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start gap-4">
                  {/* Doctor Avatar */}
                  <div className="flex-shrink-0">
                    {favorite.doctor_picture ? (
                      <img
                        src={favorite.doctor_picture}
                        alt={favorite.doctor_name}
                        className="w-16 h-16 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-teal-400 flex items-center justify-center">
                        <Stethoscope className="w-8 h-8 text-white" />
                      </div>
                    )}
                  </div>

                  {/* Doctor Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <h4 className="text-lg font-semibold text-gray-900">
                          Dr. {favorite.doctor_name}
                        </h4>
                        <p className="text-sm text-gray-600">{favorite.doctor_specialty}</p>
                        
                        {favorite.doctor_clinic_name && (
                          <div className="flex items-center gap-1 mt-1 text-sm text-gray-500">
                            <Building2 className="w-4 h-4" />
                            {favorite.doctor_clinic_name}
                          </div>
                        )}
                      </div>

                      {/* Favorite Badge */}
                      <div className="flex items-center gap-2">
                        <Heart className="w-5 h-5 text-red-500 fill-red-500" />
                      </div>
                    </div>

                    {/* Stats Row */}
                    <div className="flex flex-wrap items-center gap-4 mt-3 text-sm">
                      {favorite.total_appointments > 0 && (
                        <div className="flex items-center gap-1 text-gray-600">
                          <CalendarDays className="w-4 h-4" />
                          <span>
                            {favorite.total_appointments} {t('favorites.appointments')}
                          </span>
                        </div>
                      )}
                      
                      {favorite.last_appointment_date && (
                        <div className="flex items-center gap-1 text-gray-600">
                          <Clock className="w-4 h-4" />
                          <span>
                            {t('favorites.lastVisit')}: {formatDate(favorite.last_appointment_date)}
                          </span>
                        </div>
                      )}

                      {favorite.doctor_consultation_duration && (
                        <div className="flex items-center gap-1 text-gray-600">
                          <Clock className="w-4 h-4" />
                          <span>{favorite.doctor_consultation_duration} min</span>
                        </div>
                      )}

                      {favorite.doctor_consultation_fee && (
                        <div className="flex items-center gap-1 text-green-600 font-medium">
                          <span>{favorite.doctor_consultation_fee} LEI</span>
                        </div>
                      )}
                    </div>

                    {/* Notes */}
                    {favorite.notes && (
                      <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-gray-700">
                        <span className="font-medium">{t('favorites.notes')}:</span> {favorite.notes}
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center gap-2 mt-3">
                      <button
                        onClick={() => bookAppointment(favorite)}
                        className="px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg text-sm font-medium hover:shadow-md transition-all flex items-center gap-2"
                      >
                        <Calendar className="w-4 h-4" />
                        {t('favorites.bookAppointment')}
                      </button>
                      
                      <button
                        onClick={() => removeFavorite(favorite.favorite_id)}
                        disabled={removing === favorite.favorite_id}
                        className="px-4 py-2 border border-red-200 text-red-600 rounded-lg text-sm font-medium hover:bg-red-50 transition-all flex items-center gap-2 disabled:opacity-50"
                      >
                        {removing === favorite.favorite_id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                        {t('favorites.remove')}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tips */}
      {favorites.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
              <Heart className="w-4 h-4 text-white fill-white" />
            </div>
            <div>
              <h4 className="font-semibold text-blue-900">{t('favorites.tipTitle')}</h4>
              <p className="text-sm text-blue-700 mt-1">{t('favorites.tipDescription')}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FavoriteDoctorsPage;
