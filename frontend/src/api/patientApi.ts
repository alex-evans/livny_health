import type { Patient, AllergyCheckResult, DrugInteractionCheckResult, LabHistoryResponse, VisitHistoryResponse, VisitHistoryParams, VisitProvidersResponse, ProblemDetailResponse, Problem } from '../types';

const BFF_URL = 'http://localhost:8000';

export interface AllergyOverrideLogRequest {
  patient_id: string;
  medication_name: string;
  allergen: string;
  severity: string;
  justification: string;
  acknowledged_at: string;
  prescribed_at: string;
}

export async function logAllergyOverride(
  override: AllergyOverrideLogRequest
): Promise<{ success: boolean; logId: string }> {
  const response = await fetch(`${BFF_URL}/allergy-overrides`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(override),
  });

  if (!response.ok) {
    throw new Error('Failed to log allergy override');
  }

  return response.json();
}

export async function checkAllergyConflict(
  patientId: string,
  medicationName: string
): Promise<AllergyCheckResult> {
  const response = await fetch(`${BFF_URL}/patients/${patientId}/check-allergy`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ medication_name: medicationName }),
  });

  if (!response.ok) {
    throw new Error('Failed to check allergy');
  }

  return response.json();
}

export async function getPatients(): Promise<Patient[]> {
  const response = await fetch(`${BFF_URL}/patients`);
  if (!response.ok) {
    throw new Error('Failed to fetch patients');
  }
  return response.json();
}

export async function getPatient(patientId: string): Promise<Patient> {
  const response = await fetch(`${BFF_URL}/patients/${patientId}`);
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Patient not found');
    }
    throw new Error('Failed to fetch patient');
  }
  return response.json();
}

export async function checkDrugInteractions(
  patientId: string,
  medicationName: string
): Promise<DrugInteractionCheckResult> {
  const response = await fetch(`${BFF_URL}/patients/${patientId}/check-interactions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ medication_name: medicationName }),
  });

  if (!response.ok) {
    throw new Error('Failed to check drug interactions');
  }

  return response.json();
}

export interface InteractionOverrideLogRequest {
  patient_id: string;
  medication_name: string;
  interacting_drugs: string[];
  severities: string[];
  justification: string;
  acknowledged_at: string;
  prescribed_at: string;
}

export async function logInteractionOverride(
  override: InteractionOverrideLogRequest
): Promise<{ success: boolean; logId: string }> {
  const response = await fetch(`${BFF_URL}/interaction-overrides`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(override),
  });

  if (!response.ok) {
    throw new Error('Failed to log interaction override');
  }

  return response.json();
}

export interface PrescribedMedication {
  name: string;
  dosage: string;
  frequency: string;
  duration_days: number;
  instructions?: string;
}

export interface PrescriptionResponse {
  success: boolean;
  prescriptionId: string;
  medications: {
    id: string;
    name: string;
    dosage: string;
    frequency: string;
    started: string;
  }[];
}

export async function submitPrescription(
  patientId: string,
  medications: PrescribedMedication[]
): Promise<PrescriptionResponse> {
  const response = await fetch(`${BFF_URL}/medications/${patientId}/prescriptions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ medications }),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Patient not found');
    }
    throw new Error('Failed to submit prescription');
  }

  return response.json();
}

export async function getLabHistory(
  patientId: string,
  testName: string,
  daysBack: number = 365
): Promise<LabHistoryResponse> {
  const response = await fetch(
    `${BFF_URL}/patients/${patientId}/labs/${encodeURIComponent(testName)}/history?days_back=${daysBack}`
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Lab history not found');
    }
    throw new Error('Failed to fetch lab history');
  }

  return response.json();
}

export async function getProblemDetail(
  patientId: string,
  icd10Code: string
): Promise<ProblemDetailResponse | null> {
  const response = await fetch(
    `${BFF_URL}/patients/${patientId}/problems/${encodeURIComponent(icd10Code)}`
  );

  if (!response.ok) {
    if (response.status === 404) {
      return null;
    }
    throw new Error('Failed to fetch problem detail');
  }

  return response.json();
}

export async function reactivateProblem(
  patientId: string,
  icd10Code: string,
  providerName: string
): Promise<Problem> {
  const response = await fetch(
    `${BFF_URL}/patients/${patientId}/problems/${encodeURIComponent(icd10Code)}/reactivate`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ providerName }),
    }
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Problem not found');
    }
    throw new Error('Failed to reactivate problem');
  }

  return response.json();
}

// Mock visit data for development with full SOAP notes, vitals, medications, and orders
const mockVisits: VisitHistoryResponse = {
  offset: 0,
  limit: 20,
  visits: [
    {
      id: 'v1',
      date: '2025-12-15T10:30:00Z',
      visitType: 'office_visit',
      status: 'completed',
      chiefComplaint: 'Annual wellness exam',
      diagnoses: [
        { code: 'Z00.00', description: 'Encounter for general adult medical examination without abnormal findings', isPrimary: true },
        { code: 'E11.9', description: 'Type 2 diabetes mellitus without complications', isPrimary: false },
      ],
      provider: { id: 'p1', name: 'Dr. Emily Chen', role: 'Attending', specialty: 'Internal Medicine' },
      location: 'Livny Health Clinic - Main',
      duration: 45,
      soapNote: {
        subjective: 'Patient presents for annual wellness exam. Reports feeling generally well. Denies chest pain, shortness of breath, or palpitations. Diabetes well-controlled with current regimen. Occasional mild headaches, relieved with acetaminophen. Sleep quality good, 7-8 hours nightly. No recent weight changes.',
        objective: 'General: Well-appearing, no acute distress. HEENT: PERRLA, oropharynx clear. CV: RRR, no murmurs. Lungs: CTA bilaterally. Abdomen: Soft, non-tender, no organomegaly. Extremities: No edema, pulses 2+ bilaterally. Skin: No rashes or lesions. Neuro: A&O x3, cranial nerves intact.',
        assessment: '1. Type 2 diabetes mellitus - well controlled on current regimen\n2. Essential hypertension - at goal\n3. Hyperlipidemia - stable on statin therapy\n4. Health maintenance up to date',
        plan: '1. Continue current medications\n2. HbA1c in 3 months\n3. Lipid panel in 6 months\n4. Schedule colonoscopy (due for screening)\n5. Flu vaccine administered today\n6. Return in 6 months or sooner if concerns',
      },
      vitals: {
        bloodPressureSystolic: 132,
        bloodPressureDiastolic: 78,
        heartRate: 72,
        temperature: 98.4,
        temperatureUnit: 'F',
        weight: 156,
        weightUnit: 'lbs',
        oxygenSaturation: 98,
        respiratoryRate: 16,
      },
      medications: [
        { id: 'vm-1', name: 'Influenza Vaccine', dosage: '0.5mL', frequency: 'once', action: 'prescribed', route: 'IM', instructions: 'Administered left deltoid' },
      ],
      orders: [
        { id: 'ord-1', orderType: 'lab', name: 'HbA1c', status: 'completed', orderedAt: '2025-12-15T10:30:00Z', completedAt: '2025-12-17T14:00:00Z', result: '6.8%', priority: 'routine' },
        { id: 'ord-2', orderType: 'lab', name: 'Lipid Panel', status: 'completed', orderedAt: '2025-12-15T10:30:00Z', completedAt: '2025-12-17T14:00:00Z', result: 'TC 210, LDL 135, HDL 55, TG 150', priority: 'routine' },
        { id: 'ord-3', orderType: 'referral', name: 'Colonoscopy - GI', status: 'pending', orderedAt: '2025-12-15T10:30:00Z', priority: 'routine' },
      ],
    },
    {
      id: 'v2',
      date: '2025-10-22T14:00:00Z',
      visitType: 'follow_up',
      status: 'completed',
      chiefComplaint: 'Diabetes follow-up, medication review',
      diagnoses: [
        { code: 'E11.65', description: 'Type 2 diabetes mellitus with hyperglycemia', isPrimary: true },
      ],
      provider: { id: 'p1', name: 'Dr. Emily Chen', role: 'Attending', specialty: 'Internal Medicine' },
      location: 'Livny Health Clinic - Main',
      duration: 30,
      soapNote: {
        subjective: 'Patient returns for diabetes follow-up. Reports good compliance with metformin. Checking blood sugars 2-3x weekly, fasting readings 110-130. No hypoglycemic episodes. Denies polyuria, polydipsia, or blurred vision. Diet adherence fair - admits to occasional sweets.',
        objective: 'General: NAD. Weight stable. CV: RRR. Extremities: No ulcers, sensation intact to monofilament bilateral feet. Skin: No concerning lesions.',
        assessment: 'Type 2 DM with recent hyperglycemia, improving with lifestyle modifications. A1C elevated at 7.2% (down from 7.8%).',
        plan: '1. Continue metformin 500mg BID\n2. Reinforce dietary counseling - limit simple carbohydrates\n3. Increase home glucose monitoring to daily fasting\n4. Recheck A1C in 3 months\n5. Annual eye exam due - referral placed\n6. Follow up in 3 months',
      },
      vitals: {
        bloodPressureSystolic: 138,
        bloodPressureDiastolic: 82,
        heartRate: 76,
        temperature: 98.6,
        weight: 158,
        weightUnit: 'lbs',
        oxygenSaturation: 97,
      },
      orders: [
        { id: 'ord-4', orderType: 'lab', name: 'HbA1c', status: 'completed', orderedAt: '2025-10-22T14:00:00Z', completedAt: '2025-10-24T10:00:00Z', result: '7.2%', priority: 'routine' },
        { id: 'ord-5', orderType: 'referral', name: 'Ophthalmology - Diabetic Eye Exam', status: 'completed', orderedAt: '2025-10-22T14:00:00Z', completedAt: '2025-11-20T09:00:00Z', result: 'No diabetic retinopathy', priority: 'routine' },
      ],
    },
    {
      id: 'v3',
      date: '2025-09-08T09:15:00Z',
      visitType: 'urgent_care',
      status: 'completed',
      chiefComplaint: 'Acute sinusitis symptoms x 5 days',
      diagnoses: [
        { code: 'J01.90', description: 'Acute sinusitis, unspecified', isPrimary: true },
      ],
      provider: { id: 'p2', name: 'Dr. Michael Torres', role: 'Attending', specialty: 'Family Medicine' },
      location: 'Livny Health Urgent Care',
      duration: 20,
      notes: 'Prescribed azithromycin due to penicillin allergy. Return if symptoms worsen.',
      soapNote: {
        subjective: 'Patient presents with 5-day history of nasal congestion, facial pressure/pain over maxillary sinuses bilaterally, thick yellow-green nasal discharge, and low-grade fever (100.2°F at home). Tried OTC decongestants with minimal relief. Denies severe headache, vision changes, or neck stiffness. Has known penicillin allergy (anaphylaxis).',
        objective: 'T 99.8°F. General: Mild distress due to congestion. HEENT: Tenderness to palpation over maxillary sinuses bilaterally, nasal mucosa erythematous with purulent discharge, posterior pharynx with postnasal drip, TMs clear. Lungs: CTA. No lymphadenopathy.',
        assessment: 'Acute bacterial sinusitis, likely secondary to viral URI. Patient has penicillin allergy precluding amoxicillin use.',
        plan: '1. Azithromycin 500mg day 1, then 250mg days 2-5 (Z-pack) - avoiding penicillin class due to allergy\n2. Nasal saline irrigation TID\n3. Sudafed 30mg q6h PRN congestion\n4. Increase fluid intake\n5. Return if worsening, high fever, or no improvement in 72 hours\n6. Follow up with PCP if symptoms persist beyond 10 days',
      },
      vitals: {
        bloodPressureSystolic: 128,
        bloodPressureDiastolic: 76,
        heartRate: 84,
        temperature: 99.8,
        weight: 155,
        weightUnit: 'lbs',
        oxygenSaturation: 98,
      },
      medications: [
        { id: 'vm-2', name: 'Azithromycin (Z-pack)', dosage: '250mg', frequency: 'daily x 5 days', action: 'prescribed', route: 'oral', instructions: '500mg day 1, then 250mg days 2-5' },
      ],
    },
    {
      id: 'v4',
      date: '2025-07-14T11:00:00Z',
      visitType: 'telehealth',
      status: 'completed',
      chiefComplaint: 'Blood pressure medication refill',
      diagnoses: [
        { code: 'I10', description: 'Essential (primary) hypertension', isPrimary: true },
      ],
      provider: { id: 'p1', name: 'Dr. Emily Chen', role: 'Attending', specialty: 'Internal Medicine' },
      duration: 15,
      soapNote: {
        subjective: 'Telehealth visit for BP medication refill. Patient reports home BP readings averaging 130-135/80-85. Taking lisinopril 10mg daily as prescribed. No dizziness, cough, or swelling. No chest pain or shortness of breath.',
        objective: 'Patient appears well via video. Alert and oriented. No visible distress. Patient reports home BP today 134/82.',
        assessment: 'Essential hypertension, reasonably controlled on current regimen.',
        plan: '1. Continue lisinopril 10mg daily\n2. Refill authorized - 90-day supply with 3 refills\n3. Continue home BP monitoring\n4. Labs due at next in-person visit\n5. Follow up in 6 months or sooner if BP consistently elevated',
      },
      medications: [
        { id: 'vm-3', name: 'Lisinopril', dosage: '10mg', frequency: 'daily', action: 'continued', route: 'oral' },
      ],
    },
    {
      id: 'v5',
      date: '2025-05-03T08:30:00Z',
      visitType: 'lab_only',
      status: 'completed',
      chiefComplaint: 'Routine lab work - HbA1c, lipid panel',
      diagnoses: [
        { code: 'Z13.1', description: 'Encounter for screening for diabetes mellitus', isPrimary: true },
      ],
      provider: { id: 'p3', name: 'Lab Services', role: 'Laboratory', specialty: undefined },
      location: 'Livny Health Lab Services',
      duration: 10,
      soapNote: {
        subjective: 'Patient presents for scheduled lab work. Fasting since midnight. No acute complaints.',
        objective: 'Venipuncture performed, left antecubital fossa. Hemostasis achieved.',
        assessment: 'Lab draw completed without complication.',
        plan: 'Results to be reviewed by PCP and communicated to patient.',
      },
      vitals: {
        bloodPressureSystolic: 130,
        bloodPressureDiastolic: 80,
        heartRate: 70,
      },
      orders: [
        { id: 'ord-6', orderType: 'lab', name: 'HbA1c', status: 'completed', orderedAt: '2025-05-03T08:30:00Z', completedAt: '2025-05-04T10:00:00Z', result: '7.8%', priority: 'routine' },
        { id: 'ord-7', orderType: 'lab', name: 'Lipid Panel', status: 'completed', orderedAt: '2025-05-03T08:30:00Z', completedAt: '2025-05-04T10:00:00Z', result: 'TC 225, LDL 142, HDL 48, TG 165', priority: 'routine' },
      ],
    },
    {
      id: 'v6',
      date: '2025-03-20T10:00:00Z',
      visitType: 'office_visit',
      status: 'completed',
      chiefComplaint: 'Follow-up hypertension, diabetes management',
      diagnoses: [
        { code: 'I10', description: 'Essential (primary) hypertension', isPrimary: true },
        { code: 'E11.9', description: 'Type 2 diabetes mellitus without complications', isPrimary: false },
      ],
      provider: { id: 'p1', name: 'Dr. Emily Chen', role: 'Attending', specialty: 'Internal Medicine' },
      location: 'Livny Health Clinic - Main',
      duration: 30,
      soapNote: {
        subjective: 'Patient here for chronic disease management. BP has been elevated at home, averaging 145/90. Some dietary indiscretions over holidays. Diabetes: checking sugars sporadically, fasting 130-150. No hypoglycemia. No chest pain, SOB, edema, or vision changes.',
        objective: 'BP 148/92 (elevated). Weight up 4 lbs since last visit. CV: RRR, no murmurs. Lungs: Clear. Extremities: Trace bilateral ankle edema.',
        assessment: '1. Hypertension - suboptimally controlled\n2. Type 2 DM - fair control, needs reinforcement\n3. Weight gain - likely contributing to above',
        plan: '1. Add HCTZ 25mg daily for better BP control\n2. Continue metformin, lisinopril at current doses\n3. Dietary counseling - DASH diet handout provided\n4. Increase physical activity - goal 150 min/week\n5. Labs in 2 weeks to check electrolytes\n6. Follow up in 1 month',
      },
      vitals: {
        bloodPressureSystolic: 148,
        bloodPressureDiastolic: 92,
        heartRate: 78,
        temperature: 98.4,
        weight: 160,
        weightUnit: 'lbs',
        oxygenSaturation: 97,
      },
      medications: [
        { id: 'vm-4', name: 'Hydrochlorothiazide', dosage: '25mg', frequency: 'daily', action: 'prescribed', route: 'oral', instructions: 'Take in the morning' },
      ],
      orders: [
        { id: 'ord-8', orderType: 'lab', name: 'BMP (Basic Metabolic Panel)', status: 'completed', orderedAt: '2025-03-20T10:00:00Z', completedAt: '2025-04-03T14:00:00Z', result: 'Na 140, K 4.2, Cr 0.9, all WNL', priority: 'routine' },
      ],
    },
    {
      id: 'v7',
      date: '2024-11-15T13:30:00Z',
      visitType: 'procedure',
      status: 'completed',
      chiefComplaint: 'Colonoscopy - routine screening',
      diagnoses: [
        { code: 'Z12.11', description: 'Encounter for screening for malignant neoplasm of colon', isPrimary: true },
        { code: 'K63.5', description: 'Polyp of colon', isPrimary: false },
      ],
      provider: { id: 'p4', name: 'Dr. Sarah Kim', role: 'Attending', specialty: 'Gastroenterology' },
      location: 'Livny Health Surgery Center',
      duration: 60,
      notes: 'Two small polyps removed and sent to pathology. Recommend follow-up colonoscopy in 5 years.',
      soapNote: {
        subjective: 'Patient presents for routine screening colonoscopy. Age-appropriate screening. No family history of colon cancer. No recent GI symptoms, bleeding, or weight loss. Completed bowel prep without difficulty.',
        objective: 'Procedure: Colonoscopy performed under moderate sedation (midazolam 3mg, fentanyl 75mcg). Scope advanced to cecum. Cecal landmarks identified. Two small sessile polyps (3mm and 4mm) identified in sigmoid colon and removed via cold snare polypectomy. No complications. Patient tolerated procedure well.',
        assessment: '1. Screening colonoscopy - complete to cecum\n2. Two small sigmoid polyps - removed, sent to pathology',
        plan: '1. Await pathology results (typically 5-7 days)\n2. If tubular adenomas: repeat colonoscopy in 5 years\n3. If hyperplastic only: repeat in 10 years\n4. Resume regular diet today\n5. No driving for 24 hours due to sedation\n6. Call if fever, severe pain, or bleeding',
      },
      vitals: {
        bloodPressureSystolic: 125,
        bloodPressureDiastolic: 75,
        heartRate: 68,
        oxygenSaturation: 99,
      },
      orders: [
        { id: 'ord-9', orderType: 'procedure', name: 'Colonoscopy with polypectomy', status: 'completed', orderedAt: '2024-11-15T13:30:00Z', completedAt: '2024-11-15T14:30:00Z', priority: 'routine' },
        { id: 'ord-10', orderType: 'lab', name: 'Pathology - Colon polyps', status: 'completed', orderedAt: '2024-11-15T14:30:00Z', completedAt: '2024-11-22T10:00:00Z', result: 'Two tubular adenomas, low-grade dysplasia. Margins clear.', priority: 'routine' },
      ],
    },
    {
      id: 'v8',
      date: '2024-08-05T16:00:00Z',
      visitType: 'emergency',
      status: 'completed',
      chiefComplaint: 'Chest pain, shortness of breath',
      diagnoses: [
        { code: 'R07.9', description: 'Chest pain, unspecified', isPrimary: true },
        { code: 'R06.02', description: 'Shortness of breath', isPrimary: false },
        { code: 'F41.9', description: 'Anxiety disorder, unspecified', isPrimary: false },
      ],
      provider: { id: 'p5', name: 'Dr. James Wilson', role: 'Attending', specialty: 'Emergency Medicine' },
      location: 'Livny Health Emergency Department',
      duration: 180,
      notes: 'Cardiac workup negative. Symptoms attributed to anxiety/panic attack. Discharged with PCP follow-up.',
      soapNote: {
        subjective: '45 y/o female presents to ED with acute onset chest tightness and shortness of breath x 2 hours. Describes pressure-like sensation across chest, non-radiating. Associated with palpitations and feeling of impending doom. Symptoms began while at work during stressful meeting. No prior cardiac history. Denies diaphoresis, nausea, or arm/jaw pain. History of occasional anxiety. No recent illness, travel, or immobilization.',
        objective: 'T 98.2, HR 102, BP 145/88, RR 22, SpO2 98% RA. General: Anxious-appearing, mild distress. CV: Tachycardic, regular rhythm, no murmurs/rubs/gallops. Lungs: CTA bilaterally, no wheezes. Chest wall non-tender. Extremities: No edema, calves non-tender.\n\nEKG: Sinus tachycardia, no ST changes, no ischemic changes.\nTroponin: <0.01 (negative) x2 at 0h and 3h\nD-dimer: Normal\nCXR: No acute cardiopulmonary process\nBMP: Normal',
        assessment: 'Chest pain with negative cardiac workup. Clinical presentation most consistent with acute anxiety/panic attack. Low suspicion for ACS given negative troponins, normal EKG, and atypical presentation. PE ruled out with normal D-dimer and low pretest probability.',
        plan: '1. Cardiac workup negative - reassurance provided\n2. Discussed anxiety as likely etiology\n3. Lorazepam 0.5mg given in ED with symptom resolution\n4. Discharge home in stable condition\n5. Follow up with PCP within 1 week\n6. Consider outpatient cardiology referral if symptoms recur\n7. Discussed stress management techniques\n8. Return precautions reviewed: return immediately if chest pain recurs, worsens, or associated with diaphoresis/radiation',
      },
      vitals: {
        bloodPressureSystolic: 145,
        bloodPressureDiastolic: 88,
        heartRate: 102,
        temperature: 98.2,
        oxygenSaturation: 98,
        respiratoryRate: 22,
      },
      medications: [
        { id: 'vm-5', name: 'Lorazepam', dosage: '0.5mg', frequency: 'once', action: 'prescribed', route: 'oral', instructions: 'Given in ED for acute anxiety' },
      ],
      orders: [
        { id: 'ord-11', orderType: 'lab', name: 'Troponin I (serial)', status: 'completed', orderedAt: '2024-08-05T16:00:00Z', completedAt: '2024-08-05T19:00:00Z', result: '<0.01 ng/mL (negative x2)', priority: 'stat' },
        { id: 'ord-12', orderType: 'lab', name: 'D-dimer', status: 'completed', orderedAt: '2024-08-05T16:00:00Z', completedAt: '2024-08-05T17:00:00Z', result: '0.3 (normal <0.5)', priority: 'stat' },
        { id: 'ord-13', orderType: 'lab', name: 'BMP', status: 'completed', orderedAt: '2024-08-05T16:00:00Z', completedAt: '2024-08-05T17:00:00Z', result: 'All values within normal limits', priority: 'stat' },
        { id: 'ord-14', orderType: 'imaging', name: 'Chest X-ray', status: 'completed', orderedAt: '2024-08-05T16:15:00Z', completedAt: '2024-08-05T16:45:00Z', result: 'No acute cardiopulmonary process', priority: 'stat' },
        { id: 'ord-15', orderType: 'procedure', name: 'EKG', status: 'completed', orderedAt: '2024-08-05T16:05:00Z', completedAt: '2024-08-05T16:10:00Z', result: 'Sinus tachycardia, no ischemic changes', priority: 'stat' },
      ],
    },
  ],
  totalCount: 8,
  hasMore: false,
};

export async function getVisitHistory(
  patientId: string,
  params: VisitHistoryParams = {}
): Promise<VisitHistoryResponse> {
  const queryParams = new URLSearchParams();

  if (params.daysBack !== undefined) {
    queryParams.set('days_back', params.daysBack.toString());
  }
  if (params.includeAll !== undefined) {
    queryParams.set('include_all', params.includeAll.toString());
  }
  if (params.limit !== undefined) {
    queryParams.set('limit', params.limit.toString());
  }
  if (params.offset !== undefined) {
    queryParams.set('offset', params.offset.toString());
  }
  if (params.visitType) {
    queryParams.set('visit_type', params.visitType);
  }
  if (params.providerId) {
    queryParams.set('provider_id', params.providerId);
  }
  if (params.diagnosisCode) {
    queryParams.set('diagnosis_code', params.diagnosisCode);
  }
  if (params.searchQuery) {
    queryParams.set('search_query', params.searchQuery);
  }
  if (params.dateFrom) {
    queryParams.set('date_from', params.dateFrom);
  }
  if (params.dateTo) {
    queryParams.set('date_to', params.dateTo);
  }

  try {
    const response = await fetch(
      `${BFF_URL}/patients/${patientId}/visits?${queryParams}`
    );

    if (response.ok) {
      return response.json();
    }
  } catch {
    // Fall through to mock data
  }

  // Return mock data as fallback during development
  // Apply client-side filtering for mock data
  let filteredVisits = [...mockVisits.visits];

  if (params.visitType) {
    filteredVisits = filteredVisits.filter(v => v.visitType === params.visitType);
  }
  if (params.providerId) {
    filteredVisits = filteredVisits.filter(v => v.provider.id === params.providerId);
  }
  if (params.searchQuery) {
    const query = params.searchQuery.toLowerCase();
    filteredVisits = filteredVisits.filter(v => {
      const searchableText = [
        v.chiefComplaint,
        v.soapNote?.subjective,
        v.soapNote?.objective,
        v.soapNote?.assessment,
        v.soapNote?.plan,
        ...v.diagnoses.map(d => `${d.code} ${d.description}`),
      ].filter(Boolean).join(' ').toLowerCase();
      return searchableText.includes(query);
    });
  }
  if (params.diagnosisCode) {
    const code = params.diagnosisCode.toUpperCase();
    filteredVisits = filteredVisits.filter(v =>
      v.diagnoses.some(d => d.code.toUpperCase().includes(code))
    );
  }

  const offset = params.offset ?? 0;
  const limit = params.limit ?? 20;
  const paginatedVisits = filteredVisits.slice(offset, offset + limit);

  return {
    visits: paginatedVisits,
    totalCount: filteredVisits.length,
    hasMore: (offset + paginatedVisits.length) < filteredVisits.length,
    offset,
    limit,
  };
}

export async function getVisitProviders(
  patientId: string
): Promise<VisitProvidersResponse> {
  try {
    const response = await fetch(
      `${BFF_URL}/patients/${patientId}/visits/providers`
    );

    if (response.ok) {
      return response.json();
    }
  } catch {
    // Fall through to mock data
  }

  // Return mock providers from mock visits as fallback
  const seen = new Set<string>();
  const providers = mockVisits.visits
    .map(v => v.provider)
    .filter(p => {
      if (seen.has(p.id)) return false;
      seen.add(p.id);
      return true;
    });

  return { providers };
}
