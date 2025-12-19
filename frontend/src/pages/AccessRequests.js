import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { UserPlus, Clock, CheckCircle, XCircle, Loader2, Mail, MapPin, Building2 } from 'lucide-react';
import { api } from '../App';
import { useAuth } from '../App';

const AccessRequests = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('PENDING');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');

  // Approve form state
  const [approveForm, setApproveForm] = useState({
    role: 'LOCATION_ADMIN',
    assigned_location_ids: [],
    create_new_location: false
  });

  // Reject form state
  const [rejectForm, setRejectForm] = useState({
    rejection_reason: ''
  });

  const [locations, setLocations] = useState([]);

  useEffect(() => {
    fetchRequests();
    fetchLocations();
  }, [filter]);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/access-requests?status=${filter}`);
      setRequests(res.data);
    } catch (error) {
      console.error('Error fetching requests:', error);
      setError(t('accessRequests.failedToLoad'));
    } finally {
      setLoading(false);
    }
  };

  const fetchLocations = async () => {
    try {
      const res = await api.get('/locations');
      setLocations(res.data);
    } catch (error) {
      console.error('Error fetching locations:', error);
    }
  };

  const handleApprove = async () => {
    if (!selectedRequest) return;

    setActionLoading(true);
    setError('');

    try {
      await api.post(`/access-requests/${selectedRequest.request_id}/approve`, approveForm);
      
      // Refresh requests
      await fetchRequests();
      
      // Close modal and reset
      setShowApproveModal(false);
      setSelectedRequest(null);
      setApproveForm({
        role: 'LOCATION_ADMIN',
        assigned_location_ids: [],
        create_new_location: false
      });
    } catch (err) {
      setError(err.response?.data?.detail || t('accessRequests.failedToApprove'));
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedRequest || !rejectForm.rejection_reason.trim()) {
      setError(t('accessRequests.provideRejectionReason'));
      return;
    }

    setActionLoading(true);
    setError('');

    try {
      await api.post(`/access-requests/${selectedRequest.request_id}/reject`, rejectForm);
      
      // Refresh requests
      await fetchRequests();
      
      // Close modal and reset
      setShowRejectModal(false);
      setSelectedRequest(null);
      setRejectForm({ rejection_reason: '' });
    } catch (err) {
      setError(err.response?.data?.detail || t('accessRequests.failedToReject'));
    } finally {
      setActionLoading(false);
    }
  };

  const openApproveModal = (request) => {
    setSelectedRequest(request);
    setShowApproveModal(true);
    setError('');
  };

  const openRejectModal = (request) => {
    setSelectedRequest(request);
    setShowRejectModal(true);
    setError('');
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    const badges = {
      PENDING: { color: 'bg-yellow-100 text-yellow-800', icon: Clock },
      APPROVED: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      REJECTED: { color: 'bg-red-100 text-red-800', icon: XCircle }
    };
    
    const badge = badges[status] || badges.PENDING;
    const Icon = badge.icon;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}>
        <Icon className="w-3 h-3" />
        {t(`accessRequests.${status.toLowerCase()}`)}
      </span>
    );
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <UserPlus className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">{t('accessRequests.title')}</h1>
        </div>
        <p className="text-gray-600">{t('accessRequests.subtitle')}</p>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6 bg-white p-1 rounded-lg border border-gray-200 w-fit">
        {['PENDING', 'APPROVED', 'REJECTED'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              filter === status
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            {t(`accessRequests.${status.toLowerCase()}`)}
            {requests.length > 0 && filter === status && (
              <span className="ml-2 px-2 py-0.5 bg-white/20 rounded-full text-xs">
                {requests.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-600 rounded-lg">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : requests.length === 0 ? (
        /* Empty State */
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <UserPlus className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {filter === 'PENDING' 
              ? t('accessRequests.noPendingRequests')
              : t('accessRequests.noRequestsFound', { status: t(`accessRequests.${filter.toLowerCase()}`) })
            }
          </h3>
          <p className="text-gray-500">
            {filter === 'PENDING' 
              ? t('accessRequests.noPendingRequestsDesc')
              : t('accessRequests.noRequestsFound', { status: t(`accessRequests.${filter.toLowerCase()}`) })
            }
          </p>
        </div>
      ) : (
        /* Request Cards */
        <div className="space-y-4">
          {requests.map((request) => (
            <div
              key={request.request_id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <UserPlus className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {request.requester_name}
                    </h3>
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                      <Mail className="w-4 h-4" />
                      {request.requester_email}
                    </div>
                    {request.requester_phone && (
                      <p className="text-sm text-gray-500">
                        📞 {request.requester_phone}
                      </p>
                    )}
                  </div>
                </div>
                {getStatusBadge(request.status)}
              </div>

              {/* Proposed Location */}
              {request.proposed_location_name && (
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <p className="text-xs font-medium text-gray-500 mb-2">{t('accessRequests.proposedLocation')}</p>
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-gray-600" />
                    <span className="font-medium text-gray-900">{request.proposed_location_name}</span>
                    {request.proposed_location_city && (
                      <>
                        <MapPin className="w-4 h-4 text-gray-400 ml-2" />
                        <span className="text-gray-600">{request.proposed_location_city}</span>
                      </>
                    )}
                  </div>
                </div>
              )}

              {/* Metadata */}
              <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
                <span>{t('accessRequests.requestId')}: {request.request_id}</span>
                <span>•</span>
                <span>{t('accessRequests.submitted')}: {formatDate(request.created_at)}</span>
              </div>

              {/* Actions */}
              {request.status === 'PENDING' && (
                <div className="flex gap-3">
                  <button
                    onClick={() => openApproveModal(request)}
                    className="flex-1 py-2 px-4 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    {t('accessRequests.approve')}
                  </button>
                  <button
                    onClick={() => openRejectModal(request)}
                    className="flex-1 py-2 px-4 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <XCircle className="w-4 h-4" />
                    {t('accessRequests.reject')}
                  </button>
                </div>
              )}

              {/* Rejection Reason */}
              {request.status === 'REJECTED' && request.rejection_reason && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-xs font-medium text-red-800 mb-1">{t('accessRequests.rejectionReason')}:</p>
                  <p className="text-sm text-red-700">{request.rejection_reason}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Approve Modal */}
      {showApproveModal && selectedRequest && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">{t('accessRequests.approveRequest')}</h2>
            
            <div className="mb-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm font-medium text-gray-900">{selectedRequest.requester_name}</p>
              <p className="text-xs text-gray-600">{selectedRequest.requester_email}</p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Role Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('accessRequests.assignRole')}
              </label>
              <select
                value={approveForm.role}
                onChange={(e) => setApproveForm({ ...approveForm, role: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="SUPER_ADMIN">{t('accessRequests.roles.superAdmin')}</option>
                <option value="LOCATION_ADMIN">{t('accessRequests.roles.locationAdmin')}</option>
                <option value="STAFF">{t('accessRequests.roles.staff')}</option>
                <option value="DOCTOR">{t('accessRequests.roles.doctor')}</option>
                <option value="ASSISTANT">{t('accessRequests.roles.assistant')}</option>
              </select>
            </div>

            {/* Location Assignment */}
            {approveForm.role !== 'SUPER_ADMIN' && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('accessRequests.assignLocations')}
                </label>
                <div className="space-y-2 max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-3">
                  {locations.map((location) => (
                    <label key={location.location_id} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={approveForm.assigned_location_ids.includes(location.location_id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setApproveForm({
                              ...approveForm,
                              assigned_location_ids: [...approveForm.assigned_location_ids, location.location_id]
                            });
                          } else {
                            setApproveForm({
                              ...approveForm,
                              assigned_location_ids: approveForm.assigned_location_ids.filter(id => id !== location.location_id)
                            });
                          }
                        }}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">{location.name} - {location.city}</span>
                    </label>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {t('accessRequests.leaveEmptyForAll')}
                </p>
              </div>
            )}

            {/* Create New Location Option */}
            {selectedRequest.proposed_location_name && (
              <div className="mb-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={approveForm.create_new_location}
                    onChange={(e) => setApproveForm({ ...approveForm, create_new_location: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">
                    {t('accessRequests.createProposedLocation')}: <span className="font-medium">{selectedRequest.proposed_location_name}</span>
                  </span>
                </label>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowApproveModal(false);
                  setSelectedRequest(null);
                  setError('');
                }}
                disabled={actionLoading}
                className="flex-1 py-2 px-4 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={handleApprove}
                disabled={actionLoading}
                className="flex-1 py-2 px-4 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {actionLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                {t('accessRequests.approve')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && selectedRequest && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">{t('accessRequests.rejectRequest')}</h2>
            
            <div className="mb-4 p-3 bg-red-50 rounded-lg">
              <p className="text-sm font-medium text-gray-900">{selectedRequest.requester_name}</p>
              <p className="text-xs text-gray-600">{selectedRequest.requester_email}</p>
            </div>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Rejection Reason */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('accessRequests.rejectionReasonRequired')}
              </label>
              <textarea
                value={rejectForm.rejection_reason}
                onChange={(e) => setRejectForm({ rejection_reason: e.target.value })}
                placeholder={t('accessRequests.rejectionReasonPlaceholder')}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
              />
              <p className="text-xs text-gray-500 mt-1">
                {t('accessRequests.rejectionReasonHelp')}
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setSelectedRequest(null);
                  setError('');
                }}
                disabled={actionLoading}
                className="flex-1 py-2 px-4 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={handleReject}
                disabled={actionLoading || !rejectForm.rejection_reason.trim()}
                className="flex-1 py-2 px-4 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {actionLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                {t('accessRequests.reject')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AccessRequests;
