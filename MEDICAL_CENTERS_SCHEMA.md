# Medical Centers Location-Based Filtering System

## Overview
This document describes the implementation of a location-based filtering system for medical centers in Romania using MongoDB and string-based matching (no geolocation/Google Maps API).

## Database Schema

### Collection: `medical_centers`

```javascript
{
  center_id: String,        // Unique identifier (e.g., "center_a1b2c3d4e5f6")
  name: String,             // Medical center name
  specialty: String,        // Primary specialty (e.g., "Cardiology", "Dermatology")
  address: String,          // Full street address
  city: String,             // City name (e.g., "București", "Cluj-Napoca")
  county: String,           // County/Județ (e.g., "București", "Cluj")
  phone: String,            // Contact phone (optional)
  email: String,            // Contact email (optional)
  description: String,      // Description of services (optional)
  created_at: DateTime      // Timestamp of creation
}
```

### Indexes (Recommended)
For optimal query performance, create the following indexes:

```javascript
// Single field indexes
db.medical_centers.createIndex({ "name": 1 })
db.medical_centers.createIndex({ "city": 1 })
db.medical_centers.createIndex({ "specialty": 1 })

// Compound index for common queries
db.medical_centers.createIndex({ "city": 1, "name": 1 })

// Text index for full-text search (optional)
db.medical_centers.createIndex({ 
  "name": "text", 
  "specialty": "text",
  "description": "text"
})
```

## API Endpoints

### GET /api/centers
Search and filter medical centers.

**Query Parameters:**
- `search_term` (optional): Search by name or specialty (case-insensitive)
- `city_filter` (optional): Filter by city. Use "all" or omit for national search

**Examples:**
```bash
# National search for cardiology
GET /api/centers?search_term=cardiology&city_filter=all

# Search in specific city
GET /api/centers?search_term=dermatology&city_filter=București

# Get all centers in a city
GET /api/centers?city_filter=Cluj-Napoca

# National search (no filters)
GET /api/centers
```

**Response:**
```json
{
  "count": 15,
  "city_filter": "București",
  "search_term": "cardiology",
  "results": [
    {
      "center_id": "center_abc123",
      "name": "Cardio Med Center",
      "specialty": "Cardiology",
      "address": "Str. Victoriei 123",
      "city": "București",
      "county": "București",
      "phone": "+40 21 123 4567",
      "email": "contact@cardiomed.ro",
      "description": "Specialized cardiology center...",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### GET /api/centers/{center_id}
Get a specific medical center by ID.

### POST /api/centers
Create a new medical center.

**Request Body:**
```json
{
  "name": "New Medical Center",
  "specialty": "General Practice",
  "address": "Str. Mihai Eminescu 45",
  "city": "Iași",
  "county": "Iași",
  "phone": "+40 232 123 456",
  "email": "contact@newcenter.ro",
  "description": "Full-service medical center"
}
```

### PUT /api/centers/{center_id}
Update an existing medical center.

### DELETE /api/centers/{center_id}
Delete a medical center.

### GET /api/centers/cities/list
Get a list of all unique cities from the database.

**Response:**
```json
{
  "cities": ["Alba Iulia", "Arad", "Bacău", "București", "Cluj-Napoca", ...]
}
```

## Frontend Implementation

### Location Dropdown
The frontend provides a dropdown with:
1. **Default option**: "All Romania" (value: `all`)
2. **City options**: Populated from a static list of Romanian cities

### Search Flow
1. User enters search term (name/specialty) and selects location
2. Frontend calls `/api/centers` with appropriate query parameters
3. Results are displayed in a grid layout
4. If no results in specific city, show fallback message with option to search nationally

### Fallback UX
When searching in a specific city with no results:
```
"No clinics found in [City]. Would you like to see results from All Romania?"
[Show All Romania Button]
```

## Query Logic

### National Search (city_filter = "all" or empty)
```javascript
// MongoDB query
{
  $or: [
    { name: { $regex: searchTerm, $options: "i" } },
    { specialty: { $regex: searchTerm, $options: "i" } }
  ]
}
```

### City-Specific Search
```javascript
// MongoDB query
{
  city: { $regex: `^${cityFilter}$`, $options: "i" },
  $or: [
    { name: { $regex: searchTerm, $options: "i" } },
    { specialty: { $regex: searchTerm, $options: "i" } }
  ]
}
```

## Romanian Cities List
The system includes a predefined list of major Romanian cities:
- București
- Cluj-Napoca
- Timișoara
- Iași
- Constanța
- Craiova
- Brașov
- Galați
- Ploiești
- Oradea
- And 30+ more cities...

## Sample Data

### Example Documents
```javascript
// Example 1: Cardiology center in București
{
  center_id: "center_abc123def456",
  name: "Regina Maria - Cardiology",
  specialty: "Cardiology",
  address: "Bulevardul Aviatorilor 42",
  city: "București",
  county: "București",
  phone: "+40 21 9699",
  email: "contact@reginamaria.ro",
  description: "Leading cardiology center with state-of-the-art equipment",
  created_at: ISODate("2025-01-15T10:00:00Z")
}

// Example 2: Dermatology center in Cluj-Napoca
{
  center_id: "center_xyz789ghi012",
  name: "DermaClinic Cluj",
  specialty: "Dermatology",
  address: "Strada Memorandumului 28",
  city: "Cluj-Napoca",
  county: "Cluj",
  phone: "+40 264 123 456",
  email: "info@dermaclinic.ro",
  description: "Specialized dermatology and aesthetic treatments",
  created_at: ISODate("2025-01-16T14:30:00Z")
}
```

## Implementation Notes

1. **No Geolocation**: System uses string-based city matching only
2. **Case-Insensitive**: All searches are case-insensitive using regex
3. **Cost-Free**: No external APIs (Google Maps, etc.)
4. **Scalable**: MongoDB indexes ensure fast queries even with large datasets
5. **Flexible**: Easy to add new cities or expand to county-level filtering

## Testing

### Sample Queries for Testing
```bash
# Test 1: National search
curl "http://localhost:8000/api/centers?search_term=cardiology&city_filter=all"

# Test 2: City-specific search
curl "http://localhost:8000/api/centers?search_term=dermatology&city_filter=București"

# Test 3: No results scenario
curl "http://localhost:8000/api/centers?search_term=xyz&city_filter=Sibiu"

# Test 4: Get all centers in a city
curl "http://localhost:8000/api/centers?city_filter=Cluj-Napoca"
```

## Future Enhancements

1. **County-level filtering**: Add county dropdown alongside city
2. **Specialty categories**: Group specialties into categories
3. **Distance estimation**: Add approximate distance based on city proximity
4. **Autocomplete**: Implement city name autocomplete
5. **Favorites**: Allow users to save favorite centers
6. **Reviews**: Integrate with existing review system
7. **Availability**: Show real-time appointment availability

## Files Modified/Created

### Backend
- `/backend/app/schemas/center.py` - Pydantic models for medical centers
- `/backend/app/routers/centers.py` - API endpoints for centers
- `/backend/app/main.py` - Registered centers router

### Frontend
- `/frontend/src/pages/Centers.js` - Main centers search page
- `/frontend/src/lib/ro-cities.js` - Romanian cities list
- `/frontend/src/App.js` - Added Centers route
- `/frontend/src/i18n/locales/en.json` - Added translation keys

### Documentation
- `/MEDICAL_CENTERS_SCHEMA.md` - This file
