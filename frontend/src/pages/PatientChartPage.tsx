import { useState, useEffect, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, Input, Button, Select, AllergyBlockModal, AllergyWarningBanner, DrugInteractionWarning, DrugInteractionBlockModal, ClinicalAlertBanner, AlertBadge, type AllergyOverrideData, type InteractionOverrideData } from '../components/ui';
import { MedicationDetailModal, MedicationTooltip } from '../components/medication';
import { AllergiesSection, RecentLabsSection, VisitTimeline, ProblemListSection, ProblemDetailModal, ImagingSection, VitalSignsSection, SocialFamilyHistorySection, ChartNavigation } from '../components/patient';
import { useDebounce, useMedicationFreshness, useChartNavigation, useKeyboardShortcuts, useAlerts } from '../hooks';
import { searchMedications, getMedicationDefaults, checkAllergyConflict, logAllergyOverride, checkDrugInteractions, logInteractionOverride, submitPrescription, discontinueMedication, getProblemDetail, reactivateProblem } from '../api';
import type { MedicationSearchResult, SelectedMedication, User, AllergyAlert, DrugInteraction, ActiveMedication, Problem, ProblemDetailResponse, ChartSectionId } from '../types';
import type { MedicationForm } from '../utils/quantityCalculator';
import { cn } from '../utils/cn';
import {
  FREQUENCY_OPTIONS,
  calculateQuantity,
  parseFrequencyFromDosing,
  parseDosesPerAdmin,
  getUnitForForm,
} from '../utils/quantityCalculator';

interface MedicationResultCardProps {
  medication: MedicationSearchResult;
  isSelected: boolean;
  onSelect: (medication: MedicationSearchResult) => void;
}

function MedicationResultCard({ medication, isSelected, onSelect }: MedicationResultCardProps) {
  return (
    <Card
      hoverable
      onClick={() => onSelect(medication)}
      className={cn(
        'cursor-pointer transition-all duration-150',
        isSelected && 'ring-2 ring-glacier-blue bg-arctic'
      )}
    >
      <CardContent>
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-[15px] font-medium text-text-primary">{medication.name}</h4>
            <p className="text-[13px] text-text-secondary mt-1">
              {medication.form} - {medication.strength}
            </p>
          </div>
          {medication.isControlled && (
            <span className="px-2 py-1 text-[11px] font-medium uppercase tracking-wide bg-warning/10 text-warning rounded">
              Controlled
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

interface MedicationDetailsProps {
  medication: SelectedMedication;
  onDosingSelect: (dosing: string) => void;
  onFrequencyChange: (frequency: string) => void;
  onDurationChange: (days: number) => void;
  onInstructionsChange: (instructions: string) => void;
  onProceed: () => void;
  onBack: () => void;
}

function MedicationDetails({
  medication,
  onDosingSelect,
  onFrequencyChange,
  onDurationChange,
  onInstructionsChange,
  onProceed,
  onBack,
}: MedicationDetailsProps) {
  const hasCommonDosing = medication.commonDosing && medication.commonDosing.length > 0;
  const frequencyOptions = FREQUENCY_OPTIONS.map((f) => ({ value: f.value, label: f.label }));

  const canProceed =
    medication.selectedDosing && medication.frequency && medication.durationDays;

  return (
    <Card className="mt-normal">
      <CardContent>
        <div className="flex items-start justify-between mb-comfortable">
          <div>
            <h3 className="text-xl font-semibold text-deep-ice">{medication.name}</h3>
            <p className="text-[15px] text-text-secondary mt-1">
              {medication.form && medication.strength
                ? `${medication.form} - ${medication.strength}`
                : medication.form || medication.strength || ''}
            </p>
          </div>
          <button
            onClick={onBack}
            className="text-text-tertiary hover:text-text-secondary transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="mb-comfortable">
          <label className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
            {hasCommonDosing ? 'Dose' : 'Dosing Instructions'}
          </label>
          {hasCommonDosing ? (
            <div className="flex flex-wrap gap-tight">
              {medication.commonDosing.map((dosing) => (
                <button
                  key={dosing}
                  onClick={() => onDosingSelect(dosing)}
                  className={cn(
                    'px-4 py-2 rounded-md text-[15px] transition-all duration-150',
                    medication.selectedDosing === dosing
                      ? 'bg-glacier-blue text-white'
                      : 'bg-frost text-text-primary hover:bg-arctic'
                  )}
                >
                  {dosing}
                </button>
              ))}
            </div>
          ) : (
            <Input
              type="text"
              placeholder="e.g., 500mg twice daily"
              value={medication.selectedDosing || ''}
              onChange={(e) => onDosingSelect(e.target.value)}
            />
          )}
        </div>

        <div className="grid grid-cols-2 gap-normal mb-comfortable">
          <div>
            <label className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
              Frequency
            </label>
            <Select
              options={frequencyOptions}
              value={medication.frequency || ''}
              onChange={onFrequencyChange}
              placeholder="Select frequency"
            />
          </div>
          <div>
            <label className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
              Duration
            </label>
            <div className="flex items-center gap-tight">
              <Input
                type="number"
                value={medication.durationDays?.toString() || ''}
                onChange={(e) => onDurationChange(parseInt(e.target.value, 10) || 0)}
                className="w-24"
              />
              <span className="text-[15px] text-text-secondary">days</span>
            </div>
          </div>
        </div>

        {medication.calculatedQuantity !== undefined && medication.calculatedQuantity > 0 && (
          <div className="mb-comfortable p-normal bg-arctic rounded-md">
            <label className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
              Calculated Quantity
            </label>
            <p className="text-xl font-semibold text-deep-ice">
              {medication.calculatedQuantity} {medication.quantityUnit}
              {medication.imperialEquivalent && (
                <span className="text-[15px] font-normal text-text-secondary ml-2">
                  ({medication.imperialEquivalent.formatted})
                </span>
              )}
              {medication.isQuantityEstimate && (
                <span className="text-[13px] font-normal text-text-secondary ml-2">
                  (estimated max)
                </span>
              )}
            </p>
          </div>
        )}

        <div className="mb-comfortable">
          <label className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
            Additional Instructions <span className="font-normal">(optional)</span>
          </label>
          <Input
            type="text"
            placeholder="e.g., Take with food, Avoid alcohol"
            value={medication.instructions || ''}
            onChange={(e) => onInstructionsChange(e.target.value)}
          />
        </div>

        <div className="flex justify-end gap-normal pt-normal border-t border-frost">
          <Button variant="secondary" onClick={onBack}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={onProceed}
            disabled={!canProceed}
          >
            Add to Prescription
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function calculateAge(dateOfBirth: string): number {
  const dob = new Date(dateOfBirth);
  const today = new Date();
  let years = today.getFullYear() - dob.getFullYear();
  const monthDiff = today.getMonth() - dob.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
    years--;
  }
  return Math.max(0, years);
}

function formatDOB(dateOfBirth: string): string {
  const dob = new Date(dateOfBirth);
  const month = String(dob.getMonth() + 1).padStart(2, '0');
  const day = String(dob.getDate()).padStart(2, '0');
  const year = dob.getFullYear();
  return `${month}/${day}/${year}`;
}

function getGenderAbbrev(gender: string): string {
  const g = gender.toLowerCase();
  if (g === 'male' || g === 'm') return 'M';
  if (g === 'female' || g === 'f') return 'F';
  return gender.charAt(0).toUpperCase();
}

// 'prescribe' is a special workflow action, not a chart section
type ExtendedSection = ChartSectionId | 'prescribe';

export function PatientChartPage() {
  const navigate = useNavigate();
  const { patientId } = useParams<{ patientId: string }>();
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  // Chart navigation with API data
  const {
    sections: chartSections,
    setActiveSection: setChartSection,
    isLoading: isLoadingChartSections,
  } = useChartNavigation({ patientId });

  // Extended section state that includes 'prescribe' action
  const [activeSection, setActiveSection] = useState<ExtendedSection>('visits');

  // Sync extended section with chart section
  const handleNavigate = (sectionId: ChartSectionId | 'prescribe') => {
    setActiveSection(sectionId);
    if (sectionId !== 'prescribe') {
      setChartSection(sectionId);
    }
  };

  // Set up keyboard shortcuts
  useKeyboardShortcuts({
    shortcuts: chartSections.map((section) => ({
      shortcut: section.keyboardShortcut,
      sectionId: section.id,
    })),
    onNavigate: handleNavigate,
    enabled: chartSections.length > 0,
  });

  // Use the medication freshness hook for patient data with real-time capabilities
  const {
    patient,
    isLoading: isLoadingPatient,
    isRefetching,
    error: patientError,
    refetch: refetchPatient,
    addMedications,
    removeMedication,
    timeSinceUpdate,
  } = useMedicationFreshness(patientId);

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<MedicationSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedMedication, setSelectedMedication] = useState<SelectedMedication | null>(null);
  const [prescription, setPrescription] = useState<SelectedMedication[]>([]);
  const [allergyAlert, setAllergyAlert] = useState<AllergyAlert | null>(null);
  const [pendingMedication, setPendingMedication] = useState<MedicationSearchResult | null>(null);
  const [drugInteractions, setDrugInteractions] = useState<DrugInteraction[]>([]);
  const [criticalInteractions, setCriticalInteractions] = useState<DrugInteraction[]>([]);
  const [pendingInteractionMedication, setPendingInteractionMedication] = useState<MedicationSearchResult | null>(null);
  const [isSubmittingPrescription, setIsSubmittingPrescription] = useState(false);
  const [prescriptionSuccess, setPrescriptionSuccess] = useState(false);
  const [showAllMedications, setShowAllMedications] = useState(false);
  const [selectedActiveMedication, setSelectedActiveMedication] = useState<ActiveMedication | null>(null);
  const [medicationSortBy, setMedicationSortBy] = useState<'name' | 'started' | 'drugClass'>('started');
  const [medicationFilter, setMedicationFilter] = useState('');
  const [isDiscontinuing, setIsDiscontinuing] = useState(false);

  // Problem detail modal state
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
  const [problemDetail, setProblemDetail] = useState<ProblemDetailResponse | null>(null);
  const [isLoadingProblemDetail, setIsLoadingProblemDetail] = useState(false);
  const [problemDetailError, setProblemDetailError] = useState<string | null>(null);

  const debouncedSearch = useDebounce(searchQuery, 300);

  // Clinical alerts hook
  const {
    alerts,
    summary: alertSummary,
    isLoading: isLoadingAlerts,
    acknowledge: acknowledgeAlert,
  } = useAlerts({ patientId: patientId || '', status: 'active' });

  // Filter and sort active medications
  const filteredAndSortedMedications = useMemo(() => {
    if (!patient?.activeMedications) return [];

    let medications = [...patient.activeMedications];

    // Filter by name or drug class
    if (medicationFilter.trim()) {
      const filterLower = medicationFilter.toLowerCase();
      medications = medications.filter(
        (med) =>
          med.name.toLowerCase().includes(filterLower) ||
          med.brandName?.toLowerCase().includes(filterLower) ||
          med.drugClass?.toLowerCase().includes(filterLower)
      );
    }

    // Sort medications
    medications.sort((a, b) => {
      switch (medicationSortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'started': {
          // Parse MM/DD/YYYY format
          const parseDate = (dateStr: string) => {
            const [month, day, year] = dateStr.split('/').map(Number);
            return new Date(year, month - 1, day);
          };
          return parseDate(b.started).getTime() - parseDate(a.started).getTime();
        }
        case 'drugClass':
          return (a.drugClass || 'zzz').localeCompare(b.drugClass || 'zzz');
        default:
          return 0;
      }
    });

    return medications;
  }, [patient?.activeMedications, medicationFilter, medicationSortBy]);

  useEffect(() => {
    const userJson = sessionStorage.getItem('currentUser');
    if (userJson) {
      setCurrentUser(JSON.parse(userJson));
    } else {
      navigate('/login');
    }
  }, [navigate]);

  useEffect(() => {
    async function performSearch() {
      if (debouncedSearch.length < 3) {
        setSearchResults([]);
        return;
      }

      setIsSearching(true);
      try {
        const results = await searchMedications(debouncedSearch);
        setSearchResults(results);
      } finally {
        setIsSearching(false);
      }
    }

    performSearch();
  }, [debouncedSearch]);

  const proceedWithMedication = async (medication: MedicationSearchResult) => {
    const form = (medication.form || 'tablet') as MedicationForm;

    // Set initial state with default duration, then fetch from API
    setSelectedMedication({
      ...medication,
      selectedDosing: undefined,
      frequency: undefined,
      durationDays: 30, // Default fallback
      calculatedQuantity: undefined,
      quantityUnit: getUnitForForm(form),
      isQuantityEstimate: false,
    });

    // Fetch defaults from API
    try {
      const defaults = await getMedicationDefaults(medication.name);
      setSelectedMedication((prev) =>
        prev ? { ...prev, durationDays: defaults.defaultDuration } : prev
      );
    } catch {
      // Keep fallback duration on error
    }
  };

  const handleMedicationSelect = async (medication: MedicationSearchResult) => {
    if (!patientId) return;

    // Check for allergy conflicts first
    try {
      const result = await checkAllergyConflict(patientId, medication.name);
      if (result.hasConflict && result.alert) {
        setAllergyAlert(result.alert);
        // Only block for severe allergies (blocked=true)
        if (result.alert.blocked) {
          setPendingMedication(medication);
          return; // Block selection until override
        }
        // For non-blocking (mild/moderate), show warning but continue with selection
      }
    } catch {
      // Continue if allergy check fails - don't block the workflow
    }

    // Check for drug interactions with current medications
    try {
      const interactionResult = await checkDrugInteractions(patientId, medication.name);
      if (interactionResult.hasInteractions) {
        const criticalOnes = interactionResult.interactions.filter(
          (i) => i.severity === 'major'
        );

        if (criticalOnes.length > 0) {
          // Block on critical interactions - require override
          setCriticalInteractions(interactionResult.interactions);
          setPendingInteractionMedication(medication);
          return; // Block selection until override
        }

        // For non-critical interactions, show warning but continue
        setDrugInteractions(interactionResult.interactions);
      }
    } catch {
      // Continue if interaction check fails - don't block the workflow
    }

    await proceedWithMedication(medication);
  };

  const recalculateQuantity = (
    med: SelectedMedication,
    frequency?: string,
    durationDays?: number
  ): SelectedMedication => {
    const freq = frequency ?? med.frequency;
    const duration = durationDays ?? med.durationDays;
    const form = (med.form || 'tablet') as MedicationForm;

    if (!freq || !duration || !med.selectedDosing) {
      return {
        ...med,
        frequency: freq,
        durationDays: duration,
        calculatedQuantity: undefined,
      };
    }

    const dosesPerAdmin = parseDosesPerAdmin(med.selectedDosing, form);
    const result = calculateQuantity(freq, duration, dosesPerAdmin, form);

    return {
      ...med,
      frequency: freq,
      durationDays: duration,
      calculatedQuantity: result.quantity,
      quantityUnit: result.unit,
      isQuantityEstimate: result.isEstimate,
      imperialEquivalent: result.imperialEquivalent,
    };
  };

  const handleDosingSelect = (dosing: string) => {
    if (selectedMedication) {
      // Try to parse frequency from the dosing string (e.g., "500mg TID" -> "TID")
      const parsedFrequency = parseFrequencyFromDosing(dosing);
      const frequency = parsedFrequency || selectedMedication.frequency;

      const updated = recalculateQuantity(
        { ...selectedMedication, selectedDosing: dosing },
        frequency,
        selectedMedication.durationDays
      );
      setSelectedMedication(updated);
    }
  };

  const handleFrequencyChange = (frequency: string) => {
    if (selectedMedication) {
      const updated = recalculateQuantity(selectedMedication, frequency);
      setSelectedMedication(updated);
    }
  };

  const handleDurationChange = (days: number) => {
    if (selectedMedication) {
      const updated = recalculateQuantity(selectedMedication, undefined, days);
      setSelectedMedication(updated);
    }
  };

  const handleInstructionsChange = (instructions: string) => {
    if (selectedMedication) {
      setSelectedMedication({
        ...selectedMedication,
        instructions,
      });
    }
  };

  const handleProceed = async () => {
    if (
      !selectedMedication?.selectedDosing ||
      !selectedMedication.frequency ||
      !selectedMedication.durationDays ||
      !patientId
    ) {
      return;
    }

    // If there's an allergy override, log it to the backend
    if (selectedMedication.allergyOverride) {
      try {
        await logAllergyOverride({
          patient_id: patientId,
          medication_name: selectedMedication.name,
          allergen: selectedMedication.allergyOverride.allergen,
          severity: selectedMedication.allergyOverride.severity,
          justification: selectedMedication.allergyOverride.justification,
          acknowledged_at: selectedMedication.allergyOverride.acknowledgedAt,
          prescribed_at: new Date().toISOString(),
        });
      } catch (error) {
        console.error('Failed to log allergy override:', error);
        // Continue with prescription even if logging fails
      }
    }

    // If there's an interaction override, log it to the backend
    if (selectedMedication.interactionOverride) {
      try {
        await logInteractionOverride({
          patient_id: patientId,
          medication_name: selectedMedication.name,
          interacting_drugs: selectedMedication.interactionOverride.interactions.map(
            (i) => i.interactingDrug
          ),
          severities: selectedMedication.interactionOverride.interactions.map(
            (i) => i.severity
          ),
          justification: selectedMedication.interactionOverride.justification,
          acknowledged_at: selectedMedication.interactionOverride.acknowledgedAt,
          prescribed_at: new Date().toISOString(),
        });
      } catch (error) {
        console.error('Failed to log interaction override:', error);
        // Continue with prescription even if logging fails
      }
    }

    setPrescription([...prescription, selectedMedication]);
    setSelectedMedication(null);
    setAllergyAlert(null);
    setDrugInteractions([]);
    setSearchQuery('');
    setSearchResults([]);
  };

  const handleClearSelection = () => {
    setSelectedMedication(null);
    setDrugInteractions([]);
  };

  const handleWarningDismiss = () => {
    // Just hide the warning, keep the medication selected
    setAllergyAlert(null);
  };

  const handleSelectAlternative = () => {
    // Clear warning and selection, go back to search
    setAllergyAlert(null);
    setDrugInteractions([]);
    setSelectedMedication(null);
    setPendingMedication(null);
  };

  const handleInteractionDismiss = () => {
    // Just hide the warning, keep the medication selected
    setDrugInteractions([]);
  };

  const handleAllergyAlertClose = () => {
    // For blocking modal - clear everything
    setAllergyAlert(null);
    setPendingMedication(null);
  };

  const handleAllergyOverride = async (overrideData: AllergyOverrideData) => {
    if (!pendingMedication || !allergyAlert) return;

    // Store override data to be logged when prescription is completed
    const overrideInfo = {
      allergen: allergyAlert.allergen,
      severity: allergyAlert.severity,
      justification: overrideData.justification,
      acknowledgedAt: overrideData.acknowledgedAt,
    };

    // Proceed with the medication, attaching the override data
    const form = (pendingMedication.form || 'tablet') as MedicationForm;
    setSelectedMedication({
      ...pendingMedication,
      selectedDosing: undefined,
      frequency: undefined,
      durationDays: 30,
      calculatedQuantity: undefined,
      quantityUnit: getUnitForForm(form),
      isQuantityEstimate: false,
      allergyOverride: overrideInfo,
    });

    // Fetch defaults from API
    try {
      const defaults = await getMedicationDefaults(pendingMedication.name);
      setSelectedMedication((prev) =>
        prev ? { ...prev, durationDays: defaults.defaultDuration } : prev
      );
    } catch {
      // Keep fallback duration on error
    }

    // Clear the alert and pending state
    setAllergyAlert(null);
    setPendingMedication(null);
  };

  const handleCriticalInteractionClose = () => {
    // For blocking modal - clear everything
    setCriticalInteractions([]);
    setPendingInteractionMedication(null);
  };

  const handleInteractionOverride = async (overrideData: InteractionOverrideData) => {
    if (!pendingInteractionMedication || criticalInteractions.length === 0 || !patientId) return;

    // Store override data to be logged when prescription is completed
    const overrideInfo = {
      interactions: criticalInteractions,
      justification: overrideData.justification,
      acknowledgedAt: overrideData.acknowledgedAt,
    };

    // Proceed with the medication, attaching the override data
    const form = (pendingInteractionMedication.form || 'tablet') as MedicationForm;
    setSelectedMedication({
      ...pendingInteractionMedication,
      selectedDosing: undefined,
      frequency: undefined,
      durationDays: 30,
      calculatedQuantity: undefined,
      quantityUnit: getUnitForForm(form),
      isQuantityEstimate: false,
      interactionOverride: overrideInfo,
    });

    // Fetch defaults from API
    try {
      const defaults = await getMedicationDefaults(pendingInteractionMedication.name);
      setSelectedMedication((prev) =>
        prev ? { ...prev, durationDays: defaults.defaultDuration } : prev
      );
    } catch {
      // Keep fallback duration on error
    }

    // Clear the alert and pending state
    setCriticalInteractions([]);
    setPendingInteractionMedication(null);
  };

  const handleBack = () => {
    navigate(-1);
  };

  const handleDiscontinueMedication = async (medicationId: string, reason?: string) => {
    setIsDiscontinuing(true);
    try {
      const result = await discontinueMedication(medicationId, reason);
      if (result.success) {
        // Remove the medication from the active list immediately
        removeMedication(medicationId);
        // Close the detail modal
        setSelectedActiveMedication(null);
      }
    } catch (error) {
      console.error('Failed to discontinue medication:', error);
    } finally {
      setIsDiscontinuing(false);
    }
  };

  const handleProblemClick = async (problem: Problem) => {
    if (!patientId) return;

    setSelectedProblem(problem);
    setProblemDetail(null);
    setProblemDetailError(null);
    setIsLoadingProblemDetail(true);

    try {
      const detail = await getProblemDetail(patientId, problem.icd10Code);
      setProblemDetail(detail);
    } catch (error) {
      console.error('Failed to fetch problem detail:', error);
      setProblemDetailError('Failed to load problem details');
    } finally {
      setIsLoadingProblemDetail(false);
    }
  };

  const handleCloseProblemDetail = () => {
    setSelectedProblem(null);
    setProblemDetail(null);
    setProblemDetailError(null);
  };

  const handleReactivateProblem = async (icd10Code: string) => {
    if (!patientId) return;

    try {
      // For now, using a hardcoded provider name - in a real app this would come from auth context
      await reactivateProblem(patientId, icd10Code, 'Dr. Emily Chen');
      // Refresh patient data to get updated problem list
      window.location.reload();
    } catch (error) {
      console.error('Failed to reactivate problem:', error);
    }
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await acknowledgeAlert(alertId);
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const handleSubmitPrescription = async () => {
    if (!patientId || prescription.length === 0) return;

    setIsSubmittingPrescription(true);
    try {
      const medications = prescription.map((med) => ({
        name: med.name,
        dosage: med.selectedDosing || '',
        frequency: med.frequency || '',
        duration_days: med.durationDays || 0,
        instructions: med.instructions,
      }));

      const result = await submitPrescription(patientId, medications);

      if (result.success) {
        // Update patient's active medications using the freshness hook
        addMedications(result.medications);

        // Clear the prescription and show success
        setPrescription([]);
        setPrescriptionSuccess(true);

        // Hide success message after 5 seconds
        setTimeout(() => {
          setPrescriptionSuccess(false);
        }, 5000);
      }
    } catch (error) {
      console.error('Failed to submit prescription:', error);
    } finally {
      setIsSubmittingPrescription(false);
    }
  };

  if (!currentUser) {
    return null;
  }

  if (isLoadingPatient) {
    return (
      <div className="min-h-screen bg-snow flex items-center justify-center">
        <p className="text-[15px] text-text-secondary">Loading patient...</p>
      </div>
    );
  }

  if (patientError || !patient) {
    return (
      <div className="min-h-screen bg-snow flex items-center justify-center">
        <div className="text-center">
          <p className="text-[15px] text-critical mb-normal">{patientError || 'Patient not found'}</p>
          <Button variant="secondary" onClick={() => navigate('/')}>
            Back to Schedule
          </Button>
        </div>
      </div>
    );
  }

  // Render the active section content
  const renderMainContent = () => {
    switch (activeSection) {
      case 'visits':
        return <VisitTimeline patientId={patientId || ''} onNavigateToSection={handleNavigate} />;
      case 'allergies':
        return (
          <AllergiesSection
            allergies={patient.allergies}
            allergyReviewStatus={patient.allergyReviewStatus}
          />
        );
      case 'labs':
        return <RecentLabsSection recentLabs={patient.recentLabs} patientId={patientId || ''} />;
      case 'medications':
        return (
          <Card>
            <CardContent>
              <div className="flex items-center justify-between mb-normal">
                <div className="flex items-center gap-2">
                  <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                    Active Medications
                  </h3>
                  {patient.activeMedications && patient.activeMedications.length > 0 && (
                    <span className="text-[11px] text-text-tertiary">
                      ({filteredAndSortedMedications.length} of {patient.activeMedications.length})
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {timeSinceUpdate && (
                    <span className="text-[11px] text-text-tertiary">
                      {timeSinceUpdate}
                    </span>
                  )}
                  <button
                    onClick={() => refetchPatient()}
                    disabled={isRefetching}
                    className={cn(
                      'p-1 rounded text-text-tertiary hover:text-glacier-blue hover:bg-arctic transition-colors',
                      isRefetching && 'animate-spin'
                    )}
                    title="Refresh medications"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Search and Sort Controls */}
              {patient.activeMedications && patient.activeMedications.length > 0 && (
                <div className="flex gap-tight mb-normal">
                  <div className="flex-1">
                    <input
                      type="text"
                      placeholder="Filter by name or class..."
                      value={medicationFilter}
                      onChange={(e) => setMedicationFilter(e.target.value)}
                      className="w-full px-3 py-1.5 rounded-md border border-frost bg-white text-[13px] text-text-primary placeholder:text-text-tertiary focus:outline-none focus:ring-1 focus:ring-glacier-blue focus:border-transparent"
                    />
                  </div>
                  <select
                    value={medicationSortBy}
                    onChange={(e) => setMedicationSortBy(e.target.value as 'name' | 'started' | 'drugClass')}
                    className="px-2 py-1.5 rounded-md border border-frost bg-white text-[13px] text-text-primary focus:outline-none focus:ring-1 focus:ring-glacier-blue"
                  >
                    <option value="name">A-Z</option>
                    <option value="started">Newest</option>
                    <option value="drugClass">Class</option>
                  </select>
                </div>
              )}

              {patient.activeMedications && patient.activeMedications.length > 0 ? (
                <>
                  {filteredAndSortedMedications.length > 0 ? (
                    <>
                      <ul className="space-y-3">
                        {filteredAndSortedMedications
                          .slice(0, showAllMedications ? undefined : 10)
                          .map((med) => {
                            const [month, day, year] = med.started.split('/').map(Number);
                            const startDate = new Date(year, month - 1, day);
                            const sevenDaysAgo = new Date();
                            sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
                            const isNew = startDate >= sevenDaysAgo;

                            return (
                              <li key={med.id} className="text-[15px] text-text-primary">
                                <div className="flex items-baseline gap-1">
                                  <span className="text-text-tertiary">•</span>
                                  <div className="flex items-center gap-2 flex-wrap">
                                    <MedicationTooltip medication={med}>
                                      <button
                                        onClick={() => setSelectedActiveMedication(med)}
                                        className="text-left hover:text-glacier-blue transition-colors cursor-pointer"
                                      >
                                        <span className="font-medium">{med.name}</span>
                                        {med.brandName && <span className="text-text-secondary"> ({med.brandName})</span>}
                                        {med.strength && <span className="text-text-secondary"> {med.strength}</span>}
                                        {med.form && <span className="text-text-tertiary text-[13px]"> {med.form}</span>}
                                      </button>
                                    </MedicationTooltip>
                                    {isNew && (
                                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium bg-glacier-blue/10 text-glacier-blue">
                                        New
                                      </span>
                                    )}
                                    {med.isPRN && (
                                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium bg-amber-100 text-amber-700">
                                        PRN
                                      </span>
                                    )}
                                    {med.isControlled && (
                                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-medium bg-red-100 text-red-700" title="Controlled Substance">
                                        ℞
                                      </span>
                                    )}
                                  </div>
                                </div>
                                <div className="ml-3 text-[13px] text-text-secondary">
                                  {med.frequency}
                                  {med.route && <span> · {med.route}</span>}
                                  {med.started && <span> · {med.started}</span>}
                                </div>
                              </li>
                            );
                          })}
                      </ul>
                      {filteredAndSortedMedications.length > 10 && (
                        <button
                          onClick={() => setShowAllMedications(!showAllMedications)}
                          className="mt-normal text-[13px] text-glacier-blue hover:text-deep-ice transition-colors"
                        >
                          {showAllMedications ? 'Show Less' : `View All (${filteredAndSortedMedications.length})`}
                        </button>
                      )}
                    </>
                  ) : (
                    <p className="text-[15px] text-text-secondary">No medications match your filter</p>
                  )}
                </>
              ) : (
                <p className="text-[15px] text-text-secondary">No active medications</p>
              )}
            </CardContent>
          </Card>
        );
      case 'problems':
        return <ProblemListSection problemList={patient.problemList} onProblemClick={handleProblemClick} onReactivateProblem={handleReactivateProblem} />;
      case 'imaging':
        return <ImagingSection patientId={patientId || ''} />;
      case 'vitals':
        return <VitalSignsSection patientId={patientId || ''} />;
      case 'social-family':
        return <SocialFamilyHistorySection patientId={patientId || ''} />;
      case 'prescribe':
        return renderPrescribeSection();
      default:
        return <VisitTimeline patientId={patientId || ''} />;
    }
  };

  const renderPrescribeSection = () => (
    <div>

        {prescriptionSuccess && (
          <div className="mb-comfortable p-normal bg-success/10 border border-success/20 rounded-md">
            <div className="flex items-center gap-tight">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <p className="text-[15px] text-success font-medium">
                Prescription sent to pharmacy successfully
              </p>
            </div>
          </div>
        )}

        {prescription.length > 0 && (
          <Card className="mb-comfortable">
            <CardContent>
              <h3 className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-normal">
                Current Prescription ({prescription.length})
              </h3>
              <div className="flex flex-col gap-normal">
                {prescription.map((med, index) => {
                  const frequencyLabel = FREQUENCY_OPTIONS.find(
                    (f) => f.value === med.frequency
                  )?.label;
                  return (
                    <div
                      key={`${med.id}-${index}`}
                      className="px-4 py-3 bg-arctic rounded-md"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-[15px] font-medium text-deep-ice">
                            {med.name}
                          </p>
                          <div className="mt-2 space-y-1">
                            <p className="text-[15px] text-text-primary">
                              <span className="text-text-tertiary">Dose:</span>{' '}
                              {med.selectedDosing}
                            </p>
                            <p className="text-[15px] text-text-primary">
                              <span className="text-text-tertiary">Frequency:</span>{' '}
                              {frequencyLabel || med.frequency}
                            </p>
                            <p className="text-[15px] text-text-primary">
                              <span className="text-text-tertiary">Duration:</span>{' '}
                              {med.durationDays} days
                            </p>
                            {med.instructions && (
                              <p className="text-[15px] text-text-primary">
                                <span className="text-text-tertiary">Instructions:</span>{' '}
                                {med.instructions}
                              </p>
                            )}
                          </div>
                        </div>
                        {med.calculatedQuantity && (
                          <div className="text-right">
                            <p className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
                              Quantity
                            </p>
                            <p className="text-xl font-semibold text-deep-ice">
                              {med.calculatedQuantity}
                            </p>
                            <p className="text-[13px] text-text-secondary">
                              {med.quantityUnit}
                              {med.imperialEquivalent && ` (${med.imperialEquivalent.formatted})`}
                              {med.isQuantityEstimate && ' (est.)'}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-end pt-normal mt-normal border-t border-frost">
                <Button
                  variant="primary"
                  onClick={handleSubmitPrescription}
                  disabled={isSubmittingPrescription}
                >
                  {isSubmittingPrescription ? 'Sending...' : 'Prescribe'}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardContent>
            <label
              htmlFor="medication-search"
              className="block text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight"
            >
              Search Medications
            </label>
            <Input
              id="medication-search"
              type="search"
              placeholder="Type at least 3 characters to search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              autoComplete="off"
            />

            {searchQuery.length > 0 && searchQuery.length < 3 && (
              <p className="text-[13px] text-text-tertiary mt-tight">
                Type {3 - searchQuery.length} more character{3 - searchQuery.length !== 1 ? 's' : ''} to search
              </p>
            )}
          </CardContent>
        </Card>

        {isSearching && (
          <div className="mt-normal text-center">
            <p className="text-[15px] text-text-secondary">Searching...</p>
          </div>
        )}

        {!isSearching && searchResults.length > 0 && !selectedMedication && (
          <div className="mt-normal">
            <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-tight">
              Results ({searchResults.length})
            </h3>
            <div className="flex flex-col gap-tight">
              {searchResults.map((medication) => (
                <MedicationResultCard
                  key={medication.id}
                  medication={medication}
                  isSelected={false}
                  onSelect={handleMedicationSelect}
                />
              ))}
            </div>
          </div>
        )}

        {!isSearching && debouncedSearch.length >= 3 && searchResults.length === 0 && (
          <div className="mt-normal text-center py-generous">
            <p className="text-[15px] text-text-secondary">
              No medications found for "{debouncedSearch}"
            </p>
          </div>
        )}

        {allergyAlert && !allergyAlert.blocked && (
          <AllergyWarningBanner
            alert={allergyAlert}
            onDismiss={handleWarningDismiss}
            onSelectAlternative={handleSelectAlternative}
          />
        )}

        {drugInteractions.length > 0 && (
          <DrugInteractionWarning
            interactions={drugInteractions}
            onDismiss={handleInteractionDismiss}
            onSelectAlternative={handleSelectAlternative}
          />
        )}

        {selectedMedication && (
          <MedicationDetails
            medication={selectedMedication}
            onDosingSelect={handleDosingSelect}
            onFrequencyChange={handleFrequencyChange}
            onDurationChange={handleDurationChange}
            onInstructionsChange={handleInstructionsChange}
            onProceed={handleProceed}
            onBack={handleClearSelection}
          />
        )}
    </div>
  );

  return (
    <div className="min-h-screen bg-snow">
      <div className="max-w-7xl mx-auto px-normal py-normal">
        {/* Patient Info Card - Compact Header */}
        <Card className="mb-normal">
          <CardContent>
            <div className="flex items-start gap-normal">
              <button
                onClick={handleBack}
                className="text-text-tertiary hover:text-text-primary transition-colors mt-1"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-tight">
                    <h1 className="text-xl font-semibold text-deep-ice">{patient.name}</h1>
                    {!isLoadingAlerts && alertSummary.totalActive > 0 && (
                      <AlertBadge summary={alertSummary} />
                    )}
                  </div>
                  <span className="text-[15px] text-text-secondary">MRN: {patient.mrn}</span>
                </div>
                <div className="flex items-center justify-between mt-1">
                  <p className="text-[15px] text-text-secondary">
                    {calculateAge(patient.dateOfBirth)}{getGenderAbbrev(patient.gender)} | DOB: {formatDOB(patient.dateOfBirth)}
                  </p>
                  <button
                    onClick={() => {
                      const info = `${patient.name}\nMRN: ${patient.mrn}\nDOB: ${formatDOB(patient.dateOfBirth)}`;
                      navigator.clipboard.writeText(info);
                    }}
                    className="text-[15px] text-glacier-blue hover:text-deep-ice transition-colors flex items-center gap-1"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                    </svg>
                    Copy
                  </button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Two Column Layout: Left Nav + Main Content */}
        <div className="grid grid-cols-12 gap-normal">
          {/* Left Sidebar Navigation */}
          <div className="col-span-3">
            <ChartNavigation
              sections={chartSections}
              activeSection={activeSection === 'prescribe' ? 'medications' : activeSection}
              onNavigate={handleNavigate}
              isLoading={isLoadingChartSections}
              onPrescribeClick={() => handleNavigate('prescribe')}
              prescriptionCount={prescription.length}
              isPrescribeActive={activeSection === 'prescribe'}
            />
          </div>

          {/* Main Content Area */}
          <div className="col-span-9">
            {/* Clinical Alerts Banner */}
            {!isLoadingAlerts && alerts.length > 0 && (
              <ClinicalAlertBanner
                alerts={alerts}
                onAcknowledge={handleAcknowledgeAlert}
                className="mb-normal"
              />
            )}
            {renderMainContent()}
          </div>
        </div>
      </div>

      {/* Modals */}
      {allergyAlert && allergyAlert.blocked && (
        <AllergyBlockModal
          alert={allergyAlert}
          onClose={handleAllergyAlertClose}
          onOverride={handleAllergyOverride}
        />
      )}

      {criticalInteractions.length > 0 && pendingInteractionMedication && (
        <DrugInteractionBlockModal
          interactions={criticalInteractions}
          medicationName={pendingInteractionMedication.name}
          onClose={handleCriticalInteractionClose}
          onOverride={handleInteractionOverride}
        />
      )}

      {selectedActiveMedication && (
        <MedicationDetailModal
          medication={selectedActiveMedication}
          onClose={() => setSelectedActiveMedication(null)}
          onDiscontinue={handleDiscontinueMedication}
          isDiscontinuing={isDiscontinuing}
        />
      )}

      {selectedProblem && (
        <ProblemDetailModal
          isOpen={true}
          onClose={handleCloseProblemDetail}
          problem={selectedProblem}
          problemDetail={problemDetail}
          isLoading={isLoadingProblemDetail}
          error={problemDetailError}
        />
      )}
    </div>
  );
}
