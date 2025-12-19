import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Building2, Lock, Eye, EyeOff, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { api } from '../App';

const AcceptInvitation = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [invitation, setInvitation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ password: '', confirmPassword: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!token) {
      setError(t('invitation.invalidLink'));
      setLoading(false);
      return;
    }
    fetchInvitationDetails();
  }, [token]);

  const fetchInvitationDetails = async () => {
    try {
      const res = await api.get(`/invitations/token/${token}`);
      setInvitation(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || t('invitation.invalidLink'));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password.length < 8) {
      setError(t('auth.passwordTooShort'));
      return;
    }

    if (form.password !== form.confirmPassword) {
      setError(t('auth.passwordMismatch'));
      return;
    }

    setSubmitting(true);
    try {
      const res = await api.post('/invitations/accept', {
        token,
        password: form.password
      });
      setSuccess(true);
      sessionStorage.setItem('just_authenticated', 'true');

      // Redirect based on response
      setTimeout(() => {
        const redirectTo = res.data.user.redirect_to || '/staff-dashboard';
        navigate(redirectTo, { replace: true, state: { user: res.data.user } });
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setSubmitting(false);
    }
  };

  const getRoleDisplay = (role) => {
    const roleMap = {
      'DOCTOR': t('staff.doctor'),
      'ASSISTANT': t('staff.assistant'),
      'RECEPTIONIST': t('staff.receptionist'),
      'NURSE': t('staff.nurse'),
      'ADMIN': t('staff.admin'),
      'LOCATION_ADMIN': 'Location Admin',
      'SUPER_ADMIN': 'Super Admin'
    };
    return roleMap[role] || role;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-3" />
          <p className="text-gray-600">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  if (error && !invitation) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">{t('invitation.invalidLinkTitle')}</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Link
            to="/login"
            className="inline-block px-6 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all"
          >
            {t('auth.backToLogin')}
          </Link>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">{t('invitation.successTitle')}</h2>
          <p className="text-gray-600 mb-4">{t('invitation.successMessage')}</p>
          <p className="text-sm text-gray-500">{t('invitation.redirecting')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50 flex flex-col page-fade">
      <div className="flex justify-between items-center p-4">
        <Link to="/" className="flex items-center gap-2">
          <Building2 className="w-8 h-8 text-blue-600" />
          <span className="font-bold text-xl text-gray-900">MediConnect</span>
        </Link>
        <LanguageSwitcher />
      </div>

      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-teal-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Building2 className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-1">{t('invitation.welcomeTitle')}</h2>
              <p className="text-gray-500">{t('invitation.welcomeSubtitle')}</p>
            </div>

            {/* Invitation Details */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-600 mb-2">{t('invitation.youreInvitedTo')}</p>
              <p className="font-semibold text-gray-900 text-lg">{invitation?.organization_name}</p>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-sm text-gray-600">{t('invitation.as')}</span>
                <span className="text-sm font-medium px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">
                  {getRoleDisplay(invitation?.role)}
                </span>
              </div>
              {invitation?.location_names && invitation.location_names.length > 0 && (
                <p className="text-sm text-gray-500 mt-2">
                  {t('invitation.locations')}: {invitation.location_names.join(', ')}
                </p>
              )}
              <p className="text-sm text-gray-500 mt-2">
                {t('invitation.email')}: {invitation?.email}
              </p>
              <p className="text-xs text-gray-400 mt-2">
                {t('invitation.invitedBy')}: {invitation?.invited_by_name}
              </p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <p className="text-sm text-gray-600 mb-4">{t('invitation.setPasswordDesc')}</p>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.newPassword')}</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={form.password}
                    onChange={(e) => setForm({ ...form, password: e.target.value })}
                    className="w-full pl-10 pr-10 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder={t('auth.placeholders.enterPassword')}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">{t('auth.passwordMinChars')}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.confirmPassword')}</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    value={form.confirmPassword}
                    onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
                    className="w-full pl-10 pr-10 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder={t('auth.placeholders.confirmPassword')}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {submitting && <Loader2 className="w-5 h-5 animate-spin" />}
                {t('invitation.acceptAndContinue')}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AcceptInvitation;