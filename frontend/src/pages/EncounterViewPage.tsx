import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
  getEncounter,
  transitionEncounterStatus,
  getEncounterAudit,
  createAddendum,
} from '../api/encounterApi';
import type { EncounterWithContext, EncounterStatus, StatusAuditEntry } from '../types';
import {
  EncounterPatientBanner,
  EncounterDataPanel,
  NoteComposer,
  VersionConflictModal,
  EncounterStatusBanner,
  EncounterActionBar,
  SignatureBlock,
  AddendumComposer,
  AuditTrailModal,
  SOAPViewPanel,
} from '../components/encounter';
import { useSOAPMapping } from '../hooks/useSOAPMapping';
import type { NoteComposerRef } from '../components/encounter';
import { cn } from '../utils/cn';

export function EncounterViewPage() {
  const { encounterId } = useParams<{ encounterId: string }>();
  const [data, setData] = useState<EncounterWithContext | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isNoteExpanded, setIsNoteExpanded] = useState(false);
  const [isNoteMinimized, setIsNoteMinimized] = useState(false);
  const [showSOAPView, setShowSOAPView] = useState(false);
  const [noteContent, setNoteContent] = useState('');
  const [conflictData, setConflictData] = useState<{
    myContent: string;
    serverContent: string;
    serverVersion: number;
  } | null>(null);

  // Status transition state
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [showAddendumModal, setShowAddendumModal] = useState(false);
  const [showAuditModal, setShowAuditModal] = useState(false);
  const [auditEntries, setAuditEntries] = useState<StatusAuditEntry[]>([]);
  const [isLoadingAudit, setIsLoadingAudit] = useState(false);

  const noteComposerRef = useRef<NoteComposerRef>(null);

  // SOAP mapping hook
  const { mapping: soapMapping, isLoading: soapLoading, error: soapError } = useSOAPMapping({
    encounterId: encounterId || '',
    content: noteContent,
    enabled: showSOAPView && !!encounterId,
  });

  // Get user info from session storage
  const getUserInfo = useCallback(() => {
    const userJson = sessionStorage.getItem('currentUser');
    if (userJson) {
      const user = JSON.parse(userJson);
      return { userId: user.id, userName: user.name };
    }
    return { userId: undefined, userName: undefined };
  }, []);

  const refreshEncounter = useCallback(async () => {
    if (!encounterId) return;
    try {
      const result = await getEncounter(encounterId);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reload encounter');
    }
  }, [encounterId]);

  useEffect(() => {
    if (!encounterId) {
      setError('No encounter ID provided');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    getEncounter(encounterId)
      .then((result) => {
        setData(result);
        setNoteContent(result.encounter.noteContent || '');
      })
      .catch((err) => {
        setError(err.message || 'Failed to load encounter');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [encounterId]);

  const handleToggleExpand = useCallback(() => {
    setIsNoteExpanded((prev) => !prev);
  }, []);

  const handleToggleMinimize = useCallback(() => {
    setIsNoteMinimized((prev) => !prev);
  }, []);

  const handleToggleSOAPView = useCallback(() => {
    setShowSOAPView((prev) => !prev);
  }, []);

  const handleNoteContentChange = useCallback((content: string) => {
    setNoteContent(content);
  }, []);

  const handleConflict = useCallback(
    (serverContent: string, serverVersion: number) => {
      const myContent = noteComposerRef.current?.getContent() || '';
      setConflictData({
        myContent,
        serverContent,
        serverVersion,
      });
    },
    []
  );

  const handleUseMine = useCallback(() => {
    setConflictData(null);
  }, []);

  const handleUseServer = useCallback(() => {
    if (encounterId) {
      setConflictData(null);
      setLoading(true);
      refreshEncounter().finally(() => setLoading(false));
    }
  }, [encounterId, refreshEncounter]);

  const handleCloseConflict = useCallback(() => {
    setConflictData(null);
  }, []);

  // Status transition handlers
  const handleStatusTransition = useCallback(
    async (newStatus: EncounterStatus, reason?: string) => {
      if (!encounterId) return;

      setIsTransitioning(true);
      try {
        const { userId, userName } = getUserInfo();
        await transitionEncounterStatus(
          encounterId,
          newStatus,
          reason,
          userId,
          userName
        );
        await refreshEncounter();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to transition status');
      } finally {
        setIsTransitioning(false);
      }
    },
    [encounterId, getUserInfo, refreshEncounter]
  );

  const handleComplete = useCallback(() => {
    handleStatusTransition('completed');
  }, [handleStatusTransition]);

  const handleSign = useCallback(() => {
    handleStatusTransition('signed');
  }, [handleStatusTransition]);

  const handleReopen = useCallback(() => {
    handleStatusTransition('in_progress', 'Reopened for editing');
  }, [handleStatusTransition]);

  const handleAddAddendum = useCallback(() => {
    setShowAddendumModal(true);
  }, []);

  const handleSubmitAddendum = useCallback(
    async (content: string, reason: string) => {
      if (!encounterId) return;

      const { userId, userName } = getUserInfo();
      await createAddendum(encounterId, {
        content,
        reason,
        userId,
        userName,
      });
      await refreshEncounter();
    },
    [encounterId, getUserInfo, refreshEncounter]
  );

  const handleViewAudit = useCallback(async () => {
    if (!encounterId) return;

    setShowAuditModal(true);
    setIsLoadingAudit(true);
    try {
      const result = await getEncounterAudit(encounterId);
      setAuditEntries(result.entries);
    } catch (err) {
      console.error('Failed to load audit trail:', err);
    } finally {
      setIsLoadingAudit(false);
    }
  }, [encounterId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-arctic flex items-center justify-center">
        <div className="text-text-secondary text-[15px]">
          Loading encounter...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-arctic flex items-center justify-center">
        <div className="text-center">
          <div className="text-status-critical text-[15px] mb-2">{error}</div>
          <a
            href="/schedule"
            className="text-glacier-blue text-[14px] hover:underline"
          >
            Return to schedule
          </a>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-arctic flex items-center justify-center">
        <div className="text-text-secondary text-[15px]">
          Encounter not found
        </div>
      </div>
    );
  }

  const status = data.encounter.status;
  const isReadOnly = status === 'completed' || status === 'signed';
  const isSigned = status === 'signed';

  return (
    <div className="min-h-screen bg-arctic flex flex-col">
      {/* Patient Banner - sticky top */}
      <EncounterPatientBanner
        patient={data.patient}
        encounter={data.encounter}
        className="sticky top-0 z-10"
      />

      {/* Status Banner (for completed/signed states) */}
      <EncounterStatusBanner
        status={status}
        signedByName={data.encounter.signedByName}
        signedAt={data.encounter.signedAt}
        onReopen={handleReopen}
        onSign={handleSign}
        onAddAddendum={handleAddAddendum}
        onViewAudit={handleViewAudit}
        isLoading={isTransitioning}
      />

      {/* Main content area */}
      <div
        className={cn(
          'flex-1 flex flex-col overflow-hidden',
          isNoteExpanded ? 'pb-[400px]' : 'pb-[180px]'
        )}
      >
        {/* Upper zone - scrollable clinical data */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-6xl mx-auto py-normal">
            {/* Show SOAP view or EncounterDataPanel based on toggle */}
            {showSOAPView ? (
              <SOAPViewPanel
                mapping={soapMapping}
                isLoading={soapLoading}
                error={soapError}
                className="mx-comfortable"
              />
            ) : (
              <EncounterDataPanel
                context={data.context}
                className="bg-white rounded-lg shadow-card mx-comfortable"
              />
            )}

            {/* Signature block for signed encounters */}
            {isSigned && data.encounter.signedByName && data.encounter.signedAt && (
              <div className="bg-white rounded-lg shadow-card mx-comfortable mt-normal p-comfortable">
                <SignatureBlock
                  signedByName={data.encounter.signedByName}
                  signedAt={data.encounter.signedAt}
                />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Note Composer - fixed bottom */}
      <div className="fixed bottom-0 left-0 right-0 z-10">
        {/* Action Bar for in_progress encounters */}
        {status === 'in_progress' && (
          <EncounterActionBar
            status={status}
            onComplete={handleComplete}
            onSign={handleSign}
            isLoading={isTransitioning}
          />
        )}
        <NoteComposer
          ref={noteComposerRef}
          encounterId={data.encounter.id}
          initialContent={data.encounter.noteContent || ''}
          initialVersion={data.encounter.noteVersion}
          isExpanded={isNoteExpanded}
          isMinimized={isNoteMinimized}
          onToggleExpand={handleToggleExpand}
          onToggleMinimize={handleToggleMinimize}
          onConflict={handleConflict}
          onContentChange={handleNoteContentChange}
          showSOAPView={showSOAPView}
          onToggleSOAPView={handleToggleSOAPView}
          readOnly={isReadOnly}
        />
      </div>

      {/* Version Conflict Modal */}
      <VersionConflictModal
        isOpen={conflictData !== null}
        myContent={conflictData?.myContent || ''}
        serverContent={conflictData?.serverContent || ''}
        serverVersion={conflictData?.serverVersion || 0}
        onUseMine={handleUseMine}
        onUseServer={handleUseServer}
        onClose={handleCloseConflict}
      />

      {/* Addendum Modal */}
      <AddendumComposer
        isOpen={showAddendumModal}
        onSubmit={handleSubmitAddendum}
        onClose={() => setShowAddendumModal(false)}
      />

      {/* Audit Trail Modal */}
      <AuditTrailModal
        isOpen={showAuditModal}
        entries={auditEntries}
        isLoading={isLoadingAudit}
        onClose={() => setShowAuditModal(false)}
      />
    </div>
  );
}
