export type AppointmentStatus =
  | 'scheduled'
  | 'checked_in'
  | 'in_progress'
  | 'completed'
  | 'no_show'
  | 'canceled';

export type VisitType =
  | 'Office Visit'
  | 'Follow-up'
  | 'Annual Physical'
  | 'Urgent'
  | 'New Patient'
  | 'Procedure';

export interface PatientFlag {
  type: 'critical_lab' | 'overdue_screening' | 'special_needs' | 'new_patient';
  message: string;
}

export interface AppointmentPatient {
  id: string;
  name: string;
  dateOfBirth: string;
  gender: 'Male' | 'Female' | 'Other';
  mrn: string;
}

export interface Appointment {
  id: string;
  patient: AppointmentPatient;
  appointmentTime: string;
  endTime: string;
  durationMinutes: number;
  visitType: VisitType;
  chiefComplaint?: string;
  status: AppointmentStatus;
  flags: PatientFlag[];
  isDoubleBooked?: boolean;
}

export interface DailySchedule {
  date: string;
  providerId: string;
  providerName: string;
  appointments: Appointment[];
}
