import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LoginPage, PrescribePage } from './pages';

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/prescribe" element={<PrescribePage />} />
      </Routes>
    </BrowserRouter>
  );
}
