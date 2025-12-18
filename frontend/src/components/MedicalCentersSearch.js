import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../App';
import { Search, MapPin, Phone, Mail, Building2, AlertCircle } from 'lucide-react';
import { ROMANIAN_COUNTIES, getCitiesForCounty } from '../lib/ro-cities';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';

const MedicalCentersSearch = () => {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [countyFilter, setCountyFilter] = useState('all');
  const [cityFilter, setCityFilter] = useState('all');
  const [availableCities, setAvailableCities] = useState([]);
  const [centers, setCenters] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showFallback, setShowFallback] = useState(false);
  const [lastSearchLocation, setLastSearchLocation] = useState('');

  // Update available cities when county changes
  useEffect(() => {
    if (countyFilter && countyFilter !== 'all') {
      const cities = getCitiesForCounty(countyFilter);
      setAvailableCities(cities);
      setCityFilter('all'); // Reset city when county changes
    } else {
      setAvailableCities([]);
      setCityFilter('all');
    }
  }, [countyFilter]);

  // Fetch centers based on filters
  const fetchCenters = async (search = searchTerm, county = countyFilter, city = cityFilter) => {
    setLoading(true);
    setError(null);
    setShowFallback(false);

    try {
      const params = new URLSearchParams();
      if (search && search.trim()) {
        params.append('search_term', search.trim());
      }
      if (county && county !== 'all') {
        params.append('county_filter', county);
      }
      if (city && city !== 'all') {
        params.append('city_filter', city);
      }

      const response = await api.get(`/centers?${params.toString()}`);
      const data = response.data;

      setCenters(data.results || []);

      // Show fallback message if searching in a specific location with no results
      if (data.results.length === 0 && (county !== 'all' || city !== 'all')) {
        setShowFallback(true);
        if (city !== 'all') {
          setLastSearchLocation(city);
        } else if (county !== 'all') {
          setLastSearchLocation(county);
        }
      }
    } catch (err) {
      console.error('Error fetching centers:', err);
      setError(t('centers.errorFetching') || 'Error fetching medical centers');
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchCenters();
  }, []);

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    fetchCenters();
  };

  // Handle county filter change
  const handleCountyChange = (value) => {
    setCountyFilter(value);
    fetchCenters(searchTerm, value, 'all');
  };

  // Handle city filter change
  const handleCityChange = (value) => {
    setCityFilter(value);
    fetchCenters(searchTerm, countyFilter, value);
  };

  // Handle "Show All Romania" button click
  const handleShowAllRomania = () => {
    setCountyFilter('all');
    setCityFilter('all');
    setShowFallback(false);
    fetchCenters(searchTerm, 'all', 'all');
  };

  return (
    <div className="space-y-4">
      {/* Search and Filter Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t('centers.searchTitle') || 'Search Medical Centers'}</CardTitle>
          <CardDescription className="text-sm">
            {t('centers.searchDescription') || 'Find medical centers by name, specialty, or location'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              {/* Search Input */}
              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  {t('centers.searchLabel') || 'Search by name or specialty'}
                </label>
                <div className="relative">
                  <Search className="absolute left-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    type="text"
                    placeholder={t('centers.searchPlaceholder') || 'e.g., Cardiology, Dermatology...'}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-9 h-9 text-sm"
                  />
                </div>
              </div>

              {/* County Dropdown */}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  {t('centers.countyLabel') || 'County'}
                </label>
                <Select value={countyFilter} onValueChange={handleCountyChange}>
                  <SelectTrigger className="h-9 text-sm">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-gray-400" />
                      <SelectValue />
                    </div>
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">
                      {t('centers.allRomania') || 'All Romania'}
                    </SelectItem>
                    {ROMANIAN_COUNTIES.map((county) => (
                      <SelectItem key={county} value={county}>
                        {county}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* City Dropdown */}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  {t('centers.cityLabel') || 'City'}
                </label>
                <Select
                  value={cityFilter}
                  onValueChange={handleCityChange}
                  disabled={countyFilter === 'all' || availableCities.length === 0}
                >
                  <SelectTrigger className="h-9 text-sm">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3.5 h-3.5 text-gray-400" />
                      <SelectValue />
                    </div>
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">
                      {t('centers.allCities') || 'All Cities'}
                    </SelectItem>
                    {availableCities.map((city) => (
                      <SelectItem key={city} value={city}>
                        {city}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Search Button */}
            <div className="flex justify-end">
              <Button type="submit" disabled={loading} size="sm">
                <Search className="w-3.5 h-3.5 mr-1.5" />
                {loading ? (t('common.searching') || 'Searching...') : (t('common.search') || 'Search')}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Error Message */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Fallback Message - No results in specific location */}
      {showFallback && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>
              {t('centers.noResultsInLocation', { location: lastSearchLocation }) ||
                `No clinics found in ${lastSearchLocation}. Would you like to see results from All Romania?`}
            </span>
            <Button onClick={handleShowAllRomania} variant="outline" size="sm" className="ml-4">
              {t('centers.showAllRomania') || 'Show All Romania'}
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Results Section */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-base font-semibold text-gray-900">
            {t('centers.results') || 'Results'} ({centers.length})
          </h3>
          {(countyFilter !== 'all' || cityFilter !== 'all') && (
            <span className="text-xs text-gray-600">
              {t('centers.filteringBy') || 'Filtering by'}: <strong>
                {cityFilter !== 'all' ? cityFilter : countyFilter}
              </strong>
            </span>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        )}

        {/* Results Grid */}
        {!loading && centers.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {centers.map((center) => (
              <Card key={center.center_id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-teal-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Building2 className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-base mb-0.5 truncate">{center.name}</CardTitle>
                      <CardDescription className="text-xs">{center.specialty}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2 pt-0">
                  <div className="flex items-start gap-2 text-xs text-gray-600">
                    <MapPin className="w-3.5 h-3.5 mt-0.5 flex-shrink-0 text-gray-400" />
                    <div>
                      <p>{center.address}</p>
                      <p className="font-medium text-blue-600">{center.city}, {center.county}</p>
                    </div>
                  </div>
                  {center.phone && (
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <Phone className="w-3.5 h-3.5 flex-shrink-0 text-gray-400" />
                      <a href={`tel:${center.phone}`} className="hover:text-blue-600">
                        {center.phone}
                      </a>
                    </div>
                  )}
                  {center.email && (
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <Mail className="w-3.5 h-3.5 flex-shrink-0 text-gray-400" />
                      <a href={`mailto:${center.email}`} className="hover:text-blue-600 truncate">
                        {center.email}
                      </a>
                    </div>
                  )}
                  {center.description && (
                    <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                      {center.description}
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* No Results */}
        {!loading && centers.length === 0 && !showFallback && (
          <Card>
            <CardContent className="py-12 text-center">
              <Building2 className="w-14 h-14 text-gray-300 mx-auto mb-3" />
              <h3 className="text-base font-semibold text-gray-900 mb-2">
                {t('centers.noResults') || 'No medical centers found'}
              </h3>
              <p className="text-sm text-gray-600">
                {t('centers.noResultsDescription') || 'Try adjusting your search criteria or location filter'}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default MedicalCentersSearch;
