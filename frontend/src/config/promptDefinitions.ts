import type { DocumentationPrompt, SOAPSectionKey, EncounterType } from '../types/guidance';

export const SECTION_LABELS: Record<SOAPSectionKey, string> = {
  subjective: 'Subjective',
  objective: 'Objective',
  assessment: 'Assessment',
  plan: 'Plan',
};

export const SECTION_LETTERS: Record<SOAPSectionKey, string> = {
  subjective: 'S',
  objective: 'O',
  assessment: 'A',
  plan: 'P',
};

const ALL_ENCOUNTER_TYPES: EncounterType[] = [
  'office_visit',
  'telehealth',
  'urgent_care',
  'emergency',
  'hospital_admission',
  'procedure',
  'lab_only',
  'follow_up',
  'annual_physical',
];

export const SUBJECTIVE_PROMPTS: DocumentationPrompt[] = [
  {
    id: 'chief_complaint',
    label: 'Chief Complaint',
    description: 'Primary reason for the visit in patient\'s words',
    keywords: ['chief complaint', 'cc:', 'presents with', 'presenting', 'reason for visit', 'here for', 'complains of', 'complaining of'],
    required: true,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
  {
    id: 'hpi',
    label: 'History of Present Illness',
    description: 'Detailed description of current symptoms and timeline',
    keywords: ['hpi', 'history of present illness', 'onset', 'duration', 'location', 'quality', 'severity', 'timing', 'context', 'modifying factors', 'associated symptoms', 'began', 'started', 'worsening', 'improving'],
    required: true,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
  {
    id: 'ros',
    label: 'Review of Systems',
    description: 'Systematic review of body systems',
    keywords: ['ros', 'review of systems', 'constitutional', 'eyes', 'ent', 'cardiovascular', 'respiratory', 'gastrointestinal', 'genitourinary', 'musculoskeletal', 'integumentary', 'neurological', 'psychiatric', 'endocrine', 'hematologic', 'allergic', 'denies', 'positive for', 'negative for'],
    required: false,
    encounterTypes: ['office_visit', 'follow_up', 'annual_physical', 'urgent_care'],
  },
  {
    id: 'relevant_history',
    label: 'Relevant History',
    description: 'Pertinent past medical, surgical, family, social history',
    keywords: ['pmh', 'past medical history', 'psh', 'past surgical history', 'fh', 'family history', 'sh', 'social history', 'medications', 'allergies', 'immunizations'],
    required: false,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
  {
    id: 'patient_concerns',
    label: 'Patient Concerns',
    description: 'Patient\'s questions, goals, or concerns',
    keywords: ['patient concerns', 'patient questions', 'patient goals', 'worried about', 'concerned about', 'wants to know', 'asks about', 'fears', 'expectations'],
    required: false,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
];

export const OBJECTIVE_PROMPTS: DocumentationPrompt[] = [
  {
    id: 'vital_signs',
    label: 'Vital Signs',
    description: 'Temperature, BP, HR, RR, SpO2, weight',
    keywords: ['vitals', 'vital signs', 'bp', 'blood pressure', 'hr', 'heart rate', 'pulse', 'rr', 'respiratory rate', 'temp', 'temperature', 'spo2', 'oxygen saturation', 'weight', 'bmi', 'height'],
    required: true,
    encounterTypes: ['office_visit', 'procedure', 'urgent_care', 'emergency', 'annual_physical'],
  },
  {
    id: 'general_appearance',
    label: 'General Appearance',
    description: 'Overall patient presentation',
    keywords: ['general', 'appearance', 'well-appearing', 'ill-appearing', 'alert', 'oriented', 'no acute distress', 'nad', 'comfortable', 'anxious', 'fatigued'],
    required: true,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
  {
    id: 'physical_exam',
    label: 'Physical Exam',
    description: 'Examination findings by body system',
    keywords: ['physical exam', 'pe', 'examination', 'heent', 'lungs', 'heart', 'abdomen', 'extremities', 'skin', 'neurologic', 'musculoskeletal', 'auscultation', 'palpation', 'percussion', 'inspection', 'normal', 'abnormal', 'unremarkable', 'notable for'],
    required: true,
    encounterTypes: ['office_visit', 'follow_up', 'procedure', 'urgent_care', 'emergency', 'annual_physical'],
  },
  {
    id: 'results',
    label: 'Results',
    description: 'Lab values, imaging, diagnostic test results',
    keywords: ['results', 'labs', 'laboratory', 'imaging', 'x-ray', 'ct', 'mri', 'ultrasound', 'ekg', 'ecg', 'cbc', 'cmp', 'bmp', 'urinalysis', 'culture', 'pathology', 'biopsy'],
    required: false,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
];

export const ASSESSMENT_PROMPTS: DocumentationPrompt[] = [
  {
    id: 'diagnosis',
    label: 'Diagnosis',
    description: 'Primary and secondary diagnoses',
    keywords: ['diagnosis', 'diagnoses', 'dx', 'impression', 'assessment', 'icd', 'condition', 'disease', 'disorder', 'syndrome', 'infection', 'inflammation'],
    required: true,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
  {
    id: 'problem_status',
    label: 'Problem Status',
    description: 'Status of each problem (stable, improving, worsening)',
    keywords: ['stable', 'improving', 'worsening', 'resolved', 'controlled', 'uncontrolled', 'acute', 'chronic', 'exacerbation', 'remission', 'new', 'ongoing', 'status'],
    required: false,
    encounterTypes: ['follow_up', 'annual_physical'],
  },
  {
    id: 'clinical_reasoning',
    label: 'Clinical Reasoning',
    description: 'Explanation of diagnostic thinking',
    keywords: ['clinical reasoning', 'because', 'due to', 'likely', 'suggests', 'consistent with', 'indicative of', 'based on', 'given the', 'findings suggest', 'concerning for'],
    required: false,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
  {
    id: 'differential',
    label: 'Differential Diagnosis',
    description: 'Alternative diagnoses being considered',
    keywords: ['differential', 'ddx', 'rule out', 'r/o', 'versus', 'vs', 'consider', 'possible', 'alternative diagnoses', 'less likely'],
    required: false,
    encounterTypes: ['office_visit', 'urgent_care', 'emergency'],
  },
];

export const PLAN_PROMPTS: DocumentationPrompt[] = [
  {
    id: 'medications',
    label: 'Medications',
    description: 'Prescriptions, changes, or discontinuations',
    keywords: ['medication', 'medications', 'rx', 'prescribe', 'prescribed', 'start', 'continue', 'discontinue', 'stop', 'increase', 'decrease', 'refill', 'dose', 'mg', 'daily', 'twice daily', 'bid', 'tid', 'qid', 'prn'],
    required: false,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
  {
    id: 'orders',
    label: 'Orders',
    description: 'Labs, imaging, referrals, procedures ordered',
    keywords: ['order', 'orders', 'ordered', 'lab', 'imaging', 'referral', 'refer', 'consult', 'procedure', 'schedule', 'obtain', 'check', 'send', 'request'],
    required: false,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
  {
    id: 'follow_up',
    label: 'Follow-Up',
    description: 'When and why to return',
    keywords: ['follow up', 'follow-up', 'f/u', 'return', 'recheck', 'weeks', 'months', 'if worsens', 'if no improvement', 'prn', 'as needed', 'schedule', 'appointment'],
    required: true,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
  {
    id: 'patient_education',
    label: 'Patient Education',
    description: 'Instructions and counseling provided',
    keywords: ['education', 'counseled', 'discussed', 'explained', 'instructions', 'advised', 'encouraged', 'handout', 'diet', 'exercise', 'lifestyle', 'smoking cessation', 'compliance', 'adherence'],
    required: false,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
  {
    id: 'contingency',
    label: 'Contingency Plan',
    description: 'What to do if condition changes',
    keywords: ['contingency', 'if worsens', 'if no improvement', 'return precautions', 'warning signs', 'seek care if', 'emergency', 'call if', 'go to er if', 'red flags'],
    required: false,
    encounterTypes: ALL_ENCOUNTER_TYPES,
  },
];

export const ALL_PROMPTS: Record<SOAPSectionKey, DocumentationPrompt[]> = {
  subjective: SUBJECTIVE_PROMPTS,
  objective: OBJECTIVE_PROMPTS,
  assessment: ASSESSMENT_PROMPTS,
  plan: PLAN_PROMPTS,
};

export function getPromptsForEncounterType(
  section: SOAPSectionKey,
  encounterType: EncounterType
): DocumentationPrompt[] {
  return ALL_PROMPTS[section].filter((prompt) =>
    prompt.encounterTypes.includes(encounterType)
  );
}

export function getAllPromptsForEncounterType(
  encounterType: EncounterType
): Record<SOAPSectionKey, DocumentationPrompt[]> {
  return {
    subjective: getPromptsForEncounterType('subjective', encounterType),
    objective: getPromptsForEncounterType('objective', encounterType),
    assessment: getPromptsForEncounterType('assessment', encounterType),
    plan: getPromptsForEncounterType('plan', encounterType),
  };
}
