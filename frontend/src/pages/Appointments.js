import { useState, useEffect } from 'react';
import { api, useAuth } from '../App';

const Appointments = () => {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [filteredAppointments, setFilteredAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);

  useEffect(() => {
    fetchAppointments();
  }, []);

  useEffect(() => {
    filterAppointments();
  }, [appointments, statusFilter, searchTerm]);

  const fetchAppointments = async () => {
    try {
      const response = await api.get('/appointments');
      setAppointments(response.data);
    } catch (error) {
      console.error('Error fetching appointments:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterAppointments = () => {
    let filtered = [...appointments];

    if (statusFilter !== 'all') {
      filtered = filtered.filter(apt => apt.status === statusFilter);
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(apt =>
        apt.doctor_name?.toLowerCase().includes(term) ||
        apt.patient_name?.toLowerCase().includes(term) ||
        apt.doctor_specialty?.toLowerCase().includes(term)
      );
    }

    // Sort by date
    filtered.sort((a, b) => new Date(b.date_time) - new Date(a.date_time));

    setFilteredAppointments(filtered);
  };

  const handleCancelAppointment = async () => {
    if (!selectedAppointment) return;

    try {
      await api.delete(`/appointments/${selectedAppointment.appointment_id}`);
      await fetchAppointments();
      setShowCancelModal(false);
      setSelectedAppointment(null);
    } catch (error) {
      console.error('Error cancelling appointment:', error);
      alert('Failed to cancel appointment');
    }
  };

  const handleUpdateStatus = async (appointmentId, newStatus) => {
    try {
      await api.put(`/appointments/${appointmentId}`, { status: newStatus });
      await fetchAppointments();
    } catch (error) {
      console.error('Error updating appointment:', error);
      alert('Failed to update appointment');
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      'SCHEDULED': 'bg-blue-100 text-blue-700 border-blue-200',
      'CONFIRMED': 'bg-green-100 text-green-700 border-green-200',
      'CANCELLED': 'bg-red-100 text-red-700 border-red-200',
      'COMPLETED': 'bg-purple-100 text-purple-700 border-purple-200'
    };
    return colors[status] || 'bg-gray-100 text-gray-700 border-gray-200';
  };

  const isUpcoming = (dateStr) => {
    return new Date(dateStr) > new Date();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="appointments-page">
      {/* Filters */}
      <div className="bg-white rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search appointments..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                data-testid="search-appointments"
                className="pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
              />
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {['all', 'SCHEDULED', 'CONFIRMED', 'COMPLETED', 'CANCELLED'].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                data-testid={`filter-${status.toLowerCase()}`}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  statusFilter === status
                    ? 'bg-gradient-to-r from-blue-600 to-teal-500 text-white shadow-lg shadow-blue-500/25'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {status === 'all' ? 'All' : status}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total', count: appointments.length, color: 'bg-gray-100 text-gray-700' },
          { label: 'Scheduled', count: appointments.filter(a => a.status === 'SCHEDULED').length, color: 'bg-blue-100 text-blue-700' },
          { label: 'Confirmed', count: appointments.filter(a => a.status === 'CONFIRMED').length, color: 'bg-green-100 text-green-700' },
          { label: 'Completed', count: appointments.filter(a => a.status === 'COMPLETED').length, color: 'bg-purple-100 text-purple-700' },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl p-4 shadow-sm">
            <p className="text-sm text-gray-500">{stat.label}</p>
            <p className={`text-2xl font-bold mt-1 ${stat.color.split(' ')[1]}`}>{stat.count}</p>
          </div>
        ))}
      </div>

      {/* Appointments List */}
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        {filteredAppointments.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <p className="text-gray-500">No appointments found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {filteredAppointments.map((apt) => (
              <div
                key={apt.appointment_id}
                className="p-6 hover:bg-gray-50 transition-colors"
                data-testid={`appointment-row-${apt.appointment_id}`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start space-x-4">
                    <div className="w-14 h-14 bg-gradient-to-br from-blue-100 to-teal-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{apt.doctor_name?.startsWith('Dr.') ? apt.doctor_name : `Dr. ${apt.doctor_name}`}</p>
                      <p className="text-sm text-gray-500">{apt.doctor_specialty}</p>
                      {user?.role === 'ADMIN' && (
                        <p className="text-sm text-gray-500 mt-1">
                          Patient: {apt.patient_name} ({apt.patient_email})
                        </p>
                      )}
                      {apt.notes && (
                        <p className="text-sm text-gray-400 mt-1 italic">"{apt.notes}"</p>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col md:flex-row md:items-center gap-4">
                    <div className="text-right">
                      <p className="font-medium text-gray-900">{formatDate(apt.date_time)}</p>
                      <p className="text-sm text-gray-500">{formatTime(apt.date_time)}</p>
                    </div>

                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(apt.status)}`}>
                      {apt.status}
                    </span>

                    {/* Actions */}
                    {apt.status !== 'CANCELLED' && apt.status !== 'COMPLETED' && isUpcoming(apt.date_time) && (
                      <div className="flex items-center space-x-2">
                        {user?.role === 'ADMIN' && apt.status === 'SCHEDULED' && (
                          <button
                            onClick={() => handleUpdateStatus(apt.appointment_id, 'CONFIRMED')}
                            data-testid={`confirm-${apt.appointment_id}`}
                            className="px-3 py-1.5 rounded-lg bg-green-100 text-green-700 hover:bg-green-200 text-sm font-medium transition-colors"
                          >
                            Confirm
                          </button>
                        )}
                        {user?.role === 'ADMIN' && (
                          <button
                            onClick={() => handleUpdateStatus(apt.appointment_id, 'COMPLETED')}
                            data-testid={`complete-${apt.appointment_id}`}
                            className="px-3 py-1.5 rounded-lg bg-purple-100 text-purple-700 hover:bg-purple-200 text-sm font-medium transition-colors"
                          >
                            Complete
                          </button>
                        )}
                        <button
                          onClick={() => {
                            setSelectedAppointment(apt);
                            setShowCancelModal(true);
                          }}
                          data-testid={`cancel-${apt.appointment_id}`}
                          className="px-3 py-1.5 rounded-lg bg-red-100 text-red-700 hover:bg-red-200 text-sm font-medium transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Cancel Modal */}
      {showCancelModal && selectedAppointment && (
        <div className="fixed inset-0 z-50 flex items-center justify-center modal-backdrop" data-testid="cancel-modal">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md mx-4 animate-fadeIn">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Cancel Appointment</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to cancel your appointment with Dr. {selectedAppointment.doctor_name} on {formatDate(selectedAppointment.date_time)} at {formatTime(selectedAppointment.date_time)}?
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowCancelModal(false);
                  setSelectedAppointment(null);
                }}
                className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                Keep Appointment
              </button>
              <button
                onClick={handleCancelAppointment}
                data-testid="confirm-cancel"
                className="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700"
              >
                Yes, Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Appointments;
