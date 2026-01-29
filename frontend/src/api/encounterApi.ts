import type {
  EncounterWithContext,
  NoteSaveResult,
  NoteVersionsResponse,
  VersionConflictError,
  EncounterStatus,
  StatusAuditEntry,
  StatusTransitionResult,
  AddendumResult,
  EncounterNote,
} from '../types';

const BFF_URL = 'http://localhost:8000';

export interface CreateEncounterRequest {
  patientId: string;
  providerId: string;
  encounterType?: string;
  chiefComplaint?: string;
}

export interface SaveNoteRequest {
  content: string;
  expectedVersion: number;
  saveType?: 'auto' | 'manual';
}

export class VersionConflictException extends Error {
  readonly expectedVersion: number;
  readonly currentVersion: number;
  readonly serverContent: string;

  constructor(
    expectedVersion: number,
    currentVersion: number,
    serverContent: string
  ) {
    super('Version conflict detected');
    this.name = 'VersionConflictException';
    this.expectedVersion = expectedVersion;
    this.currentVersion = currentVersion;
    this.serverContent = serverContent;
  }
}

export async function createEncounter(
  patientId: string,
  request: Omit<CreateEncounterRequest, 'patientId'>
): Promise<EncounterWithContext> {
  const response = await fetch(`${BFF_URL}/patients/${patientId}/encounters`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      patientId,
      ...request,
    }),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Patient or provider not found');
    }
    throw new Error('Failed to create encounter');
  }

  return response.json();
}

export async function getEncounter(
  encounterId: string
): Promise<EncounterWithContext> {
  const response = await fetch(`${BFF_URL}/encounters/${encounterId}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Encounter not found');
    }
    throw new Error('Failed to fetch encounter');
  }

  return response.json();
}

export async function saveEncounterNote(
  encounterId: string,
  request: SaveNoteRequest
): Promise<NoteSaveResult> {
  const response = await fetch(`${BFF_URL}/encounters/${encounterId}/note`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content: request.content,
      expectedVersion: request.expectedVersion,
      saveType: request.saveType || 'auto',
    }),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Encounter not found');
    }
    if (response.status === 409) {
      const errorData = (await response.json()) as { detail: VersionConflictError };
      throw new VersionConflictException(
        errorData.detail.expectedVersion,
        errorData.detail.currentVersion,
        errorData.detail.serverContent
      );
    }
    throw new Error('Failed to save note');
  }

  return response.json();
}

export async function getNoteVersions(
  encounterId: string
): Promise<NoteVersionsResponse> {
  const response = await fetch(`${BFF_URL}/encounters/${encounterId}/versions`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Encounter not found');
    }
    throw new Error('Failed to fetch note versions');
  }

  return response.json();
}

export async function getNoteVersionContent(
  encounterId: string,
  version: number
): Promise<{ encounterId: string; version: number; content: string }> {
  const response = await fetch(
    `${BFF_URL}/encounters/${encounterId}/versions/${version}`
  );

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Version not found');
    }
    throw new Error('Failed to fetch version content');
  }

  return response.json();
}

export interface TransitionStatusRequest {
  newStatus: EncounterStatus;
  reason?: string;
  userId?: string;
  userName?: string;
}

export class InvalidTransitionException extends Error {
  readonly currentStatus: EncounterStatus;
  readonly targetStatus: EncounterStatus;
  readonly allowedTransitions: EncounterStatus[];

  constructor(
    currentStatus: EncounterStatus,
    targetStatus: EncounterStatus,
    allowedTransitions: EncounterStatus[]
  ) {
    super(`Cannot transition from ${currentStatus} to ${targetStatus}`);
    this.name = 'InvalidTransitionException';
    this.currentStatus = currentStatus;
    this.targetStatus = targetStatus;
    this.allowedTransitions = allowedTransitions;
  }
}

export async function transitionEncounterStatus(
  encounterId: string,
  newStatus: EncounterStatus,
  reason?: string,
  userId?: string,
  userName?: string
): Promise<StatusTransitionResult> {
  const response = await fetch(`${BFF_URL}/encounters/${encounterId}/status`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      newStatus,
      reason,
      userId,
      userName,
    }),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Encounter not found');
    }
    if (response.status === 400) {
      const errorData = await response.json();
      if (errorData.detail?.error === 'invalid_transition') {
        throw new InvalidTransitionException(
          errorData.detail.currentStatus,
          errorData.detail.targetStatus,
          errorData.detail.allowedTransitions
        );
      }
      throw new Error(errorData.detail?.message || 'Invalid status transition');
    }
    throw new Error('Failed to transition status');
  }

  return response.json();
}

export async function getEncounterAudit(
  encounterId: string
): Promise<{ encounterId: string; entries: StatusAuditEntry[] }> {
  const response = await fetch(`${BFF_URL}/encounters/${encounterId}/audit`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Encounter not found');
    }
    throw new Error('Failed to fetch audit trail');
  }

  return response.json();
}

export interface CreateAddendumRequest {
  content: string;
  reason: string;
  userId?: string;
  userName?: string;
}

export async function createAddendum(
  encounterId: string,
  request: CreateAddendumRequest
): Promise<AddendumResult> {
  const response = await fetch(`${BFF_URL}/encounters/${encounterId}/addendum`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Encounter not found');
    }
    if (response.status === 400) {
      const errorData = await response.json();
      throw new Error(errorData.detail?.message || 'Cannot add addendum to this encounter');
    }
    throw new Error('Failed to create addendum');
  }

  return response.json();
}

export async function getEncounterByAppointment(
  appointmentId: string
): Promise<{ appointmentId: string; encounter: EncounterNote | null }> {
  const response = await fetch(
    `${BFF_URL}/appointments/${appointmentId}/encounter`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch encounter for appointment');
  }

  return response.json();
}
