import React from 'react';
import PropTypes from 'prop-types';
import '../styles/components/Card.css';

/**
 * Composant Card pour afficher des contenus en boîtes
 */
const Card = ({
  children,
  title,
  icon,
  actionButton,
  className = '',
  footer,
  loading = false,
  ...props
}) => {
  const cardClasses = [
    'n-card',
    loading ? 'n-card--loading' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={cardClasses} {...props}>
      {(title || icon || actionButton) && (
        <div className="n-card__header">
          <div className="n-card__header-content">
            {icon && <div className="n-card__icon"><i className={`bx ${icon}`}></i></div>}
            {title && <h3 className="n-card__title">{title}</h3>}
          </div>
          {actionButton && <div className="n-card__action">{actionButton}</div>}
        </div>
      )}
      
      <div className="n-card__content">
        {loading ? (
          <div className="n-card__loading">
            <i className="bx bx-loader-alt bx-spin"></i>
            <span>Chargement...</span>
          </div>
        ) : (
          children
        )}
      </div>
      
      {footer && (
        <div className="n-card__footer">
          {footer}
        </div>
      )}
    </div>
  );
};

Card.propTypes = {
  children: PropTypes.node,
  title: PropTypes.node,
  icon: PropTypes.string,
  actionButton: PropTypes.node,
  className: PropTypes.string,
  footer: PropTypes.node,
  loading: PropTypes.bool,
};

export default Card; 