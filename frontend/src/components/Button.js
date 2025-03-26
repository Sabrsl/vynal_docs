import React from 'react';
import './Button.css';

/**
 * Composant Button avec le design n8n
 */
const Button = ({
  children,
  variant = 'default',
  type = 'button',
  onClick,
  disabled = false,
  size = 'medium',
  icon,
  className = '',
  fullWidth = false,
  style,
  ...props
}) => {
  // Construire les classes CSS
  const buttonClass = [
    'button',
    `button-${variant}`,
    `button-${size}`,
    fullWidth ? 'button-full-width' : '',
    icon && !children ? 'button-icon-only' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      type={type}
      className={buttonClass}
      onClick={onClick}
      disabled={disabled}
      style={style}
      {...props}
    >
      {icon && <i className={`bx ${icon}`}></i>}
      {children}
    </button>
  );
};

export default Button; 