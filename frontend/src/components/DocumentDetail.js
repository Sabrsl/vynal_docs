import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import Button from './Button';
import Card from './Card';
import Loader from './Loader';

const DocumentDetail = ({ documentId, onClose }) => {
  const { documents, updateDocument, deleteDocument, isLoading } = useAppContext();
  const [isEditing, setIsEditing] = useState(false);
  const [documentData, setDocumentData] = useState({});
  
  // Trouver le document correspondant dans le contexte
  const document = documents.find(doc => doc.id === documentId);
  
  React.useEffect(() => {
    if (document) {
      setDocumentData(document);
    }
  }, [document]);
  
  if (!document) {
    return <div>Document non trouvé</div>;
  }
  
  if (isLoading) {
    return <Loader text="Chargement du document..." />;
  }
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setDocumentData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleSave = async () => {
    try {
      await updateDocument(documentId, documentData);
      setIsEditing(false);
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
    }
  };
  
  const handleDelete = async () => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) {
      try {
        await deleteDocument(documentId);
        onClose();
      } catch (error) {
        console.error('Erreur lors de la suppression:', error);
      }
    }
  };
  
  // Déterminer l'icône du document
  const getDocumentIcon = (type) => {
    switch (type) {
      case 'document':
        return 'bx bxs-file-doc';
      case 'presentation':
        return 'bx bxs-slideshow';
      case 'spreadsheet':
        return 'bx bxs-spreadsheet';
      default:
        return 'bx bx-file';
    }
  };
  
  return (
    <Card
      title={isEditing ? "Modifier le document" : document.title}
      icon={getDocumentIcon(document.type)}
      actionButton={
        <div style={{ display: 'flex', gap: '8px' }}>
          {isEditing ? (
            <>
              <Button variant="primary" onClick={handleSave}>Enregistrer</Button>
              <Button variant="text" onClick={() => setIsEditing(false)}>Annuler</Button>
            </>
          ) : (
            <>
              <Button variant="text" icon="bx-edit" onClick={() => setIsEditing(true)}>Modifier</Button>
              <Button variant="text" icon="bx-share-alt">Partager</Button>
              <Button variant="text" icon="bx-trash" onClick={handleDelete}>Supprimer</Button>
              <Button variant="text" icon="bx-x" onClick={onClose}></Button>
            </>
          )}
        </div>
      }
    >
      <div className="document-detail">
        {isEditing ? (
          <div className="document-edit-form">
            <div className="form-group">
              <label htmlFor="title">Titre</label>
              <input 
                type="text" 
                id="title" 
                name="title" 
                value={documentData.title || ''} 
                onChange={handleInputChange}
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label htmlFor="content">Contenu</label>
              <textarea 
                id="content" 
                name="content" 
                value={documentData.content || ''} 
                onChange={handleInputChange}
                className="form-control"
                rows="10"
              />
            </div>
          </div>
        ) : (
          <>
            <div className="document-metadata">
              <div className="metadata-item">
                <span className="metadata-label">Type:</span>
                <span className="metadata-value">{document.type}</span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">Modifié:</span>
                <span className="metadata-value">{document.modified}</span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">Vues:</span>
                <span className="metadata-value">{document.views}</span>
              </div>
            </div>
            <div className="document-content">
              <h3>Contenu</h3>
              <p>{document.content || "Aucun contenu disponible"}</p>
            </div>
          </>
        )}
      </div>
    </Card>
  );
};

export default DocumentDetail; 