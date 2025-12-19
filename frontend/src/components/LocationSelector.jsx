import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Building2, ChevronDown, Check } from 'lucide-react';
import { api } from '../App';

/**
 * LocationSelector Component
 * 
 * For multi-location organizations, allows SuperAdmin to:
 * 1. View all locations in their organization
 * 2. Switch between locations
 * 3. Access global dashboard
 * 
 * For single-location, redirects directly to location dashboard
 */
const LocationSelector = ({ user }) => {
  const navigate = useNavigate();
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  useEffect(() => {
    if (user?.organization_id) {
      fetchLocations();
    }
  }, [user]);

  const fetchLocations = async () => {
    try {
      const res = await api.get('/locations', {
        params: { organization_id: user.organization_id }
      });
      setLocations(res.data);
      
      // If user has a primary location, select it
      if (user.primary_location_id) {
        const primary = res.data.find(loc => loc.location_id === user.primary_location_id);
        if (primary) {
          setSelectedLocation(primary);
        }
      }
    } catch (err) {
      console.error('Failed to fetch locations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLocationSelect = (location) => {
    setSelectedLocation(location);
    setDropdownOpen(false);
    
    // Navigate to location-specific dashboard
    navigate(`/location/${location.location_id}/dashboard`);
  };

  const handleGlobalDashboard = () => {
    setSelectedLocation(null);
    setDropdownOpen(false);
    navigate('/dashboard');
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
        <MapPin className="w-4 h-4 text-gray-400 animate-pulse" />
        <span className="text-sm text-gray-500">Loading locations...</span>
      </div>
    );
  }

  // Single location - show location name only
  if (locations.length === 1) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 rounded-lg">
        <MapPin className="w-4 h-4 text-blue-600" />
        <span className="text-sm font-medium text-blue-900">
          {locations[0].name}
        </span>
      </div>
    );
  }

  // Multi-location - show dropdown selector
  return (
    <div className="relative">
      <button
        onClick={() => setDropdownOpen(!dropdownOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <MapPin className="w-4 h-4 text-gray-600" />
        <span className="text-sm font-medium text-gray-900">
          {selectedLocation ? selectedLocation.name : 'All Locations'}
        </span>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
      </button>

      {dropdownOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setDropdownOpen(false)}
          />
          
          {/* Dropdown Menu */}
          <div className="absolute right-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-20 max-h-96 overflow-y-auto">
            {/* Global Dashboard Option (SuperAdmin only) */}
            {user?.role === 'SUPER_ADMIN' && (
              <>
                <button
                  onClick={handleGlobalDashboard}
                  className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors text-left"
                >
                  <Building2 className="w-5 h-5 text-blue-600" />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">
                      Global Dashboard
                    </div>
                    <div className="text-xs text-gray-500">
                      View all locations
                    </div>
                  </div>
                  {!selectedLocation && (
                    <Check className="w-4 h-4 text-blue-600" />
                  )}
                </button>
                <div className="border-t border-gray-100" />
              </>
            )}

            {/* Location List */}
            <div className="py-1">
              {locations.map((location) => (
                <button
                  key={location.location_id}
                  onClick={() => handleLocationSelect(location)}
                  className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors text-left"
                >
                  <MapPin className="w-5 h-5 text-gray-400" />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">
                      {location.name}
                    </div>
                    {location.city && (
                      <div className="text-xs text-gray-500">
                        {location.city}
                        {location.county && `, ${location.county}`}
                      </div>
                    )}
                  </div>
                  {selectedLocation?.location_id === location.location_id && (
                    <Check className="w-4 h-4 text-blue-600" />
                  )}
                </button>
              ))}
            </div>

            {/* Location Count */}
            <div className="border-t border-gray-100 px-4 py-2 bg-gray-50">
              <div className="text-xs text-gray-500">
                {locations.length} location{locations.length !== 1 ? 's' : ''} total
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LocationSelector;
