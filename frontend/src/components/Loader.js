import React from 'react';
import '../styles/components/Loader.css';

const Loader = ({ size = 'medium', fullPage = false, text = 'Chargement...' }) => {
  const sizeClass = `loader--${size}`;
  const containerClass = fullPage ? 'loader-container fullpage' : 'loader-container';
  
  return (
    <div className={containerClass}>
      <div className={`loader ${sizeClass}`}>
        <i className="bx bx-loader-alt bx-spin"></i>
        {text && <span className="loader-text">{text}</span>}
      </div>
    </div>
  );
};

export default Loader; 