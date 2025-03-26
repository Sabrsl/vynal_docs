import React from 'react';
import PropTypes from 'prop-types';
import '../styles/components/Card.css';

/**
 * Composant Card avec le design n8n
 */
const Card = ({
  children,
  title = '',
  subtitle = '',
  actions = null,
  className = '',
  hoverable = false,
  compact = false,
  noShadow = false,
  ...props
}) => {
  const styles = {
    card: {
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 6px rgba(0, 0, 0, 0.08)',
      overflow: 'hidden',
    },
    header: {
      padding: '16px',
      borderBottom: title || subtitle ? '1px solid #f0f0f5' : 'none',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    content: {
      padding: '16px',
    },
    title: {
      margin: 0,
      fontSize: '16px',
      fontWeight: '600',
      color: '#333',
    },
    subtitle: {
      margin: '4px 0 0 0',
      fontSize: '14px',
      color: '#666',
    },
    actions: {
      display: 'flex',
      gap: '8px',
    }
  };

  const cardClass = `n-card ${
    hoverable ? 'n-card--hoverable' : ''
  } ${
    compact ? 'n-card--compact' : ''
  } ${
    noShadow ? 'n-card--no-shadow' : ''
  } ${className}`;

  return (
    <div 
      className={cardClass}
      style={styles.card}
      {...props}
    >
      {(title || actions) && (
        <div style={styles.header}>
          <div>
            {title && <h3 style={styles.title}>{title}</h3>}
            {subtitle && <p style={styles.subtitle}>{subtitle}</p>}
          </div>
          {actions && <div style={styles.actions}>{actions}</div>}
        </div>
      )}
      <div style={styles.content}>
        {children}
      </div>
    </div>
  );
};

Card.propTypes = {
  children: PropTypes.node,
  title: PropTypes.node,
  subtitle: PropTypes.node,
  actions: PropTypes.node,
  className: PropTypes.string,
  hoverable: PropTypes.bool,
  compact: PropTypes.bool,
  noShadow: PropTypes.bool,
};

export default Card; 