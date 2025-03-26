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
  style = {},
  ...props
}) => {
  // Utilisation des classes CSS correctes correspondant à Button.css
  const baseClass = 'n-button';
  const variantClass = `n-button--${variant}`;
  const sizeClass = `n-button--${size}`;
  const iconOnlyClass = icon && !children ? 'n-button--icon-only' : '';
  const loadingClass = loading ? 'n-button--loading' : '';
  const fullWidthClass = fullWidth ? 'n-button--full' : '';
  
  const classes = [
    baseClass,
    variantClass,
    sizeClass,
    iconOnlyClass,
    loadingClass,
    fullWidthClass,
    className
  ].filter(Boolean).join(' ');
  
  return (
    <button
      type={submit ? 'submit' : 'button'}
      className={classes}
      disabled={disabled || loading}
      onClick={onClick}
      style={style}
      {...props}
    >
      {loading && <i className="bx bx-loader-alt bx-spin"></i>}
      {icon && !loading && <i className={`bx ${icon}`}></i>}
      <span>{children}</span>
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
  style: PropTypes.object,
};

export default Button; 