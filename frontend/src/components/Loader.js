import React from 'react';
import './Loader.css';

const Loader = ({ size = 'medium', text = 'Chargement...' }) => {
  const sizeClass = `loader-${size}`;
  
  return (
    <div className="loader-container">
      <div className={`loader ${sizeClass}`}>
        <div className="loader-spinner"></div>
      </div>
      {text && <div className="loader-text">{text}</div>}
    </div>
  );
};

export default Loader; 