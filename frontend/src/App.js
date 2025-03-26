import React, { useState } from 'react';
import './App.css';
import logo from './assets/logo.svg';
import avatar from './assets/avatar.svg';

// Import des composants
import Button from './components/Button';
import Card from './components/Card';
import Input from './components/Input';

// Import des pages
import HomePage from './pages/HomePage';
import DocumentsPage from './pages/DocumentsPage';
import TemplatesPage from './pages/TemplatesPage';
import CategoriesPage from './pages/CategoriesPage';
import UsersPage from './pages/UsersPage';
import SharePage from './pages/SharePage';
import StatsPage from './pages/StatsPage';
import TrashPage from './pages/TrashPage';

function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Données fictives pour le tableau de bord
  const recentDocs = [
    { id: 1, name: 'Contrat de vente.pdf', type: 'pdf', date: '2024-03-24' },
    { id: 2, name: 'Procédure qualité.doc', type: 'doc', date: '2024-03-23' },
    { id: 3, name: 'Notes de réunion.txt', type: 'txt', date: '2024-03-22' },
  ];
  
  const stats = {
    documents: 145,
    templates: 12,
    categories: 8,
    storage: '2.4 GB',
  };
  
  // Fonction pour formater les dates
  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('fr-FR', { 
      day: '2-digit', month: '2-digit', year: 'numeric' 
    }).format(date);
  };
  
  // Fonction pour afficher la page active
  const renderActivePage = () => {
    switch (activeSection) {
      case 'dashboard':
        return <HomePage />;
      case 'documents':
        return <DocumentsPage />;
      case 'templates':
        return <TemplatesPage />;
      case 'categories':
        return <CategoriesPage />;
      case 'users':
        return <UsersPage />;
      case 'share':
        return <SharePage />;
      case 'stats':
        return <StatsPage />;
      case 'trash':
        return <TrashPage />;
      default:
        return <HomePage />;
    }
  };
  
  return (
    <div className="app">
      {/* En-tête */}
      <header className="app-header">
        <div className="app-logo">
          <img src={logo} alt="Logo" width="26" />
          <span>Vynal <span className="app-title">Docs</span></span>
        </div>
        
        <div className="app-search">
          <Input 
            type="search" 
            placeholder="Rechercher un document..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            icon="bx-search"
          />
        </div>
        
        <div className="app-actions">
          <Button icon="bx-bell" variant="text" />
          <Button icon="bx-cog" variant="text" />
          <div className="user-menu">
            <img src={avatar} alt="Avatar" className="user-avatar" />
            <span className="user-name">Jean Dupont</span>
          </div>
        </div>
      </header>
      
      {/* Contenu principal */}
      <div className="app-content">
        {/* Barre latérale */}
        <nav className="app-sidebar">
          <div 
            className={`sidebar-item ${activeSection === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveSection('dashboard')}
          >
            <i className='bx bx-grid-alt'></i>
            <span>Tableau de bord</span>
          </div>
          <div 
            className={`sidebar-item ${activeSection === 'documents' ? 'active' : ''}`} 
            onClick={() => setActiveSection('documents')}
          >
            <i className='bx bx-file'></i>
            <span>Documents</span>
          </div>
          <div 
            className={`sidebar-item ${activeSection === 'templates' ? 'active' : ''}`} 
            onClick={() => setActiveSection('templates')}
          >
            <i className='bx bx-duplicate'></i>
            <span>Modèles</span>
          </div>
          <div 
            className={`sidebar-item ${activeSection === 'categories' ? 'active' : ''}`} 
            onClick={() => setActiveSection('categories')}
          >
            <i className='bx bx-category'></i>
            <span>Catégories</span>
          </div>
          <div 
            className={`sidebar-item ${activeSection === 'users' ? 'active' : ''}`}
            onClick={() => setActiveSection('users')}
          >
            <i className='bx bx-user'></i>
            <span>Utilisateurs</span>
          </div>
          <div 
            className={`sidebar-item ${activeSection === 'share' ? 'active' : ''}`} 
            onClick={() => setActiveSection('share')}
          >
            <i className='bx bx-share-alt'></i>
            <span>Partage</span>
          </div>
          <div 
            className={`sidebar-item ${activeSection === 'stats' ? 'active' : ''}`} 
            onClick={() => setActiveSection('stats')}
          >
            <i className='bx bx-bar-chart-alt-2'></i>
            <span>Statistiques</span>
          </div>
          <div 
            className={`sidebar-item ${activeSection === 'trash' ? 'active' : ''}`} 
            onClick={() => setActiveSection('trash')}
          >
            <i className='bx bx-trash'></i>
            <span>Corbeille</span>
          </div>
        </nav>
        
        {/* Contenu principal - Rendu de la page active */}
        <main className="app-main">
          {renderActivePage()}
        </main>
      </div>
    </div>
  );
}

export default App;
