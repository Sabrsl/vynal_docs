import React from 'react';
import Button from './Button';
import './EmptyState.css';

/**
 * Composant pour afficher un état vide avec une icône, un message et éventuellement un bouton d'action
 */
const EmptyState = ({ 
  icon = 'bx-search',
  title = 'Aucun résultat',
  message = 'Aucun élément trouvé',
  actionText,
  onAction
}) => {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">
        <i className={`bx ${icon}`}></i>
      </div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-message">{message}</p>
      {actionText && onAction && (
        <Button variant="primary" onClick={onAction}>
          {actionText}
        </Button>
      )}
    </div>
  );
};

export default EmptyState; 