import React from 'react';
import PropTypes from 'prop-types';
import '../styles/components/Input.css';

/**
 * Composant Input avec le design n8n
 */
const Input = ({
  label = '',
  name = '',
  value = '',
  placeholder = '',
  type = 'text',
  size = 'medium', // 'small', 'medium', 'large'
  disabled = false,
  readOnly = false,
  required = false,
  invalid = false,
  prefixIcon = null,
  suffixIcon = null,
  prefix = null,
  suffix = null,
  className = '',
  helpText = '',
  errorText = '',
  onChange,
  id,
  error,
  helperText,
  ...props
}) => {
  const uniqueId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  // Classes CSS pour le conteneur principal
  const containerClasses = [
    'n-input',
    `n-input--${size}`,
    invalid || error ? 'n-input--invalid' : '',
    disabled ? 'n-input--disabled' : '',
    readOnly ? 'n-input--readonly' : '',
    prefixIcon ? 'n-input--prefix-icon' : '',
    suffixIcon ? 'n-input--suffix-icon' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={containerClasses}>
      {label && (
        <label htmlFor={uniqueId} className="n-input__label">
          {label}
          {required && <span className="n-input__required">*</span>}
        </label>
      )}
      
      <div className="n-input__wrapper">
        {prefixIcon && (
          <div className="n-input__prefix-icon">
            <i className={`bx ${prefixIcon}`}></i>
          </div>
        )}
        
        {prefix && <div className="n-input__prefix">{prefix}</div>}
        
        <input
          id={uniqueId}
          name={name || uniqueId}
          type={type}
          value={value}
          placeholder={placeholder}
          disabled={disabled}
          readOnly={readOnly}
          required={required}
          className="n-input__inner"
          onChange={onChange}
          {...props}
        />
        
        {suffix && <div className="n-input__suffix">{suffix}</div>}
        
        {suffixIcon && (
          <div className="n-input__suffix-icon">
            <i className={`bx ${suffixIcon}`}></i>
          </div>
        )}
      </div>
      
      {error && <div className="n-input__error">{error}</div>}
      {helpText && !error && <div className="n-input__help">{helpText}</div>}
    </div>
  );
};

Input.propTypes = {
  label: PropTypes.string,
  name: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  placeholder: PropTypes.string,
  type: PropTypes.string,
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  disabled: PropTypes.bool,
  readOnly: PropTypes.bool,
  required: PropTypes.bool,
  invalid: PropTypes.bool,
  prefixIcon: PropTypes.string,
  suffixIcon: PropTypes.string,
  prefix: PropTypes.node,
  suffix: PropTypes.node,
  className: PropTypes.string,
  helpText: PropTypes.string,
  errorText: PropTypes.string,
  onChange: PropTypes.func,
  id: PropTypes.string,
  error: PropTypes.string,
  helperText: PropTypes.string,
};

export default Input; 