import React, { useState } from 'react';
import './SearchBar.css';

const SearchBar = ({ placeholder = 'Rechercher...', onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch && query.trim()) {
      onSearch(query);
    }
  };

  const handleChange = (e) => {
    setQuery(e.target.value);
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit}>
        <div className="search-input-wrapper">
          <i className='bx bx-search'></i>
          <input
            type="text"
            className="search-input"
            placeholder={placeholder}
            value={query}
            onChange={handleChange}
          />
          {query && (
            <button 
              type="button" 
              className="search-clear-btn"
              onClick={() => setQuery('')}
            >
              <i className='bx bx-x'></i>
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default SearchBar; 