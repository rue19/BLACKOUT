import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './components/landing/LandingPage';
import DashboardPage from './components/landing/DashboardPage';

/**
 * App — BLACKOUT application router.
 *
 * Routes:
 *   /           → LandingPage (hero page)
 *   /dashboard  → DashboardPage (existing dashboard, preserved intact)
 *   *           → redirect to /
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
