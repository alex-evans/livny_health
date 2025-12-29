import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui';
import type { User } from '../types';

const testPatient = {
  id: 'patient-001',
  name: 'Test Patient',
  dateOfBirth: '1985-03-15',
  mrn: 'MRN-12345',
};

export function PatientListPage() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    const userJson = sessionStorage.getItem('currentUser');
    if (userJson) {
      setCurrentUser(JSON.parse(userJson));
    } else {
      navigate('/');
    }
  }, [navigate]);

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
        <div className="flex flex-col gap-normal">
          <Card hoverable onClick={() => handlePatientSelect(testPatient.id)}>
            <div className="flex items-center gap-normal">
              <div className="w-12 h-12 rounded-full bg-arctic flex items-center justify-center flex-shrink-0">
                <span className="text-lg font-semibold text-deep-ice">TP</span>
              </div>
              <div>
                <h2 className="text-[15px] font-semibold text-text-primary">{testPatient.name}</h2>
                <p className="text-[13px] text-text-secondary">
                  DOB: {testPatient.dateOfBirth} | {testPatient.mrn}
                </p>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
