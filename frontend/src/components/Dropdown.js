import React, { useState, useRef, useEffect } from 'react';
import '../styles/components.css';

const Dropdown = ({ 
  options, 
  value, 
  onChange, 
  placeholder = 'Sélectionner', 
  icon,
  disabled = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  
  const selectedOption = options.find(option => option.value === value);
  
  const toggleDropdown = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };
  
  const handleOptionClick = (optionValue) => {
    onChange(optionValue);
    setIsOpen(false);
  };
  
  // Ferme le dropdown si l'utilisateur clique en dehors
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  return (
    <div className={`dropdown ${disabled ? 'disabled' : ''}`} ref={dropdownRef}>
      <div className="dropdown-header" onClick={toggleDropdown}>
        {icon && <i className={icon}></i>}
        <span className="dropdown-selected">
          {selectedOption ? selectedOption.label : placeholder}
        </span>
        <i className={`fas fa-chevron-down dropdown-arrow ${isOpen ? 'open' : ''}`}></i>
      </div>
      
      {isOpen && (
        <div className="dropdown-options">
          {options.map((option) => (
            <div
              key={option.value}
              className={`dropdown-option ${option.value === value ? 'selected' : ''}`}
              onClick={() => handleOptionClick(option.value)}
            >
              {option.icon && <i className={option.icon}></i>}
              {option.label}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dropdown; 