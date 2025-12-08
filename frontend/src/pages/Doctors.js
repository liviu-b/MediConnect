import { useState, useEffect } from 'react';
import { api, useAuth } from '../App';

const Doctors = () => {
  const { user } = useAuth();
  const [doctors, setDoctors] = useState([]);
  const [clinics, setClinics] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState(null);
  const [formData, setFormData] = useState({
    user_id: '',
    clinic_id: '',
    specialty: '',
    bio: '',
    consultation_duration: 30
  });
  const [saving, setSaving] = useState(false);

  const specialties = [
    'General Medicine',
    'Cardiology',
    'Dermatology',
    'Pediatrics',
    'Orthopedics',
    'Neurology',
    'Gynecology',
    'Ophthalmology',
    'ENT',
    'Psychiatry',
    'Dentistry',
    'Oncology',
    'Gastroenterology',
    'Urology',
    'Endocrinology'
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [doctorsRes, clinicsRes, usersRes] = await Promise.all([
        api.get('/doctors'),
        api.get('/clinics'),
        api.get('/users')
      ]);
      setDoctors(doctorsRes.data);
      setClinics(clinicsRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      if (editingDoctor) {
        await api.put(`/doctors/${editingDoctor.doctor_id}`, formData);
      } else {
        await api.post('/doctors', formData);
      }
      await fetchData();
      handleCloseModal();
    } catch (error) {
      console.error('Error saving doctor:', error);
      alert(error.response?.data?.detail || 'Failed to save doctor');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (doctorId) => {
    if (!window.confirm('Are you sure you want to remove this doctor?')) return;

    try {
      await api.delete(`/doctors/${doctorId}`);
      await fetchData();
    } catch (error) {
      console.error('Error deleting doctor:', error);
      alert(error.response?.data?.detail || 'Failed to delete doctor');
    }
  };

  const handleOpenModal = (doctor = null) => {
    if (doctor) {
      setEditingDoctor(doctor);
      setFormData({
        user_id: doctor.user_id,
        clinic_id: doctor.clinic_id,
        specialty: doctor.specialty,
        bio: doctor.bio || '',
        consultation_duration: doctor.consultation_duration || 30
      });
    } else {
      setEditingDoctor(null);
      setFormData({
        user_id: '',
        clinic_id: '',
        specialty: '',
        bio: '',
        consultation_duration: 30
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingDoctor(null);
    setFormData({
      user_id: '',
      clinic_id: '',
      specialty: '',
      bio: '',
      consultation_duration: 30
    });
  };

  const getClinicName = (clinicId) => {
    const clinic = clinics.find(c => c.clinic_id === clinicId);
    return clinic?.name || 'Unknown Clinic';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (user?.role !== 'ADMIN') {
    return (
      <div className="bg-white rounded-2xl p-12 text-center shadow-sm">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h3>
        <p className="text-gray-500">You don't have permission to view this page.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="doctors-page">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <p className="text-gray-500">Manage doctors and their specialties</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          data-testid="add-doctor-btn"
          className="bg-gradient-to-r from-blue-600 to-teal-500 text-white px-4 py-2.5 rounded-lg font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all flex items-center space-x-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span>Add Doctor</span>
        </button>
      </div>

      {/* Doctors Grid */}
      {doctors.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 text-center shadow-sm">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-gray-500 mb-4">No doctors registered yet</p>
          <button
            onClick={() => handleOpenModal()}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Add your first doctor
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {doctors.map((doctor) => (
            <div
              key={doctor.doctor_id}
              className="bg-white rounded-2xl p-6 shadow-sm hover-card"
              data-testid={`doctor-card-${doctor.doctor_id}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-4">
                  {doctor.picture ? (
                    <img
                      src={doctor.picture}
                      alt={doctor.name}
                      className="w-14 h-14 rounded-xl object-cover"
                    />
                  ) : (
                    <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-teal-500 rounded-xl flex items-center justify-center text-white text-xl font-bold">
                      {doctor.name?.charAt(0) || 'D'}
                    </div>
                  )}
                  <div>
                    <h3 className="font-semibold text-gray-900">{doctor.name?.startsWith('Dr.') ? doctor.name : `Dr. ${doctor.name}`}</h3>
                    <p className="text-sm text-blue-600 font-medium">{doctor.specialty}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleOpenModal(doctor)}
                    data-testid={`edit-doctor-${doctor.doctor_id}`}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDelete(doctor.doctor_id)}
                    data-testid={`delete-doctor-${doctor.doctor_id}`}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>

              {doctor.bio && (
                <p className="text-gray-500 text-sm mb-4 line-clamp-2">{doctor.bio}</p>
              )}

              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2 text-gray-600">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <span>{getClinicName(doctor.clinic_id)}</span>
                </div>
                <div className="flex items-center space-x-2 text-gray-600">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{doctor.consultation_duration} min consultation</span>
                </div>
                {doctor.email && (
                  <div className="flex items-center space-x-2 text-gray-600">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <span className="truncate">{doctor.email}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center modal-backdrop" data-testid="doctor-modal">
          <div className="bg-white rounded-2xl p-6 w-full max-w-lg mx-4 animate-fadeIn max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">
              {editingDoctor ? 'Edit Doctor' : 'Add New Doctor'}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">User Account</label>
                <select
                  value={formData.user_id}
                  onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                  required
                  disabled={!!editingDoctor}
                  data-testid="doctor-user-select"
                  className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                >
                  <option value="">Select a user...</option>
                  {users.map(u => (
                    <option key={u.user_id} value={u.user_id}>
                      {u.name} ({u.email})
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">Select an existing user to make them a doctor</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Clinic</label>
                <select
                  value={formData.clinic_id}
                  onChange={(e) => setFormData({ ...formData, clinic_id: e.target.value })}
                  required
                  data-testid="doctor-clinic-select"
                  className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select a clinic...</option>
                  {clinics.map(clinic => (
                    <option key={clinic.clinic_id} value={clinic.clinic_id}>
                      {clinic.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Specialty</label>
                <select
                  value={formData.specialty}
                  onChange={(e) => setFormData({ ...formData, specialty: e.target.value })}
                  required
                  data-testid="doctor-specialty-select"
                  className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select specialty...</option>
                  {specialties.map(spec => (
                    <option key={spec} value={spec}>{spec}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Consultation Duration (minutes)</label>
                <select
                  value={formData.consultation_duration}
                  onChange={(e) => setFormData({ ...formData, consultation_duration: parseInt(e.target.value) })}
                  data-testid="doctor-duration-select"
                  className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value={15}>15 minutes</option>
                  <option value={30}>30 minutes</option>
                  <option value={45}>45 minutes</option>
                  <option value={60}>60 minutes</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bio (optional)</label>
                <textarea
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  data-testid="doctor-bio-input"
                  className="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                  placeholder="Brief description of the doctor's experience and expertise"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  data-testid="save-doctor-btn"
                  className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-teal-500 text-white font-medium hover:shadow-lg disabled:opacity-50"
                >
                  {saving ? 'Saving...' : editingDoctor ? 'Update Doctor' : 'Add Doctor'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Doctors;
