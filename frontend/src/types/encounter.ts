/**
 * Encounter types for clinical workflow.
 */

// Encounter status represents the clinical workflow state
export type EncounterStatus = 'scheduled' | 'in_progress' | 'completed' | 'signed';

// The current mode of the encounter workspace UI
export type EncounterWorkspaceMode = 'review' | 'documentation' | 'completed' | 'signed';

// Core encounter note data
export interface EncounterNote {
  id: string;
  status: EncounterStatus;
  type?: string;
  chiefComplaint?: string;
  // Note content
  noteContent?: string;
  noteVersion: number;
  noteWordCount: number;
  noteUpdatedAt?: string;
  // Workflow timestamps
  openedAt?: string;
  completedAt?: string;
  signedAt?: string;
  reopenedAt?: string;
  // Signature info
  signedById?: string;
  signedByName?: string;
  // Time info
  startTime?: string;
  endTime?: string;
}

// Patient summary for encounter context
export interface PatientSummary {
  id: string;
  name: string;
  dateOfBirth: string;
  gender: string;
  mrn: string;
}

// Vital sign for context display
export interface ContextVital {
  id: string;
  vitalType: string;
  displayName?: string;
  value: number;
  unit: string;
  displayValue?: string;
  status: 'normal' | 'abnormal' | 'critical';
  recordedAt: string;
}

// Medication for context display
export interface ContextMedication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
}

// Allergy for context display
export interface ContextAllergy {
  id: string;
  allergen: string;
  reaction: string;
  severity: 'mild' | 'moderate' | 'severe';
  isAnaphylaxis: boolean;
}

// Problem for context display
export interface ContextProblem {
  name: string;
  icd10Code: string;
  status: 'active' | 'inactive' | 'resolved';
  isCritical: boolean;
}

// Lab result for context display
export interface ContextLab {
  id: string;
  testName: string;
  value: string;
  unit: string;
  status: 'normal' | 'abnormal' | 'critical';
  collectionDate: string;
}

// Recent visit for context display
export interface ContextVisit {
  id: string;
  date: string;
  visitType: string;
  chiefComplaint: string;
}

// Context shown alongside the encounter
export interface EncounterContext {
  vitals: ContextVital[];
  medications: ContextMedication[];
  allergies: ContextAllergy[];
  problems: ContextProblem[];
  recentLabs: ContextLab[];
  recentVisits: ContextVisit[];
}

// Full encounter with context
export interface EncounterWithContext {
  encounter: EncounterNote;
  patient: PatientSummary;
  context: EncounterContext;
}

// Result from saving a note
export interface NoteSaveResult {
  success: boolean;
  version: number;
  wordCount: number;
  savedAt: string;
}

// Version conflict error details
export interface VersionConflictError {
  expectedVersion: number;
  currentVersion: number;
  serverContent: string;
}

// Note version history entry
export interface NoteVersion {
  version: number;
  wordCount: number;
  saveType: 'auto' | 'manual';
  createdAt: string;
}

// Response for note versions
export interface NoteVersionsResponse {
  encounterId: string;
  currentVersion: number;
  versions: NoteVersion[];
}

// Status audit trail entry
export interface StatusAuditEntry {
  id: string;
  fromStatus: EncounterStatus | null;
  toStatus: EncounterStatus;
  changedById?: string;
  changedByName?: string;
  changedAt: string;
  reason?: string;
}

// Result from status transition
export interface StatusTransitionResult {
  encounterId: string;
  previousStatus: EncounterStatus;
  newStatus: EncounterStatus;
  transitionedAt: string;
  signedByName?: string;
}

// Addendum data
export interface Addendum {
  id: string;
  content: string;
  reason: string;
  createdAt: string;
  createdById?: string;
  createdByName?: string;
}

// Result from creating addendum
export interface AddendumResult {
  encounterId: string;
  addendum: Addendum;
}

// SOAP section completeness
export type SOAPCompleteness = 'empty' | 'partial' | 'complete';

// Individual SOAP section
export interface SOAPSection {
  content: string;
  completeness: SOAPCompleteness;
  wordCount: number;
}

// Full SOAP mapping response
export interface SOAPMappingResponse {
  subjective: SOAPSection;
  objective: SOAPSection;
  assessment: SOAPSection;
  plan: SOAPSection;
  overallCompleteness: SOAPCompleteness;
}
