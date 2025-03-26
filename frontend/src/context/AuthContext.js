import React, { createContext, useContext, useState, useEffect } from 'react';

// Création du contexte d'authentification
const AuthContext = createContext();

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null
};

// Provider component
export const AuthProvider = ({ children }) => {
  const [authState, setAuthState] = useState(initialState);

  // Vérifier si l'utilisateur est déjà connecté (au chargement)
  useEffect(() => {
    const checkLoggedIn = async () => {
      try {
        // Vérifier le localStorage pour un token
        const token = localStorage.getItem('authToken');
        
        if (token) {
          // Simuler la vérification du token et récupération des informations utilisateur
          // Dans une application réelle, vous feriez une requête API pour valider le token
          await new Promise(resolve => setTimeout(resolve, 500));
          
          const userData = {
            id: 1,
            name: 'Jean Dupont',
            email: 'jean.dupont@example.com',
            role: 'admin',
            avatar: '/avatar.png'
          };
          
          setAuthState({
            user: userData,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
        } else {
          setAuthState({
            ...initialState,
            isLoading: false
          });
        }
      } catch (error) {
        setAuthState({
          ...initialState,
          isLoading: false,
          error: 'Erreur lors de la vérification de l\'authentification'
        });
      }
    };
    
    checkLoggedIn();
  }, []);
  
  // Fonction de connexion
  const login = async (email, password) => {
    setAuthState({
      ...authState,
      isLoading: true,
      error: null
    });
    
    try {
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Vérification simulée des identifiants
      if (email === 'demo@example.com' && password === 'password') {
        const userData = {
          id: 1,
          name: 'Jean Dupont',
          email: email,
          role: 'admin',
          avatar: '/avatar.png'
        };
        
        // Stocker le token dans localStorage
        localStorage.setItem('authToken', 'fake-jwt-token-12345');
        
        setAuthState({
          user: userData,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });
        
        return true;
      } else {
        throw new Error('Identifiants invalides');
      }
    } catch (error) {
      setAuthState({
        ...authState,
        isLoading: false,
        error: error.message || 'Erreur lors de la connexion'
      });
      return false;
    }
  };
  
  // Fonction de déconnexion
  const logout = () => {
    // Supprimer le token du localStorage
    localStorage.removeItem('authToken');
    
    setAuthState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null
    });
  };
  
  // Fonction d'inscription
  const register = async (name, email, password) => {
    setAuthState({
      ...authState,
      isLoading: true,
      error: null
    });
    
    try {
      // Simuler un appel API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const userData = {
        id: Date.now(),
        name: name,
        email: email,
        role: 'user',
        avatar: '/avatar.png'
      };
      
      // Stocker le token dans localStorage
      localStorage.setItem('authToken', 'fake-jwt-token-register-12345');
      
      setAuthState({
        user: userData,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });
      
      return true;
    } catch (error) {
      setAuthState({
        ...authState,
        isLoading: false,
        error: error.message || 'Erreur lors de l\'inscription'
      });
      return false;
    }
  };
  
  // Valeur exposée par le contexte
  const value = {
    ...authState,
    login,
    logout,
    register
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook personnalisé pour utiliser le contexte
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth doit être utilisé à l\'intérieur d\'un AuthProvider');
  }
  return context;
}; 