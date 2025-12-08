import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import {
  CalendarDays,
  Users,
  Stethoscope,
  Building2,
  Clock,
  CalendarPlus,
  UserCog,
  Briefcase,
  ClipboardList,
  TrendingUp
} from 'lucide-react';

const Dashboard = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, aptsRes] = await Promise.all([
        api.get('/stats'),
        api.get('/appointments')
      ]);
      setStats(statsRes.data);
      // Sort and get upcoming appointments
      const now = new Date();
      const upcoming = aptsRes.data
        .filter(a => new Date(a.date_time) >= now && a.status !== 'CANCELLED')
        .sort((a, b) => new Date(a.date_time) - new Date(b.date_time))
        .slice(0, 5);
      setAppointments(upcoming);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  const isClinicAdmin = user?.role === 'CLINIC_ADMIN';

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
  };

  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-600 to-teal-500 rounded-xl p-4 text-white">
        <h1 className="text-xl font-bold">{t('dashboard.welcomeBack', { name: user?.name?.split(' ')[0] })}</h1>
        <p className="text-white/80 text-sm">
          {isClinicAdmin ? t('dashboard.adminSubtitle') : t('dashboard.patientSubtitle')}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {isClinicAdmin ? (
          <>
            <StatCard icon={CalendarDays} label={t('dashboard.stats.todayAppointments')} value={stats?.today_appointments || 0} color="blue" />
            <StatCard icon={Clock} label={t('dashboard.stats.upcoming')} value={stats?.upcoming_appointments || 0} color="teal" />
            <StatCard icon={Stethoscope} label={t('dashboard.stats.totalDoctors')} value={stats?.total_doctors || 0} color="purple" />
            <StatCard icon={Users} label={t('dashboard.stats.totalPatients')} value={stats?.total_patients || 0} color="orange" />
          </>
        ) : (
          <>
            <StatCard icon={CalendarDays} label={t('dashboard.stats.totalAppointments')} value={stats?.total_appointments || 0} color="blue" />
            <StatCard icon={Clock} label={t('dashboard.stats.upcoming')} value={stats?.upcoming_appointments || 0} color="teal" />
          </>
        )}
      </div>

      {/* Quick Actions & Upcoming */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Quick Actions */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h2 className="font-semibold text-gray-900 mb-3">{t('dashboard.quickActions')}</h2>
          <div className="grid grid-cols-2 gap-2">
            {isClinicAdmin ? (
              <>
                <ActionButton icon={CalendarDays} label={t('dashboard.viewAllAppointments')} onClick={() => navigate('/appointments')} />
                <ActionButton icon={Stethoscope} label={t('dashboard.manageDoctors')} onClick={() => navigate('/doctors')} />
                <ActionButton icon={UserCog} label={t('dashboard.manageStaff')} onClick={() => navigate('/staff')} />
                <ActionButton icon={Briefcase} label={t('dashboard.manageServices')} onClick={() => navigate('/services')} />
              </>
            ) : (
              <>
                <ActionButton icon={CalendarPlus} label={t('dashboard.bookAppointment')} onClick={() => navigate('/calendar')} />
                <ActionButton icon={CalendarDays} label={t('dashboard.viewAllAppointments')} onClick={() => navigate('/appointments')} />
                <ActionButton icon={Building2} label={t('dashboard.browseClinics')} onClick={() => navigate('/clinics')} />
              </>
            )}
          </div>
        </div>

        {/* Upcoming Appointments */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h2 className="font-semibold text-gray-900 mb-3">
            {isClinicAdmin ? t('dashboard.todaySchedule') : t('dashboard.upcomingAppointments')}
          </h2>
          {appointments.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              <CalendarDays className="w-10 h-10 mx-auto mb-2 text-gray-300" />
              <p className="text-sm">{t('dashboard.noUpcoming')}</p>
              {!isClinicAdmin && (
                <button
                  onClick={() => navigate('/calendar')}
                  className="mt-2 text-sm text-blue-600 hover:underline"
                >
                  {t('dashboard.bookFirst')}
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-2">
              {appointments.map((apt) => (
                <div
                  key={apt.appointment_id}
                  className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                  onClick={() => navigate('/appointments')}
                >
                  <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center text-blue-600 flex-shrink-0">
                    <Clock className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 text-sm truncate">
                      {isClinicAdmin ? apt.patient_name : `Dr. ${apt.doctor_name}`}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatDate(apt.date_time)} • {formatTime(apt.date_time)}
                    </p>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    apt.status === 'SCHEDULED' ? 'bg-blue-100 text-blue-700' :
                    apt.status === 'CONFIRMED' ? 'bg-green-100 text-green-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {t(`appointments.${apt.status.toLowerCase()}`)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Clinic Admin Extra Stats */}
      {isClinicAdmin && (
        <div className="grid grid-cols-3 gap-3">
          <StatCard icon={UserCog} label={t('dashboard.stats.totalStaff')} value={stats?.total_staff || 0} color="indigo" small />
          <StatCard icon={Briefcase} label={t('dashboard.stats.totalServices')} value={stats?.total_services || 0} color="pink" small />
          <StatCard icon={ClipboardList} label={t('dashboard.stats.totalAppointments')} value={stats?.total_appointments || 0} color="cyan" small />
        </div>
      )}
    </div>
  );
};

const StatCard = ({ icon: Icon, label, value, color, small = false }) => {
  const colors = {
    blue: 'bg-blue-50 text-blue-600',
    teal: 'bg-teal-50 text-teal-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
    indigo: 'bg-indigo-50 text-indigo-600',
    pink: 'bg-pink-50 text-pink-600',
    cyan: 'bg-cyan-50 text-cyan-600'
  };

  return (
    <div className={`bg-white rounded-xl border border-gray-200 ${small ? 'p-3' : 'p-4'}`}>
      <div className="flex items-center gap-3">
        <div className={`${small ? 'w-8 h-8' : 'w-10 h-10'} rounded-lg ${colors[color]} flex items-center justify-center`}>
          <Icon className={small ? 'w-4 h-4' : 'w-5 h-5'} />
        </div>
        <div>
          <p className={`${small ? 'text-lg' : 'text-2xl'} font-bold text-gray-900`}>{value}</p>
          <p className="text-xs text-gray-500 truncate">{label}</p>
        </div>
      </div>
    </div>
  );
};

const ActionButton = ({ icon: Icon, label, onClick }) => (
  <button
    onClick={onClick}
    className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg hover:bg-blue-50 hover:text-blue-600 transition-all text-left group"
  >
    <Icon className="w-5 h-5 text-gray-400 group-hover:text-blue-500" />
    <span className="text-sm font-medium truncate">{label}</span>
  </button>
);

export default Dashboard;
