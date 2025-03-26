import React, { useState, useEffect } from 'react';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import '../styles/base.css';
import './ContactsPage.css';
import avatar from '../assets/avatar.svg';

/**
 * Page de gestion des contacts avec le design n8n pour l'automatisation des documents
 */
const ContactsPage = () => {
  // État pour les contacts
  const [contacts, setContacts] = useState([]);
  const [filteredContacts, setFilteredContacts] = useState([]);
  const [loading, setLoading] = useState(true);

  // États pour les filtres
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [viewMode, setViewMode] = useState('table'); // 'table' ou 'grid'
  const [showVariables, setShowVariables] = useState(false); // Variables masquées par défaut

  // États pour les modales
  const [addContactModal, setAddContactModal] = useState(false);
  const [editContactModal, setEditContactModal] = useState(false);
  const [deleteContactModal, setDeleteContactModal] = useState(false);
  const [currentContact, setCurrentContact] = useState(null);
  const [generateDocModal, setGenerateDocModal] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  // État local pour le formulaire
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
  
  // État pour la photo de profil
  const [profilePhoto, setProfilePhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);

  // Réinitialiser le formulaire lorsque currentContact change
  useEffect(() => {
    if (currentContact) {
      setFormData({
        name: currentContact.name || '',
        email: currentContact.email || '',
        phone: currentContact.phone || '',
        company: currentContact.company || '',
        position: currentContact.position || '',
        address: currentContact.address || '',
        category: currentContact.category || 'client',
        customVariables: currentContact.variables || {}
      });
      
      // Si le contact a une photo, l'afficher en prévisualisation
      if (currentContact.photo) {
        setPhotoPreview(currentContact.photo);
      } else {
        setPhotoPreview(null);
      }
      setProfilePhoto(null);
    } else {
      setFormData({
        name: '',
        email: '',
        phone: '',
        company: '',
        position: '',
        address: '',
        category: 'client',
        customVariables: {}
      });
      setPhotoPreview(null);
      setProfilePhoto(null);
    }
  }, [currentContact]);

  // Gérer les changements dans le formulaire
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Gérer les changements dans les variables personnalisées
  const handleVariableChange = (key, value) => {
    setFormData(prev => ({
      ...prev,
      customVariables: {
        ...prev.customVariables,
        [key]: value
      }
    }));
  };

  // Ajouter une nouvelle variable personnalisée
  const [newVariable, setNewVariable] = useState({ key: '', value: '' });
  
  const handleAddVariable = () => {
    if (newVariable.key.trim()) {
      handleVariableChange(newVariable.key.trim(), newVariable.value);
      setNewVariable({ key: '', value: '' });
    }
  };

  // Gérer le changement de photo de profil
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

  // Supprimer la photo de profil
  const handleRemovePhoto = () => {
    setProfilePhoto(null);
    setPhotoPreview(null);
  };

  // Données contacts fictives
  const mockContacts = [
    {
      id: 1,
      email: 'john.doe@company.com',
      name: 'John Doe',
      category: 'client',
      phone: '+33 6 12 34 56 78',
      company: 'Acme Inc.',
      position: 'CEO',
      address: '123 Avenue de la République, 75011 Paris',
      photo: 'https://randomuser.me/api/portraits/men/1.jpg',
      variables: {
        firstName: 'John',
        lastName: 'Doe',
        companyName: 'Acme Inc.',
        taxId: 'FR123456789',
        clientNumber: 'CLI-001'
      },
      lastUpdated: '2025-03-25T10:30:00',
      created: '2024-10-12T08:45:00',
      documentsGenerated: 12
    },
    {
      id: 2,
      email: 'alice.smith@company.com',
      name: 'Alice Smith',
      category: 'prospect',
      phone: '+33 6 23 45 67 89',
      company: 'Tech Solutions',
      position: 'CTO',
      address: '45 Rue du Commerce, 69002 Lyon',
      photo: 'https://randomuser.me/api/portraits/women/2.jpg',
      variables: {
        firstName: 'Alice',
        lastName: 'Smith',
        companyName: 'Tech Solutions',
        taxId: 'FR987654321',
        clientNumber: 'PRO-002'
      },
      lastUpdated: '2025-03-24T14:15:00',
      created: '2024-10-15T09:20:00',
      documentsGenerated: 3
    },
    {
      id: 3,
      email: 'robert.johnson@company.com',
      name: 'Robert Johnson',
      category: 'fournisseur',
      phone: '+33 7 34 56 78 90',
      company: 'Supply Co',
      position: 'Directeur commercial',
      address: '78 Boulevard Haussmann, 75008 Paris',
      variables: {
        firstName: 'Robert',
        lastName: 'Johnson',
        companyName: 'Supply Co',
        taxId: 'FR456789123',
        vendorId: 'VEN-003'
      },
      lastUpdated: '2025-03-10T11:45:00',
      created: '2024-11-05T16:30:00',
      documentsGenerated: 8
    },
    {
      id: 4,
      email: 'emma.wilson@company.com',
      name: 'Emma Wilson',
      category: 'client',
      phone: '+33 6 45 67 89 01',
      company: 'Wilson & Co',
      position: 'Directrice financière',
      address: '12 Rue de la Paix, 44000 Nantes',
      photo: 'https://randomuser.me/api/portraits/women/3.jpg',
      variables: {
        firstName: 'Emma',
        lastName: 'Wilson',
        companyName: 'Wilson & Co',
        taxId: 'FR789123456',
        clientNumber: 'CLI-004'
      },
      lastUpdated: '2025-03-26T08:20:00',
      created: '2024-09-28T10:15:00',
      documentsGenerated: 15
    },
    {
      id: 5,
      email: 'michael.brown@company.com',
      name: 'Michael Brown',
      category: 'partenaire',
      phone: '+33 7 56 78 90 12',
      company: 'Brown Partners',
      position: 'Directeur marketing',
      address: '34 Avenue des Champs-Élysées, 75008 Paris',
      variables: {
        firstName: 'Michael',
        lastName: 'Brown',
        companyName: 'Brown Partners',
        taxId: 'FR321654987',
        partnerId: 'PAR-005'
      },
      lastUpdated: '2025-03-22T16:40:00',
      created: '2024-10-30T13:45:00',
      documentsGenerated: 7
    },
    {
      id: 6,
      email: 'sophia.taylor@company.com',
      name: 'Sophia Taylor',
      category: 'prospect',
      phone: '+33 6 67 89 01 23',
      company: 'Taylor Group',
      position: 'Responsable RH',
      address: '56 Rue de la Liberté, 33000 Bordeaux',
      photo: 'https://randomuser.me/api/portraits/women/4.jpg',
      variables: {
        firstName: 'Sophia',
        lastName: 'Taylor',
        companyName: 'Taylor Group',
        taxId: 'FR654987321',
        clientNumber: 'PRO-006'
      },
      lastUpdated: '2025-03-20T09:30:00',
      created: '2024-12-05T11:20:00',
      documentsGenerated: 0
    }
  ];

  // Charger les contacts au chargement du composant
  useEffect(() => {
    const loadContacts = async () => {
      // Simuler une requête API
      setTimeout(() => {
        setContacts(mockContacts);
        setFilteredContacts(mockContacts);
        setLoading(false);
      }, 1000);
    };

    loadContacts();
  }, []);

  // Filtrer et trier les contacts
  useEffect(() => {
    let result = [...contacts];

    // Filtrer par recherche
    if (searchQuery) {
      const lowerCaseQuery = searchQuery.toLowerCase();
      result = result.filter(
        contact => 
          contact.name.toLowerCase().includes(lowerCaseQuery) || 
          contact.email.toLowerCase().includes(lowerCaseQuery) ||
          contact.company.toLowerCase().includes(lowerCaseQuery)
      );
    }

    // Filtrer par catégorie
    if (categoryFilter !== 'all') {
      result = result.filter(contact => contact.category === categoryFilter);
    }

    // Trier
    result.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];

      // Si c'est une date, convertir en timestamps
      if (sortBy === 'lastUpdated' || sortBy === 'created') {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredContacts(result);
  }, [contacts, searchQuery, categoryFilter, sortBy, sortOrder]);

  // Fonctions utilitaires
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const getInitials = (name) => {
    if (!name) return 'NN';
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .substring(0, 2)
      .toUpperCase();
  };

  // Gestionnaires d'événements
  const handleAddContact = () => {
    // Initialiser un nouvel objet contact avec des valeurs par défaut
    setCurrentContact({
      name: '',
      email: '',
      phone: '',
      company: '',
      position: '',
      address: '',
      category: 'client',
      variables: {}
    });
    setAddContactModal(true);
  };

  const handleEditContact = (contact) => {
    setCurrentContact(contact);
    setEditContactModal(true);
  };

  const handleDeleteContact = (contact) => {
    setCurrentContact(contact);
    setDeleteContactModal(true);
  };

  const handleGenerateDocument = (contact) => {
    setCurrentContact(contact);
    setGenerateDocModal(true);
  };

  const handleTemplateSelect = (templateId) => {
    setSelectedTemplate(templateId);
    // En production, ici nous naviguerions vers l'éditeur de document avec le template et les variables du contact
    console.log(`Génération d'un document avec le template ${templateId} et les variables du contact ${currentContact.id}`);
    setGenerateDocModal(false);
    setCurrentContact(null);
    setSelectedTemplate(null);
  };

  const handleSaveContact = (e) => {
    e.preventDefault();
    
    // Diviser le nom en prénom et nom de famille
    const nameParts = formData.name.trim().split(' ');
    const firstName = nameParts[0] || '';
    const lastName = nameParts.slice(1).join(' ') || '';
    
    // Créer les variables automatiquement à partir des détails du contact
    const generatedVariables = {
      firstName,
      lastName,
      companyName: formData.company,
      email: formData.email,
      phone: formData.phone,
      position: formData.position,
      address: formData.address,
      // Ajouter un ID en fonction de la catégorie
      ...(formData.category === 'client' && { clientNumber: `CLI-${Math.floor(Math.random()*1000).toString().padStart(3, '0')}` }),
      ...(formData.category === 'prospect' && { prospectNumber: `PRO-${Math.floor(Math.random()*1000).toString().padStart(3, '0')}` }),
      ...(formData.category === 'fournisseur' && { vendorId: `VEN-${Math.floor(Math.random()*1000).toString().padStart(3, '0')}` }),
      ...(formData.category === 'partenaire' && { partnerId: `PAR-${Math.floor(Math.random()*1000).toString().padStart(3, '0')}` }),
      ...formData.customVariables
    };
    
    const contactData = {
      name: formData.name,
      email: formData.email,
      phone: formData.phone,
      company: formData.company,
      position: formData.position,
      address: formData.address,
      category: formData.category,
      variables: generatedVariables,
      photo: photoPreview
    };
    
    // Ici, vous implémenteriez la logique pour envoyer les données à l'API
    if (currentContact && currentContact.id) {
      // Édition
      const updatedContacts = contacts.map(contact => 
        contact.id === currentContact.id ? { ...contact, ...contactData } : contact
      );
      setContacts(updatedContacts);
    } else {
      // Ajout
      const newContact = {
        id: contacts.length + 1,
        ...contactData,
        created: new Date().toISOString(),
        lastUpdated: new Date().toISOString(),
        documentsGenerated: 0
      };
      setContacts([...contacts, newContact]);
    }

    // Fermer les modales
    setAddContactModal(false);
    setEditContactModal(false);
    setCurrentContact(null);
  };

  const handleConfirmDelete = () => {
    if (currentContact) {
      const updatedContacts = contacts.filter(contact => contact.id !== currentContact.id);
      setContacts(updatedContacts);
      setDeleteContactModal(false);
      setCurrentContact(null);
    }
  };

  const handleViewModeChange = (mode) => {
    setViewMode(mode);
    // Si on passe à la vue grille, on s'assure que les variables sont masquées par défaut
    if (mode === 'grid') {
      setShowVariables(false);
    }
  };

  // Render des modales
  const renderAddEditContactModal = () => {
    const isEdit = !!currentContact?.id;
    
    return (
      <div className="modal-overlay">
        <div className="modal">
          <div className="modal-header">
            <h2>{isEdit ? 'Modifier le contact' : 'Ajouter un contact'}</h2>
            <button className="close-button" onClick={() => {
              setAddContactModal(false);
              setEditContactModal(false);
              setCurrentContact(null);
            }}>
              <i className="bx bx-x"></i>
            </button>
          </div>
          <div className="modal-body">
            <form onSubmit={handleSaveContact}>
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
                      {getInitials(formData.name || 'Ajouter Photo')}
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
                  onChange={handleInputChange}
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
                  onChange={handleInputChange}
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
                  onChange={handleInputChange}
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
                  onChange={handleInputChange}
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
                  onChange={handleInputChange}
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
                  onChange={handleInputChange}
                />
              </div>
              <div className="form-group">
                <label htmlFor="category">Catégorie</label>
                <select 
                  id="category"
                  name="category"
                  className="n-input__inner" 
                  value={formData.category}
                  onChange={handleInputChange}
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
              
              <div className="modal-footer">
                <Button 
                  type="text" 
                  onClick={() => {
                    setAddContactModal(false);
                    setEditContactModal(false);
                    setCurrentContact(null);
                  }}
                >
                  Annuler
                </Button>
                <Button 
                  type="primary"
                  htmlType="submit"
                >
                  {isEdit ? 'Enregistrer' : 'Ajouter'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  const renderDeleteContactModal = () => {
    return (
      <div className="modal-overlay">
        <div className="modal confirm-modal">
          <div className="modal-header">
            <h2>Confirmer la suppression</h2>
            <button className="close-button" onClick={() => {
              setDeleteContactModal(false);
              setCurrentContact(null);
            }}>
              <i className="bx bx-x"></i>
            </button>
          </div>
          <div className="modal-body">
            <div className="confirm-message">
              <i className="bx bx-error-circle"></i>
              <p>
                Êtes-vous sûr de vouloir supprimer le contact 
                <strong> {currentContact?.name}</strong> ? <br />
                Cette action est irréversible.
              </p>
            </div>
          </div>
          <div className="modal-footer">
            <Button 
              type="text" 
              onClick={() => {
                setDeleteContactModal(false);
                setCurrentContact(null);
              }}
            >
              Annuler
            </Button>
            <Button 
              type="danger" 
              onClick={handleConfirmDelete}
            >
              Supprimer
            </Button>
          </div>
        </div>
      </div>
    );
  };

  const renderGenerateDocModal = () => {
    return (
      <div className="modal-overlay">
        <div className="modal">
          <div className="modal-header">
            <h2>Générer un document pour {currentContact?.name}</h2>
            <button className="close-button" onClick={() => {
              setGenerateDocModal(false);
              setCurrentContact(null);
              setSelectedTemplate(null);
            }}>
              <i className="bx bx-x"></i>
            </button>
          </div>
          <div className="modal-body">
            <p className="template-info">
              Sélectionnez un modèle pour créer un document avec les variables de ce contact :
            </p>
            
            <div className="template-list">
              {/* Ici, nous utiliserions des données réelles de templates */}
              <div 
                className={`template-item ${selectedTemplate === 'template1' ? 'selected' : ''}`}
                onClick={() => setSelectedTemplate('template1')}
              >
                <i className="bx bxs-file-doc"></i>
                <span>Contrat de prestation</span>
              </div>
              <div 
                className={`template-item ${selectedTemplate === 'template2' ? 'selected' : ''}`}
                onClick={() => setSelectedTemplate('template2')}
              >
                <i className="bx bxs-file-doc"></i>
                <span>Facture standard</span>
              </div>
              <div 
                className={`template-item ${selectedTemplate === 'template3' ? 'selected' : ''}`}
                onClick={() => setSelectedTemplate('template3')}
              >
                <i className="bx bxs-file-doc"></i>
                <span>Devis détaillé</span>
              </div>
              <div 
                className={`template-item ${selectedTemplate === 'template4' ? 'selected' : ''}`}
                onClick={() => setSelectedTemplate('template4')}
              >
                <i className="bx bxs-file-doc"></i>
                <span>Lettre de relance</span>
              </div>
            </div>
            
            <div className="variables-preview">
              <h4>Variables qui seront utilisées :</h4>
              {currentContact && currentContact.variables && Object.entries(currentContact.variables).map(([key, value]) => (
                <div className="variable-item" key={key}>
                  <span className="variable-key">{key}:</span>
                  <span className="variable-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="modal-footer">
            <Button 
              type="text" 
              onClick={() => {
                setGenerateDocModal(false);
                setCurrentContact(null);
                setSelectedTemplate(null);
              }}
            >
              Annuler
            </Button>
            <Button 
              type="primary"
              disabled={!selectedTemplate}
              onClick={() => handleTemplateSelect(selectedTemplate)}
            >
              Générer le document
            </Button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="contacts-page">
      <div className="page-header">
        <h1>Contacts pour l'automatisation</h1>
        <div className="page-actions">
          <Button
            type="primary"
            icon="bx bx-plus"
            onClick={handleAddContact}
          >
            Ajouter un contact
          </Button>
        </div>
      </div>

      <Card className="contacts-filters">
        <div className="filter-group">
          <Input
            prefixIcon="bx bx-search"
            placeholder="Rechercher un contact..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="filter-group">
          <label>Catégorie :</label>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="all">Toutes les catégories</option>
            <option value="client">Clients</option>
            <option value="prospect">Prospects</option>
            <option value="fournisseur">Fournisseurs</option>
            <option value="partenaire">Partenaires</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Trier par :</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="name">Nom</option>
            <option value="company">Entreprise</option>
            <option value="lastUpdated">Dernière mise à jour</option>
            <option value="created">Date de création</option>
            <option value="documentsGenerated">Documents générés</option>
          </select>
        </div>
        <div className="filter-group">
          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
          >
            <option value="asc">Croissant</option>
            <option value="desc">Décroissant</option>
          </select>
        </div>
        <div className="view-toggle">
          {viewMode === 'grid' && (
            <Button
              icon={`bx ${showVariables ? 'bx-hide' : 'bx-show'}`}
              type="text"
              onClick={() => setShowVariables(!showVariables)}
              title={showVariables ? "Masquer les variables" : "Afficher les variables"}
            >
              {showVariables ? "Masquer variables" : "Afficher variables"}
            </Button>
          )}
          <Button
            icon={`bx bx-list-ul ${viewMode === 'table' ? 'active' : ''}`}
            type={viewMode === 'table' ? 'primary' : 'text'}
            onClick={() => handleViewModeChange('table')}
          />
          <Button
            icon={`bx bx-grid-alt ${viewMode === 'grid' ? 'active' : ''}`}
            type={viewMode === 'grid' ? 'primary' : 'text'}
            onClick={() => handleViewModeChange('grid')}
          />
        </div>
      </Card>

      {loading ? (
        <Card className="contacts-loading-card">
          <div className="loading-spinner">
            <i className="bx bx-loader-alt bx-spin"></i>
            <p>Chargement des contacts...</p>
          </div>
        </Card>
      ) : (
        <>
          {viewMode === 'table' ? (
            <Card className="contacts-table-card">
              <table className="contacts-table">
                <thead>
                  <tr>
                    <th>Contact</th>
                    <th>Catégorie</th>
                    <th>Entreprise</th>
                    <th>Téléphone</th>
                    <th>Documents</th>
                    <th>Dernière mise à jour</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredContacts.length > 0 ? (
                    filteredContacts.map((contact) => (
                      <tr key={contact.id}>
                        <td>
                          <div className="contact-name-cell">
                            {contact.photo ? (
                              <img src={contact.photo} alt={contact.name} className="contact-avatar" />
                            ) : (
                              <div className={`contact-avatar-initials category-${contact.category}`}>
                                {getInitials(contact.name)}
                              </div>
                            )}
                            <div>
                              <div className="font-medium">{contact.name}</div>
                              <div className="text-lighter text-xs">{contact.email}</div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`category-badge category-${contact.category}`}>
                            {contact.category === 'client' && 'Client'}
                            {contact.category === 'prospect' && 'Prospect'}
                            {contact.category === 'fournisseur' && 'Fournisseur'}
                            {contact.category === 'partenaire' && 'Partenaire'}
                          </span>
                        </td>
                        <td>{contact.company}</td>
                        <td>{contact.phone}</td>
                        <td>{contact.documentsGenerated}</td>
                        <td>{formatDate(contact.lastUpdated)}</td>
                        <td className="actions-cell">
                          <Button
                            icon="bx bx-edit-alt"
                            type="text"
                            onClick={() => handleEditContact(contact)}
                          />
                          <Button
                            icon="bx bx-trash"
                            type="text"
                            className="danger"
                            onClick={() => handleDeleteContact(contact)}
                          />
                          <Button
                            icon="bx bx-file-blank"
                            type="text"
                            className="primary"
                            onClick={() => handleGenerateDocument(contact)}
                            title="Générer un document"
                          />
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7">
                        <div className="no-results">
                          <i className="bx bx-search-alt"></i>
                          <p>Aucun contact trouvé</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </Card>
          ) : (
            <div className="contacts-grid">
              {filteredContacts.length > 0 ? (
                filteredContacts.map((contact) => (
                  <Card key={contact.id} className="contact-card">
                    <div className="contact-card-header">
                      {contact.photo ? (
                        <img src={contact.photo} alt={contact.name} className="contact-card-photo" />
                      ) : (
                        <div className={`contact-avatar-initials category-${contact.category}`}>
                          {getInitials(contact.name)}
                        </div>
                      )}
                      <div className="contact-card-name">
                        <h3>{contact.name}</h3>
                        <p>{contact.email}</p>
                      </div>
                      <div className="contact-card-badges">
                        <span className={`category-badge category-${contact.category}`}>
                          {contact.category === 'client' && 'Client'}
                          {contact.category === 'prospect' && 'Prospect'}
                          {contact.category === 'fournisseur' && 'Fournisseur'}
                          {contact.category === 'partenaire' && 'Partenaire'}
                        </span>
                      </div>
                    </div>
                    <div className="contact-card-body">
                      <div className="contact-info-grid">
                        <div className="contact-card-stat">
                          <i className="bx bx-building"></i>
                          <div>
                            <span>Entreprise</span>
                            <p>{contact.company}</p>
                          </div>
                        </div>
                        <div className="contact-card-stat">
                          <i className="bx bx-phone"></i>
                          <div>
                            <span>Téléphone</span>
                            <p>{contact.phone}</p>
                          </div>
                        </div>
                        <div className="contact-card-stat">
                          <i className="bx bx-map"></i>
                          <div>
                            <span>Adresse</span>
                            <p className="address-truncate">{contact.address}</p>
                          </div>
                        </div>
                        <div className="contact-card-stat">
                          <i className="bx bx-file"></i>
                          <div>
                            <span>Documents générés</span>
                            <p>{contact.documentsGenerated}</p>
                          </div>
                        </div>
                      </div>
                      
                      {showVariables && (
                        <div className="contact-variables">
                          <div className="variables-header">
                            <h4>Variables disponibles ({Object.keys(contact.variables).length})</h4>
                            <Button
                              icon="bx bx-hide"
                              type="text"
                              className="hide-variables-btn"
                              onClick={() => setShowVariables(false)}
                              title="Masquer les variables"
                            />
                          </div>
                          <div className="variables-list">
                            {contact.variables && Object.entries(contact.variables).map(([key, value]) => (
                              <div className="variable-item" key={key}>
                                <span className="variable-key">{key}:</span>
                                <span className="variable-value">{value}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {!showVariables && (
                        <div className="variables-collapse" onClick={() => setShowVariables(true)}>
                          <Button
                            icon="bx bx-show"
                            type="text"
                            onClick={(e) => {
                              e.stopPropagation();
                              setShowVariables(true);
                            }}
                            className="show-variables-btn"
                          >
                            Afficher {Object.keys(contact.variables).length} variables disponibles
                          </Button>
                        </div>
                      )}
                    </div>
                    <div className="contact-card-footer">
                      <div className="contact-card-actions">
                        <div className="main-buttons">
                          <Button
                            icon="bx bx-edit-alt"
                            type="outlined"
                            className="edit-btn"
                            onClick={() => handleEditContact(contact)}
                            title="Modifier le contact"
                          >
                            Modifier
                          </Button>
                          <Button
                            icon="bx bx-file-blank"
                            type="primary"
                            className="doc-btn"
                            onClick={() => handleGenerateDocument(contact)}
                            title="Générer un document avec ce contact"
                          >
                            Générer un document
                          </Button>
                        </div>
                        <Button
                          icon="bx bx-trash"
                          type="text"
                          className="delete-btn"
                          onClick={() => handleDeleteContact(contact)}
                          title="Supprimer ce contact"
                        />
                      </div>
                    </div>
                  </Card>
                ))
              ) : (
                <div className="no-results-card">
                  <i className="bx bx-search-alt"></i>
                  <p>Aucun contact trouvé</p>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Modales */}
      {(addContactModal || editContactModal) && renderAddEditContactModal()}
      {deleteContactModal && renderDeleteContactModal()}
      {generateDocModal && renderGenerateDocModal()}
    </div>
  );
};

export default ContactsPage; 