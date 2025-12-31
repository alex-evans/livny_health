import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui';

const drEmily = {
  id: 'dr-emily-chen',
  name: 'Dr. Emily Chen',
  title: 'The Attentive Physician',
  specialty: 'Internal Medicine',
  persona: 'A seasoned physician who values thorough documentation. She relies on the EHR to review patient histories, order tests, and make informed decisions. She appreciates clinical decision support alerts and ensures patient safety.',
};

export function LoginPage() {
  const navigate = useNavigate();

  const handleLaunch = () => {
    sessionStorage.setItem('currentUser', JSON.stringify({
      id: drEmily.id,
      name: drEmily.name,
      role: 'physician',
      specialty: drEmily.specialty,
    }));
    navigate('/patients');
  };

  return (
    <div className="min-h-screen bg-snow flex flex-col items-center justify-center p-generous">
      <Card hoverable onClick={handleLaunch} className="w-full max-w-xs">
        <div className="flex items-center gap-normal mb-normal">
          <div className="w-12 h-12 rounded-full bg-arctic flex items-center justify-center flex-shrink-0">
            <span className="text-lg font-semibold text-deep-ice">EC</span>
          </div>
          <div>
            <h2 className="text-[15px] font-semibold text-deep-ice">{drEmily.name}</h2>
            <p className="text-[13px] text-glacier-blue">{drEmily.title}</p>
          </div>
        </div>

        <p className="text-[13px] text-text-secondary leading-relaxed">
          {drEmily.persona}
        </p>

        <div className="mt-normal pt-normal border-t border-frost">
          <span className="text-[11px] font-medium uppercase tracking-wide text-text-tertiary">
            {drEmily.specialty}
          </span>
        </div>
      </Card>
    </div>
  );
}
