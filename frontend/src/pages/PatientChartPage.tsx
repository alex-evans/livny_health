import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, Input, Button } from '../components/ui';
import { useDebounce } from '../hooks';
import { searchMedications } from '../api';
import type { MedicationSearchResult, SelectedMedication, User } from '../types';
import { cn } from '../utils/cn';

const testPatient = {
  id: 'patient-001',
  name: 'Test Patient',
  dateOfBirth: '1985-03-15',
  mrn: 'MRN-12345',
};

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
  onProceed: () => void;
  onBack: () => void;
}

function MedicationDetails({ medication, onDosingSelect, onProceed, onBack }: MedicationDetailsProps) {
  const hasCommonDosing = medication.commonDosing && medication.commonDosing.length > 0;

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
            {hasCommonDosing ? 'Common Dosing' : 'Dosing Instructions'}
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

        <div className="flex justify-end gap-normal pt-normal border-t border-frost">
          <Button variant="secondary" onClick={onBack}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={onProceed}
            disabled={!medication.selectedDosing}
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
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<MedicationSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedMedication, setSelectedMedication] = useState<SelectedMedication | null>(null);
  const [prescription, setPrescription] = useState<SelectedMedication[]>([]);

  const debouncedSearch = useDebounce(searchQuery, 300);

  // For now, just use the test patient
  const patient = patientId === testPatient.id ? testPatient : null;

  useEffect(() => {
    const userJson = sessionStorage.getItem('currentUser');
    if (userJson) {
      setCurrentUser(JSON.parse(userJson));
    } else {
      navigate('/');
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

  const handleMedicationSelect = (medication: MedicationSearchResult) => {
    setSelectedMedication({
      ...medication,
      selectedDosing: undefined,
    });
  };

  const handleDosingSelect = (dosing: string) => {
    if (selectedMedication) {
      setSelectedMedication({
        ...selectedMedication,
        selectedDosing: dosing,
      });
    }
  };

  const handleProceed = () => {
    if (selectedMedication?.selectedDosing) {
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

  if (!currentUser || !patient) {
    return null;
  }

  return (
    <div className="min-h-screen bg-snow">
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

        {prescription.length > 0 && (
          <Card className="mb-comfortable">
            <CardContent>
              <h3 className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary mb-normal">
                Current Prescription ({prescription.length})
              </h3>
              <div className="flex flex-wrap gap-tight">
                {prescription.map((med, index) => (
                  <span
                    key={`${med.id}-${index}`}
                    className="px-3 py-2 bg-arctic text-deep-ice rounded-md text-[15px]"
                  >
                    {med.name} - {med.selectedDosing}
                  </span>
                ))}
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
            onProceed={handleProceed}
            onBack={handleClearSelection}
          />
        )}
      </main>
    </div>
  );
}
