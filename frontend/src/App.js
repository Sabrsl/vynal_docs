import React, { useState, useEffect } from 'react';
import { Route, Routes, useNavigate, useLocation, Navigate } from 'react-router-dom';
import './App.css';
import logo from './assets/logo.svg';
import avatar from './assets/avatar.svg';

// Import des composants
import Button from './components/Button';
import Card from './components/Card';
import Input from './components/Input';
import Loader from './components/Loader';
import Navbar from './components/Navbar/Navbar';
import Sidebar from './components/Sidebar/Sidebar';
import SearchBar from './components/SearchBar/SearchBar';
import PrivateRoute from './components/PrivateRoute';

// Import du contexte
import { useAppContext } from './context/AppContext';
import { useAuth } from './context/AuthContext';

// Import des pages
import HomePage from './pages/HomePage';
import DocumentsPage from './pages/DocumentsPage';
import TemplatesPage from './pages/TemplatesPage';
import CategoriesPage from './pages/CategoriesPage';
import UsersPage from './pages/UsersPage';
import SharePage from './pages/SharePage';
import StatsPage from './pages/StatsPage';
import TrashPage from './pages/TrashPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

const MainApp = () => {
  const { 
    activeSection, 
    setActiveSection, 
    isLoading,
    documents,
    activities
  } = useAppContext();
  
  const { user, logout } = useAuth();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();
  
  // Synchroniser la section active avec le chemin de l'URL
  useEffect(() => {
    const path = location.pathname.substring(1) || 'dashboard';
    if (path !== activeSection) {
      setActiveSection(path);
    }
  }, [location, activeSection, setActiveSection]);
  
  // Gestionnaires d'événements explicites
  const handleSectionClick = (section) => {
    setActiveSection(section);
    navigate(`/${section === 'dashboard' ? '' : section}`);
  };
  
  const handleBellClick = () => {
    console.log('Notifications clicked');
    alert('Notifications cliquées!');
    // Implémenter l'ouverture du panneau de notifications
  };
  
  const handleSettingsClick = () => {
    console.log('Settings clicked');
    alert('Paramètres cliqués!');
    // Implémenter l'ouverture des paramètres
  };
  
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };
  
  const handleUserMenuClick = () => {
    setShowUserMenu(!showUserMenu);
  };
  
  const handleProfileClick = () => {
    alert('Profil utilisateur');
    setShowUserMenu(false);
  };
  
  const handleSettingsMenuClick = () => {
    alert('Paramètres du compte');
    setShowUserMenu(false);
  };
  
  const handleLogoutClick = () => {
    logout();
    navigate('/login');
    setShowUserMenu(false);
  };
  
  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      alert(`Recherche de: ${searchQuery}`);
      // Implémenter la recherche
    }
  };
  
  return (
    <div className="app-container">
      <Navbar>
        <div className="logo" onClick={() => handleSectionClick('dashboard')}>
          <img src={logo} alt="Vynal Docs" className="logo-image" />
          <h1 className="logo-text">Vynal Docs</h1>
        </div>
        <SearchBar placeholder="Rechercher..." />
        <div className="navbar-actions">
          <Button variant="transparent" onClick={handleSettingsClick}>
            <i className='bx bx-cog'></i>
          </Button>
          <Button variant="transparent" onClick={handleBellClick}>
            <i className='bx bx-bell'></i>
          </Button>
          <div className="user-profile" onClick={handleUserMenuClick}>
            <img src={user?.avatar || avatar} alt="User Avatar" className="user-avatar" />
            <span className="user-name">{user?.name || 'Utilisateur'}</span>
            {showUserMenu && (
              <div className="user-dropdown">
                <div className="user-dropdown-header">
                  <img src={user?.avatar || avatar} alt="User Avatar" className="user-dropdown-avatar" />
                  <div className="user-dropdown-info">
                    <div className="user-dropdown-name">{user?.name || 'Utilisateur'}</div>
                    <div className="user-dropdown-email">{user?.email || 'email@example.com'}</div>
                  </div>
                </div>
                <div className="user-dropdown-divider"></div>
                <div className="user-dropdown-item" onClick={handleProfileClick}>
                  <i className="bx bx-user"></i> Profil
                </div>
                <div className="user-dropdown-item" onClick={handleSettingsMenuClick}>
                  <i className="bx bx-cog"></i> Paramètres
                </div>
                <div className="user-dropdown-divider"></div>
                <div className="user-dropdown-item" onClick={handleLogoutClick}>
                  <i className="bx bx-log-out"></i> Déconnexion
                </div>
              </div>
            )}
          </div>
        </div>
      </Navbar>
      
      <div className="main-content">
        <Sidebar onSectionClick={handleSectionClick} activeSection={activeSection} />
        
        <div className="content-area">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/templates" element={<TemplatesPage />} />
            <Route path="/categories" element={<CategoriesPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/share" element={<SharePage />} />
            <Route path="/stats" element={<StatsPage />} />
            <Route path="/trash" element={<TrashPage />} />
          </Routes>
        </div>
      </div>
    </div>
  );
};

const App = () => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <Loader text="Chargement..." />
      </div>
    );
  }
  
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      <Route path="/*" element={
        isAuthenticated ? <MainApp /> : <Navigate to="/login" />
      } />
    </Routes>
  );
};

export default App;
