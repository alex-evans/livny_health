import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LoginPage, PatientListPage, PatientChartPage } from './pages';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/patients" element={<PatientListPage />} />
        <Route path="/patients/:patientId" element={<PatientChartPage />} />
      </Routes>
    </BrowserRouter>
  );
}
