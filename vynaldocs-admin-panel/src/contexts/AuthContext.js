import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

// Create the auth context
const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Check if we have a token in local storage on initial load
  useEffect(() => {
    const token = localStorage.getItem('adminToken');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        
        // Check if the token is expired
        if (decoded.exp * 1000 < Date.now()) {
          localStorage.removeItem('adminToken');
          setCurrentUser(null);
        } else if (decoded.role === 'admin') {
          // Only set the user if they have admin role
          setCurrentUser(decoded);
          // Set the default authorization header for all future requests
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
          // User doesn't have admin role
          localStorage.removeItem('adminToken');
          setCurrentUser(null);
        }
      } catch (error) {
        localStorage.removeItem('adminToken');
        setCurrentUser(null);
      }
    }
    setLoading(false);
  }, []);

  // Login function
  const login = async (email, password) => {
    try {
      setError('');
      setLoading(true);
      const response = await axios.post(process.env.REACT_APP_API_URL + '/api/auth/login', {
        email,
        password
      });

      const { token, user } = response.data;
      
      // Verify the user has admin role
      if (user.role !== 'admin') {
        setError('Accès non autorisé. Droits administrateur requis.');
        setLoading(false);
        return false;
      }
      
      localStorage.setItem('adminToken', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setCurrentUser(user);
      setLoading(false);
      return true;
    } catch (error) {
      setError(
        error.response?.data?.error || 
        'Échec de connexion. Vérifiez vos identifiants.'
      );
      setLoading(false);
      return false;
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('adminToken');
    delete axios.defaults.headers.common['Authorization'];
    setCurrentUser(null);
  };

  const value = {
    currentUser,
    loading,
    error,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 