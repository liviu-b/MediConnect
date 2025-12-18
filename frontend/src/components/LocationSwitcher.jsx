import { useState, useEffect } from 'react';
import { MapPin, ChevronDown, Building2, Loader2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { api } from '../App';

/**
 * LocationSwitcher Component
 * 
 * Displays a dropdown allowing users to switch between accessible locations.
 * Stores the active location in localStorage and updates API calls accordingly.
 */
const LocationSwitcher = ({ compact = false }) => {
  const { t } = useTranslation();
  const [locations, setLocations] = useState([]);
  const [activeLocation, setActiveLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/locations');
      const locationsList = response.data;
      
      setLocations(locationsList);
      
      // Get stored active location or use first location
      const storedLocationId = localStorage.getItem('active_location_id');
      const initialLocation = storedLocationId 
        ? locationsList.find(loc => loc.location_id === storedLocationId) || locationsList[0]
        : locationsList[0];
      
      if (initialLocation) {
        setActiveLocation(initialLocation);
        localStorage.setItem('active_location_id', initialLocation.location_id);
      }
    } catch (error) {
      console.error('Error fetching locations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLocationChange = (location) => {
    setActiveLocation(location);
    localStorage.setItem('active_location_id', location.location_id);
    setDropdownOpen(false);
    
    // Trigger a custom event to notify other components
    window.dispatchEvent(new CustomEvent('locationChanged', { 
      detail: { locationId: location.location_id } 
    }));
    
    // Reload the page to refresh data for new location
    window.location.reload();
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
        <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
        {!compact && <span className="text-sm text-gray-500">{t('locations.loading')}</span>}
      </div>
    );
  }

  if (locations.length === 0) {
    return null; // Don't show if no locations
  }

  if (locations.length === 1) {
    // Only one location - show as static label
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-blue-50 rounded-lg border border-blue-200">
        <MapPin className="w-4 h-4 text-blue-600" />
        {!compact && (
          <div className="text-left">
            <p className="text-sm font-medium text-blue-900">{activeLocation?.name}</p>
            {activeLocation?.city && (
              <p className="text-xs text-blue-600">{activeLocation.city}</p>
            )}
          </div>
        )}
      </div>
    );
  }

  // Multiple locations - show dropdown
  return (
    <div className="relative">
      <button
        onClick={() => setDropdownOpen(!dropdownOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <MapPin className="w-4 h-4 text-blue-600 flex-shrink-0" />
        {!compact && activeLocation && (
          <div className="text-left">
            <p className="text-sm font-medium text-gray-900">{activeLocation.name}</p>
            {activeLocation.city && (
              <p className="text-xs text-gray-500">{activeLocation.city}</p>
            )}
          </div>
        )}
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
      </button>

      {dropdownOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setDropdownOpen(false)}
          />
          
          {/* Dropdown Menu */}
          <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50 max-h-96 overflow-y-auto">
            <div className="px-3 py-2 border-b border-gray-100">
              <p className="text-xs font-medium text-gray-500 uppercase">
                {t('locations.switchLocation')}
              </p>
            </div>
            
            {locations.map((location) => {
              const isActive = activeLocation?.location_id === location.location_id;
              const isPrimary = location.is_primary;
              
              return (
                <button
                  key={location.location_id}
                  onClick={() => handleLocationChange(location)}
                  className={`w-full flex items-start gap-3 px-3 py-2 hover:bg-gray-50 transition-colors ${
                    isActive ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    isActive 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    <Building2 className="w-4 h-4" />
                  </div>
                  
                  <div className="flex-1 text-left">
                    <div className="flex items-center gap-2">
                      <p className={`text-sm font-medium ${
                        isActive ? 'text-blue-900' : 'text-gray-900'
                      }`}>
                        {location.name}
                      </p>
                      {isPrimary && (
                        <span className="px-1.5 py-0.5 bg-green-100 text-green-700 text-xs rounded">
                          {t('locations.primary')}
                        </span>
                      )}
                    </div>
                    
                    {location.city && (
                      <p className={`text-xs ${
                        isActive ? 'text-blue-600' : 'text-gray-500'
                      }`}>
                        <MapPin className="w-3 h-3 inline mr-1" />
                        {location.city}
                        {location.county && `, ${location.county}`}
                      </p>
                    )}
                    
                    {location.address && (
                      <p className="text-xs text-gray-400 mt-0.5">
                        {location.address}
                      </p>
                    )}
                  </div>
                  
                  {isActive && (
                    <div className="flex-shrink-0">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};

export default LocationSwitcher;
