import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Bell,
  CheckCheck,
  Trash2,
  Settings as SettingsIcon,
  Loader2,
  Mail,
  Smartphone,
  MessageSquare,
  Clock,
  Moon,
  Save,
  Check,
  X,
  AlertCircle
} from 'lucide-react';
import { api } from '../App';

const NotificationsPage = () => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('notifications');
  const [notifications, setNotifications] = useState([]);
  const [stats, setStats] = useState({});
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [filter, setFilter] = useState('all'); // all, unread

  useEffect(() => {
    fetchNotifications();
    fetchStats();
    fetchPreferences();
  }, []);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await api.get('/notifications/me?limit=100');
      setNotifications(response.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/notifications/me/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchPreferences = async () => {
    try {
      const response = await api.get('/notifications/preferences');
      setPreferences(response.data);
    } catch (error) {
      console.error('Error fetching preferences:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await api.put(`/notifications/${notificationId}`, { is_read: true });
      await fetchNotifications();
      await fetchStats();
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await api.post('/notifications/mark-all-read');
      await fetchNotifications();
      await fetchStats();
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      await api.delete(`/notifications/${notificationId}`);
      await fetchNotifications();
      await fetchStats();
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const clearAll = async () => {
    if (!window.confirm(t('notifications.clearAllConfirm') || 'Clear all notifications?')) {
      return;
    }
    try {
      await api.delete('/notifications/clear-all');
      await fetchNotifications();
      await fetchStats();
    } catch (error) {
      console.error('Error clearing notifications:', error);
    }
  };

  const savePreferences = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await api.put('/notifications/preferences', preferences);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Error saving preferences:', error);
      alert(t('notifications.error'));
    } finally {
      setSaving(false);
    }
  };

  const updatePreference = (key, value) => {
    setPreferences({ ...preferences, [key]: value });
  };

  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const getNotificationIcon = (type) => {
    const iconClass = "w-5 h-5";
    
    switch (type) {
      case 'APPOINTMENT_REMINDER_24H':
      case 'APPOINTMENT_REMINDER_1H':
        return <Bell className={`${iconClass} text-blue-600`} />;
      case 'APPOINTMENT_CONFIRMED':
        return <Check className={`${iconClass} text-green-600`} />;
      case 'APPOINTMENT_CANCELLED':
        return <X className={`${iconClass} text-red-600`} />;
      case 'PRESCRIPTION_ADDED':
      case 'MEDICAL_RECORD_ADDED':
        return <CheckCheck className={`${iconClass} text-purple-600`} />;
      default:
        return <Bell className={`${iconClass} text-gray-600`} />;
    }
  };

  const getPriorityBadge = (priority) => {
    const badges = {
      URGENT: 'bg-red-100 text-red-700',
      HIGH: 'bg-orange-100 text-orange-700',
      MEDIUM: 'bg-blue-100 text-blue-700',
      LOW: 'bg-gray-100 text-gray-700'
    };
    return badges[priority] || badges.LOW;
  };

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'unread') return !n.is_read;
    return true;
  });

  return (
    <div className="max-w-6xl mx-auto space-y-4">
      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-blue-600" />
            <h3 className="text-base font-semibold text-gray-900">{t('notifications.title')}</h3>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab('notifications')}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                activeTab === 'notifications'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {t('notifications.title')}
            </button>
            <button
              onClick={() => setActiveTab('preferences')}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                activeTab === 'preferences'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <SettingsIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {activeTab === 'notifications' ? (
        /* Notifications Tab */
        <>
          {/* Stats & Actions */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="text-sm">
                  <span className="text-gray-500">{t('notifications.total') || 'Total'}:</span>
                  <span className="ml-2 font-semibold text-gray-900">{stats.total_notifications || 0}</span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-500">{t('notifications.unread') || 'Unread'}:</span>
                  <span className="ml-2 font-semibold text-blue-600">{stats.unread_count || 0}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">{t('common.all')}</option>
                  <option value="unread">{t('notifications.unread') || 'Unread'}</option>
                </select>
                {stats.unread_count > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex items-center gap-1"
                  >
                    <CheckCheck className="w-4 h-4" />
                    {t('notifications.markAllRead')}
                  </button>
                )}
                {notifications.length > 0 && (
                  <button
                    onClick={clearAll}
                    className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors flex items-center gap-1"
                  >
                    <Trash2 className="w-4 h-4" />
                    {t('notifications.clearAll')}
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Notifications List */}
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            {loading ? (
              <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              </div>
            ) : filteredNotifications.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 px-4">
                <Bell className="w-16 h-16 text-gray-300 mb-3" />
                <p className="text-gray-500 font-medium">{t('notifications.noNotifications')}</p>
                <p className="text-sm text-gray-400">{t('notifications.noNotificationsDesc')}</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {filteredNotifications.map((notification) => (
                  <div
                    key={notification.notification_id}
                    className={`p-4 hover:bg-gray-50 transition-colors ${
                      !notification.is_read ? 'bg-blue-50/30' : ''
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      {/* Icon */}
                      <div className="flex-shrink-0 mt-1">
                        {getNotificationIcon(notification.type)}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <h4 className={`text-sm font-medium ${
                                !notification.is_read ? 'text-gray-900' : 'text-gray-700'
                              }`}>
                                {notification.title}
                              </h4>
                              {!notification.is_read && (
                                <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                              {notification.message}
                            </p>
                            <div className="flex items-center gap-3 mt-2">
                              <span className="text-xs text-gray-400">
                                {formatTime(notification.created_at)}
                              </span>
                              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getPriorityBadge(notification.priority)}`}>
                                {notification.priority}
                              </span>
                              {notification.type && (
                                <span className="text-xs text-gray-500">
                                  {t(`notifications.types.${notification.type}`) || notification.type}
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex items-center gap-1">
                            {!notification.is_read && (
                              <button
                                onClick={() => markAsRead(notification.notification_id)}
                                className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                                title={t('notifications.markRead') || 'Mark as read'}
                              >
                                <Check className="w-4 h-4 text-gray-600" />
                              </button>
                            )}
                            <button
                              onClick={() => deleteNotification(notification.notification_id)}
                              className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                              title={t('common.delete')}
                            >
                              <Trash2 className="w-4 h-4 text-gray-600 hover:text-red-600" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      ) : (
        /* Preferences Tab */
        <div className="space-y-4">
          {!preferences ? (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
            </div>
          ) : (
            <>
              {/* Email Notifications */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Mail className="w-5 h-5 text-blue-600" />
                  <h4 className="font-semibold text-gray-900">{t('notifications.emailNotifications')}</h4>
                </div>
                <div className="space-y-3">
                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{t('notifications.emailEnabled') || 'Enable email notifications'}</span>
                    <input
                      type="checkbox"
                      checked={preferences.email_enabled}
                      onChange={(e) => updatePreference('email_enabled', e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{t('notifications.appointmentReminders')}</span>
                    <input
                      type="checkbox"
                      checked={preferences.email_appointment_reminders}
                      onChange={(e) => updatePreference('email_appointment_reminders', e.target.checked)}
                      disabled={!preferences.email_enabled}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    />
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{t('notifications.appointmentChanges')}</span>
                    <input
                      type="checkbox"
                      checked={preferences.email_appointment_changes}
                      onChange={(e) => updatePreference('email_appointment_changes', e.target.checked)}
                      disabled={!preferences.email_enabled}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    />
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{t('notifications.medicalRecords')}</span>
                    <input
                      type="checkbox"
                      checked={preferences.email_medical_records}
                      onChange={(e) => updatePreference('email_medical_records', e.target.checked)}
                      disabled={!preferences.email_enabled}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    />
                  </label>
                </div>
              </div>

              {/* Push Notifications */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Smartphone className="w-5 h-5 text-green-600" />
                  <h4 className="font-semibold text-gray-900">{t('notifications.pushNotifications')}</h4>
                </div>
                <div className="space-y-3">
                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{t('notifications.pushEnabled') || 'Enable push notifications'}</span>
                    <input
                      type="checkbox"
                      checked={preferences.push_enabled}
                      onChange={(e) => updatePreference('push_enabled', e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{t('notifications.appointmentReminders')}</span>
                    <input
                      type="checkbox"
                      checked={preferences.push_appointment_reminders}
                      onChange={(e) => updatePreference('push_appointment_reminders', e.target.checked)}
                      disabled={!preferences.push_enabled}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    />
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{t('notifications.appointmentChanges')}</span>
                    <input
                      type="checkbox"
                      checked={preferences.push_appointment_changes}
                      onChange={(e) => updatePreference('push_appointment_changes', e.target.checked)}
                      disabled={!preferences.push_enabled}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    />
                  </label>
                </div>
              </div>

              {/* Reminder Timing */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Clock className="w-5 h-5 text-purple-600" />
                  <h4 className="font-semibold text-gray-900">{t('notifications.reminderTiming') || 'Reminder Timing'}</h4>
                </div>
                <div className="space-y-3">
                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{t('notifications.reminder24h')}</span>
                    <input
                      type="checkbox"
                      checked={preferences.reminder_24h_before}
                      onChange={(e) => updatePreference('reminder_24h_before', e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{t('notifications.reminder1h')}</span>
                    <input
                      type="checkbox"
                      checked={preferences.reminder_1h_before}
                      onChange={(e) => updatePreference('reminder_1h_before', e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  </label>
                </div>
              </div>

              {/* Quiet Hours */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Moon className="w-5 h-5 text-indigo-600" />
                  <h4 className="font-semibold text-gray-900">{t('notifications.quietHours')}</h4>
                </div>
                <p className="text-sm text-gray-500 mb-3">{t('notifications.quietHoursDesc')}</p>
                <div className="space-y-3">
                  <label className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{t('notifications.quietHoursEnabled') || 'Enable quiet hours'}</span>
                    <input
                      type="checkbox"
                      checked={preferences.quiet_hours_enabled}
                      onChange={(e) => updatePreference('quiet_hours_enabled', e.target.checked)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  </label>
                  {preferences.quiet_hours_enabled && (
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">{t('notifications.quietHoursStart')}</label>
                        <input
                          type="time"
                          value={preferences.quiet_hours_start || '22:00'}
                          onChange={(e) => updatePreference('quiet_hours_start', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">{t('notifications.quietHoursEnd')}</label>
                        <input
                          type="time"
                          value={preferences.quiet_hours_end || '08:00'}
                          onChange={(e) => updatePreference('quiet_hours_end', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Save Button */}
              <div className="flex items-center gap-3">
                <button
                  onClick={savePreferences}
                  disabled={saving}
                  className="px-6 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-semibold hover:shadow-md disabled:opacity-50 flex items-center gap-2"
                >
                  {saving ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : saved ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    <Save className="w-4 h-4" />
                  )}
                  {saved ? t('notifications.preferencesUpdated') : t('notifications.savePreferences')}
                </button>
                {saved && (
                  <div className="flex items-center gap-2 text-green-600 text-sm">
                    <Check className="w-4 h-4" />
                    {t('notifications.preferencesUpdated')}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationsPage;
