# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Livny Health is a modern EHR (Electronic Health Record) system with an ice/Nordic aesthetic, focused on progressive disclosure and context-driven UI. Current focus: physician prescribing workflow.

## Tech Stack

- **Frontend**: React 19 + TypeScript + Tailwind CSS + Vite
- **Backend**: FastAPI (Python) - BFF pattern
- **Dev server**: http://localhost:5173 (frontend), http://localhost:8000 (backend)

## Commands

All commands run from `frontend/`:

```bash
npm run dev      # Start dev server with HMR
npm run build    # TypeScript check + production build
npm run lint     # Run ESLint
npm run preview  # Preview production build
```

## Reference Files

Before modifying UI code, consult:
- `.claude/DESIGN_SYSTEM.md` - Colors, typography, spacing
- `.claude/COMPONENT_PATTERNS.md` - Component structure
- `.claude/API_CONTRACTS.md` - API specifications
- `frontend/tailwind.config.js` - Design tokens

## Architecture

```
frontend/src/
├── components/
│   ├── ui/           # Base components (Button, Card, Input, Alert)
│   ├── patient/      # Patient domain components
│   └── medication/   # Medication domain components
├── pages/            # Page-level components
├── api/              # API client
├── hooks/            # Custom React hooks
├── utils/            # Utilities (includes cn() for Tailwind class merging)
└── types/            # TypeScript definitions
```

## Code Standards

### Component Pattern
- Named exports only (no default exports)
- TypeScript interfaces for all props (suffix with `Props`)
- Include loading/error/empty states for data-fetching components
- Composition over props drilling

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  children: React.ReactNode;
}

export function Button({ variant = 'primary', children }: ButtonProps) {
  return (
    <button className={cn('px-6 py-3', variant === 'primary' && 'bg-glacier-blue')}>
      {children}
    </button>
  );
}
```

### Styling
- Tailwind only (no CSS modules, no inline styles)
- Use design tokens: `glacier-blue`, `deep-ice`, `arctic`, `snow`, `frost`
- Spacing tokens: `tight` (8px), `normal` (16px), `comfortable` (24px), `generous` (32px)
- Shadows: `shadow-card`, `shadow-card-hover` (not borders)

### Design Constraints
- 15px minimum font size
- Max 3 colors per screen
- 2-3 actions max per screen
- Cards over tables
- Generous white space
- No permanent sidebars
