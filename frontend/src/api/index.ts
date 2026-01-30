export { searchMedications, getMedicationDefaults, discontinueMedication } from './medicationApi';
export { getPatients, getPatient, checkAllergyConflict, logAllergyOverride, checkDrugInteractions, logInteractionOverride, submitPrescription, getVisitHistory, getVisitProviders, getProblemDetail, reactivateProblem } from './patientApi';
export type { AllergyOverrideLogRequest, InteractionOverrideLogRequest, PrescribedMedication, PrescriptionResponse } from './patientApi';
export { getDailySchedule } from './scheduleApi';
export { getChartSections } from './chartApi';
export { mockUsers, mockMedications } from './mockData';
export { getPatientAlerts, getAlertSummary, acknowledgeAlert, dismissAlert } from './alertApi';
export type { GetAlertsParams, AcknowledgeAlertParams, DismissAlertParams } from './alertApi';
export {
  createEncounter,
  getEncounter,
  saveEncounterNote,
  getNoteVersions,
  getNoteVersionContent,
  transitionEncounterStatus,
  getEncounterAudit,
  createAddendum,
  getEncounterByAppointment,
  VersionConflictException,
  InvalidTransitionException,
} from './encounterApi';
export type { CreateEncounterRequest, SaveNoteRequest, TransitionStatusRequest, CreateAddendumRequest } from './encounterApi';
export { getPatientContext, getQuickContextSummary } from './patientContextApi';
