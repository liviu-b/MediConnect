import { useLocation, Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { CheckCircle2, Building2, Mail, Clock, ArrowLeft } from 'lucide-react';
import { useEffect } from 'react';

const AccessRequestSent = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const { requestId, organizationName, email } = location.state || {};

  useEffect(() => {
    // Redirect if no state data
    if (!requestId) {
      navigate('/register-clinic', { replace: true });
    }
  }, [requestId, navigate]);

  if (!requestId) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Success Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
          {/* Success Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle2 className="w-12 h-12 text-green-600" />
            </div>
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold text-center text-gray-900 mb-3">
            Access Request Sent!
          </h1>
          
          {/* Subtitle */}
          <p className="text-center text-gray-600 mb-8">
            Your request to join <span className="font-semibold text-gray-900">{organizationName}</span> has been submitted successfully.
          </p>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <div className="flex items-start gap-3 mb-4">
              <Building2 className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900 mb-1">Organization</p>
                <p className="text-gray-700">{organizationName}</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <Mail className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900 mb-1">Your Email</p>
                <p className="text-gray-700">{email}</p>
              </div>
            </div>
          </div>

          {/* What's Next Section */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-teal-600" />
              What Happens Next?
            </h2>
            
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center text-teal-600 font-semibold text-sm">
                  1
                </div>
                <div>
                  <p className="font-medium text-gray-900">Review Process</p>
                  <p className="text-sm text-gray-600">
                    The organization administrators will review your access request.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center text-teal-600 font-semibold text-sm">
                  2
                </div>
                <div>
                  <p className="font-medium text-gray-900">Email Notification</p>
                  <p className="text-sm text-gray-600">
                    You'll receive an email at <span className="font-medium">{email}</span> when your request is approved or rejected.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center text-teal-600 font-semibold text-sm">
                  3
                </div>
                <div>
                  <p className="font-medium text-gray-900">Access Granted</p>
                  <p className="text-sm text-gray-600">
                    Once approved, you can log in with your credentials and start using the platform.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Request ID */}
          <div className="bg-gray-50 rounded-lg p-4 mb-8">
            <p className="text-xs text-gray-500 mb-1">Request ID</p>
            <p className="text-sm font-mono text-gray-700">{requestId}</p>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3">
            <Link
              to="/register-clinic?tab=login"
              className="flex-1 py-3 px-6 bg-gradient-to-r from-teal-600 to-blue-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all text-center"
            >
              Go to Login
            </Link>
            <Link
              to="/"
              className="flex-1 py-3 px-6 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-all text-center flex items-center justify-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Link>
          </div>

          {/* Help Text */}
          <p className="text-center text-sm text-gray-500 mt-6">
            Questions? Contact the organization administrators directly or reach out to our support team.
          </p>
        </div>

        {/* MediConnect Logo */}
        <div className="text-center mt-8">
          <Link to="/" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors">
            <Building2 className="w-5 h-5" />
            <span className="font-semibold">MediConnect</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AccessRequestSent;
