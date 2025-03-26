import React from 'react';
import './Sidebar.css';
import { useAppContext } from '../../context/AppContext';

const Sidebar = ({ onSectionClick, activeSection }) => {
  const { documents, activities } = useAppContext();

  return (
    <nav className="sidebar">
      <div className="sidebar-menu">
        <div 
          className={`sidebar-item ${activeSection === 'dashboard' ? 'active' : ''}`}
          onClick={() => onSectionClick('dashboard')}
        >
          <i className='bx bx-grid-alt'></i>
          <span>Tableau de bord</span>
        </div>
        <div 
          className={`sidebar-item ${activeSection === 'documents' ? 'active' : ''}`} 
          onClick={() => onSectionClick('documents')}
        >
          <i className='bx bx-file'></i>
          <span>Documents</span>
          {documents.length > 0 && <span className="sidebar-badge">{documents.length}</span>}
        </div>
        <div 
          className={`sidebar-item ${activeSection === 'templates' ? 'active' : ''}`} 
          onClick={() => onSectionClick('templates')}
        >
          <i className='bx bx-duplicate'></i>
          <span>Modèles</span>
        </div>
        <div 
          className={`sidebar-item ${activeSection === 'categories' ? 'active' : ''}`} 
          onClick={() => onSectionClick('categories')}
        >
          <i className='bx bx-category'></i>
          <span>Catégories</span>
        </div>
        <div 
          className={`sidebar-item ${activeSection === 'vynalgpt' ? 'active' : ''}`} 
          onClick={() => onSectionClick('vynalgpt')}
        >
          <i className='bx bx-bot'></i>
          <span>Vynal GPT</span>
        </div>
        <div 
          className={`sidebar-item ${activeSection === 'users' ? 'active' : ''}`} 
          onClick={() => onSectionClick('users')}
        >
          <i className='bx bx-user'></i>
          <span>Utilisateurs</span>
        </div>
        <div 
          className={`sidebar-item ${activeSection === 'share' ? 'active' : ''}`} 
          onClick={() => onSectionClick('share')}
        >
          <i className='bx bx-share-alt'></i>
          <span>Partage</span>
        </div>
        <div 
          className={`sidebar-item ${activeSection === 'stats' ? 'active' : ''}`} 
          onClick={() => onSectionClick('stats')}
        >
          <i className='bx bx-bar-chart-alt-2'></i>
          <span>Statistiques</span>
          {activities.length > 0 && <span className="sidebar-badge">{activities.length}</span>}
        </div>
        <div 
          className={`sidebar-item ${activeSection === 'trash' ? 'active' : ''}`} 
          onClick={() => onSectionClick('trash')}
        >
          <i className='bx bx-trash'></i>
          <span>Corbeille</span>
        </div>
      </div>
    </nav>
  );
};

export default Sidebar; 