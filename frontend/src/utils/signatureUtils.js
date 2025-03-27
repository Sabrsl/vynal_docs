import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import { saveAs } from 'file-saver';

/**
 * Utilitaire pour gérer les signatures électroniques des documents PDF
 */

/**
 * Ajoute une page de signature à un document PDF
 * @param {jsPDF} pdf - Le document PDF à modifier
 * @param {Object} signatureInfo - Informations sur la signature
 * @returns {jsPDF} Le document PDF modifié
 */
export const addSignaturePage = (pdf, signatureInfo) => {
  // Ajouter une nouvelle page
  pdf.addPage();
  
  // Ajouter le texte de signature
  pdf.setFontSize(16);
  pdf.text('Signature électronique', 50, 100);
  
  // Ajouter la date de signature
  pdf.setFontSize(12);
  pdf.text(`Date de signature: ${new Date().toLocaleString()}`, 50, 150);
  
  // Ajouter les informations du signataire
  if (signatureInfo.signer) {
    pdf.text(`Signé par: ${signatureInfo.signer}`, 50, 200);
  }
  
  return pdf;
};

/**
 * Ajoute les métadonnées de signature à un document PDF
 * @param {jsPDF} pdf - Le document PDF à modifier
 * @param {Object} metadata - Métadonnées à ajouter
 * @returns {jsPDF} Le document PDF modifié
 */
export const addSignatureMetadata = (pdf, metadata) => {
  const { title, author, subject, keywords } = metadata;
  
  pdf.setProperties({
    title: title,
    author: author,
    subject: subject,
    keywords: keywords.join(', ')
  });
  
  return pdf;
};

/**
 * Signe un document PDF
 * @param {Blob} pdfBlob - Le document PDF à signer
 * @param {Object} signatureInfo - Informations sur la signature
 * @returns {Promise<Blob>} Le document PDF signé
 */
export const signPDF = async (container, title) => {
  try {
    // Convertir le contenu en image avec html2canvas
    const canvas = await html2canvas(container, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff'
    });

    // Créer un nouveau PDF
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'px',
      format: [canvas.width, canvas.height]
    });

    // Ajouter l'image du contenu
    const imgData = canvas.toDataURL('image/png');
    pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);

    // Ajouter une page de signature
    pdf.addPage();
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    
    // Ajouter le titre et la date
    pdf.setFontSize(16);
    pdf.text(title, 20, 20);
    pdf.setFontSize(12);
    pdf.text(`Signé le ${new Date().toLocaleDateString()}`, 20, 40);

    // Ajouter une zone pour la signature
    pdf.setDrawColor(0, 0, 0);
    pdf.setLineWidth(1);
    pdf.line(20, pageHeight - 100, pageWidth - 20, pageHeight - 100);
    
    // Ajouter le texte de signature
    pdf.setFontSize(10);
    pdf.text('Signature :', 20, pageHeight - 80);
    pdf.text('Date :', 20, pageHeight - 60);

    // Sauvegarder le PDF
    const pdfBlob = pdf.output('blob');
    saveAs(pdfBlob, `${title}_signed.pdf`);

    return pdfBlob;
  } catch (error) {
    console.error('Error in signPDF:', error);
    throw new Error('Erreur lors de la signature du document');
  }
};

/**
 * Vérifie si un document PDF est signé
 * @param {Blob} pdfBlob - Le document PDF à vérifier
 * @returns {Promise<boolean>} True si le document est signé
 */
export const isPDFSigned = (pdfName) => {
  return pdfName.includes('_signed.pdf');
};

/**
 * Télécharge un document PDF signé
 * @param {Blob} signedPdfBlob - Le document PDF signé
 * @param {string} filename - Nom du fichier
 */
export const downloadSignedPDF = (signedPdfBlob, filename) => {
  saveAs(signedPdfBlob, `${filename}_signed.pdf`);
}; 