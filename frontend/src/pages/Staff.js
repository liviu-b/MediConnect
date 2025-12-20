import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import {
  Plus,
  Trash2,
  Edit2,
  UserCog,
  Mail,
  Phone,
  Loader2,
  X,
  Clock,
  CheckCircle,
  RefreshCw,
  Send,
  Save
} from 'lucide-react';

const Staff = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [staff, setStaff] = useState([]);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingStaff, setEditingStaff] = useState(null);
  const [form, setForm] = useState({ name: '', email: '', phone: '', role: 'RECEPTIONIST', location_id: '' });
  const [saving, setSaving] = useState(false);
  const [resendingId, setResendingId] = useState(null);
  const [error, setError] = useState('');
  const [deleteConfirmModal, setDeleteConfirmModal] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchStaff();
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      const res = await api.get('/locations');
      setLocations(res.data);
    } catch (err) {
      console.error('Error fetching locations:', err);
    }
  };

  const fetchStaff = async () => {
    try {
      const res = await api.get('/staff');
      setStaff(res.data);
    } catch (err) {
      console.error('Error fetching staff:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (staffMember = null) => {
    if (staffMember) {
      setEditingStaff(staffMember);
      setForm({
        name: staffMember.name,
        email: staffMember.email,
        phone: staffMember.phone || '',
        role: staffMember.role
      });
    } else {
      setEditingStaff(null);
      setForm({ name: '', email: '', phone: '', role: 'RECEPTIONIST' });
    }
    setShowModal(true);
    setError('');
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingStaff(null);
    setForm({ name: '', email: '', phone: '', role: 'RECEPTIONIST' });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      if (editingStaff) {
        // Update existing staff
        await api.put(`/staff/${editingStaff.staff_id}`, {
          name: form.name,
          phone: form.phone,
          role: form.role
        });
      } else {
        // Create new staff (invite)
        await api.post('/staff', form);
      }
      handleCloseModal();
      fetchStaff();
    } catch (err) {
      console.error('Error saving staff:', err);
      setError(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setSaving(false);
    }
  };

  const handleResendInvitation = async (staffId) => {
    setResendingId(staffId);
    try {
      await api.post(`/staff/${staffId}/resend-invitation`);
      fetchStaff();
    } catch (err) {
      console.error('Error resending invitation:', err);
    } finally {
      setResendingId(null);
    }
  };

  const handleDeleteClick = (member) => {
    setDeleteConfirmModal(member);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirmModal) return;
    setDeleting(true);
    try {
      await api.delete(`/staff/${deleteConfirmModal.staff_id}`);
      setDeleteConfirmModal(null);
      fetchStaff();
    } catch (err) {
      console.error('Error deleting staff:', err);
      alert(err.response?.data?.detail || t('notifications.error'));
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirmModal(null);
  };

  const getRoleLabel = (role) => {
    switch (role) {
      case 'LOCATION_ADMIN': return t('staff.locationAdmin') || 'Location Admin';
      case 'RECEPTIONIST': return t('staff.receptionist');
      case 'NURSE': return t('staff.nurse');
      case 'ADMIN': return t('staff.admin'); // Legacy
      case 'DOCTOR': return t('staff.doctor');
      default: return role;
    }
  };

  const getStatusBadge = (status) => {
    if (status === 'ACCEPTED') {
      return (
        <span className="flex items-center gap-1 text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded-full">
          <CheckCircle className="w-3 h-3" />
          {t('staff.statusAccepted')}
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 text-xs px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded-full">
        <Clock className="w-3 h-3" />
        {t('staff.statusPending')}
      </span>
    );
  };

  // Allow SUPER_ADMIN, LOCATION_ADMIN, and CLINIC_ADMIN to manage staff
  // DOCTORS should NEVER access this page - they have their own StaffDashboard
  const isAdmin = ['SUPER_ADMIN', 'LOCATION_ADMIN', 'CLINIC_ADMIN'].includes(user?.role);
  
  if (!isAdmin) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <X className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">{t('auth.accessDenied')}</h2>
          <p className="text-gray-500 mb-4">{t('auth.noPermission')}</p>
          <p className="text-sm text-gray-400">
            {user?.role === 'DOCTOR' ? 'Doctors should use the Staff Dashboard instead.' : 'Only administrators can manage staff.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('staff.title')}</h1>
          <p className="text-sm text-gray-500">{t('staff.subtitle')}</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all"
        >
          <Plus className="w-4 h-4" />
          {t('staff.inviteStaff')}
        </button>
      </div>

      {/* Staff Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : staff.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
          <UserCog className="w-12 h-12 mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500">{t('staff.noStaff')}</p>
          <button
            onClick={() => handleOpenModal()}
            className="mt-3 text-blue-600 hover:underline text-sm"
          >
            {t('staff.addFirst')}
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
          {staff.map((member) => (
            <div key={member.staff_id} className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-teal-400 flex items-center justify-center text-white shadow-sm">
                    <UserCog className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{member.name}</h3>
                    <div className="flex flex-wrap items-center gap-1 mt-1">
                      <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full font-medium">
                        {getRoleLabel(member.role)}
                      </span>
                      {getStatusBadge(member.invitation_status)}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleOpenModal(member)}
                    className="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors"
                    title={t('staff.editStaff')}
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  {member.invitation_status === 'PENDING' && (
                    <button
                      onClick={() => handleResendInvitation(member.staff_id)}
                      disabled={resendingId === member.staff_id}
                      className="p-1.5 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
                      title={t('staff.resendInvitation')}
                    >
                      {resendingId === member.staff_id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <RefreshCw className="w-4 h-4" />
                      )}
                    </button>
                  )}
                  <button
                    onClick={() => handleDeleteClick(member)}
                    className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    title={t('common.delete')}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="mt-3 space-y-1 text-sm text-gray-500">
                <p className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  {member.email}
                </p>
                {member.phone && (
                  <p className="flex items-center gap-2">
                    <Phone className="w-4 h-4" />
                    {member.phone}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Staff Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-md">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div>
                <h2 className="font-semibold text-gray-900">
                  {editingStaff ? t('staff.editStaff') : t('staff.inviteStaff')}
                </h2>
                <p className="text-sm text-gray-500">
                  {editingStaff ? t('staff.editSubtitle') : t('staff.inviteSubtitle')}
                </p>
              </div>
              <button onClick={handleCloseModal} className="p-1 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            {error && (
              <div className="mx-4 mt-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="p-4 space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('staff.staffName')}</label>
                <input
                  type="text"
                  required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('staff.staffEmail')}</label>
                <input
                  type="email"
                  required
                  disabled={editingStaff !== null}
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className={`w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    editingStaff ? 'bg-gray-50 cursor-not-allowed' : ''
                  }`}
                />
                {!editingStaff && (
                  <p className="text-xs text-gray-500 mt-1">{t('staff.emailHelp')}</p>
                )}
                {editingStaff && (
                  <p className="text-xs text-gray-400 mt-1">{t('staff.emailCannotChange')}</p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('staff.staffPhone')}</label>
                <input
                  type="tel"
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('staff.staffRole')}</label>
                <select
                  value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {/* Only SUPER_ADMIN can invite Location Admin */}
                  {user?.role === 'SUPER_ADMIN' && (
                    <option value="LOCATION_ADMIN">Location Admin</option>
                  )}
                  <option value="RECEPTIONIST">{t('staff.receptionist') || 'Receptionist'}</option>
                  <option value="DOCTOR">{t('staff.doctor') || 'Doctor'}</option>
                  <option value="NURSE">{t('staff.nurse') || 'Nurse'}</option>
                </select>
                {user?.role === 'SUPER_ADMIN' && form.role === 'LOCATION_ADMIN' && (
                  <p className="text-xs text-gray-500 mt-1">
                    Location Admins can manage their assigned locations
                  </p>
                )}
              </div>
              
              {/* Location Selector - Show only for Location Admin */}
              {!editingStaff && form.role === 'LOCATION_ADMIN' && locations.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Assigned Location <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={form.location_id}
                    onChange={(e) => setForm({ ...form, location_id: e.target.value })}
                    required
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select a location...</option>
                    {locations.map((location) => (
                      <option key={location.location_id} value={location.location_id}>
                        {location.name}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    This Location Admin will manage this location
                  </p>
                </div>
              )}
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="flex-1 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition-all"
                >
                  {t('common.cancel')}
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 py-2 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {saving ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : editingStaff ? (
                    <Save className="w-4 h-4" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  {editingStaff ? t('common.save') : t('staff.sendInvitation')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-md shadow-xl">
            <div className="p-6">
              <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mx-auto mb-4">
                <Trash2 className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 text-center mb-2">
                {t('staff.deleteConfirm')}
              </h3>
              <p className="text-sm text-gray-500 text-center mb-6">
                {deleteConfirmModal.name} ({deleteConfirmModal.email})
              </p>
              <div className="flex gap-3">
                <button
                  onClick={handleDeleteCancel}
                  disabled={deleting}
                  className="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  {t('common.cancel')}
                </button>
                <button
                  onClick={handleDeleteConfirm}
                  disabled={deleting}
                  className="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {deleting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      {t('common.delete')}...
                    </>
                  ) : (
                    <>
                      <Trash2 className="w-4 h-4" />
                      {t('common.delete')}
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Staff;