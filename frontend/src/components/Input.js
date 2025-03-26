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
  
  const styles = {
    container: {
      display: 'flex',
      flexDirection: 'column',
      marginBottom: '16px',
      width: '100%',
    },
    label: {
      fontSize: '14px',
      fontWeight: '500',
      marginBottom: '8px',
      color: '#333',
    },
    inputWrapper: {
      position: 'relative',
      display: 'flex',
      alignItems: 'center',
      width: '100%',
    },
    input: {
      width: '100%',
      padding: prefixIcon ? '8px 16px 8px 40px' : '8px 16px',
      fontSize: '14px',
      border: `1px solid ${error ? '#ff4d4f' : '#ddd'}`,
      borderRadius: '4px',
      backgroundColor: disabled ? '#f5f5f5' : 'white',
      transition: 'border-color 0.2s ease',
      outline: 'none',
    },
    icon: {
      position: 'absolute',
      left: '12px',
      fontSize: '18px',
      color: '#999',
    },
    error: {
      color: '#ff4d4f',
      fontSize: '12px',
      marginTop: '4px',
    },
    helperText: {
      color: '#666',
      fontSize: '12px',
      marginTop: '4px',
    }
  };
  
  // Styles pseudo-classes
  const hoverStyle = !disabled && !readOnly ? {
    ':hover': {
      borderColor: '#6933FF',
    }
  } : {};
  
  const focusStyle = !disabled && !readOnly ? {
    ':focus': {
      borderColor: '#6933FF',
      boxShadow: '0 0 0 2px rgba(105, 51, 255, 0.1)',
    }
  } : {};
  
  const inputStyles = {
    ...styles.input,
    ...hoverStyle,
    ...focusStyle,
  };

  const inputClass = `n-input n-input--${size} ${
    invalid ? 'n-input--invalid' : ''
  } ${
    disabled ? 'n-input--disabled' : ''
  } ${
    readOnly ? 'n-input--readonly' : ''
  } ${
    prefixIcon ? 'n-input--prefix-icon' : ''
  } ${
    suffixIcon ? 'n-input--suffix-icon' : ''
  } ${className}`;

  return (
    <div style={styles.container} className={`input-field ${inputClass}`}>
      {label && (
        <label htmlFor={uniqueId} style={styles.label}>
          {label}
          {required && <span style={{ color: '#ff4d4f' }}> *</span>}
        </label>
      )}
      
      <div style={styles.inputWrapper}>
        {prefixIcon && <i className={`bx ${prefixIcon}`} style={styles.icon}></i>}
        
        <input
          id={uniqueId}
          name={name || uniqueId}
          type={type}
          value={value}
          placeholder={placeholder}
          disabled={disabled}
          readOnly={readOnly}
          required={required}
          style={inputStyles}
          onChange={onChange}
          {...props}
        />
      </div>
      
      {error && <p style={styles.error}>{error}</p>}
      {helpText && !error && <p style={styles.helperText}>{helpText}</p>}
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