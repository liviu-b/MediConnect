import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Mail, Lock, User, Building2, Loader2, ArrowLeft, CheckCircle2, XCircle, AlertCircle, Eye, EyeOff, LogIn } from 'lucide-react';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { api } from '../App';

const RegisterClinic = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('register'); // 'register' or 'login'
  const [form, setForm] = useState({
    cui: '',
    admin_name: '',
    admin_email: '',
    admin_password: '',
    confirm_password: ''
  });
  const [loginForm, setLoginForm] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [cuiStatus, setCuiStatus] = useState(null);
  const [cuiChecked, setCuiChecked] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [showLoginPassword, setShowLoginPassword] = useState(false);

  const validateCUI = async (cui) => {
    if (!cui || cui.length < 2) {
      setCuiStatus(null);
      setCuiChecked(false);
      return;
    }
    
    setCuiStatus('checking');
    try {
      const res = await api.post(`/auth/validate-cui?cui=${cui}`);
      if (res.data.valid && res.data.available) {
        setCuiStatus('valid');
      } else if (res.data.valid && !res.data.available) {
        setCuiStatus('taken');
      } else {
        setCuiStatus('invalid');
      }
      setCuiChecked(true);
    } catch (err) {
      setCuiStatus('invalid');
      setCuiChecked(true);
    }
  };

  const handleCuiChange = (e) => {
    const value = e.target.value.replace(/\D/g, '');
    setForm({ ...form, cui: value });
    setCuiChecked(false);
    setCuiStatus(null);
  };

  const handleCuiBlur = () => {
    if (form.cui.length >= 2) {
      validateCUI(form.cui);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.admin_password !== form.confirm_password) {
      setError(t('auth.passwordMismatch'));
      return;
    }

    if (form.admin_password.length < 8) {
      setError(t('auth.passwordTooShort'));
      return;
    }

    if (!cuiChecked || cuiStatus !== 'valid') {
      setError(t('auth.cuiInvalid'));
      return;
    }

    setLoading(true);
    try {
      const res = await api.post('/auth/register-clinic', {
        cui: form.cui,
        admin_name: form.admin_name,
        admin_email: form.admin_email,
        admin_password: form.admin_password
      });
      sessionStorage.setItem('just_authenticated', 'true');
      navigate('/settings', { replace: true, state: { user: res.data.user, isNewClinic: true } });
    } catch (err) {
      setError(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await api.post('/auth/login', loginForm);
      sessionStorage.setItem('just_authenticated', 'true');
      navigate('/dashboard', { replace: true, state: { user: res.data.user } });
    } catch (err) {
      setError(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setLoading(false);
    }
  };

  const getCuiIcon = () => {
    switch (cuiStatus) {
      case 'checking':
        return <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />;
      case 'valid':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'taken':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'invalid':
        return <AlertCircle className="w-5 h-5 text-orange-500" />;
      default:
        return null;
    }
  };

  const getCuiMessage = () => {
    switch (cuiStatus) {
      case 'valid':
        return <span className="text-green-600">{t('auth.cuiAvailable')}</span>;
      case 'taken':
        return <span className="text-red-600">{t('auth.cuiTaken')}</span>;
      case 'invalid':
        return <span className="text-orange-600">{t('auth.cuiInvalidFormat')}</span>;
      default:
        return null;
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
          <h1 className="text-4xl font-bold mb-4">{t('auth.clinicSignUpTitle')}</h1>
          <p className="text-lg text-white/80 mb-6">{t('auth.clinicSignUpSubtitle')}</p>
          
          <div className="bg-white/10 rounded-xl p-4 space-y-3">
            <h3 className="font-semibold">{t('auth.howItWorks')}</h3>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-sm flex-shrink-0">1</div>
              <p className="text-sm text-white/80">{t('auth.step1Cui')}</p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-sm flex-shrink-0">2</div>
              <p className="text-sm text-white/80">{t('auth.step2Admin')}</p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-sm flex-shrink-0">3</div>
              <p className="text-sm text-white/80">{t('auth.step3Complete')}</p>
            </div>
          </div>
        </div>
        <p className="text-white/60 text-sm">© 2025 MediConnect</p>
      </div>

      {/* Right Panel */}
      <div className="flex-1 flex flex-col">
        <div className="flex justify-between items-center p-4">
          <Link to="/login" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
            <ArrowLeft className="w-5 h-5" />
            <span className="hidden sm:inline">{t('common.back')}</span>
          </Link>
          <div className="ml-auto">
            <LanguageSwitcher />
          </div>
        </div>

        <div className="flex-1 flex items-center justify-center p-6 overflow-y-auto">
          <div className="w-full max-w-md">
            {/* Tabs */}
            <div className="flex mb-6 bg-gray-100 rounded-lg p-1">
              <button
                type="button"
                onClick={() => { setActiveTab('register'); setError(''); }}
                className={`flex-1 py-2.5 px-4 rounded-md text-sm font-medium transition-all ${
                  activeTab === 'register'
                    ? 'bg-white text-teal-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Building2 className="w-4 h-4 inline mr-2" />
                {t('auth.newClinic')}
              </button>
              <button
                type="button"
                onClick={() => { setActiveTab('login'); setError(''); }}
                className={`flex-1 py-2.5 px-4 rounded-md text-sm font-medium transition-all ${
                  activeTab === 'login'
                    ? 'bg-white text-teal-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <LogIn className="w-4 h-4 inline mr-2" />
                {t('auth.alreadyRegistered')}
              </button>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}

            {activeTab === 'login' ? (
              /* Login Form for Already Registered Clinics */
              <>
                <div className="flex items-center gap-2 mb-2">
                  <LogIn className="w-6 h-6 text-teal-600" />
                  <h2 className="text-2xl font-bold text-gray-900">{t('auth.clinicLogin')}</h2>
                </div>
                <p className="text-gray-500 mb-6">{t('auth.clinicLoginSubtitle')}</p>

                <form onSubmit={handleLogin} className="space-y-4">
                  {/* Admin Email */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('auth.adminEmail')} <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="email"
                        required
                        value={loginForm.email}
                        onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                        placeholder="email@example.com"
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  {/* Password */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('auth.password')} <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type={showLoginPassword ? 'text' : 'password'}
                        required
                        value={loginForm.password}
                        onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                        placeholder={t('auth.placeholders.enterPassword')}
                        className="w-full pl-10 pr-10 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                      <button
                        type="button"
                        onClick={() => setShowLoginPassword(!showLoginPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showLoginPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  {/* Forgot Password Link */}
                  <div className="text-right">
                    <Link to="/forgot-password" className="text-sm text-teal-600 hover:underline">
                      {t('auth.forgotPassword')}
                    </Link>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-2.5 bg-gradient-to-r from-teal-600 to-blue-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {loading && <Loader2 className="w-5 h-5 animate-spin" />}
                    {t('common.signIn')}
                  </button>
                </form>
              </>
            ) : (
              /* Registration Form for New Clinics */
              <>
                <div className="flex items-center gap-2 mb-6">
                  <Building2 className="w-6 h-6 text-teal-600" />
                  <h2 className="text-2xl font-bold text-gray-900">{t('auth.registerAsClinic')}</h2>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* CUI Field */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('auth.cui')} <span className="text-red-500">*</span>
                    </label>
                    <p className="text-xs text-gray-500 mb-2">{t('auth.cuiHelp')}</p>
                    <div className="relative">
                      <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="text"
                        required
                        maxLength={10}
                        value={form.cui}
                        onChange={handleCuiChange}
                        onBlur={handleCuiBlur}
                        placeholder={t('auth.placeholders.cui')}
                        className={`w-full pl-10 pr-10 py-2.5 border rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent ${
                          cuiStatus === 'valid' ? 'border-green-300' :
                          cuiStatus === 'taken' || cuiStatus === 'invalid' ? 'border-red-300' :
                          'border-gray-200'
                        }`}
                      />
                      <div className="absolute right-3 top-1/2 -translate-y-1/2">
                        {getCuiIcon()}
                      </div>
                    </div>
                    {cuiStatus && (
                      <p className="mt-1 text-xs">{getCuiMessage()}</p>
                    )}
                  </div>

                  {/* Admin Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('auth.adminName')} <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="text"
                        required
                        value={form.admin_name}
                        onChange={(e) => setForm({ ...form, admin_name: e.target.value })}
                        placeholder={t('auth.placeholders.adminName')}
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  {/* Admin Email */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('auth.adminEmail')} <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="email"
                        required
                        value={form.admin_email}
                        onChange={(e) => setForm({ ...form, admin_email: e.target.value })}
                        placeholder="email@example.com"
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  {/* Admin Password */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('auth.adminPassword')} <span className="text-red-500">*</span>
                    </label>
                    <p className="text-xs text-gray-500 mb-1">{t('auth.passwordMinChars')}</p>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        required
                        minLength={8}
                        value={form.admin_password}
                        onChange={(e) => setForm({ ...form, admin_password: e.target.value })}
                        placeholder={t('auth.placeholders.enterPassword')}
                        className="w-full pl-10 pr-10 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  {/* Confirm Password */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {t('auth.confirmPassword')} <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        required
                        minLength={8}
                        value={form.confirm_password}
                        onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
                        placeholder={t('auth.placeholders.confirmPassword')}
                        className="w-full pl-10 pr-10 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
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
                    disabled={loading || cuiStatus !== 'valid'}
                    className="w-full py-2.5 bg-gradient-to-r from-teal-600 to-blue-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                {loading && <Loader2 className="w-5 h-5 animate-spin" />}
                {t('auth.registerClinic')}
              </button>
            </form>

            <p className="mt-6 text-center text-sm text-gray-500">
              {t('auth.hasAccount')}{' '}
              <Link to="/login" className="text-teal-600 hover:underline font-medium">
                {t('common.signIn')}
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterClinic;
