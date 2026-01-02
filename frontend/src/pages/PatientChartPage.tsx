import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, Input, Button, Select } from '../components/ui';
import { AllergyBanner } from '../components/patient';
import { ActiveMedicationsList } from '../components/medication';
import { useDebounce } from '../hooks';
import { searchMedications, getPatient } from '../api';
import type { MedicationSearchResult, SelectedMedication, User, Patient } from '../types';
import type { MedicationForm } from '../utils/quantityCalculator';
import { cn } from '../utils/cn';
import {
  FREQUENCY_OPTIONS,
  calculateQuantity,
  parseFrequencyFromDosing,
  parseDosesPerAdmin,
  getDefaultDuration,
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

export function PatientChartPage() {
  const navigate = useNavigate();
  const { patientId } = useParams<{ patientId: string }>();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [patient, setPatient] = useState<Patient | null>(null);
  const [isLoadingPatient, setIsLoadingPatient] = useState(true);
  const [patientError, setPatientError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<MedicationSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedMedication, setSelectedMedication] = useState<SelectedMedication | null>(null);
  const [prescription, setPrescription] = useState<SelectedMedication[]>([]);

  const debouncedSearch = useDebounce(searchQuery, 300);

  useEffect(() => {
    const userJson = sessionStorage.getItem('currentUser');
    if (userJson) {
      setCurrentUser(JSON.parse(userJson));
    } else {
      navigate('/');
    }
  }, [navigate]);

  useEffect(() => {
    async function fetchPatient() {
      if (!patientId) {
        setPatientError('No patient ID provided');
        setIsLoadingPatient(false);
        return;
      }

      try {
        const patientData = await getPatient(patientId);
        setPatient(patientData);
      } catch (err) {
        setPatientError(err instanceof Error ? err.message : 'Failed to load patient');
      } finally {
        setIsLoadingPatient(false);
      }
    }

    fetchPatient();
  }, [patientId]);

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

  const handleMedicationSelect = (medication: MedicationSearchResult) => {
    const defaultDuration = getDefaultDuration(medication.name);
    const form = (medication.form || 'tablet') as MedicationForm;
    setSelectedMedication({
      ...medication,
      selectedDosing: undefined,
      frequency: undefined,
      durationDays: defaultDuration,
      calculatedQuantity: undefined,
      quantityUnit: getUnitForForm(form),
      isQuantityEstimate: false,
    });
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

  const handleProceed = () => {
    if (
      selectedMedication?.selectedDosing &&
      selectedMedication.frequency &&
      selectedMedication.durationDays
    ) {
      setPrescription([...prescription, selectedMedication]);
      setSelectedMedication(null);
      setSearchQuery('');
      setSearchResults([]);
    }
  };

  const handleClearSelection = () => {
    setSelectedMedication(null);
  };

  const handleBack = () => {
    navigate('/patients');
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
          <Button variant="secondary" onClick={() => navigate('/patients')}>
            Back to Patients
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-snow">
      <AllergyBanner allergies={patient.allergies ?? []} />
      <header className="bg-white shadow-card">
        <div className="max-w-5xl mx-auto px-generous py-normal">
          <div className="flex items-center gap-normal mb-tight">
            <button
              onClick={handleBack}
              className="text-text-tertiary hover:text-text-primary transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-semibold text-deep-ice">{patient.name}</h1>
              <p className="text-[13px] text-text-tertiary">
                DOB: {patient.dateOfBirth} | {patient.mrn}
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-generous py-generous">
        <h2 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-normal">
          Medications
        </h2>

        {patient.activeMedications && patient.activeMedications.length > 0 && (
          <ActiveMedicationsList medications={patient.activeMedications} />
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
                              {med.isQuantityEstimate && ' (est.)'}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
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
      </main>
    </div>
  );
}
