import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider } from './contexts/AuthContext';

import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import Users from './pages/Users';
import Licenses from './pages/Licenses';
import Notifications from './pages/Notifications';
import Updates from './pages/Updates';

// Composant simple pour remplacer ThemeProvider
const ThemeProvider = ({ children }) => {
  return <>{children}</>;
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Toaster />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="users" element={<Users />} />
              <Route path="licenses" element={<Licenses />} />
              <Route path="notifications" element={<Notifications />} />
              <Route path="updates" element={<Updates />} />
              <Route path="settings" element={<Settings />} />
              {/* Redirection pour toute route non trouvée */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App; 