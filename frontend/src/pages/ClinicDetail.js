import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import {
  Building2,
  MapPin,
  Phone,
  Mail,
  Clock,
  ArrowLeft,
  Loader2,
  Star,
  StarHalf,
  Briefcase,
  User,
  Calendar,
  Send,
  MessageSquare
} from 'lucide-react';

const DAYS_ORDER = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

const ClinicDetail = () => {
  const { t } = useTranslation();
  const { clinicId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [clinic, setClinic] = useState(null);
  const [services, setServices] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState({ average_rating: 0, review_count: 0 });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('info');

  // Review form
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' });
  const [submittingReview, setSubmittingReview] = useState(false);
  const [reviewError, setReviewError] = useState('');

  // Admin response state
  const [respondingToReview, setRespondingToReview] = useState(null);
  const [responseText, setResponseText] = useState('');
  const [submittingResponse, setSubmittingResponse] = useState(false);

  useEffect(() => {
    fetchClinicData();
  }, [clinicId]);

  const fetchClinicData = async () => {
    setLoading(true);
    try {
      const [clinicRes, servicesRes, reviewsRes, statsRes] = await Promise.all([
        api.get(`/clinics/${clinicId}`),
        api.get(`/services?clinic_id=${clinicId}`),
        api.get(`/clinics/${clinicId}/reviews`),
        api.get(`/clinics/${clinicId}/stats`)
      ]);

      setClinic(clinicRes.data);
      setServices(servicesRes.data);
      setReviews(reviewsRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Error fetching clinic data:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (rating, size = 'md') => {
    const sizeClass = size === 'lg' ? 'w-5 h-5' : 'w-4 h-4';
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 0; i < fullStars; i++) {
      stars.push(<Star key={i} className={`${sizeClass} fill-yellow-400 text-yellow-400`} />);
    }
    if (hasHalfStar) {
      stars.push(<StarHalf key="half" className={`${sizeClass} fill-yellow-400 text-yellow-400`} />);
    }
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<Star key={`empty-${i}`} className={`${sizeClass} text-gray-300`} />);
    }

    return stars;
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    setSubmittingReview(true);
    setReviewError('');

    try {
      await api.post(`/clinics/${clinicId}/reviews`, {
        clinic_id: clinicId,
        rating: reviewForm.rating,
        comment: reviewForm.comment
      });

      setShowReviewForm(false);
      setReviewForm({ rating: 5, comment: '' });
      fetchClinicData(); // Refresh reviews
    } catch (err) {
      setReviewError(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setSubmittingReview(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const getCurrencySymbol = (currency) => {
    return currency === 'EURO' ? '€' : 'LEI';
  };

  const formatPrice = (price, currency) => {
    const symbol = getCurrencySymbol(currency);
    if (currency === 'LEI') {
      return `${price.toFixed(2)} ${symbol}`;
    }
    return `${symbol}${price.toFixed(2)}`;
  };

  const handleRespondToReview = async (reviewId) => {
    setSubmittingResponse(true);
    try {
      await api.post(`/clinics/${clinicId}/reviews/${reviewId}/respond`, {
        response: responseText
      });
      setRespondingToReview(null);
      setResponseText('');
      fetchClinicData(); // Refresh reviews
    } catch (err) {
      console.error('Error responding to review:', err);
      alert(t('notifications.error'));
    } finally {
      setSubmittingResponse(false);
    }
  };

  const isClinicAdmin = user?.role === 'CLINIC_ADMIN' && user?.clinic_id === clinicId;

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!clinic) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">{t('clinics.notFound')}</p>
        <Link to="/clinics" className="text-blue-600 hover:underline mt-2 inline-block">
          {t('common.goBack')}
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Back Button */}
      <button
        onClick={() => {
          // Navigate back to appropriate page based on user role
          if (user?.role === 'PATIENT') {
            navigate('/patient-dashboard?tab=clinics');
          } else {
            navigate('/clinics');
          }
        }}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        {t('common.goBack')}
      </button>

      {/* Clinic Header */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-blue-500 to-teal-400 flex items-center justify-center text-white flex-shrink-0">
            <Building2 className="w-8 h-8" />
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900">{clinic.name}</h1>
            {clinic.description && (
              <p className="text-gray-600 mt-1">{clinic.description}</p>
            )}

            {/* Rating */}
            <div className="flex items-center gap-2 mt-2">
              <div className="flex">{renderStars(stats.average_rating, 'lg')}</div>
              <span className="text-lg font-semibold text-gray-900">{stats.average_rating.toFixed(1)}</span>
              <span className="text-gray-500">({stats.review_count} {t('clinics.reviews')})</span>
            </div>
          </div>
        </div>

        {/* Contact Info */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
          <p className="flex items-center gap-2 text-gray-600">
            <MapPin className="w-4 h-4 text-gray-400" />
            {clinic.address}
          </p>
          {clinic.phone && (
            <p className="flex items-center gap-2 text-gray-600">
              <Phone className="w-4 h-4 text-gray-400" />
              {clinic.phone}
            </p>
          )}
          {clinic.email && (
            <p className="flex items-center gap-2 text-gray-600">
              <Mail className="w-4 h-4 text-gray-400" />
              {clinic.email}
            </p>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('info')}
          className={`px-4 py-2 font-medium transition-colors ${activeTab === 'info'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
            }`}
        >
          {t('clinics.info')}
        </button>
        <button
          onClick={() => setActiveTab('services')}
          className={`px-4 py-2 font-medium transition-colors ${activeTab === 'services'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
            }`}
        >
          {t('nav.services')} ({services.length})
        </button>
        <button
          onClick={() => setActiveTab('reviews')}
          className={`px-4 py-2 font-medium transition-colors ${activeTab === 'reviews'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-gray-500 hover:text-gray-700'
            }`}
        >
          {t('clinics.reviews')} ({reviews.length})
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'info' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-600" />
            {t('settings.operatingHours')}
          </h2>

          {clinic.working_hours ? (
            <div className="space-y-2">
              {DAYS_ORDER.map((day) => {
                const hours = clinic.working_hours[day];
                const isToday = DAYS_ORDER[new Date().getDay() === 0 ? 6 : new Date().getDay() - 1] === day;

                return (
                  <div
                    key={day}
                    className={`flex items-center justify-between py-2 px-3 rounded-lg ${isToday ? 'bg-blue-50' : ''
                      }`}
                  >
                    <span className={`font-medium ${isToday ? 'text-blue-700' : 'text-gray-700'}`}>
                      {t(`days.${day}`)}
                      {isToday && <span className="ml-2 text-xs text-blue-500">({t('clinics.today')})</span>}
                    </span>
                    <span className={hours ? 'text-gray-600' : 'text-red-500'}>
                      {hours ? `${hours.start} - ${hours.end}` : t('settings.closed')}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-gray-500">{t('clinics.noHoursSet')}</p>
          )}
        </div>
      )}

      {activeTab === 'services' && (
        <div className="space-y-3">
          {services.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
              <Briefcase className="w-12 h-12 mx-auto text-gray-300 mb-3" />
              <p className="text-gray-500">{t('services.noServices')}</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-3">
              {services.map((service) => (
                <div key={service.service_id} className="bg-white rounded-xl border border-gray-200 p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-400 flex items-center justify-center text-white">
                      <Briefcase className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{service.name}</h3>
                      {service.description && (
                        <p className="text-sm text-gray-500">{service.description}</p>
                      )}
                      <div className="flex items-center gap-4 mt-2 text-sm">
                        <span className="flex items-center gap-1 text-gray-500">
                          <Clock className="w-4 h-4" />
                          {service.duration} min
                        </span>
                        <span className="font-semibold text-green-600">
                          {formatPrice(service.price, service.currency || 'LEI')}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'reviews' && (
        <div className="space-y-4">
          {/* Add Review Button - Only for patients */}
          {user && !isClinicAdmin && !showReviewForm && (
            <button
              onClick={() => setShowReviewForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all"
            >
              <MessageSquare className="w-4 h-4" />
              {t('clinics.writeReview')}
            </button>
          )}

          {/* Review Form */}
          {showReviewForm && (
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-3">{t('clinics.writeReview')}</h3>

              {reviewError && (
                <div className="mb-3 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                  {reviewError}
                </div>
              )}

              <form onSubmit={handleSubmitReview} className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('clinics.rating')}</label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setReviewForm({ ...reviewForm, rating: star })}
                        className="focus:outline-none"
                      >
                        <Star
                          className={`w-8 h-8 transition-colors ${star <= reviewForm.rating
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-gray-300 hover:text-yellow-300'
                            }`}
                        />
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('clinics.comment')}</label>
                  <textarea
                    value={reviewForm.comment}
                    onChange={(e) => setReviewForm({ ...reviewForm, comment: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    placeholder={t('clinics.reviewPlaceholder')}
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowReviewForm(false);
                      setReviewError('');
                    }}
                    className="px-4 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                  >
                    {t('common.cancel')}
                  </button>
                  <button
                    type="submit"
                    disabled={submittingReview}
                    className="px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center gap-2"
                  >
                    {submittingReview && <Loader2 className="w-4 h-4 animate-spin" />}
                    <Send className="w-4 h-4" />
                    {t('clinics.submitReview')}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Reviews List */}
          {reviews.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
              <MessageSquare className="w-12 h-12 mx-auto text-gray-300 mb-3" />
              <p className="text-gray-500">{t('clinics.noReviews')}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {reviews.map((review) => (
                <div key={review.review_id} className="bg-white rounded-xl border border-gray-200 p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-teal-400 flex items-center justify-center text-white font-semibold">
                      {review.user_name?.charAt(0) || 'U'}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-gray-900">{review.user_name}</h4>
                        <span className="text-xs text-gray-500">{formatDate(review.created_at)}</span>
                      </div>
                      <div className="flex mt-1">{renderStars(review.rating)}</div>
                      {review.comment && (
                        <p className="text-gray-600 mt-2">{review.comment}</p>
                      )}

                      {/* Admin Response */}
                      {review.admin_response && (
                        <div className="mt-3 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                          <p className="text-sm text-gray-700">{review.admin_response}</p>
                        </div>
                      )}

                      {/* Admin - Add Response */}
                      {isClinicAdmin && !review.admin_response && (
                        <div className="mt-3">
                          {respondingToReview === review.review_id ? (
                            <div className="space-y-2">
                              <textarea
                                value={responseText}
                                onChange={(e) => setResponseText(e.target.value)}
                                rows={2}
                                placeholder={t('clinics.responseRomânăPlaceholder')}
                                className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm"
                              />
                              <div className="flex gap-2">
                                <button
                                  onClick={() => {
                                    setRespondingToReview(null);
                                    setResponseText('');
                                  }}
                                  className="px-3 py-1 text-sm border border-gray-200 rounded-lg hover:bg-gray-50"
                                >
                                  {t('common.cancel')}
                                </button>
                                <button
                                  onClick={() => handleRespondToReview(review.review_id)}
                                  disabled={submittingResponse}
                                  className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-1"
                                >
                                  {submittingResponse && <Loader2 className="w-3 h-3 animate-spin" />}
                                  {t('clinics.respond')}
                                </button>
                              </div>
                            </div>
                          ) : (
                            <button
                              onClick={() => setRespondingToReview(review.review_id)}
                              className="text-sm text-blue-600 hover:underline"
                            >
                              {t('clinics.respondToReview')}
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ClinicDetail;