import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth, api } from '../App';
import {
  Plus,
  Trash2,
  Edit2,
  Stethoscope,
  Mail,
  Phone,
  Clock,
  Loader2,
  X,
  Euro,
  Coins,
  UserCog,
  Calendar,
  Search,
  Filter,
  ChevronDown,
  MapPin,
  Building2,
  Star,
  Award,
  Users
} from 'lucide-react';

// Specialty keys for translation
const specialtyKeys = [
  'anesthesiology',
  'cardiology',
  'dentistry',
  'dermatology',
  'emergencyMedicine',
  'endocrinology',
  'gastroenterology',
  'generalPractice',
  'generalSurgery',
  'geriatrics',
  'gynecology',
  'hematology',
  'immunology',
  'medicalTests',
  'infectiousDisease',
  'nephrology',
  'neurology',
  'obstetrics',
  'oncology',
  'ophthalmology',
  'orthopedics',
  'otolaryngology',
  'pediatrics',
  'plasticSurgery',
  'psychiatry',
  'pulmonology',
  'radiology',
  'rheumatology',
  'sportsMedicine',
  'urology',
];

const CURRENCIES = [
  { code: 'LEI', symbol: 'LEI' },
  { code: 'EURO', symbol: '€' }
];

const Doctors = () => {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [doctors, setDoctors] = useState([]);
  const [filteredDoctors, setFilteredDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSpecialty, setSelectedSpecialty] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [form, setForm] = useState({
    name: '',
    email: '',
    phone: '',
    specialty: '',
    bio: '',
    consultation_duration: 30,
    consultation_fee: 0,
    currency: 'LEI'
  });
  const [saving, setSaving] = useState(false);

  const isClinicAdmin = user?.role === 'CLINIC_ADMIN';
  const isSuperAdmin = user?.role === 'SUPER_ADMIN';
  const canManageDoctors = isClinicAdmin || isSuperAdmin;

  useEffect(() => {
    fetchDoctors();
  }, []);

  // Listen for location changes
  useEffect(() => {
    const handleLocationChange = () => {
      fetchDoctors();
    };
    
    window.addEventListener('locationChanged', handleLocationChange);
    return () => window.removeEventListener('locationChanged', handleLocationChange);
  }, []);

  // Filter doctors when search or specialty changes
  useEffect(() => {
    filterDoctors();
  }, [doctors, searchTerm, selectedSpecialty]);

  const fetchDoctors = async () => {
    try {
      const res = await api.get('/doctors');
      setDoctors(res.data);
    } catch (err) {
      console.error('Error fetching doctors:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterDoctors = () => {
    let filtered = [...doctors];

    // Filter by search term
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(doctor =>
        doctor.name.toLowerCase().includes(search) ||
        doctor.email.toLowerCase().includes(search) ||
        (doctor.specialty && t(`specialties.${doctor.specialty}`).toLowerCase().includes(search))
      );
    }

    // Filter by specialty
    if (selectedSpecialty) {
      filtered = filtered.filter(doctor => doctor.specialty === selectedSpecialty);
    }

    setFilteredDoctors(filtered);
  };

  const openModal = (doctor = null) => {
    if (doctor) {
      setEditingDoctor(doctor);
      setForm({
        name: doctor.name,
        email: doctor.email,
        phone: doctor.phone || '',
        specialty: doctor.specialty,
        bio: doctor.bio || '',
        consultation_duration: doctor.consultation_duration,
        consultation_fee: doctor.consultation_fee,
        currency: doctor.currency || 'LEI'
      });
    } else {
      setEditingDoctor(null);
      setForm({
        name: '',
        email: '',
        phone: '',
        specialty: '',
        bio: '',
        consultation_duration: 30,
        consultation_fee: 0,
        currency: 'LEI'
      });
    }
    setShowModal(true);
  };
  
  const getCurrencySymbol = (currency) => {
    const curr = CURRENCIES.find(c => c.code === currency);
    return curr ? curr.symbol : currency;
  };

  const formatPrice = (price, currency) => {
    const symbol = getCurrencySymbol(currency);
    if (currency === 'LEI') {
      return `${price.toFixed(2)} ${symbol}`;
    }
    return `${symbol}${price.toFixed(2)}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingDoctor) {
        await api.put(`/doctors/${editingDoctor.doctor_id}`, form);
      } else {
        await api.post('/doctors', form);
      }
      setShowModal(false);
      fetchDoctors();
    } catch (err) {
      console.error('Error saving doctor:', err);
      alert(t('notifications.error') || 'An error occurred');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (doctorId) => {
    if (!window.confirm(t('doctors.deleteConfirm') || 'Are you sure you want to delete this doctor?')) return;
    try {
      await api.delete(`/doctors/${doctorId}`);
      fetchDoctors();
    } catch (err) {
      console.error('Error deleting doctor:', err);
      alert(t('notifications.error') || 'An error occurred');
    }
  };

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
  };

  // Get unique specialties for filter
  const uniqueSpecialties = [...new Set(doctors.map(d => d.specialty))].filter(Boolean);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('doctors.title')}</h1>
          <p className="text-sm text-gray-500 mt-1">
            {canManageDoctors 
              ? t('doctors.manageSubtitle') || 'Manage doctor profiles and availability'
              : t('doctors.viewSubtitle') || 'View doctor profiles and book appointments'
            }
          </p>
        </div>
        
        {canManageDoctors && doctors.length > 0 && (
          <button
            onClick={() => navigate('/staff')}
            className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all"
          >
            <UserCog className="w-5 h-5" />
            {t('doctors.inviteDoctor') || 'Invite Doctor'}
          </button>
        )}
      </div>

      {/* Info Banner - No Doctors */}
      {canManageDoctors && doctors.length === 0 && !loading && (
        <div className="bg-gradient-to-r from-blue-50 to-teal-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <Stethoscope className="w-6 h-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-blue-900 mb-2 text-lg">
                {t('doctors.noDoctorsYet') || 'No doctors yet'}
              </h3>
              <p className="text-sm text-blue-700 mb-4">
                {t('doctors.inviteInstructions') || 'To add doctors to your medical center, go to the Staff section and invite them. They will receive an email to set up their profile.'}
              </p>
              <button
                onClick={() => navigate('/staff')}
                className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                <UserCog className="w-5 h-5" />
                {t('doctors.goToStaff') || 'Go to Staff Section'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      {doctors.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex flex-col sm:flex-row gap-3">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder={t('doctors.searchPlaceholder') || 'Search doctors by name, email, or specialty...'}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Specialty Filter */}
            <div className="sm:w-64 relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={selectedSpecialty}
                onChange={(e) => setSelectedSpecialty(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none bg-white"
              >
                <option value="">{t('doctors.allSpecialties') || 'All Specialties'}</option>
                {uniqueSpecialties.map((specialty) => (
                  <option key={specialty} value={specialty}>
                    {t(`specialties.${specialty}`)}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
            </div>

            {/* Clear Filters */}
            {(searchTerm || selectedSpecialty) && (
              <button
                onClick={() => {
                  setSearchTerm('');
                  setSelectedSpecialty('');
                }}
                className="px-4 py-2.5 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors font-medium"
              >
                {t('common.clearFilters') || 'Clear'}
              </button>
            )}
          </div>

          {/* Results Count */}
          <div className="mt-3 text-sm text-gray-500">
            {filteredDoctors.length === doctors.length
              ? t('doctors.showingAll', { count: doctors.length }) || `Showing all ${doctors.length} doctors`
              : t('doctors.showingFiltered', { filtered: filteredDoctors.length, total: doctors.length }) || `Showing ${filteredDoctors.length} of ${doctors.length} doctors`
            }
          </div>
        </div>
      )}

      {/* Doctors Grid/List */}
      {loading ? (
        <div className="flex justify-center py-16">
          <div className="text-center">
            <Loader2 className="w-10 h-10 animate-spin text-blue-600 mx-auto mb-3" />
            <p className="text-gray-500">{t('common.loading') || 'Loading...'}</p>
          </div>
        </div>
      ) : filteredDoctors.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDoctors.map((doctor) => (
            <div 
              key={doctor.doctor_id} 
              className="bg-white rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all duration-200 overflow-hidden group"
            >
              {/* Doctor Header */}
              <div className="p-5 bg-gradient-to-br from-blue-50 to-teal-50">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-teal-400 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                      {getInitials(doctor.name)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 text-lg">Dr. {doctor.name}</h3>
                      <p className="text-sm text-blue-600 font-medium flex items-center gap-1">
                        <Stethoscope className="w-3.5 h-3.5" />
                        {t(`specialties.${doctor.specialty}`) || doctor.specialty}
                      </p>
                    </div>
                  </div>
                  
                  {canManageDoctors && (
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => openModal(doctor)}
                        className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title={t('common.edit')}
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(doctor.doctor_id)}
                        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title={t('common.delete')}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Doctor Details */}
              <div className="p-5 space-y-3">
                {/* Contact Info */}
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Mail className="w-4 h-4 flex-shrink-0" />
                    <span className="truncate">{doctor.email}</span>
                  </div>
                  {doctor.phone && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <Phone className="w-4 h-4 flex-shrink-0" />
                      <span>{doctor.phone}</span>
                    </div>
                  )}
                  {doctor.location_name && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <MapPin className="w-4 h-4 flex-shrink-0" />
                      <span className="truncate">{doctor.location_name}</span>
                    </div>
                  )}
                </div>

                {/* Bio */}
                {doctor.bio && (
                  <p className="text-sm text-gray-600 line-clamp-2 pt-2 border-t border-gray-100">
                    {doctor.bio}
                  </p>
                )}

                {/* Consultation Info */}
                <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span>{doctor.consultation_duration} {t('common.minutes') || 'min'}</span>
                  </div>
                  <div className="text-lg font-semibold text-green-600">
                    {formatPrice(doctor.consultation_fee, doctor.currency || 'LEI')}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <button
                    onClick={() => navigate(`/calendar?doctor=${doctor.doctor_id}`)}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all"
                  >
                    <Calendar className="w-4 h-4" />
                    {t('doctors.bookAppointment') || 'Book'}
                  </button>
                  {canManageDoctors && (
                    <button
                      onClick={() => openModal(doctor)}
                      className="px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {t('doctors.noResults') || 'No doctors found'}
          </h3>
          <p className="text-gray-500 mb-4">
            {t('doctors.noResultsDesc') || 'Try adjusting your search or filters'}
          </p>
          <button
            onClick={() => {
              setSearchTerm('');
              setSelectedSpecialty('');
            }}
            className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
          >
            {t('common.clearFilters') || 'Clear Filters'}
          </button>
        </div>
      )}

      {/* Add/Edit Doctor Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 sticky top-0 bg-white z-10">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  {editingDoctor ? t('doctors.editDoctor') : t('doctors.addNewDoctor')}
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  {editingDoctor 
                    ? t('doctors.editDoctorDesc') || 'Update doctor information'
                    : t('doctors.addDoctorDesc') || 'Add a new doctor to your medical center'
                  }
                </p>
              </div>
              <button 
                onClick={() => setShowModal(false)} 
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleSubmit} className="p-6 space-y-5">
              {/* Basic Information */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                  <UserCog className="w-5 h-5 text-blue-600" />
                  {t('doctors.basicInfo') || 'Basic Information'}
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('doctors.doctorName')} *
                    </label>
                    <input
                      type="text"
                      required
                      value={form.name}
                      onChange={(e) => setForm({ ...form, name: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Dr. John Doe"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('doctors.specialty')} *
                    </label>
                    <select
                      required
                      value={form.specialty}
                      onChange={(e) => setForm({ ...form, specialty: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">{t('doctors.selectSpecialty')}</option>
                      {specialtyKeys.map((key) => (
                        <option key={key} value={key}>{t(`specialties.${key}`)}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('auth.email')} *
                    </label>
                    <input
                      type="email"
                      required
                      value={form.email}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="doctor@example.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('auth.phone')}
                    </label>
                    <input
                      type="tel"
                      value={form.phone}
                      onChange={(e) => setForm({ ...form, phone: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="+40 123 456 789"
                    />
                  </div>
                </div>
              </div>

              {/* Consultation Settings */}
              <div className="space-y-4 pt-4 border-t border-gray-200">
                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-blue-600" />
                  {t('doctors.consultationSettings') || 'Consultation Settings'}
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('doctors.consultationDuration')} *
                    </label>
                    <select
                      value={form.consultation_duration}
                      onChange={(e) => setForm({ ...form, consultation_duration: parseInt(e.target.value) })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value={15}>15 {t('common.minutes') || 'min'}</option>
                      <option value={30}>30 {t('common.minutes') || 'min'}</option>
                      <option value={45}>45 {t('common.minutes') || 'min'}</option>
                      <option value={60}>60 {t('common.minutes') || 'min'}</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('doctors.consultationFee')} *
                    </label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      required
                      value={form.consultation_fee}
                      onChange={(e) => setForm({ ...form, consultation_fee: parseFloat(e.target.value) })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="0.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('services.currency')} *
                    </label>
                    <select
                      value={form.currency}
                      onChange={(e) => setForm({ ...form, currency: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      {CURRENCIES.map((currency) => (
                        <option key={currency.code} value={currency.code}>
                          {currency.code} ({currency.symbol})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Bio */}
              <div className="pt-4 border-t border-gray-200">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {t('doctors.bio')}
                </label>
                <textarea
                  value={form.bio}
                  onChange={(e) => setForm({ ...form, bio: e.target.value })}
                  rows={3}
                  placeholder={t('doctors.bioPlaceholder') || 'Brief description about the doctor...'}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {t('doctors.bioHint') || 'This will be visible to patients when booking appointments'}
                </p>
              </div>

              {/* Form Actions */}
              <div className="flex gap-3 pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-2.5 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all"
                >
                  {t('common.cancel')}
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {saving && <Loader2 className="w-5 h-5 animate-spin" />}
                  {editingDoctor ? t('doctors.updateDoctor') : t('doctors.addDoctor')}
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
