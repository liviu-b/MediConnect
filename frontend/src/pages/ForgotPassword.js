import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Mail, Building2, Loader2, ArrowLeft, CheckCircle } from 'lucide-react';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { api } from '../App';

const ForgotPassword = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await api.post('/auth/forgot-password', { email });
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50 flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-teal-600 to-blue-500 p-8 flex-col justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
            <Building2 className="w-6 h-6 text-white" />
          </div>
          <span className="text-2xl font-bold text-white">MediConnect</span>
        </div>
        <div className="text-white">
          <h1 className="text-4xl font-bold mb-4">{t('auth.forgotPasswordTitle')}</h1>
          <p className="text-lg text-white/80">{t('auth.forgotPasswordSubtitle')}</p>
        </div>
        <p className="text-white/60 text-sm">© 2025 MediConnect</p>
      </div>

      {/* Right Panel */}
      <div className="flex-1 flex flex-col">
        <div className="flex justify-between items-center p-4">
          <Link to="/register-clinic" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
            <ArrowLeft className="w-5 h-5" />
            <span className="hidden sm:inline">{t('common.back')}</span>
          </Link>
          <div className="ml-auto">
            <LanguageSwitcher />
          </div>
        </div>

        <div className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-md">
            {success ? (
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('auth.emailSent')}</h2>
                <p className="text-gray-600 mb-6">{t('auth.checkYourEmail')}</p>
                <Link
                  to="/register-clinic"
                  className="inline-block px-6 py-2.5 bg-gradient-to-r from-teal-600 to-blue-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                >
                  {t('auth.backToLogin')}
                </Link>
              </div>
            ) : (
              <>
                <div className="flex items-center gap-2 mb-2">
                  <Mail className="w-6 h-6 text-teal-600" />
                  <h2 className="text-2xl font-bold text-gray-900">{t('auth.forgotPasswordTitle')}</h2>
                </div>
                <p className="text-gray-500 mb-6">{t('auth.forgotPasswordDesc')}</p>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                    {error}
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('auth.adminEmail')} <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="email@example.com"
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-2.5 bg-gradient-to-r from-teal-600 to-blue-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {loading && <Loader2 className="w-5 h-5 animate-spin" />}
                    {t('auth.sendResetLink')}
                  </button>
                </form>

                <p className="mt-6 text-center text-sm text-gray-500">
                  {t('auth.rememberPassword')}{' '}
                  <Link to="/register-clinic" className="text-teal-600 hover:underline font-medium">
                    {t('common.signIn')}
                  </Link>
                </p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
