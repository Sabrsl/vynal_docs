import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

// Pages
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Users from './pages/Users';
import Licenses from './pages/Licenses';
import Settings from './pages/Settings';
import Notifications from './pages/Notifications';
import Layout from './components/Layout';

// Protected route component
const ProtectedRoute = ({ children }) => {
  // DÉSACTIVÉ POUR LE DÉVELOPPEMENT: ignorer la vérification d'authentification
  // Décommentez le code ci-dessous et supprimez "return children" quand vous êtes prêt pour la production
  return children; 
  
  /* CODE DE PRODUCTION:
  const { currentUser, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (!currentUser) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
  */
};

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<Dashboard />} />
        <Route path="users" element={<Users />} />
        <Route path="licenses" element={<Licenses />} />
        <Route path="settings" element={<Settings />} />
        <Route path="notifications" element={<Notifications />} />
      </Route>
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App; 