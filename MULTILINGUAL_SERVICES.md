# Multilingual Services System

## Overview
MediConnect now supports multilingual service names and descriptions in English and Romanian. Service names and descriptions will automatically display in the user's selected language.

## Features

### 1. **Automatic Language Detection**
- Services display in the current UI language (EN or RO)
- Seamless switching between languages
- Fallback to default name if translation is missing

### 2. **Multilingual Fields**
Each service now has:
- `name_en` - English name
- `name_ro` - Romanian name
- `description_en` - English description (optional)
- `description_ro` - Romanian description (optional)
- `name` - Default name (for backward compatibility)

### 3. **Visual Indicators**
- Services with multilingual support show a 🌐 globe icon
- Easy identification of translated services

## How to Use

### For Admins: Creating/Editing Services

1. **Navigate to Services** section in your admin dashboard
2. **Click "Add Service"** or edit an existing service
3. **Fill in both language fields:**
   - **English Name** (required): e.g., "Cardiology"
   - **Romanian Name** (required): e.g., "Cardiologie"
   - **English Description** (optional): Detailed description in English
   - **Romanian Description** (optional): Detailed description in Romanian
4. **Set duration, price, and currency** as usual
5. **Save** the service

### For Users: Viewing Services

- Services automatically display in your selected language
- Switch language using the language selector (EN/RO)
- Service names and descriptions update instantly

## Migration of Existing Services

### Automatic Migration
When you first deploy this feature, existing services need to be migrated:

1. **Login as a Clinic Admin**
2. **Make a POST request** to `/api/migrate/services-multilingual`
3. This will copy existing service names to both EN and RO fields
4. **Edit each service** to provide proper translations

### Manual Migration via API
```bash
curl -X POST http://localhost:3000/api/migrate/services-multilingual \
  -H "Content-Type: application/json" \
  -H "Cookie: your-session-cookie"
```

## Technical Implementation

### Backend Changes

#### Schema (service.py)
```python
class Service(BaseModel):
    name: str  # Backward compatibility
    name_en: Optional[str] = None
    name_ro: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    description_ro: Optional[str] = None
    # ... other fields
```

#### API Endpoints
- `POST /api/services` - Create service with multilingual fields
- `PUT /api/services/{id}` - Update service with multilingual fields
- `GET /api/services` - Retrieve services (includes all language fields)
- `POST /api/migrate/services-multilingual` - Migrate existing services

### Frontend Changes

#### Services.js
- **Form with language tabs** for entering EN and RO names
- **Automatic language detection** using `i18n.language`
- **Fallback logic** if translation is missing
- **Visual indicators** (globe icon) for multilingual services

#### Display Logic
```javascript
const getLocalizedName = (service) => {
  if (i18n.language === 'ro' && service.name_ro) {
    return service.name_ro;
  }
  if (i18n.language === 'en' && service.name_en) {
    return service.name_en;
  }
  return service.name; // Fallback
};
```

## Database Schema

### Before Migration
```json
{
  "service_id": "svc_abc123",
  "name": "Cardiologie",
  "description": "Consultație cardiologie",
  "duration": 60,
  "price": 250.00,
  "currency": "LEI"
}
```

### After Migration
```json
{
  "service_id": "svc_abc123",
  "name": "Cardiologie",
  "name_en": "Cardiology",
  "name_ro": "Cardiologie",
  "description": "Consultație cardiologie",
  "description_en": "Cardiology consultation",
  "description_ro": "Consultație cardiologie",
  "duration": 60,
  "price": 250.00,
  "currency": "LEI"
}
```

## Best Practices

### 1. **Always Provide Both Languages**
- Fill in both EN and RO fields when creating services
- Ensures consistent experience for all users

### 2. **Use Professional Translations**
- Avoid machine translations for medical terms
- Consult medical professionals for accurate terminology

### 3. **Keep Names Concise**
- Service names should be short and descriptive
- Use descriptions for detailed information

### 4. **Regular Updates**
- Review and update translations periodically
- Ensure consistency across all services

## Troubleshooting

### Service Names Not Translating
1. **Check if multilingual fields are filled:**
   - Edit the service
   - Verify both `name_en` and `name_ro` have values

2. **Run migration if needed:**
   - POST to `/api/migrate/services-multilingual`
   - Edit services to add proper translations

### Missing Translations
- Services without translations will show the default `name` field
- Globe icon only appears when multilingual fields exist
- Edit the service to add missing translations

## Future Enhancements

Potential additions to the multilingual system:
- Support for additional languages (French, German, etc.)
- Bulk translation import/export
- Translation management interface
- Automatic translation suggestions
- Translation history and versioning

## Support

For issues or questions about the multilingual service system:
1. Check this documentation
2. Review the migration logs
3. Contact the development team
4. Submit an issue on GitHub

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-15  
**Compatibility:** MediConnect v2.0.0+
