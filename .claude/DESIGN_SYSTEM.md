# Livny Health Design System

## Visual Identity: Ice/Nordic Theme

### Core Philosophy
- Lots of white space (like fresh snow)
- Cool blues as accents (ice, clear winter sky)
- Crisp typography
- Minimal borders - use subtle shadows instead
- Clean, calm, focused

## Color Palette

### Primary (Ice/Snow)
```css
--color-white: #FFFFFF;           /* Main background */
--color-snow: #F8FAFB;            /* Secondary background, cards */
--color-frost: #F0F4F7;           /* Tertiary, hover states */
```

### Accent (Nordic Blue)
```css
--color-glacier-blue: #4A90E2;    /* Primary actions, links */
--color-deep-ice: #2E5C8A;        /* Headers, important text */
--color-arctic: #E8F2F9;          /* Selected states, highlights */
```

### Functional
```css
--color-critical: #E74C3C;        /* Allergies, critical alerts */
--color-warning: #F39C12;         /* Warnings */
--color-success: #27AE60;         /* Completed, success */
--color-info: #3498DB;            /* Informational */
```

### Text
```css
--color-text-primary: #2C3E50;    /* Almost black, but softer */
--color-text-secondary: #5D6D7E;  /* Supporting text */
--color-text-tertiary: #95A5A6;   /* Labels, hints */
```

## Typography

### Font Stack
```css
font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
```

### Type Scale
- **Headers**: 24px/20px/18px (weight 600)
- **Body**: 15px (weight 400)
- **Small**: 13px (weight 400)
- **Tiny labels**: 11px uppercase (weight 500, letter-spacing: 0.5px)

## Spacing System

Everything is multiples of 8:
```css
--spacing-tight: 8px;
--spacing-normal: 16px;
--spacing-comfortable: 24px;
--spacing-generous: 32px;
--spacing-section: 48px;
```

## Component Patterns

### Card
Standard white card with subtle shadow:
```css
.card {
  background: var(--color-white);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}
```

### Button
```css
/* Primary */
.btn-primary {
  background: var(--color-glacier-blue);
  color: white;
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 500;
  border: none;
  box-shadow: 0 2px 4px rgba(74, 144, 226, 0.2);
}

.btn-primary:hover {
  background: #3A7BC8;
  box-shadow: 0 4px 8px rgba(74, 144, 226, 0.3);
}

/* Secondary */
.btn-secondary {
  background: white;
  color: var(--color-glacier-blue);
  border: 1px solid var(--color-arctic);
  padding: 12px 24px;
  border-radius: 6px;
}
```

### Input
```css
input, textarea {
  background: white;
  border: 1px solid var(--color-arctic);
  border-radius: 6px;
  padding: 12px 16px;
  font-size: 15px;
  transition: all 0.2s;
}

input:focus {
  outline: none;
  border-color: var(--color-glacier-blue);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}
```

### Alert
```css
/* Critical */
.alert-critical {
  background: #FADBD8;
  border-left: 4px solid var(--color-critical);
  padding: 20px;
  border-radius: 6px;
}

/* Warning */
.alert-warning {
  background: #FEF5E7;
  border-left: 4px solid var(--color-warning);
  padding: 20px;
  border-radius: 6px;
}
```

## Layout Principles

### Max Content Width
Don't stretch content across ultra-wide monitors:
```css
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 32px;
}
```

### No Clutter Rules
1. **No permanent sidebars** - navigation is contextual
2. **No tab overload** - one primary view at a time
3. **Generous white space** - content breathes
4. **2-3 actions max** at bottom of screen

## Animation
Subtle, purposeful motion only:
```css
/* Transitions */
transition: all 150ms ease-out;

/* Page transitions */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* NO bouncing, sliding, spinning, flipping */
```

## DO's and DON'Ts

### DO:
✅ Use generous white space
✅ Limit information on screen
✅ Use subtle shadows instead of borders
✅ Keep actions to 2-3 per screen
✅ Use progressive disclosure
✅ Make text readable (15px minimum)

### DON'T:
❌ Cram multiple panels on screen
❌ Use heavy borders
❌ Use more than 3 colors per screen
❌ Use emojis (except for patient-facing)
❌ Create walls of text
❌ Use table layouts (prefer cards)
