import React from 'react';
import '../styles/components.css';

const SearchBox = ({ 
  value, 
  onChange, 
  placeholder = 'Rechercher...', 
  icon = 'fas fa-search',
  onClear,
  disabled = false
}) => {
  const handleClear = () => {
    if (onClear) {
      onClear();
    } else if (onChange) {
      // Si onClear n'est pas fourni mais onChange l'est, simuler une suppression
      onChange({ target: { value: '' } });
    }
  };

  return (
    <div className={`search-box ${disabled ? 'disabled' : ''}`}>
      {icon && <i className={`search-box-icon ${icon}`}></i>}
      <input
        type="text"
        className="search-box-input"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
      />
      {value && (
        <button 
          className="search-box-clear" 
          onClick={handleClear}
          type="button"
          disabled={disabled}
        >
          <i className="fas fa-times"></i>
        </button>
      )}
    </div>
  );
};

export default SearchBox; 