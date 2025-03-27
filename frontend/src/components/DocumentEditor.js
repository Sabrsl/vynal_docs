import React, { useState, useEffect } from 'react';
import TiptapEditor from './TiptapEditor';
import { saveDocument, updateDocument, createDocument } from '../utils/api';
import { signPDF } from '../utils/signatureUtils';
import './DocumentEditor.css';

const DocumentEditor = ({ document, onSave, onClose }) => {
  const [content, setContent] = useState(document?.content || '');
  const [title, setTitle] = useState(document?.title || '');
  const [isSigning, setIsSigning] = useState(false);
  const [isSigned, setIsSigned] = useState(false);

  useEffect(() => {
    if (document?.isSigned) {
      setIsSigned(true);
    }
  }, [document]);

  const handleContentChange = (newContent) => {
    setContent(newContent);
  };

  const handleTitleChange = (e) => {
    setTitle(e.target.value);
  };

  const handleSave = async () => {
    try {
      const docData = {
        title,
        content,
        lastModified: new Date().toISOString(),
      };

      if (document?.id) {
        await updateDocument(document.id, docData);
      } else {
        await createDocument(docData);
      }

      onSave?.();
    } catch (error) {
      console.error('Error saving document:', error);
      alert('Une erreur est survenue lors de la sauvegarde du document.');
    }
  };

  const handleSignDocument = async () => {
    try {
      setIsSigning(true);
      
      // Créer un conteneur temporaire pour le contenu
      const tempContainer = document.createElement('div');
      tempContainer.innerHTML = content;
      
      // Convertir le contenu en PDF
      const pdf = await signPDF(tempContainer, title);
      
      // Sauvegarder le document signé
      const docData = {
        title: `${title}_signed`,
        content,
        isSigned: true,
        signedAt: new Date().toISOString(),
        lastModified: new Date().toISOString(),
      };

      if (document?.id) {
        await updateDocument(document.id, docData);
      } else {
        await createDocument(docData);
      }

      setIsSigned(true);
      onSave?.();
      alert('Document signé avec succès !');
    } catch (error) {
      console.error('Error signing document:', error);
      alert('Une erreur est survenue lors de la signature du document.');
    } finally {
      setIsSigning(false);
    }
  };

  return (
    <div className="document-editor">
      <div className="document-editor-header">
        <input
          type="text"
          value={title}
          onChange={handleTitleChange}
          placeholder="Titre du document"
          className="document-title-input"
        />
        <div className="document-editor-actions">
          <button
            onClick={handleSave}
            className="btn btn-primary"
            disabled={isSigned}
          >
            Sauvegarder
          </button>
          <button
            onClick={handleSignDocument}
            className="btn btn-success"
            disabled={isSigning || isSigned}
          >
            {isSigning ? 'Signature en cours...' : 'Signer ce document'}
          </button>
          <button onClick={onClose} className="btn btn-secondary">
            Fermer
          </button>
        </div>
      </div>
      <div className="document-editor-content">
        <TiptapEditor
          content={content}
          onChange={handleContentChange}
          readOnly={isSigned}
        />
      </div>
    </div>
  );
};

export default DocumentEditor;