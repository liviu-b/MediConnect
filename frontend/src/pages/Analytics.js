import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import {
  TrendingUp,
  Users,
  Calendar,
  Stethoscope,
  MapPin,
  Briefcase,
  Clock,
  Loader2,
  BarChart3,
  PieChart,
  Activity,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';

const Analytics = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    fetchAnalytics();
  }, [days]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/analytics/overview?days=${days}`);
      setAnalytics(res.data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center">
          <Loader2 className="w-10 h-10 animate-spin text-blue-600 mx-auto mb-3" />
          <p className="text-gray-500">{t('analytics.loading')}</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">{t('analytics.noData')}</p>
      </div>
    );
  }

  const { overview, appointments_trend, appointments_by_location, appointments_by_status, top_doctors, busiest_days, busiest_hours } = analytics;

  return (
    <div className="space-y-6">
      {/* Header with Time Range Selector */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('analytics.title')}</h1>
          <p className="text-sm text-gray-500 mt-1">
            {t('analytics.subtitle')}
          </p>
        </div>
        
        {/* Time Range Selector */}
        <div className="flex items-center gap-2">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                days === d
                  ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white shadow-lg'
                  : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              {d} {t('analytics.days')}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Appointments */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
            <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
              {overview.completion_rate}% Complete
            </span>
          </div>
          <h3 className="text-2xl font-bold text-gray-900">{overview.total_appointments}</h3>
          <p className="text-sm text-gray-500 mt-1">{t('analytics.overview.totalAppointments')}</p>
          <div className="mt-3 flex items-center gap-4 text-xs">
            <span className="text-green-600 flex items-center gap-1">
              <CheckCircle className="w-3 h-3" />
              {overview.completed_appointments}
            </span>
            <span className="text-red-600 flex items-center gap-1">
              <XCircle className="w-3 h-3" />
              {overview.cancelled_appointments}
            </span>
          </div>
        </div>

        {/* Total Patients */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-teal-600" />
            </div>
            <span className="text-xs font-medium text-teal-600 bg-teal-50 px-2 py-1 rounded-full">
              +{overview.new_patients} New
            </span>
          </div>
          <h3 className="text-2xl font-bold text-gray-900">{overview.total_patients}</h3>
          <p className="text-sm text-gray-500 mt-1">{t('analytics.overview.totalPatients')}</p>
        </div>

        {/* Total Doctors */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Stethoscope className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900">{overview.total_doctors}</h3>
          <p className="text-sm text-gray-500 mt-1">{t('analytics.overview.totalDoctors')}</p>
        </div>

        {/* Total Locations */}
        <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <MapPin className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900">{overview.total_locations}</h3>
          <p className="text-sm text-gray-500 mt-1">{t('analytics.overview.totalLocations')}</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Appointments Trend */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">{t('analytics.charts.appointmentsTrend')}</h3>
          </div>
          <div className="h-64 flex items-end justify-between gap-1">
            {appointments_trend.slice(-14).map((item, index) => {
              const maxCount = Math.max(...appointments_trend.map(d => d.count), 1);
              const height = (item.count / maxCount) * 100;
              return (
                <div key={index} className="flex-1 flex flex-col items-center group">
                  <div className="relative w-full">
                    <div
                      className="w-full bg-gradient-to-t from-blue-600 to-teal-400 rounded-t-lg transition-all hover:opacity-80 cursor-pointer"
                      style={{ height: `${Math.max(height, 5)}%` }}
                      title={`${item.date}: ${item.count} appointments`}
                    />
                  </div>
                  <span className="text-xs text-gray-400 mt-2 rotate-45 origin-left">
                    {new Date(item.date).getDate()}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Appointments by Status */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <PieChart className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">{t('analytics.charts.appointmentsByStatus')}</h3>
          </div>
          <div className="space-y-3">
            {appointments_by_status.map((item, index) => {
              const percentage = overview.total_appointments > 0
                ? ((item.count / overview.total_appointments) * 100).toFixed(1)
                : 0;
              
              // Translate status labels
              const statusKey = item.status.toLowerCase();
              const translatedStatus = t(`analytics.status.${statusKey}`) || item.status;
              
              return (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">{translatedStatus}</span>
                    <span className="text-sm font-semibold text-gray-900">{item.count}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: item.color
                      }}
                    />
                  </div>
                  <span className="text-xs text-gray-500">{percentage}%</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Locations & Doctors Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Appointments by Location */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <MapPin className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">{t('analytics.charts.appointmentsByLocation')}</h3>
          </div>
          {appointments_by_location.length > 0 ? (
            <div className="space-y-3">
              {appointments_by_location.slice(0, 5).map((item, index) => {
                const maxCount = Math.max(...appointments_by_location.map(l => l.count), 1);
                const percentage = ((item.count / maxCount) * 100).toFixed(1);
                return (
                  <div key={index}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700 truncate">{item.location}</span>
                      <span className="text-sm font-semibold text-gray-900">{item.count}</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div
                        className="h-2 rounded-full bg-gradient-to-r from-blue-600 to-teal-400 transition-all"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-500 text-center py-8">{t('analytics.noData')}</p>
          )}
        </div>

        {/* Top Doctors */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Stethoscope className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">{t('analytics.charts.topDoctors')}</h3>
          </div>
          {top_doctors.length > 0 ? (
            <div className="space-y-3">
              {top_doctors.slice(0, 5).map((doctor, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-teal-400 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {index + 1}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Dr. {doctor.name}</p>
                      <p className="text-xs text-gray-500">{doctor.specialty}</p>
                    </div>
                  </div>
                  <span className="text-sm font-semibold text-blue-600">{doctor.appointments}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 text-center py-8">{t('analytics.noData')}</p>
          )}
        </div>
      </div>

      {/* Time Patterns Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Busiest Days */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">{t('analytics.charts.busiestDays')}</h3>
          </div>
          {busiest_days.length > 0 ? (
            <div className="space-y-2">
              {busiest_days.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg transition-colors">
                  <span className="text-sm font-medium text-gray-700">{item.day}</span>
                  <span className="text-sm font-semibold text-gray-900">{item.count} {t('analytics.metrics.appointments')}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 text-center py-8">{t('analytics.noData')}</p>
          )}
        </div>

        {/* Busiest Hours */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-900">{t('analytics.charts.busiestHours')}</h3>
          </div>
          {busiest_hours.length > 0 ? (
            <div className="space-y-2">
              {busiest_hours.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg transition-colors">
                  <span className="text-sm font-medium text-gray-700">{item.hour}</span>
                  <span className="text-sm font-semibold text-gray-900">{item.count} {t('analytics.metrics.appointments')}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 text-center py-8">{t('analytics.noData')}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Analytics;
