import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, Input, Button } from '../components/ui';
import { useDebounce } from '../hooks';
import { searchMedications } from '../api';
import type { MedicationSearchResult, SelectedMedication, User } from '../types';
import { cn } from '../utils/cn';

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
  return (
    <Card className="mt-normal">
      <CardContent>
        <div className="flex items-start justify-between mb-comfortable">
          <div>
            <h3 className="text-xl font-semibold text-deep-ice">{medication.name}</h3>
            <p className="text-[15px] text-text-secondary mt-1">
              {medication.form} - {medication.strength}
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
            Common Dosing
          </label>
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

export function PrescribePage() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<MedicationSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedMedication, setSelectedMedication] = useState<SelectedMedication | null>(null);
  const [prescription, setPrescription] = useState<SelectedMedication[]>([]);

  const debouncedSearch = useDebounce(searchQuery, 300);

  // Load current user from session
  useEffect(() => {
    const userJson = sessionStorage.getItem('currentUser');
    if (userJson) {
      setCurrentUser(JSON.parse(userJson));
    } else {
      navigate('/');
    }
  }, [navigate]);

  // Perform search when debounced value changes
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

  const handleLogout = () => {
    sessionStorage.removeItem('currentUser');
    navigate('/');
  };

  if (!currentUser) {
    return null;
  }

  return (
    <div className="min-h-screen bg-snow">
      {/* Header */}
      <header className="bg-white shadow-card">
        <div className="max-w-5xl mx-auto px-generous py-normal flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-deep-ice">Medication Order</h1>
            <p className="text-[13px] text-text-tertiary">Prescribing as {currentUser.name}</p>
          </div>
          <button
            onClick={handleLogout}
            className="text-[15px] text-text-secondary hover:text-text-primary transition-colors"
          >
            Switch User
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-generous py-generous">
        {/* Prescription Summary */}
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

        {/* Search Section */}
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
              autoFocus
              autoComplete="off"
            />

            {searchQuery.length > 0 && searchQuery.length < 3 && (
              <p className="text-[13px] text-text-tertiary mt-tight">
                Type {3 - searchQuery.length} more character{3 - searchQuery.length !== 1 ? 's' : ''} to search
              </p>
            )}
          </CardContent>
        </Card>

        {/* Loading State */}
        {isSearching && (
          <div className="mt-normal text-center">
            <p className="text-[15px] text-text-secondary">Searching...</p>
          </div>
        )}

        {/* Search Results */}
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

        {/* No Results */}
        {!isSearching && debouncedSearch.length >= 3 && searchResults.length === 0 && (
          <div className="mt-normal text-center py-generous">
            <p className="text-[15px] text-text-secondary">
              No medications found for "{debouncedSearch}"
            </p>
          </div>
        )}

        {/* Selected Medication Details */}
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
