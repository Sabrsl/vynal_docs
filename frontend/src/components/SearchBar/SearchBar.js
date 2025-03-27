import React, { useState, useEffect, useRef } from 'react';
import { useDebounce } from '../../hooks/useDebounce';
import './SearchBar.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const SearchBar = ({ onSearch, placeholder = 'Rechercher un document...' }) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [error, setError] = useState(null);
  const debouncedQuery = useDebounce(query, 300);
  const searchRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const searchDocuments = async () => {
      if (!debouncedQuery.trim()) {
        setResults([]);
        setError(null);
        return;
      }

      setIsLoading(true);
      setError(null);
      
      try {
        const url = `${API_URL}/api/documents?search=${encodeURIComponent(debouncedQuery)}`;
        console.log('Tentative de connexion à:', url);
        
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          credentials: 'include'
        }).catch(err => {
          console.error('Erreur de connexion:', err);
          throw new Error('Impossible de se connecter au serveur. Vérifiez que le serveur est en cours d\'exécution.');
        });
        
        console.log('Statut de la réponse:', response.status);
        
        if (!response.ok) {
          if (response.status === 0) {
            throw new Error('Impossible de se connecter au serveur. Vérifiez que le serveur est en cours d\'exécution.');
          }
          const errorData = await response.json().catch(() => ({ error: 'Erreur serveur' }));
          throw new Error(errorData.error || 'Erreur lors de la recherche');
        }
        
        const data = await response.json();
        console.log('Résultats reçus:', data);
        
        if (!Array.isArray(data.documents)) {
          throw new Error('Format de réponse invalide');
        }
        
        setResults(data.documents);
        setShowResults(true);
      } catch (error) {
        console.error('Erreur détaillée:', error);
        setError(error.message);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    };

    searchDocuments();
  }, [debouncedQuery]);

  const handleInputChange = (e) => {
    const value = e.target.value;
    console.log('Valeur saisie:', value);
    setQuery(value);
    setShowResults(true);
    setError(null);
  };

  const handleResultClick = (document) => {
    console.log('Document sélectionné:', document);
    onSearch(document);
    setShowResults(false);
    setQuery('');
  };

  return (
    <div className="search-container" ref={searchRef}>
      <div className="search-input-wrapper">
        <i className="bx bx-search search-icon"></i>
        <input
          type="text"
          className="search-input"
          placeholder={placeholder}
          value={query}
          onChange={handleInputChange}
          onFocus={() => setShowResults(true)}
        />
        {isLoading && (
          <div className="search-loading">
            <div className="spinner"></div>
          </div>
        )}
      </div>

      {showResults && (query || results.length > 0) && (
        <div className="search-results">
          {error ? (
            <div className="search-error">
              <i className="bx bx-error-circle"></i>
              <p>{error}</p>
              <p className="error-details">Vérifiez que le serveur backend est en cours d'exécution sur le port 5000</p>
            </div>
          ) : results.length === 0 ? (
            <div className="no-results">
              <i className="bx bx-search"></i>
              <p>Aucun document trouvé</p>
            </div>
          ) : (
            <ul className="results-list">
              {results.map((doc) => (
                <li
                  key={doc._id}
                  className="result-item"
                  onClick={() => handleResultClick(doc)}
                >
                  <div className="result-icon">
                    <i className={`bx ${getDocumentIcon(doc.type)}`}></i>
                  </div>
                  <div className="result-content">
                    <h4>{doc.title}</h4>
                    <p>{doc.description || 'Aucune description'}</p>
                    <div className="result-meta">
                      <span className="result-type">{doc.type}</span>
                      <span className="result-date">
                        {new Date(doc.createdAt).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

const getDocumentIcon = (type) => {
  switch (type?.toLowerCase()) {
    case 'pdf':
      return 'bxs-file-pdf';
    case 'doc':
    case 'docx':
      return 'bxs-file-doc';
    case 'xls':
    case 'xlsx':
      return 'bxs-spreadsheet';
    case 'ppt':
    case 'pptx':
      return 'bxs-slideshow';
    default:
      return 'bxs-file';
  }
};

export default SearchBar; 