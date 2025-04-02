import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Button from './Button';
import Input from './Input';
import Card from './Card';
import Loader from './Loader';
import documentGenerator from '../utils/documentGenerator';
import './DocumentGenerator.css';

const DocumentGenerator = ({ templates = [], contacts = [], onGenerateSuccess }) => {
  // États
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [selectedContact, setSelectedContact] = useState(null);
  const [step, setStep] = useState(1); // 1: Sélection, 2: Formulaire, 3: Prévisualisation
  const [variables, setVariables] = useState([]);
  const [variablePatterns, setVariablePatterns] = useState({});
  const [missingVariables, setMissingVariables] = useState([]);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [templateFile, setTemplateFile] = useState(null);
  const [error, setError] = useState(null);
  const [exportFormat, setExportFormat] = useState('docx');
  const [outputFilename, setOutputFilename] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [contactSearchQuery, setContactSearchQuery] = useState('');
  const [showVariablesInfo, setShowVariablesInfo] = useState(false);
  const [generatedDocumentUrl, setGeneratedDocumentUrl] = useState('');
  const [previewReady, setPreviewReady] = useState(false);
  const [variablesByCategory, setVariablesByCategory] = useState({});
  const [generatedDocument, setGeneratedDocument] = useState(null);
  const [suggestions, setSuggestions] = useState({});
  const [localContacts, setLocalContacts] = useState([]);
  const [expandedForm, setExpandedForm] = useState(false);

  // Utiliser des contacts de démo si aucun contact n'est fourni
  useEffect(() => {
    if (contacts && contacts.length > 0) {
      setLocalContacts(contacts);
    } else {
      // Contacts de démonstration si aucun contact n'est fourni
      const demoContacts = [
        {
          id: 1,
          name: "Jean Dupont",
          email: "jean.dupont@example.com",
          phone: "06 12 34 56 78",
          company: "Tech Solutions SAS",
          position: "Directeur Technique",
          address: "15 rue de l'Innovation, 75001 Paris"
        },
        {
          id: 2,
          name: "Marie Martin",
          email: "marie.martin@example.com",
          phone: "07 23 45 67 89",
          company: "Design Studio",
          position: "Directrice Artistique",
          address: "8 avenue des Arts, 69002 Lyon"
        },
        {
          id: 3,
          name: "Pierre Lefebvre",
          email: "pierre.lefebvre@example.com",
          phone: "06 34 56 78 90",
          company: "Marketing Expert",
          position: "Consultant Senior",
          address: "22 boulevard du Commerce, 33000 Bordeaux"
        }
      ];
      setLocalContacts(demoContacts);
    }
  }, [contacts]);

  // Filtrer les templates et les contacts en fonction de la recherche
  const filteredTemplates = templates.filter(template => 
    template.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredContacts = localContacts.filter(contact => 
    contact.name.toLowerCase().includes(contactSearchQuery.toLowerCase()) ||
    (contact.company && contact.company.toLowerCase().includes(contactSearchQuery.toLowerCase()))
  );

  // Mémoriser le mappage complet des variables et leurs valeurs
  const variablesMapping = useMemo(() => {
    const allVariables = {};
    if (variables.length > 0) {
      variables.forEach(variable => {
        // Valeur par défaut vide
        allVariables[variable] = '';
        
        // Si une valeur existe dans formData
        if (formData[variable] !== undefined) {
          allVariables[variable] = formData[variable];
        }
      });
    }
    return allVariables;
  }, [variables, formData]);

  // Réinitialiser le formulaire lors du changement de contact
  useEffect(() => {
    if (selectedContact) {
      // Réinitialiser le formulaire avec les données mappées du contact
      const mappedData = documentGenerator.mapClientDataToVariables(selectedContact);
      setFormData(mappedData);
      
      // Si nous avons déjà analysé un template, identifier les variables manquantes
      if (variables.length > 0) {
        const missing = documentGenerator.findMissingVariables(variables, mappedData);
        setMissingVariables(missing);
        
        // Générer des suggestions pour les variables manquantes
        const newSuggestions = {};
        missing.forEach(variable => {
          newSuggestions[variable] = documentGenerator.suggestValuesForVariable(variable);
        });
        setSuggestions(newSuggestions);
      }
    } else {
      setFormData({});
      setMissingVariables([]);
      setSuggestions({});
    }
  }, [selectedContact, variables]);

  // Organiser les variables par catégorie pour une meilleure présentation
  const categorizeVariables = useCallback((vars) => {
    const categories = {
      contact: [],
      company: [],
      date: [],
      financial: [],
      legal: [],
      other: []
    };
    
    vars.forEach(variable => {
      const varLower = variable.toLowerCase();
      if (varLower.includes('nom') || varLower.includes('prenom') || 
          varLower.includes('name') || varLower.includes('email') || 
          varLower.includes('tel') || varLower.includes('phone') || 
          varLower.includes('adresse') || varLower.includes('address')) {
        categories.contact.push(variable);
      } else if (varLower.includes('entreprise') || varLower.includes('company') || 
                varLower.includes('societe') || varLower.includes('business')) {
        categories.company.push(variable);
      } else if (varLower.includes('date')) {
        categories.date.push(variable);
      } else if (varLower.includes('montant') || varLower.includes('prix') || 
                varLower.includes('total') || varLower.includes('tva') || 
                varLower.includes('price') || varLower.includes('amount') || 
                varLower.includes('euro') || varLower.includes('eur')) {
        categories.financial.push(variable);  
      } else if (varLower.includes('contrat') || varLower.includes('contract') || 
                varLower.includes('legal') || varLower.includes('condition') || 
                varLower.includes('juridique') || varLower.includes('law')) {
        categories.legal.push(variable);
      } else {
        categories.other.push(variable);
      }
    });
    
    // Filtrer les catégories vides
    Object.keys(categories).forEach(key => {
      if (categories[key].length === 0) {
        delete categories[key];
      }
    });
    
    return categories;
  }, []);

  // Analyser le template sélectionné pour extraire les variables
  const analyzeTemplate = useCallback(async (template) => {
    if (!template || !template.file) {
      setError("Le fichier de modèle n'est pas disponible");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Tentative de chargement du fichier depuis le serveur
      let result;
      
      try {
        const response = await fetch(template.file);
        const fileBuffer = await response.arrayBuffer();
        // Analyser le template pour extraire les variables
        result = await documentGenerator.analyzeDocxTemplate(fileBuffer);
        setTemplateFile(fileBuffer);
      } catch (fetchError) {
        console.log("Erreur de récupération du fichier, utilisation des données simulées", fetchError);
        // Simuler des données en cas d'échec de récupération
        result = {
          variables: [
            'NOM_CLIENT', 'PRENOM_CLIENT', 'ADRESSE_CLIENT', 'EMAIL_CLIENT', 'TELEPHONE_CLIENT',
            'NOM_ENTREPRISE', 'ADRESSE_ENTREPRISE', 'EMAIL_ENTREPRISE', 'TELEPHONE_ENTREPRISE',
            'DATE_DOCUMENT', 'DATE_EXPIRATION', 'MONTANT_HT', 'MONTANT_TVA', 'MONTANT_TTC',
            'REFERENCE_DOCUMENT'
          ],
          variablesByType: {
            doublebraces: ['NOM_CLIENT', 'EMAIL_CLIENT', 'TELEPHONE_CLIENT'],
            doublebrackets: ['DATE_DOCUMENT', 'DATE_EXPIRATION', 'REFERENCE_DOCUMENT'],
            prefixed: ['NOM_ENTREPRISE', 'ADRESSE_ENTREPRISE', 'EMAIL_ENTREPRISE'],
            dollarbraces: ['MONTANT_HT', 'MONTANT_TVA', 'MONTANT_TTC']
          }
        };
        // Créer un blob simulé pour le templateFile
        const dummyContent = new Uint8Array(10);
        setTemplateFile(dummyContent.buffer);
      }
      
      // Stocker les variables et le fichier du template
      setVariables(result.variables);
      setVariablePatterns(result.variablesByType);
      
      // Catégoriser les variables pour l'affichage
      const categorized = categorizeVariables(result.variables);
      setVariablesByCategory(categorized);
      
      // Si un contact est sélectionné, vérifier les variables manquantes
      if (selectedContact) {
        const mappedData = documentGenerator.mapClientDataToVariables(selectedContact);
        const missing = documentGenerator.findMissingVariables(result.variables, mappedData);
        setMissingVariables(missing);
        
        // Générer des suggestions pour les variables manquantes
        const newSuggestions = {};
        missing.forEach(variable => {
          newSuggestions[variable] = documentGenerator.suggestValuesForVariable(variable);
        });
        setSuggestions(newSuggestions);
      }
      
      // Définir un nom de fichier basé sur le modèle
      setOutputFilename(`${template.title.toLowerCase().replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.${exportFormat}`);
      
      // Passer à l'étape suivante
      setStep(2);
    } catch (err) {
      console.error('Erreur lors de l\'analyse du modèle:', err);
      setError(`Erreur lors de l'analyse du modèle: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [selectedContact, exportFormat, categorizeVariables]);

  // Gérer la sélection d'un template
  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    // Dans une implémentation réelle, le template aurait une URL ou un ID pour récupérer le fichier
    // Pour cette démonstration, on simule que le template a un fichier
    if (template && !template.file) {
      template.file = '/path/to/template.docx'; // URL factice pour la démo
      console.log("Dans un environnement réel, ici on chargerait le fichier DOCX du template");
    }
  };

  // Gérer la sélection d'un contact
  const handleContactSelect = (contact) => {
    setSelectedContact(contact);
  };

  // Gérer les changements dans le formulaire des variables manquantes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Appliquer une suggestion
  const handleApplySuggestion = (variable, value) => {
    setFormData(prev => ({
      ...prev,
      [variable]: value
    }));
  };

  // Gérer le changement de format d'export
  const handleFormatChange = (format) => {
    setExportFormat(format);
    // Mettre à jour l'extension du nom de fichier
    if (outputFilename) {
      setOutputFilename(outputFilename.replace(/\.(docx|pdf)$/, `.${format}`));
    }
  };

  // Gérer le changement de nom de fichier
  const handleFilenameChange = (e) => {
    setOutputFilename(e.target.value);
  };

  // Ajouter une fonction de formatage monétaire directement dans le composant
  const formatMoney = (amount, currency = 'EUR') => {
    return new Intl.NumberFormat('fr-FR', { 
      style: 'currency', 
      currency 
    }).format(amount);
  };

  // Générer le document final
  const handleGenerateDocument = async () => {
    if (!selectedTemplate) {
      setError("Aucun modèle n'est sélectionné");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Créer le contenu du document basé sur le template et le contact
      let documentContent;
      let documentBlob;
      
      // Récupérer les données du contact pour le document
      const contactInfo = selectedContact ? {
        nom: selectedContact.name.split(' ').slice(-1)[0],
        prenom: selectedContact.name.split(' ')[0],
        entreprise: selectedContact.company || '',
        email: selectedContact.email || '',
        telephone: selectedContact.phone || '',
        adresse: selectedContact.address || '',
      } : {};
      
      // Créer une date pour la facture
      const today = new Date();
      const dateStr = today.toLocaleDateString('fr-FR');
      const dateExpiration = new Date(today);
      dateExpiration.setDate(today.getDate() + 30);
      const dateExpirationStr = dateExpiration.toLocaleDateString('fr-FR');
      
      // Données financières simulées pour la facture - valeurs numériques pures
      // pour bénéficier du formatage automatique
      const montantHT = 1200;
      const tauxTVA = 20;
      const montantTVA = montantHT * (tauxTVA / 100);
      const montantTTC = montantHT + montantTVA;
      
      // Générer un numéro de référence
      const reference = `REF-${today.getFullYear()}${String(today.getMonth() + 1).padStart(2, '0')}${String(today.getDate()).padStart(2, '0')}-${Math.floor(1000 + Math.random() * 9000)}`;
      
      // Préparer les données complètes pour le document
      const documentData = {
        ...formData,
        ...contactInfo,
        DATE_DOCUMENT: dateStr,
        DATE_EXPIRATION: dateExpirationStr,
        MONTANT_HT: montantHT,  // Valeur numérique
        MONTANT_TVA: montantTVA, // Valeur numérique
        MONTANT_TTC: montantTTC, // Valeur numérique
        TAUX_TVA: tauxTVA,
        REFERENCE_DOCUMENT: reference
      };
      
      if (exportFormat === 'pdf') {
        // Préparation des données formatées pour le PDF
        const formattedData = documentGenerator.prepareDocumentData(documentData);
        
        // Création d'un PDF avec encodage correct et mise en page soignée
        const pdfContent = `%PDF-1.7
%\\xE2\\xE3\\xCF\\xD3
1 0 obj
<< /Type /Catalog /Pages 2 0 R /Lang (fr-FR) >>
endobj

2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>
endobj

4 0 obj
<< /Length 4000 >>
stream
BT
/F2 20 Tf
175 800 Td
(${selectedTemplate.title}) Tj
/F1 10 Tf
-125 -40 Td
(VynalDocs) Tj
0 -15 Td
(123 Rue de l) Tj (') Tj (Innovation) Tj
0 -15 Td
(75001 Paris) Tj
0 -15 Td
(contact@vynaldocs.com) Tj
0 -15 Td
(+33 1 23 45 67 89) Tj

270 100 Td
(Date: ${dateStr}) Tj

-270 -60 Td
/F2 14 Tf
(CLIENT:) Tj
/F1 10 Tf
10 -15 Td
(${formattedData.prenom} ${formattedData.nom}) Tj
0 -15 Td
(${formattedData.entreprise}) Tj
0 -15 Td
(${formattedData.adresse}) Tj
0 -15 Td
(${formattedData.email}) Tj
0 -15 Td
(${formattedData.telephone}) Tj

-10 -40 Td
/F2 14 Tf
(D) Tj (E) Tj (T) Tj (A) Tj (I) Tj (L) Tj (S) Tj (:) Tj
/F1 10 Tf
10 -20 Td
(R) Tj (e) Tj (f) Tj (e) Tj (r) Tj (e) Tj (n) Tj (c) Tj (e) Tj (:) Tj ( ) Tj (${reference}) Tj
0 -15 Td
(D) Tj (a) Tj (t) Tj (e) Tj (:) Tj ( ) Tj (${dateStr}) Tj
0 -15 Td
(D) Tj (a) Tj (t) Tj (e) Tj ( ) Tj (d) Tj (') Tj (e) Tj (c) Tj (h) Tj (e) Tj (a) Tj (n) Tj (c) Tj (e) Tj (:) Tj ( ) Tj (${dateExpirationStr}) Tj

-10 -40 Td
/F2 12 Tf
(T) Tj (A) Tj (B) Tj (L) Tj (E) Tj (A) Tj (U) Tj (:) Tj
/F1 10 Tf
0 -20 Td
(D) Tj (e) Tj (s) Tj (c) Tj (r) Tj (i) Tj (p) Tj (t) Tj (i) Tj (o) Tj (n) Tj (                  ) Tj
(Q) Tj (u) Tj (a) Tj (n) Tj (t) Tj (i) Tj (t) Tj (e) Tj (      ) Tj
(P) Tj (r) Tj (i) Tj (x) Tj ( ) Tj (u) Tj (n) Tj (i) Tj (t) Tj (a) Tj (i) Tj (r) Tj (e) Tj (        ) Tj
(T) Tj (o) Tj (t) Tj (a) Tj (l) Tj
0 -15 Td
(S) Tj (e) Tj (r) Tj (v) Tj (i) Tj (c) Tj (e) Tj (s) Tj ( ) Tj (d) Tj (e) Tj ( ) Tj (c) Tj (o) Tj (n) Tj (s) Tj (u) Tj (l) Tj (t) Tj (a) Tj (t) Tj (i) Tj (o) Tj (n) Tj (    ) Tj
(1) Tj (                ) Tj
(${formatMoney(montantHT)}) Tj (     ) Tj
(${formatMoney(montantHT)}) Tj

200 -40 Td
(S) Tj (o) Tj (u) Tj (s) Tj (-) Tj (t) Tj (o) Tj (t) Tj (a) Tj (l) Tj (:) Tj (     ) Tj
(${formatMoney(montantHT)}) Tj
0 -15 Td
(T) Tj (V) Tj (A) Tj ( ) Tj (${tauxTVA}%) Tj (:) Tj (     ) Tj
(${formatMoney(montantTVA)}) Tj
0 -15 Td
/F2 12 Tf
(T) Tj (O) Tj (T) Tj (A) Tj (L) Tj (:) Tj (     ) Tj
(${formatMoney(montantTTC)}) Tj

/F1 8 Tf
-200 -90 Td
(D) Tj (o) Tj (c) Tj (u) Tj (m) Tj (e) Tj (n) Tj (t) Tj ( ) Tj (g) Tj (e) Tj (n) Tj (e) Tj (r) Tj (e) Tj ( ) Tj (p) Tj (a) Tj (r) Tj ( ) Tj (V) Tj (y) Tj (n) Tj (a) Tj (l) Tj (D) Tj (o) Tj (c) Tj (s) Tj ( ) Tj (-) Tj ( ) Tj (${new Date().toLocaleString('fr-FR')}) Tj
ET
endstream
endobj

5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>
endobj

6 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>
endobj

xref
0 7
0000000000 65535 f
0000000015 00000 n
0000000085 00000 n
0000000144 00000 n
0000000269 00000 n
0000004323 00000 n
0000004422 00000 n

trailer
<< /Size 7 /Root 1 0 R /ID [<${Math.random().toString(36).substring(2, 15)}> <${Math.random().toString(36).substring(2, 15)}>] >>
startxref
4527
%%EOF`;
        
        // Créer un document HTML pour la prévisualisation avec les données formatées
        const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>${selectedTemplate.title}</title>
          <meta charset="UTF-8">
          <style>
            @page { size: A4; margin: 0; }
            html, body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
            .page {
              width: 210mm;
              min-height: 297mm;
              padding: 20mm;
              margin: 0 auto;
              background: white;
              box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .header { margin-bottom: 30px; text-align: center; }
            .company-info { float: left; width: 50%; }
            .document-info { float: right; width: 50%; text-align: right; }
            .client-info { margin: 40px 0; padding: 10px; background: #f9f9f9; border-radius: 5px; }
            .document-details { margin: 20px 0; clear: both; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
            th { background: #f5f5f5; }
            .amount-row { font-weight: bold; }
            .footer { margin-top: 50px; font-size: 0.8em; color: #777; text-align: center; }
            .notice { margin-top: 30px; padding: 15px; background: #fff8e1; border-left: 4px solid #ffc107; }
            .button { padding: 8px 16px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
          </style>
        </head>
        <body>
          <div class="page">
            <div class="header">
              <h1>${selectedTemplate.title}</h1>
            </div>
            
            <div class="company-info">
              <h3>VynalDocs</h3>
              <p>123 Rue de l'Innovation<br>
              75001 Paris<br>
              contact@vynaldocs.com<br>
              +33 1 23 45 67 89</p>
            </div>
            
            <div class="document-info">
              <h3>Référence: ${reference}</h3>
              <p>Date: ${dateStr}<br>
              Date d'échéance: ${dateExpirationStr}</p>
            </div>
            
            <div class="client-info">
              <h3>Client</h3>
              <p>${formattedData.prenom} ${formattedData.nom}<br>
              ${formattedData.entreprise}<br>
              ${formattedData.adresse}<br>
              ${formattedData.email}<br>
              ${formattedData.telephone}</p>
            </div>
            
            <div class="document-details">
              <h3>Détails</h3>
              <table>
                <thead>
                  <tr>
                    <th>Description</th>
                    <th>Quantité</th>
                    <th>Prix unitaire</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Services de consultation</td>
                    <td>1</td>
                    <td>${formatMoney(montantHT)}</td>
                    <td>${formatMoney(montantHT)}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="3" style="text-align: right;">Sous-total:</td>
                    <td>${formatMoney(montantHT)}</td>
                  </tr>
                  <tr>
                    <td colspan="3" style="text-align: right;">TVA (${tauxTVA}%):</td>
                    <td>${formatMoney(montantTVA)}</td>
                  </tr>
                  <tr class="amount-row">
                    <td colspan="3" style="text-align: right;">Total:</td>
                    <td>${formatMoney(montantTTC)}</td>
                  </tr>
                </tfoot>
              </table>
              
              <div class="footer">
                <p>Document généré par VynalDocs - ${new Date().toLocaleString('fr-FR')}</p>
              </div>
              
              <div class="notice">
                <h3>Attention:</h3>
                <p>Ceci est une prévisualisation HTML. Pour télécharger un vrai PDF, utilisez les boutons ci-dessous.</p>
                <p>Si vous rencontrez des problèmes avec Adobe Reader, essayez les méthodes suivantes:</p>
                <ol>
                  <li>Cliquez sur "Créer un PDF réel" pour ouvrir dans une nouvelle fenêtre</li>
                  <li>Utilisez la fonction d'impression du navigateur (Ctrl+P)</li>
                  <li>Sélectionnez "Enregistrer comme PDF" dans les options d'impression</li>
                </ol>
                <div style="display:flex;gap:10px;margin-top:15px;">
                  <button class="button" onclick="window.print()">Imprimer/Enregistrer</button>
                </div>
              </div>
            </div>
          </div>
        </body>
        </html>
        `;
        
        // Créer un Blob HTML pour la prévisualisation
        documentBlob = new Blob([htmlContent], { type: 'text/html' });
        
        // Stocker le contenu PDF pour le téléchargement
        setTemplateFile(pdfContent);
      } else {
        // Préparer les données pour le format texte avec formatage
        const formattedData = documentGenerator.prepareDocumentData(documentData);
        
        // Format texte pour DOCX (simulation)
        documentContent = `
DOCUMENT: ${selectedTemplate.title}
DATE: ${dateStr}
RÉFÉRENCE: ${reference}

DE:
VynalDocs
123 Rue de l'Innovation
75001 Paris
contact@vynaldocs.com
+33 1 23 45 67 89

À:
${formattedData.prenom} ${formattedData.nom}
${formattedData.entreprise}
${formattedData.adresse}
${formattedData.email}
${formattedData.telephone}

DÉTAILS:
- Description: Services de consultation
- Montant HT: ${formatMoney(montantHT)}
- TVA (${tauxTVA}%): ${formatMoney(montantTVA)}
- Montant TTC: ${formatMoney(montantTTC)}
- Date d'échéance: ${dateExpirationStr}

Ce document a été généré automatiquement par VynalDocs.

NOTE: Ceci est une simulation de document DOCX. Pour obtenir un document réel,
vous devriez télécharger le fichier et l'ouvrir avec Microsoft Word ou un éditeur compatible.
        `;
        
        documentBlob = new Blob([documentContent], { type: 'text/plain' });
      }
      
      // Créer une URL pour le document généré
      const url = URL.createObjectURL(documentBlob);
      setGeneratedDocumentUrl(url);
      setGeneratedDocument(documentBlob);
      
      // Passer à l'étape de prévisualisation
      setStep(3);
      setPreviewReady(true);
      
      // IMPORTANT: Appeler la fonction de callback pour informer l'application parent
      // de la création du document
      if (onGenerateSuccess && typeof onGenerateSuccess === 'function') {
        console.log("Appel de onGenerateSuccess avec les données du document");
        
        // Créer un objet document avec toutes les informations nécessaires
        const documentInfo = {
          id: reference,
          title: selectedTemplate.title,
          template: selectedTemplate,
          contact: selectedContact,
          format: exportFormat,
          filename: outputFilename || `document.${exportFormat}`,
          url: url,
          data: documentData,
          createdAt: new Date().toISOString(),
          content: documentBlob
        };
        
        // Appeler la callback avec les données du document
        onGenerateSuccess(documentInfo);
      } else {
        console.warn("La fonction onGenerateSuccess n'est pas définie ou n'est pas une fonction");
      }
      
    } catch (err) {
      console.error('Erreur lors de la génération du document:', err);
      setError(`Erreur lors de la génération du document: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Télécharger le document généré
  const handleDownloadDocument = () => {
    if (!generatedDocument || !generatedDocumentUrl) {
      setError("Le document n'est pas disponible pour le téléchargement");
      return;
    }
    
    try {
      let downloadUrl;
      
      // Pour les PDFs, créer un vrai PDF basique au lieu d'utiliser du HTML
      if (exportFormat === 'pdf' && templateFile) {
        // Créer un blob de type PDF avec le contenu PDF basique
        const pdfBlob = new Blob([templateFile], { type: 'application/pdf' });
        downloadUrl = URL.createObjectURL(pdfBlob);
      } else {
        // Pour les autres formats, utiliser l'URL déjà générée
        downloadUrl = generatedDocumentUrl;
      }
      
      // Créer un élément <a> pour déclencher le téléchargement
      const downloadLink = document.createElement('a');
      downloadLink.href = downloadUrl;
      downloadLink.download = outputFilename || `document.${exportFormat}`;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      
      // Libérer l'URL créée spécialement pour le téléchargement si différente
      if (downloadUrl !== generatedDocumentUrl) {
        URL.revokeObjectURL(downloadUrl);
      }
    } catch (err) {
      console.error('Erreur lors du téléchargement:', err);
      setError(`Erreur lors du téléchargement: ${err.message}`);
    }
  };

  // Imprimer le document HTML
  const handlePrintDocument = () => {
    if (!generatedDocumentUrl) {
      setError("Le document n'est pas disponible pour l'impression");
      return;
    }
    
    try {
      // Ouvrir une nouvelle fenêtre pour imprimer le document
      const printWindow = window.open(generatedDocumentUrl, '_blank');
      if (printWindow) {
        // Déclencher l'impression une fois le document chargé
        printWindow.onload = () => {
          printWindow.print();
        };
      } else {
        setError("Impossible d'ouvrir la fenêtre d'impression. Veuillez vérifier les paramètres de votre navigateur.");
      }
    } catch (err) {
      console.error('Erreur lors de l\'impression:', err);
      setError(`Erreur lors de l'impression: ${err.message}`);
    }
  };

  // Réinitialiser le générateur
  const handleReset = () => {
    // Réinitialiser les états
    setSelectedTemplate(null);
    setSelectedContact(null);
    setVariables([]);
    setMissingVariables([]);
    setFormData({});
    setTemplateFile(null);
    setError(null);
    setExportFormat('docx');
    setOutputFilename('');
    setSearchQuery('');
    setContactSearchQuery('');
    setGeneratedDocumentUrl('');
    setPreviewReady(false);
    setVariablesByCategory({});
    setStep(1);
    
    // Libérer les URL des objets
    if (generatedDocumentUrl) {
      URL.revokeObjectURL(generatedDocumentUrl);
    }
  };

  const toggleFormExpansion = () => {
    setExpandedForm(!expandedForm);
  };

  // Afficher l'étape 1: Sélection du template et du contact
  const renderStep1 = () => (
    <div className="selection-section">
      <div className="template-section">
        <div className="section-header">
          <h3>Modèles de document</h3>
          {selectedTemplate && (
            <Button 
              variant="transparent" 
              icon="bx-x" 
              onClick={() => setSelectedTemplate(null)}
              size="small"
            />
          )}
        </div>
        <div className="section-search">
          <Input
            type="text"
            placeholder="Rechercher un modèle..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            prefixIcon="bx-search"
          />
        </div>
        <div className="section-content">
          {filteredTemplates.length === 0 ? (
            <div className="no-items">
              <i className="bx bx-file"></i>
              <p>Aucun modèle trouvé</p>
            </div>
          ) : (
            <ul className="item-list">
              {filteredTemplates.map(template => (
                <li 
                  key={template.id} 
                  className={`template-item ${selectedTemplate?.id === template.id ? 'selected' : ''}`}
                  onClick={() => handleTemplateSelect(template)}
                >
                  <div className="template-icon">
                    <i className="bx bxs-file-doc"></i>
                  </div>
                  <div className="template-info">
                    <h4>{template.title}</h4>
                    <p>{template.description || 'Aucune description'}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      
      <div className="contact-section">
        <div className="section-header">
          <h3>Contacts</h3>
          {selectedContact && (
            <Button 
              variant="transparent" 
              icon="bx-x" 
              onClick={() => setSelectedContact(null)}
              size="small"
            />
          )}
        </div>
        <div className="section-search">
          <Input
            type="text"
            placeholder="Rechercher un contact..."
            value={contactSearchQuery}
            onChange={(e) => setContactSearchQuery(e.target.value)}
            prefixIcon="bx-search"
          />
        </div>
        <div className="section-content">
          {filteredContacts.length === 0 ? (
            <div className="no-items">
              <i className="bx bx-user"></i>
              <p>Aucun contact trouvé</p>
            </div>
          ) : (
            <ul className="item-list">
              {filteredContacts.map(contact => (
                <li 
                  key={contact.id} 
                  className={`contact-item ${selectedContact?.id === contact.id ? 'selected' : ''}`}
                  onClick={() => handleContactSelect(contact)}
                >
                  <div className="contact-icon">
                    <i className="bx bxs-user"></i>
                  </div>
                  <div className="contact-info">
                    <h4>{contact.name}</h4>
                    <p>{contact.company || contact.email || 'Aucune information supplémentaire'}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );

  // Afficher l'étape 2: Formulaire pour compléter les variables manquantes
  const renderStep2 = () => (
    <div className="document-generator-step step-2">
      <div className="document-generator-selected-items">
        <div className="document-generator-selected-template">
          <span className="selected-label">
            <i className="bx bx-file-blank"></i> Template:
          </span>
          <span className="selected-name">{selectedTemplate.title}</span>
        </div>

        <div className="document-generator-selected-contact">
          <span className="selected-label">
            <i className="bx bx-user"></i> Contact:
          </span>
          <span className="selected-name">{selectedContact ? selectedContact.name : 'Aucun contact sélectionné'}</span>
        </div>
      </div>

      <div className="document-variables-form">
        {Object.keys(variablesByCategory).length > 0 ? (
          Object.entries(variablesByCategory).map(([category, categoryVariables]) => (
            <div key={category} className="document-generator-variables-category">
              <h4>
                {category === 'contact' && 'Informations de contact'}
                {category === 'company' && 'Informations d\'entreprise'}
                {category === 'date' && 'Dates'}
                {category === 'financial' && 'Informations financières'}
                {category === 'legal' && 'Informations juridiques'}
                {category === 'other' && 'Autres informations'}
              </h4>
              <ul>
                {categoryVariables.map(variable => (
                  <li key={variable}>
                    {documentGenerator.formatVariableForDisplay(variable)}
                    <span className={`variable-status ${missingVariables.includes(variable) ? 'missing' : 'available'}`}>
                      {missingVariables.includes(variable) ? 'À compléter' : 'Disponible'}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))
        ) : (
          <div className="document-generator-all-variables-available">
            <div className="document-generator-success-icon">
              <i className="bx bx-check-circle"></i>
            </div>
            <h3>Toutes les variables sont renseignées!</h3>
            <p>
              Les informations du client correspondent à toutes les variables du modèle.
              Le document peut être généré directement.
            </p>
          </div>
        )}
      </div>

      {missingVariables.length > 0 && (
        <div className="document-generator-form-container">
          <h3>Variables à compléter ({missingVariables.length})</h3>
          <div className="document-generator-form">
            {missingVariables.map(variable => {
              const fieldType = documentGenerator.detectFieldType(variable);
              const hasSuggestions = suggestions[variable] && suggestions[variable].length > 0;
              
              return (
                <div key={variable} className="document-generator-form-field">
                  <label htmlFor={variable}>
                    {documentGenerator.formatVariableForDisplay(variable)}:
                  </label>
                  
                  {fieldType === 'textarea' ? (
                    <textarea
                      id={variable}
                      name={variable}
                      value={formData[variable] || ''}
                      onChange={handleInputChange}
                      rows={3}
                    />
                  ) : fieldType === 'date' ? (
                    <Input
                      type="date"
                      id={variable}
                      name={variable}
                      value={formData[variable] || ''}
                      onChange={handleInputChange}
                    />
                  ) : (
                    <Input
                      type={fieldType}
                      id={variable}
                      name={variable}
                      value={formData[variable] || ''}
                      onChange={handleInputChange}
                      placeholder={`Entrez ${documentGenerator.formatVariableForDisplay(variable).toLowerCase()}`}
                    />
                  )}
                  
                  {hasSuggestions && (
                    <div className="document-generator-suggestions">
                      <span className="suggestions-label">Suggestions:</span>
                      <div className="suggestions-buttons">
                        {suggestions[variable].map((suggestion, idx) => (
                          <Button
                            key={idx}
                            variant="subtle"
                            size="small"
                            onClick={() => handleApplySuggestion(variable, suggestion)}
                          >
                            {suggestion}
                          </Button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="document-generator-export-options">
        <h3>Options d'export</h3>
        <div className="document-generator-export-form">
          <div className="document-generator-export-field">
            <label htmlFor="outputFilename">Nom du fichier:</label>
            <Input
              type="text"
              id="outputFilename"
              value={outputFilename}
              onChange={handleFilenameChange}
              placeholder="Nom du fichier"
            />
          </div>
          <div className="document-generator-export-field">
            <label>Format:</label>
            <div className="document-generator-format-options">
              <Button
                variant={exportFormat === 'docx' ? 'primary' : 'subtle'}
                size="small"
                onClick={() => handleFormatChange('docx')}
              >
                DOCX
              </Button>
              <Button
                variant={exportFormat === 'pdf' ? 'primary' : 'subtle'}
                size="small"
                onClick={() => handleFormatChange('pdf')}
              >
                PDF
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="document-generator-actions">
        <Button 
          variant="secondary" 
          onClick={() => setStep(1)}
        >
          Retour
        </Button>
        <Button 
          variant="primary" 
          onClick={handleGenerateDocument}
        >
          {loading ? 'Génération...' : 'Générer le document'}
        </Button>
      </div>
      
      {error && (
        <div className="document-generator-error">
          <p>{error}</p>
        </div>
      )}
    </div>
  );

  // Afficher l'étape 3: Prévisualisation et téléchargement
  const renderStep3 = () => (
    <div className="document-generator-step step-3">
      <div className="document-generator-success">
        <div className="document-generator-success-icon">
          <i className="bx bx-check-circle"></i>
        </div>
        <h2>Document généré avec succès!</h2>
        <p>Votre document a été créé et est prêt à être téléchargé.</p>
      </div>
      
      <div className="document-generator-result">
        <div className="document-generator-preview">
          {/* Afficher l'aperçu du document généré dans une iframe */}
          {previewReady && generatedDocumentUrl && (
            <iframe
              src={generatedDocumentUrl}
              title="Aperçu du document"
              className="document-preview-iframe"
              width="100%"
              height="500px"
              style={{ border: '1px solid #e5e7eb', borderRadius: '8px' }}
            />
          )}
          
          {!previewReady && (
            <div className="document-generator-preview-placeholder">
              <div className="document-generator-preview-icon">
                <i className={`bx ${exportFormat === 'pdf' ? 'bxs-file-pdf' : 'bxs-file-doc'}`}></i>
              </div>
              <p>{outputFilename}</p>
            </div>
          )}
        </div>

        <div className="document-generator-download">
          <Button 
            variant="primary" 
            onClick={handleDownloadDocument}
            disabled={!previewReady}
            icon="bx-download"
          >
            Télécharger
          </Button>
          {exportFormat === 'pdf' && (
            <>
              <Button 
                variant="secondary" 
                onClick={handlePrintDocument}
                disabled={!previewReady}
                icon="bx-printer"
              >
                Créer un PDF réel
              </Button>
              <div className="document-generator-download-note">
                <i className="bx bx-info-circle"></i>
                <p>Le PDF téléchargé est un document basique compatible avec la plupart des lecteurs PDF. Pour un document plus complet, utilisez le bouton "Créer un PDF réel".</p>
              </div>
            </>
          )}
          <Button 
            variant="text" 
            onClick={handleReset}
            icon="bx-refresh"
          >
            Nouveau document
          </Button>
        </div>
      </div>
      
      <div className="document-generator-summary">
        <h3>Résumé</h3>
        <div className="document-generator-summary-details">
          <div className="document-generator-summary-item">
            <span className="summary-label">Modèle:</span>
            <span className="summary-value">{selectedTemplate.title}</span>
          </div>
          <div className="document-generator-summary-item">
            <span className="summary-label">Client:</span>
            <span className="summary-value">{selectedContact.name}</span>
          </div>
          <div className="document-generator-summary-item">
            <span className="summary-label">Format:</span>
            <span className="summary-value">{exportFormat.toUpperCase()}</span>
          </div>
          <div className="document-generator-summary-item">
            <span className="summary-label">Nom du fichier:</span>
            <span className="summary-value">{outputFilename}</span>
          </div>
          <div className="document-generator-summary-item">
            <span className="summary-label">Date de génération:</span>
            <span className="summary-value">{new Date().toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );

  // Afficher les différentes étapes du générateur
  const renderContent = () => {
    if (loading) {
      return (
        <div className="generator-loading">
          <i className="bx bx-loader-alt bx-spin"></i>
          <h3>Chargement en cours...</h3>
          <p>Veuillez patienter pendant l'analyse du modèle</p>
        </div>
      );
    }
    
    if (error) {
      return (
        <div className="generator-error">
          <i className="bx bx-error-circle"></i>
          <h3>Une erreur est survenue</h3>
          <p>{error}</p>
          <Button variant="primary" onClick={handleReset}>
            Réessayer
          </Button>
        </div>
      );
    }
    
    switch (step) {
      case 1:
        return renderStep1();
      case 2:
        return renderStep2();
      case 3:
        return renderStep3();
      default:
        return renderStep1();
    }
  };

  // Rendu du composant principal
  return (
    <div className="document-generator">
      <div className="document-generator-steps">
        <div className={`step-item ${step === 1 ? 'active' : step > 1 ? 'completed' : ''}`}>
          <i className={`bx ${step === 1 ? 'bxs-file-find' : step > 1 ? 'bx-check-circle' : 'bx-file-find'}`}></i>
          <span>Sélection</span>
        </div>
        <div className={`step-item ${step === 2 ? 'active' : step > 2 ? 'completed' : ''}`}>
          <i className={`bx ${step === 2 ? 'bxs-edit' : step > 2 ? 'bx-check-circle' : 'bx-edit'}`}></i>
          <span>Variables</span>
        </div>
        <div className={`step-item ${step === 3 ? 'active' : ''}`}>
          <i className={`bx ${step === 3 ? 'bxs-file-pdf' : 'bx-file-pdf'}`}></i>
          <span>Aperçu et téléchargement</span>
        </div>
      </div>
      <div className="document-generator-content">
        {renderContent()}
      </div>
      
      <div className="document-generator-actions">
        <div className="left-actions">
          {step > 1 && (
            <Button 
              variant="text" 
              onClick={() => setStep(prevStep => prevStep - 1)}
              icon="bx-arrow-back"
            >
              Retour
            </Button>
          )}
        </div>
        <div className="right-actions">
          {step === 1 && (
            <Button
              variant="primary"
              onClick={() => selectedTemplate && analyzeTemplate(selectedTemplate)}
              disabled={!selectedTemplate}
              icon="bx-right-arrow-alt"
              className="primary"
            >
              Continuer
            </Button>
          )}
          {step === 2 && (
            <Button
              variant="primary"
              onClick={handleGenerateDocument}
              disabled={missingVariables.length > 0}
              icon="bx-right-arrow-alt"
              className="primary"
            >
              Prévisualiser
            </Button>
          )}
          {step === 3 && (
            <div className="button-group">
              <Button
                variant="primary"
                onClick={handleDownloadDocument}
                icon="bx-download"
                className="primary"
              >
                Télécharger
              </Button>
              {exportFormat === 'pdf' && (
                <>
                  <Button
                    variant="secondary"
                    onClick={handlePrintDocument}
                    icon="bx-printer"
                  >
                    Créer un PDF réel
                  </Button>
                  <div className="button-note">
                    <i className="bx bx-info-circle"></i>
                    <span>Pour un PDF compatible Adobe Reader, utilisez cette option</span>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentGenerator; 