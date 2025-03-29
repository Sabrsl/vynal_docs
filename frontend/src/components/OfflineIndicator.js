import React from 'react';
import { useOffline } from '../contexts/OfflineContext';
import '../styles/OfflineIndicator.css';

const OfflineIndicator = () => {
  const { 
    isOnline, 
    syncStatus, 
    syncProgress, 
    syncErrors, 
    hasConflicts, 
    conflicts,
    syncAll, 
    resolveAllConflicts 
  } = useOffline();

  // Déterminer la classe CSS en fonction du statut de connexion
  const getStatusClass = () => {
    if (!isOnline) return 'offline';
    if (syncStatus === 'error') return 'error';
    if (syncStatus === 'syncing') return 'syncing';
    if (hasConflicts) return 'conflict';
    return 'online';
  };

  // Déterminer le texte du badge en fonction du statut de connexion
  const getStatusText = () => {
    if (!isOnline) return 'Mode hors ligne';
    if (syncStatus === 'error') return 'Erreur de synchronisation';
    if (syncStatus === 'syncing') return 'Synchronisation...';
    if (hasConflicts) return 'Conflits détectés';
    return 'Connecté';
  };

  // Obtenir l'icône en fonction du statut
  const getStatusIcon = () => {
    if (!isOnline) return '📶';
    if (syncStatus === 'error') return '❌';
    if (syncStatus === 'syncing') return '🔄';
    if (hasConflicts) return '⚠️';
    return '✅';
  };

  // Formater les erreurs de synchronisation pour l'affichage
  const formatErrors = () => {
    return syncErrors.map((error, index) => (
      <div key={index} className="offline-error">
        {error.message || JSON.stringify(error)}
      </div>
    ));
  };

  // Formatter les conflits pour l'affichage
  const formatConflicts = () => {
    return conflicts.map((conflict, index) => (
      <div key={index} className="offline-conflict">
        <span>Conflit dans {conflict.type}: {conflict.doc._id}</span>
      </div>
    ));
  };

  return (
    <div className={`offline-indicator ${getStatusClass()}`}>
      <div className="offline-badge">
        <span className="offline-icon">{getStatusIcon()}</span>
        <span className="offline-text">{getStatusText()}</span>
        
        {syncStatus === 'syncing' && (
          <div className="sync-progress">
            <div 
              className="sync-progress-bar" 
              style={{ width: `${syncProgress}%` }}
            ></div>
          </div>
        )}
      </div>
      
      {/* Afficher plus de détails en mode hors ligne ou s'il y a des erreurs */}
      {(!isOnline || syncStatus === 'error' || hasConflicts) && (
        <div className="offline-details">
          {!isOnline && (
            <div className="offline-message">
              <p>Vous travaillez actuellement hors ligne. Vos modifications seront synchronisées lorsque vous serez à nouveau connecté.</p>
            </div>
          )}
          
          {syncStatus === 'error' && (
            <div className="offline-errors">
              <h4>Erreurs de synchronisation:</h4>
              {formatErrors()}
              <button 
                className="sync-button"
                onClick={syncAll}
              >
                Réessayer la synchronisation
              </button>
            </div>
          )}
          
          {hasConflicts && (
            <div className="offline-conflicts">
              <h4>Conflits détectés:</h4>
              {formatConflicts()}
              <button 
                className="resolve-button"
                onClick={resolveAllConflicts}
              >
                Résoudre automatiquement
              </button>
              <p className="conflict-note">
                Note: La résolution automatique conserve la version la plus récente.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default OfflineIndicator; 