import React from 'react';
import './Input.css';

const Input = ({
  id,
  type = 'text',
  placeholder,
  value,
  onChange,
  prefixIcon,
  suffixIcon,
  error,
  className,
  label,
  ...props
}) => {
  const inputClass = `input-wrapper ${error ? 'error' : ''} ${className || ''}`;

  return (
    <div className={inputClass}>
      {prefixIcon && (
        <i className={`bx ${prefixIcon}`}></i>
      )}
      <input
        id={id}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        {...props}
      />
      {suffixIcon && (
        <i className={`bx ${suffixIcon}`}></i>
      )}
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default Input; 