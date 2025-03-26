import React from 'react';
import './Navbar.css';
import { useAuth } from '../../context/AuthContext';

const Navbar = ({ children }) => {
  const { isAuthenticated, user } = useAuth();

  return (
    <header className="navbar">
      {children}
    </header>
  );
};

export default Navbar; 