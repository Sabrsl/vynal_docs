import React from 'react';
import PropTypes from 'prop-types';
import '../styles/components/Button.css';

/**
 * Composant Button avec le design n8n
 */
const Button = ({
  children,
  type = 'default', // 'primary', 'secondary', 'tertiary', 'text', 'danger', 'outlined'
  size = 'medium', // 'small', 'medium', 'large'
  icon = null,
  className = '',
  submit = false,
  disabled = false,
  loading = false,
  onClick,
  variant = 'secondary',
  fullWidth = false,
  ...props
}) => {
  const baseClass = 'button';
  const variantClass = `button-${variant}`;
  const widthClass = fullWidth ? 'button-full' : '';
  const iconClass = icon ? 'button-with-icon' : '';
  
  const classes = [
    baseClass,
    variantClass,
    widthClass,
    iconClass,
    className
  ].filter(Boolean).join(' ');
  
  const styles = {
    button: {
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px',
      padding: '8px 16px',
      borderRadius: '4px',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      border: 'none',
      fontSize: '14px',
      width: fullWidth ? '100%' : 'auto',
    },
    primary: {
      backgroundColor: '#6933FF',
      color: 'white',
    },
    secondary: {
      backgroundColor: '#EAECFF',
      color: '#6933FF',
    },
    text: {
      backgroundColor: 'transparent',
      color: '#555',
      padding: icon && !children ? '8px' : '8px 16px',
    }
  };
  
  const combinedStyles = {
    ...styles.button,
    ...(styles[variant] || {}),
  };
  
  return (
    <button
      type={submit ? 'submit' : 'button'}
      className={classes}
      disabled={disabled || loading}
      onClick={onClick}
      style={combinedStyles}
      {...props}
    >
      {loading && <i className="bx bx-loader-alt bx-spin button-icon-left"></i>}
      {icon && !loading && <i className={`bx ${icon}`}></i>}
      {children}
    </button>
  );
};

Button.propTypes = {
  children: PropTypes.node,
  type: PropTypes.oneOf(['default', 'primary', 'secondary', 'tertiary', 'text', 'danger', 'outlined']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  icon: PropTypes.string,
  className: PropTypes.string,
  submit: PropTypes.bool,
  disabled: PropTypes.bool,
  loading: PropTypes.bool,
  onClick: PropTypes.func,
  variant: PropTypes.oneOf(['primary', 'secondary', 'tertiary', 'text', 'danger', 'outlined']),
  fullWidth: PropTypes.bool,
};

export default Button; 