import React, { useState } from 'react';
import Button from './Button';
import Input from './Input';

const ContactForm = ({ onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    position: '',
    address: '',
    category: 'client',
    customVariables: {}
  });

  const [profilePhoto, setProfilePhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [newVariable, setNewVariable] = useState({ key: '', value: '' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleVariableChange = (key, value) => {
    setFormData(prev => ({
      ...prev,
      customVariables: {
        ...prev.customVariables,
        [key]: value
      }
    }));
  };

  const handleAddVariable = () => {
    if (newVariable.key.trim()) {
      handleVariableChange(newVariable.key.trim(), newVariable.value);
      setNewVariable({ key: '', value: '' });
    }
  };

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProfilePhoto(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemovePhoto = () => {
    setProfilePhoto(null);
    setPhotoPreview(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // TODO: Implémenter la logique d'ajout de contact
      console.log('Contact data:', formData);
      onClose();
    } catch (error) {
      console.error('Error adding contact:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="contact-form">
      <div className="photo-upload-section">
        <div className="profile-photo-container">
          {photoPreview ? (
            <img 
              src={photoPreview} 
              alt="Profile" 
              className="profile-photo-preview" 
            />
          ) : (
            <div className={`profile-photo-placeholder category-${formData.category}`}>
              {formData.name ? formData.name.charAt(0).toUpperCase() : 'A'}
            </div>
          )}
          <div className="photo-actions">
            <label htmlFor="photo-upload" className="photo-upload-label">
              <i className="bx bx-upload"></i>
              <span>Changer</span>
            </label>
            <input
              id="photo-upload"
              type="file"
              accept="image/*"
              onChange={handlePhotoChange}
              style={{ display: 'none' }}
            />
            {photoPreview && (
              <button 
                type="button" 
                className="photo-remove-button" 
                onClick={handleRemovePhoto}
              >
                <i className="bx bx-trash"></i>
                <span>Supprimer</span>
              </button>
            )}
          </div>
        </div>
      </div>
      
      <div className="form-group">
        <label htmlFor="name">Nom complet</label>
        <Input 
          id="name"
          name="name"
          type="text" 
          placeholder="Nom complet"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="email">Email</label>
        <Input 
          id="email"
          name="email"
          type="email" 
          placeholder="email@example.com"
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="phone">Téléphone</label>
        <Input 
          id="phone"
          name="phone"
          type="tel" 
          placeholder="+33 6 12 34 56 78"
          value={formData.phone}
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label htmlFor="company">Entreprise</label>
        <Input 
          id="company"
          name="company"
          type="text" 
          placeholder="Nom de l'entreprise"
          value={formData.company}
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label htmlFor="position">Poste</label>
        <Input 
          id="position"
          name="position"
          type="text" 
          placeholder="Poste ou fonction"
          value={formData.position}
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label htmlFor="address">Adresse</label>
        <Input 
          id="address"
          name="address"
          type="text" 
          placeholder="Adresse complète"
          value={formData.address}
          onChange={handleChange}
        />
      </div>
      <div className="form-group">
        <label htmlFor="category">Catégorie</label>
        <select 
          id="category"
          name="category"
          className="n-input__inner" 
          value={formData.category}
          onChange={handleChange}
        >
          <option value="client">Client</option>
          <option value="prospect">Prospect</option>
          <option value="fournisseur">Fournisseur</option>
          <option value="partenaire">Partenaire</option>
        </select>
      </div>
      
      <div className="form-section-title">
        <h3>Variables pour les documents</h3>
        <p>Ces variables seront automatiquement générées à partir des détails du contact.</p>
      </div>
      
      <div className="variables-preview">
        <div className="variable-item">
          <span className="variable-key">firstName:</span>
          <span className="variable-value">{formData.name.split(' ')[0] || 'Prénom'}</span>
        </div>
        <div className="variable-item">
          <span className="variable-key">lastName:</span>
          <span className="variable-value">{formData.name.split(' ').slice(1).join(' ') || 'Nom'}</span>
        </div>
        <div className="variable-item">
          <span className="variable-key">companyName:</span>
          <span className="variable-value">{formData.company || 'Nom de l\'entreprise'}</span>
        </div>
        <div className="variable-item">
          <span className="variable-key">email:</span>
          <span className="variable-value">{formData.email || 'email@example.com'}</span>
        </div>
        <div className="variable-item">
          <span className="variable-key">phone:</span>
          <span className="variable-value">{formData.phone || 'Numéro de téléphone'}</span>
        </div>
        <div className="variable-item">
          <span className="variable-key">address:</span>
          <span className="variable-value">{formData.address || 'Adresse complète'}</span>
        </div>
        <div className="variable-item">
          <span className="variable-key">position:</span>
          <span className="variable-value">{formData.position || 'Poste ou fonction'}</span>
        </div>
        {formData.category === 'client' && (
          <div className="variable-item">
            <span className="variable-key">clientNumber:</span>
            <span className="variable-value">Généré automatiquement</span>
          </div>
        )}
        {formData.category === 'prospect' && (
          <div className="variable-item">
            <span className="variable-key">prospectNumber:</span>
            <span className="variable-value">Généré automatiquement</span>
          </div>
        )}
        {formData.category === 'fournisseur' && (
          <div className="variable-item">
            <span className="variable-key">vendorId:</span>
            <span className="variable-value">Généré automatiquement</span>
          </div>
        )}
        {formData.category === 'partenaire' && (
          <div className="variable-item">
            <span className="variable-key">partnerId:</span>
            <span className="variable-value">Généré automatiquement</span>
          </div>
        )}
      </div>
      
      <div className="form-section-title">
        <h3>Variables personnalisées</h3>
        <p>Ajoutez des variables supplémentaires pour vos documents.</p>
      </div>
      
      {Object.entries(formData.customVariables).map(([key, value]) => (
        <div className="form-group custom-variable-row" key={key}>
          <div className="variable-label">{key}</div>
          <Input 
            type="text" 
            value={value}
            onChange={(e) => handleVariableChange(key, e.target.value)}
            placeholder="Valeur"
          />
          <Button 
            type="text" 
            icon="bx bx-trash"
            onClick={() => {
              const newCustomVars = {...formData.customVariables};
              delete newCustomVars[key];
              setFormData({...formData, customVariables: newCustomVars});
            }}
          />
        </div>
      ))}
      
      <div className="form-group custom-variable-row">
        <Input 
          type="text" 
          placeholder="Nom de la variable"
          value={newVariable.key}
          onChange={(e) => setNewVariable({...newVariable, key: e.target.value})}
        />
        <Input 
          type="text" 
          placeholder="Valeur"
          value={newVariable.value}
          onChange={(e) => setNewVariable({...newVariable, value: e.target.value})}
        />
        <Button 
          type="text" 
          icon="bx bx-plus-circle"
          onClick={handleAddVariable}
        />
      </div>
      
      <div className="form-actions">
        <Button type="text" onClick={onClose}>
          Annuler
        </Button>
        <Button type="primary" htmlType="submit">
          Ajouter
        </Button>
      </div>
    </form>
  );
};

export default ContactForm; 