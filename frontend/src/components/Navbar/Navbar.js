import React from 'react';
import './Navbar.css';

const Navbar = ({ children }) => {
  return (
    <header className="navbar">
      {children}
    </header>
  );
};

export default Navbar; 