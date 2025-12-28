# Component Patterns

## File Structure
```
src/
├── components/
│   ├── ui/              # Base components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   └── Alert.tsx
│   ├── patient/         # Patient-specific
│   │   ├── PatientHeader.tsx
│   │   └── AllergyBadge.tsx
│   └── medication/      # Medication-specific
│       ├── DrugSearch.tsx
│       └── PrescriptionForm.tsx
```

## Component Template

Every component follows this pattern:
```typescript
import React from 'react';
import { cn } from '@/utils/classnames'; // Tailwind merge utility

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  children: React.ReactNode;
  onClick?: () => void;
  loading?: boolean;
  disabled?: boolean;
}

export function Button({
  variant = 'primary',
  children,
  onClick,
  loading = false,
  disabled = false,
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(
        // Base styles
        'px-6 py-3 rounded-md font-medium transition-all',
        // Variant styles
        variant === 'primary' && 'bg-glacier-blue text-white hover:bg-deep-ice shadow-sm',
        variant === 'secondary' && 'bg-white text-glacier-blue border border-arctic hover:bg-frost',
        variant === 'danger' && 'bg-white text-critical border border-red-100 hover:bg-red-50',
        // State styles
        disabled && 'opacity-50 cursor-not-allowed',
        loading && 'cursor-wait'
      )}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
}
```

## Key Patterns

### 1. Always Export Named Components
```typescript
// ✅ Good
export function Button() { }

// ❌ Avoid
export default Button;
```

### 2. Use TypeScript Interfaces
```typescript
// Define props interface
interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export function Card({ children, className, onClick }: CardProps) {
  // ...
}
```

### 3. Composition Over Props Drilling
```typescript
// ✅ Good - composable
<Card>
  <Card.Header>
    <Card.Title>Patient Info</Card.Title>
  </Card.Header>
  <Card.Body>
    {content}
  </Card.Body>
</Card>

// ❌ Avoid - too many props
<Card 
  title="Patient Info"
  content={content}
  showHeader={true}
  headerAlign="left"
/>
```

### 4. Use Tailwind with Design Tokens
```typescript
// Tailwind config includes our ice theme
className="bg-white text-deep-ice p-comfortable rounded-lg"
```

### 5. Loading States
Every component that fetches data needs loading state:
```typescript
export function MedicationList({ patientId }: Props) {
  const [medications, setMedications] = useState([]);
  const [loading, setLoading] = useState(true);

  if (loading) {
    return <SkeletonLoader />;
  }

  return (
    <div>
      {medications.map(med => <MedicationCard key={med.id} {...med} />)}
    </div>
  );
}
```

### 6. Error Boundaries
Wrap features in error boundaries:
```typescript
<ErrorBoundary fallback={<ErrorState />}>
  <PrescribingFlow />
</ErrorBoundary>
```

## Component Examples

### Card Component
```typescript
interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export function Card({ children, className, hover = false }: CardProps) {
  return (
    <div
      className={cn(
        'bg-white rounded-lg shadow-sm p-6 mb-4',
        hover && 'hover:shadow-md transition-shadow',
        className
      )}
    >
      {children}
    </div>
  );
}
```

### Alert Component
```typescript
interface AlertProps {
  severity: 'critical' | 'warning' | 'info' | 'success';
  title?: string;
  children: React.ReactNode;
  onDismiss?: () => void;
}

export function Alert({ severity, title, children, onDismiss }: AlertProps) {
  const styles = {
    critical: 'bg-red-50 border-l-critical text-critical',
    warning: 'bg-yellow-50 border-l-warning text-amber-900',
    info: 'bg-blue-50 border-l-info text-blue-900',
    success: 'bg-green-50 border-l-success text-green-900',
  };

  return (
    <div className={cn('border-l-4 p-5 rounded-md', styles[severity])}>
      {title && <h3 className="font-semibold mb-2">{title}</h3>}
      <div>{children}</div>
      {onDismiss && (
        <button onClick={onDismiss} className="mt-3 text-sm underline">
          Dismiss
        </button>
      )}
    </div>
  );
}
```

## When to Create New Components

Create a new component when:
- Used in 2+ places
- Has distinct visual identity
- Has its own state/logic
- Represents a domain concept (AllergyBadge, PrescriptionCard)

Keep as regular markup when:
- Used only once
- Just styling/layout
- No logic
