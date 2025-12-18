# Phase 2 Complete Implementation Plan

## Current Status

✅ **Step 1 Complete:** LocationSwitcher Component
- Component created and integrated
- API integration with X-Location-ID header
- Translation keys added

## Remaining Implementation

Due to the complexity and interdependencies, here's the complete plan for the remaining Phase 2 tasks:

### Step 2: Updated Registration Flow

**Status:** Partially started (form fields added)

**What's Needed:**

1. **Update CUI Validation** to use new endpoint:
```javascript
// Change from: /auth/validate-cui
// To: /organizations/validate-cui
const res = await api.post(`/organizations/validate-cui?cui=${cui}`);
```

2. **Update Registration Submit** to handle two scenarios:
```javascript
const res = await api.post('/organizations/register', {
  cui: form.cui,
  organization_name: form.organization_name,
  location_name: form.location_name,
  location_city: form.location_city,
  location_county: form.location_county,
  location_address: form.location_address,
  location_phone: form.location_phone,
  admin_name: form.admin_name,
  admin_email: form.admin_email,
  admin_password: form.admin_password,
  admin_phone: form.admin_phone
});

// Handle response
if (res.data.status === 'success') {
  // New organization created
  navigate('/dashboard');
} else if (res.data.status === 'access_request_created') {
  // Access request created - show confirmation
  navigate('/access-request-sent', { 
    state: { 
      requestId: res.data.request_id,
      organizationName: res.data.organization_name 
    }
  });
}
```

3. **Add Form Fields** for organization and location:
- Organization Name (optional)
- Location Name (required)
- Location City
- Location County  
- Location Address
- Location Phone

4. **Create Access Request Confirmation Page:**
```jsx
// frontend/src/pages/AccessRequestSent.js
// Shows "Your request has been sent" message
// Displays organization name
// Shows next steps
```

---

### Step 3: Access Request Management UI

**Files to Create:**

#### 1. `frontend/src/pages/AccessRequests.js`

```jsx
import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../App';
import AccessRequestCard from '../components/AccessRequestCard';

const AccessRequests = () => {
  const { t } = useTranslation();
  const [requests, setRequests] = useState([]);
  const [filter, setFilter] = useState('PENDING');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRequests();
  }, [filter]);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/access-requests?status=${filter}`);
      setRequests(res.data);
    } catch (error) {
      console.error('Error fetching requests:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Filter tabs */}
      {/* Request cards */}
      {/* Approve/Reject modals */}
    </div>
  );
};
```

#### 2. `frontend/src/components/AccessRequestCard.jsx`

```jsx
const AccessRequestCard = ({ request, onApprove, onReject }) => {
  return (
    <div className="bg-white p-6 rounded-lg border">
      {/* Requester info */}
      {/* Proposed location */}
      {/* Action buttons */}
    </div>
  );
};
```

#### 3. **Approve Modal Component**

Features:
- Select role dropdown (Super Admin, Location Admin, Staff)
- Multi-select for locations
- Checkbox: "Create proposed location"
- Confirm button

#### 4. **Reject Modal Component**

Features:
- Textarea for rejection reason
- Confirm button

---

### Step 4: Location Management UI

**Files to Create:**

#### 1. `frontend/src/pages/Locations.js`

```jsx
const Locations = () => {
  const [locations, setLocations] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingLocation, setEditingLocation] = useState(null);

  return (
    <div>
      {/* Header with "Add Location" button */}
      {/* Location cards grid */}
      {/* Create/Edit modal */}
    </div>
  );
};
```

#### 2. `frontend/src/components/LocationForm.jsx`

```jsx
const LocationForm = ({ location, onSave, onCancel }) => {
  return (
    <form>
      {/* Location Name */}
      {/* Address */}
      {/* City */}
      {/* County */}
      {/* Phone */}
      {/* Email */}
      {/* Working Hours */}
      {/* Settings */}
    </form>
  );
};
```

#### 3. **Location Card Component**

Features:
- Display location info
- Edit button
- Delete button
- Primary badge
- Active/Inactive toggle

---

### Step 5: Organization Settings

**Files to Modify:**

#### 1. Update `frontend/src/pages/Settings.js`

Add organization tab for Super Admins:

```jsx
const Settings = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('location');

  const tabs = [
    { id: 'location', label: 'Location Settings' },
  ];

  // Add organization tab for Super Admins
  if (user?.role === 'SUPER_ADMIN') {
    tabs.unshift({ id: 'organization', label: 'Organization' });
  }

  return (
    <div>
      {/* Tab navigation */}
      {activeTab === 'organization' && <OrganizationSettings />}
      {activeTab === 'location' && <LocationSettings />}
    </div>
  );
};
```

#### 2. Create `frontend/src/components/OrganizationSettings.jsx`

```jsx
const OrganizationSettings = () => {
  const [organization, setOrganization] = useState(null);

  return (
    <div>
      {/* Organization Name */}
      {/* Legal Name */}
      {/* CUI (read-only) */}
      {/* Registration Number */}
      {/* Tax Registration */}
      {/* Legal Address */}
      {/* Phone */}
      {/* Email */}
      {/* Website */}
      {/* Description */}
      {/* Settings */}
    </div>
  );
};
```

---

## Navigation Updates

Add new routes to `App.js`:

```jsx
<Route
  path="/access-requests"
  element={
    <ProtectedRoute>
      <Layout><AccessRequests /></Layout>
    </ProtectedRoute>
  }
/>
<Route
  path="/locations"
  element={
    <ProtectedRoute>
      <Layout><Locations /></Layout>
    </ProtectedRoute>
  }
/>
<Route
  path="/access-request-sent"
  element={<AccessRequestSent />}
/>
```

Add nav items for Super Admins:

```jsx
if (user?.role === 'SUPER_ADMIN') {
  navItems.push(
    { path: '/locations', labelKey: 'nav.locations', icon: MapPin },
    { path: '/access-requests', labelKey: 'nav.accessRequests', icon: UserPlus }
  );
}
```

---

## Translation Keys to Add

```json
{
  "nav": {
    "locations": "Locations",
    "accessRequests": "Access Requests"
  },
  "accessRequests": {
    "title": "Access Requests",
    "pending": "Pending",
    "approved": "Approved",
    "rejected": "Rejected",
    "noRequests": "No access requests",
    "requesterInfo": "Requester Information",
    "proposedLocation": "Proposed Location",
    "approve": "Approve Request",
    "reject": "Reject Request",
    "selectRole": "Select Role",
    "assignLocations": "Assign Locations",
    "allLocations": "All Locations",
    "specificLocations": "Specific Locations",
    "createProposedLocation": "Create proposed location",
    "rejectionReason": "Rejection Reason",
    "reasonPlaceholder": "Please provide a reason...",
    "approveSuccess": "Access request approved",
    "rejectSuccess": "Access request rejected"
  },
  "accessRequestSent": {
    "title": "Access Request Sent",
    "message": "Your access request has been sent to the administrators of",
    "nextSteps": "What happens next?",
    "step1": "The organization administrators will review your request",
    "step2": "You'll receive an email when your request is approved or rejected",
    "step3": "Once approved, you can log in with your credentials",
    "backToLogin": "Back to Login"
  }
}
```

---

## Priority Order

Given the dependencies, implement in this order:

1. ✅ **LocationSwitcher** (DONE)
2. **Updated Registration Flow** (High Priority)
   - Users need to be able to register/request access
3. **Access Request Management** (High Priority)
   - Super Admins need to approve requests
4. **Location Management** (Medium Priority)
   - Super Admins need to create locations
5. **Organization Settings** (Low Priority)
   - Nice to have, not critical for MVP

---

## Estimated Time

| Task | Time |
|------|------|
| Complete Registration Flow | 3-4 hours |
| Access Request Management | 4-5 hours |
| Location Management | 3-4 hours |
| Organization Settings | 2-3 hours |
| Testing & Bug Fixes | 2-3 hours |
| **Total** | **14-19 hours** |

---

## Testing Strategy

### Registration Flow:
1. Register with new CUI → Should create organization
2. Register with existing CUI → Should create access request
3. Verify email sent to Super Admin
4. Check access request appears in dashboard

### Access Requests:
1. Super Admin sees pending requests
2. Approve request → User can log in
3. Reject request → User receives notification
4. Create new location during approval

### Location Management:
1. Create new location
2. Edit location details
3. Delete location (soft delete)
4. Switch between locations

### Organization Settings:
1. Edit organization details
2. Update settings
3. Changes persist

---

## Next Steps

Would you like me to:
1. **Continue implementing** all remaining steps?
2. **Focus on one specific step** (e.g., complete registration flow)?
3. **Create a simplified MVP** version first?

Let me know how you'd like to proceed!
