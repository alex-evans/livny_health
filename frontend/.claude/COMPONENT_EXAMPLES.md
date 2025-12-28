# Component Examples

## Existing Components You Can Reference

### Button (src/components/ui/Button.tsx)
```typescript
import { Button } from '@/components/ui/Button';

<Button variant="primary" onClick={handleClick}>
  Prescribe
</Button>

<Button variant="secondary" onClick={handleCancel}>
  Cancel
</Button>

<Button variant="primary" loading={isSubmitting}>
  Saving...
</Button>
```

### Card (src/components/ui/Card.tsx)
```typescript
import { Card } from '@/components/ui/Card';

<Card>
  <h2 className="text-lg font-semibold mb-4">Active Medications</h2>
  {medications.map(med => (
    <div key={med.id}>{med.name}</div>
  ))}
</Card>
```

### Alert (src/components/ui/Alert.tsx)
```typescript
import { Alert } from '@/components/ui/Alert';

<Alert severity="critical" title="Allergy Alert">
  Patient has documented penicillin allergy
</Alert>

<Alert severity="warning">
  Drug interaction detected - monitor closely
</Alert>
```

## Page Structure Pattern

Every page follows this pattern:
```typescript
// src/pages/Prescribe.tsx
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { medicationApi } from '@/api/medication';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export function PrescribePage() {
  const { patientId } = useParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(false);

  return (
    <div className="max-w-4xl mx-auto p-8">
      {/* Back button */}
      <button onClick={() => navigate(-1)} className="text-glacier-blue mb-4">
        ← Back
      </button>

      {/* Page title */}
      <h1 className="text-2xl font-semibold text-deep-ice mb-8">
        Prescribe Medication
      </h1>

      {/* Content in cards */}
      <Card>
        {/* ... */}
      </Card>

      {/* Bottom actions */}
      <div className="flex justify-end space-x-4 mt-8">
        <Button variant="secondary" onClick={() => navigate(-1)}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSubmit} loading={loading}>
          Continue
        </Button>
      </div>
    </div>
  );
}
```

## API Usage Pattern
```typescript
// src/pages/SomePage.tsx
import { useState, useEffect } from 'react';
import { medicationApi } from '@/api/medication';

export function SomePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const result = await medicationApi.searchDrugs('amox');
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return <div>{/* render data */}</div>;
}
```
