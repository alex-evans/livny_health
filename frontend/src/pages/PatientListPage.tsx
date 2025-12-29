import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui';
import { getPatients } from '../api';
import type { User, Patient } from '../types';

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function PatientListPage() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const userJson = sessionStorage.getItem('currentUser');
    if (userJson) {
      setCurrentUser(JSON.parse(userJson));
    } else {
      navigate('/');
    }
  }, [navigate]);

  useEffect(() => {
    async function fetchPatients() {
      try {
        const data = await getPatients();
        setPatients(data);
      } catch (err) {
        setError('Failed to load patients');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchPatients();
  }, []);

  const handlePatientSelect = (patientId: string) => {
    navigate(`/patients/${patientId}`);
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
      <header className="bg-white shadow-card">
        <div className="max-w-5xl mx-auto px-generous py-normal flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-deep-ice">Patients</h1>
            <p className="text-[13px] text-text-tertiary">{currentUser.name}</p>
          </div>
          <button
            onClick={handleLogout}
            className="text-[15px] text-text-secondary hover:text-text-primary transition-colors"
          >
            Switch User
          </button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-generous py-generous">
        {loading && (
          <p className="text-[15px] text-text-secondary">Loading patients...</p>
        )}

        {error && (
          <p className="text-[15px] text-critical">{error}</p>
        )}

        {!loading && !error && patients.length === 0 && (
          <p className="text-[15px] text-text-secondary">No patients found</p>
        )}

        <div className="flex flex-col gap-normal">
          {patients.map((patient) => (
            <Card key={patient.id} hoverable onClick={() => handlePatientSelect(patient.id)}>
              <div className="flex items-center gap-normal">
                <div className="w-12 h-12 rounded-full bg-arctic flex items-center justify-center flex-shrink-0">
                  <span className="text-lg font-semibold text-deep-ice">
                    {getInitials(patient.name)}
                  </span>
                </div>
                <div>
                  <h2 className="text-[15px] font-semibold text-text-primary">{patient.name}</h2>
                  <p className="text-[13px] text-text-secondary">
                    DOB: {patient.dateOfBirth} | {patient.mrn}
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
