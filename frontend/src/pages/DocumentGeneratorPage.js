import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import DocumentGenerator from '../components/DocumentGenerator';
import Button from '../components/Button';
import Card from '../components/Card';
import Loader from '../components/Loader';
import './DocumentGeneratorPage.css';

const DocumentGeneratorPage = () => {
  const { documents, isLoading, error, fetchDocuments } = useAppContext();
  const [templates, setTemplates] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [generatedDocuments, setGeneratedDocuments] = useState([]);
  const [isGeneratorOpen, setIsGeneratorOpen] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(true);
  
  // Charger les templates et les contacts au démarrage
  useEffect(() => {
    const loadData = async () => {
      setIsLoadingData(true);
      try {
        // Dans une application réelle, ces données viendraient d'appels API
        
        // Récupérer les templates (documents marqués comme modèles)
        const availableTemplates = documents.filter(doc => doc.isTemplate === true);
        
        // Si aucun template n'est trouvé, créer des modèles de démonstration
        const templatesData = availableTemplates.length > 0 ? availableTemplates : [
          {
            id: 'template1',
            title: 'Contrat de prestation',
            description: 'Contrat standard de prestation de service avec conditions',
            isTemplate: true,
            file: '/path/to/template1.docx', // URL factice pour démo
            category: 'contract',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          },
          {
            id: 'template2',
            title: 'Devis Client',
            description: 'Modèle de devis personnalisable avec calculs automatiques',
            isTemplate: true,
            file: '/path/to/template2.docx', // URL factice pour démo
            category: 'quote',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          },
          {
            id: 'template3',
            title: 'Facture Standard',
            description: 'Facture avec coordonnées client et détails prestation',
            isTemplate: true,
            file: '/path/to/template3.docx', // URL factice pour démo
            category: 'invoice',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
        ];
        
        setTemplates(templatesData);
        
        // Récupérer les contacts depuis les données fictives
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
            customVariables: {
              firstName: 'John',
              lastName: 'Doe',
              companyName: 'Acme Inc.',
              taxId: 'FR123456789',
              clientNumber: 'CLI-001'
            }
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
            customVariables: {
              firstName: 'Alice',
              lastName: 'Smith',
              companyName: 'Tech Solutions',
              taxId: 'FR987654321',
              clientNumber: 'PRO-002'
            }
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
            customVariables: {
              firstName: 'Robert',
              lastName: 'Johnson',
              companyName: 'Supply Co',
              taxId: 'FR456789123',
              vendorId: 'VEN-003'
            }
          },
          {
            id: 4,
            email: 'marie.dubois@example.fr',
            name: 'Marie Dubois',
            category: 'client',
            phone: '+33 6 45 67 89 01',
            company: 'Dubois Consulting',
            position: 'Consultante',
            address: '15 Rue Saint-Denis, 33000 Bordeaux',
            photo: 'https://randomuser.me/api/portraits/women/4.jpg',
            customVariables: {
              firstName: 'Marie',
              lastName: 'Dubois',
              companyName: 'Dubois Consulting',
              taxId: 'FR345678912',
              clientNumber: 'CLI-004'
            }
          }
        ];
        
        setContacts(mockContacts);
        
        // Récupérer les documents générés précédemment (depuis localStorage pour la démo)
        const storedDocuments = localStorage.getItem('generatedDocuments');
        if (storedDocuments) {
          try {
            setGeneratedDocuments(JSON.parse(storedDocuments));
          } catch (e) {
            console.error('Erreur lors de la récupération des documents générés:', e);
            setGeneratedDocuments([]);
          }
        }
      } catch (err) {
        console.error('Erreur lors du chargement des données:', err);
      } finally {
        setIsLoadingData(false);
      }
    };
    
    loadData();
  }, [documents]);
  
  // Sauvegarder les documents générés dans localStorage
  useEffect(() => {
    if (generatedDocuments.length > 0) {
      // Supprimer les URLs pour le stockage (elles ne sont pas persistantes)
      const docsToStore = generatedDocuments.map(doc => ({
        ...doc,
        documentUrl: null // Ne pas stocker les URLs des blobs
      }));
      localStorage.setItem('generatedDocuments', JSON.stringify(docsToStore));
    }
  }, [generatedDocuments]);
  
  // Gérer le succès de la génération d'un document
  const handleGenerateSuccess = (documentInfo) => {
    const newGeneratedDoc = {
      id: Date.now(),
      template: documentInfo.template,
      contact: documentInfo.contact,
      documentUrl: documentInfo.documentUrl,
      filename: documentInfo.filename,
      format: documentInfo.format,
      date: new Date().toLocaleString()
    };
    
    setGeneratedDocuments(prev => [newGeneratedDoc, ...prev]);
    
    // Fermer le générateur après un succès
    setTimeout(() => {
      setIsGeneratorOpen(false);
    }, 500);
  };
  
  // Supprimer un document généré
  const handleDeleteDocument = (docId) => {
    setGeneratedDocuments(prev => prev.filter(doc => doc.id !== docId));
  };
  
  // Régénérer un document
  const handleRegenerateDocument = (doc) => {
    // Ouvrir le générateur à nouveau avec les mêmes paramètres
    setIsGeneratorOpen(true);
  };
  
  return (
    <div className="document-generator-page">
      <header className="document-generator-page-header">
        <h1>Générateur de Documents</h1>
        <Button 
          variant="primary" 
          onClick={() => setIsGeneratorOpen(true)}
          disabled={isGeneratorOpen}
        >
          Nouveau document
        </Button>
      </header>
      
      {(isLoading || isLoadingData) ? (
        <div className="document-generator-page-loading">
          <Loader text="Chargement des données..." />
        </div>
      ) : error ? (
        <div className="document-generator-page-error">
          <p>Une erreur est survenue: {error}</p>
          <Button variant="primary" onClick={() => fetchDocuments()}>
            Réessayer
          </Button>
        </div>
      ) : (
        <>
          {isGeneratorOpen && (
            <div className="document-generator-container">
              <div className="document-generator-header">
                <h2>Génération de document</h2>
                <Button 
                  variant="transparent" 
                  onClick={() => setIsGeneratorOpen(false)}
                >
                  ✕
                </Button>
              </div>
              <DocumentGenerator 
                templates={templates}
                contacts={contacts}
                onGenerateSuccess={handleGenerateSuccess}
              />
            </div>
          )}
          
          <section className="document-generator-page-documents">
            <h2>Documents récemment générés</h2>
            
            {generatedDocuments.length === 0 ? (
              <div className="document-generator-page-empty">
                <div className="document-generator-page-empty-icon">
                  <span role="img" aria-label="Documents">📄</span>
                </div>
                <h3>Aucun document généré</h3>
                <p>Créez votre premier document personnalisé en quelques clics</p>
                <Button 
                  variant="primary" 
                  onClick={() => setIsGeneratorOpen(true)}
                  disabled={isGeneratorOpen}
                >
                  Générer un document
                </Button>
              </div>
            ) : (
              <div className="document-generator-page-list">
                {generatedDocuments.map(doc => (
                  <Card key={doc.id} className="document-generator-page-card">
                    <div className="document-generator-page-card-icon">
                      <span role="img" aria-label="Document">
                        {doc.format === 'pdf' ? '📕' : '📄'}
                      </span>
                    </div>
                    <div className="document-generator-page-card-content">
                      <h3 className="document-generator-page-card-title">{doc.filename}</h3>
                      <div className="document-generator-page-card-details">
                        <span>Client: {doc.contact.name}</span>
                        <span>Date: {doc.date}</span>
                        <span>Modèle: {doc.template.title}</span>
                        <span>Format: {doc.format.toUpperCase()}</span>
                      </div>
                    </div>
                    <div className="document-generator-page-card-actions">
                      {doc.documentUrl && (
                        <Button 
                          variant="secondary" 
                          onClick={() => window.open(doc.documentUrl, '_blank')}
                        >
                          Télécharger
                        </Button>
                      )}
                      <Button 
                        variant="secondary" 
                        onClick={() => handleRegenerateDocument(doc)}
                      >
                        Régénérer
                      </Button>
                      <Button 
                        variant="transparent" 
                        onClick={() => handleDeleteDocument(doc.id)}
                      >
                        Supprimer
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
};

export default DocumentGeneratorPage; 