export type ChartSectionId =
  | 'visits'
  | 'medications'
  | 'allergies'
  | 'labs'
  | 'problems'
  | 'vitals'
  | 'imaging'
  | 'social-family';

export type AlertLevel = 'none' | 'info' | 'warning' | 'critical';

export type SectionIcon =
  | 'document'
  | 'pill'
  | 'exclamation-triangle'
  | 'beaker'
  | 'clipboard-list'
  | 'heart-pulse'
  | 'film'
  | 'users';

export interface KeyboardShortcut {
  key: string;
  modifier: string;
  description: string;
}

export interface ChartSection {
  id: ChartSectionId;
  name: string;
  icon: SectionIcon;
  order: number;
  hasData: boolean;
  lastUpdated: string | null;
  alertLevel: AlertLevel;
  badgeCount: number | null;
  keyboardShortcut: KeyboardShortcut;
}

export interface ChartSectionsResponse {
  patientId: string;
  sections: ChartSection[];
}
