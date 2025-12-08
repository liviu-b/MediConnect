import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Mail, Lock, User, Phone, Building2, Loader2, ArrowLeft, KeyRound, MapPin, CheckCircle2, XCircle, FileText } from 'lucide-react';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { api } from '../App';

const RegisterClinic = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [codeValid, setCodeValid] = useState(null);
  const [validatingCode, setValidatingCode] = useState(false);
  const [form, setForm] = useState({
    registration_code: '',
    clinic_name: '',
    address: '',
    phone: '',
    email: '',
    description: '',
    admin_name: '',
    admin_email: '',
    admin_password: '',
    admin_phone: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const validateCode = async () => {
    if (!form.registration_code) return;
    setValidatingCode(true);
    try {
      const res = await api.post(`/auth/validate-code?code=${form.registration_code}`);
      setCodeValid(res.data.valid);
      if (res.data.valid) {
        setStep(2);
      }
    } catch (err) {
      setCodeValid(false);
    } finally {
      setValidatingCode(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/auth/register-clinic', form);
      sessionStorage.setItem('just_authenticated', 'true');
      navigate('/dashboard', { replace: true, state: { user: res.data.user } });
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
          <h1 className="text-4xl font-bold mb-4">{t('auth.clinicSignUpTitle')}</h1>
          <p className="text-lg text-white/80">{t('auth.clinicSignUpSubtitle')}</p>
          <div className="mt-8 space-y-3">
            <div className={`flex items-center gap-3 ${step >= 1 ? 'text-white' : 'text-white/50'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-white text-teal-600' : 'bg-white/30'}`}>1</div>
              <span>{t('auth.registrationCode')}</span>
            </div>
            <div className={`flex items-center gap-3 ${step >= 2 ? 'text-white' : 'text-white/50'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-white text-teal-600' : 'bg-white/30'}`}>2</div>
              <span>{t('clinics.title')}</span>
            </div>
            <div className={`flex items-center gap-3 ${step >= 3 ? 'text-white' : 'text-white/50'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 3 ? 'bg-white text-teal-600' : 'bg-white/30'}`}>3</div>
              <span>{t('auth.adminDetails')}</span>
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

        <div className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-md">
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Step 1: Code Validation */}
            {step === 1 && (
              <div>
                <div className="flex items-center gap-2 mb-6">
                  <KeyRound className="w-6 h-6 text-teal-600" />
                  <h2 className="text-2xl font-bold text-gray-900">{t('auth.registrationCode')}</h2>
                </div>
                <p className="text-gray-500 mb-4">{t('auth.registrationCodeHelp')}</p>
                <div className="space-y-4">
                  <div className="relative">
                    <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={form.registration_code}
                      onChange={(e) => {
                        setForm({ ...form, registration_code: e.target.value.toUpperCase() });
                        setCodeValid(null);
                      }}
                      className="w-full pl-10 pr-10 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent uppercase"
                      placeholder="XXXXX"
                    />
                    {codeValid === true && <CheckCircle2 className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-green-500" />}
                    {codeValid === false && <XCircle className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-red-500" />}
                  </div>
                  {codeValid === false && (
                    <p className="text-sm text-red-500">{t('auth.codeInvalid')}</p>
                  )}
                  <button
                    onClick={validateCode}
                    disabled={!form.registration_code || validatingCode}
                    className="w-full py-2.5 bg-gradient-to-r from-teal-600 to-blue-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {validatingCode && <Loader2 className="w-5 h-5 animate-spin" />}
                    {t('auth.validateCode')}
                  </button>
                </div>
              </div>
            )}

            {/* Step 2: Clinic Details */}
            {step === 2 && (
              <div>
                <div className="flex items-center gap-2 mb-6">
                  <Building2 className="w-6 h-6 text-teal-600" />
                  <h2 className="text-2xl font-bold text-gray-900">{t('auth.clinicSignUpTitle')}</h2>
                </div>
                <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); setStep(3); }}>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.clinicName')}</label>
                    <div className="relative">
                      <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="text"
                        required
                        value={form.clinic_name}
                        onChange={(e) => setForm({ ...form, clinic_name: e.target.value })}
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.clinicAddress')}</label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="text"
                        required
                        value={form.address}
                        onChange={(e) => setForm({ ...form, address: e.target.value })}
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.clinicPhone')}</label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="tel"
                          required
                          value={form.phone}
                          onChange={(e) => setForm({ ...form, phone: e.target.value })}
                          className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.clinicEmail')}</label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="email"
                          required
                          value={form.email}
                          onChange={(e) => setForm({ ...form, email: e.target.value })}
                          className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                        />
                      </div>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.clinicDescription')}</label>
                    <div className="relative">
                      <FileText className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                      <textarea
                        value={form.description}
                        onChange={(e) => setForm({ ...form, description: e.target.value })}
                        rows={2}
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent resize-none"
                      />
                    </div>
                  </div>
                  <div className="flex gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setStep(1)}
                      className="flex-1 py-2.5 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                    >
                      {t('common.back')}
                    </button>
                    <button
                      type="submit"
                      className="flex-1 py-2.5 bg-gradient-to-r from-teal-600 to-blue-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                    >
                      {t('common.next')}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Step 3: Admin Details */}
            {step === 3 && (
              <div>
                <div className="flex items-center gap-2 mb-6">
                  <User className="w-6 h-6 text-teal-600" />
                  <h2 className="text-2xl font-bold text-gray-900">{t('auth.adminDetails')}</h2>
                </div>
                <form onSubmit={handleSubmit} className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.adminName')}</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="text"
                        required
                        value={form.admin_name}
                        onChange={(e) => setForm({ ...form, admin_name: e.target.value })}
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.adminEmail')}</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="email"
                        required
                        value={form.admin_email}
                        onChange={(e) => setForm({ ...form, admin_email: e.target.value })}
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.adminPhone')}</label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="tel"
                        value={form.admin_phone}
                        onChange={(e) => setForm({ ...form, admin_phone: e.target.value })}
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{t('auth.adminPassword')}</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        type="password"
                        required
                        minLength={6}
                        value={form.admin_password}
                        onChange={(e) => setForm({ ...form, admin_password: e.target.value })}
                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div className="flex gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setStep(2)}
                      className="flex-1 py-2.5 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                    >
                      {t('common.back')}
                    </button>
                    <button
                      type="submit"
                      disabled={loading}
                      className="flex-1 py-2.5 bg-gradient-to-r from-teal-600 to-blue-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {loading && <Loader2 className="w-5 h-5 animate-spin" />}
                      {t('common.submit')}
                    </button>
                  </div>
                </form>
              </div>
            )}

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
