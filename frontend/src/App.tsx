import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LoginPage, PatientListPage, PatientChartPage, DailySchedulePage } from './pages';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DailySchedulePage />} />
        <Route path="/schedule" element={<DailySchedulePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/patients" element={<PatientListPage />} />
        <Route path="/patients/:patientId" element={<PatientChartPage />} />
      </Routes>
    </BrowserRouter>
  );
}
