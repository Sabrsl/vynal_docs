/**
 * Configuration de l'éditeur de documents
 * Extrait dans un fichier séparé pour permettre le chargement paresseux
 */

// Custom image upload callback pour permettre l'intégration d'images
export const customImageUploadCallback = (file) => {
  return new Promise((resolve, reject) => {
    if (file) {
      try {
        const reader = new FileReader();
        reader.onload = (e) => {
          const result = e.target.result;
          console.log('Image chargée avec succès:', file.name);
          resolve({ data: { link: result } });
        };
        reader.onerror = (error) => {
          console.error('Erreur lors de la lecture du fichier:', error);
          reject(error);
        };
        reader.readAsDataURL(file);
      } catch (error) {
        console.error('Exception lors de l\'upload d\'image:', error);
        reject(error);
      }
    } else {
      console.error('Aucun fichier fourni pour l\'upload');
      reject(new Error('Aucun fichier fourni'));
    }
  });
};

// Configuration optimisée de la toolbar de l'éditeur pour un style Word professionnel
export const editorToolbar = {
  options: ['inline', 'blockType', 'fontSize', 'fontFamily', 'list', 'textAlign', 'colorPicker', 'link', 'embedded', 'emoji', 'image', 'remove', 'history'],
  inline: {
    inDropdown: false,
    options: ['bold', 'italic', 'underline', 'strikethrough', 'monospace', 'superscript', 'subscript'],
  },
  blockType: {
    inDropdown: true,
    options: ['Normal', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Blockquote'],
    className: 'blockType-dropdown',
    dropdownClassName: 'blockType-dropdown-popup',
  },
  fontSize: {
    options: [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 30, 36, 48],
    className: 'fontSize-dropdown',
    dropdownClassName: 'fontSize-dropdown-popup',
  },
  fontFamily: {
    options: ['Arial', 'Georgia', 'Impact', 'Tahoma', 'Times New Roman', 'Verdana', 'Courier New'],
    className: 'fontFamily-dropdown',
    dropdownClassName: 'fontFamily-dropdown-popup',
  },
  list: {
    inDropdown: false,
    options: ['unordered', 'ordered', 'indent', 'outdent'],
    className: 'list-dropdown',
    dropdownClassName: 'list-dropdown-popup',
  },
  textAlign: {
    inDropdown: false,
    options: ['left', 'center', 'right', 'justify'],
    defaultAlignment: 'left'
  },
  colorPicker: {
    colors: ['rgb(97,189,109)', 'rgb(26,188,156)', 'rgb(84,172,210)', 'rgb(44,130,201)',
      'rgb(147,101,184)', 'rgb(71,85,119)', '#6933FF', '#5728d5', '#000000',
      'rgb(38,38,38)', 'rgb(89,89,89)', 'rgb(140,140,140)', 'rgb(191,191,191)', 
      'rgb(242,242,242)', 'rgb(255,255,255)', '#0078D7', '#C2410C', '#15803D', 
      '#8552c2', '#c2410c', '#BB2124'],
    className: 'colorPicker-dropdown',
    popupClassName: 'colorPicker-popup',
  },
  link: {
    inDropdown: false,
    showOpenOptionOnHover: true,
    defaultTargetOption: '_self',
    options: ['link', 'unlink'],
    className: 'link-dropdown',
    popupClassName: 'link-popup',
  },
  emoji: {
    className: 'emoji-dropdown',
    popupClassName: 'emoji-popup',
    emojis: [
      '😀', '😁', '😂', '😃', '😉', '😋', '😎', '😍', '👍', '👎', '👌', '👏', '🙌',
      '👨‍💻', '👩‍💻', '📊', '📈', '📉', '📋', '📌', '📎', '📝', '📁', '📂', '🗂️',
      '📅', '🔍', '🔎', '🔒', '🔓', '📱', '💻', '🖥️', '📄', '📃', '📑', '🔖',
      '✅', '❌', '⚠️', '❗'
    ]
  },
  embedded: {
    className: 'embedded-dropdown',
    popupClassName: 'embedded-popup',
  },
  image: {
    className: 'image-dropdown',
    popupClassName: 'image-popup',
    urlEnabled: true,
    uploadEnabled: true,
    alignmentEnabled: true,
    uploadCallback: customImageUploadCallback,
    previewImage: true,
    inputAccept: 'image/gif,image/jpeg,image/jpg,image/png,image/svg',
    alt: { present: true, mandatory: false },
    defaultSize: {
      height: 'auto',
      width: '100%',
    },
    defaultTabIndex: 0,
    defaultAlignmentIndex: 0,
    title: 'Insérer une image',
  },
  history: {
    inDropdown: false,
    options: ['undo', 'redo'],
    className: 'history-dropdown',
    undo: { title: 'Annuler' },
    redo: { title: 'Rétablir' },
  }
};

// Configuration par défaut pour l'éditeur
export const editorDefaultConfig = {
  textAlignment: 'left',
  textDirectionality: 'ltr',
  defaultBlockAlignment: 'left',
  defaultTextDirection: 'ltr',
  defaultFontFamily: 'Arial',
  defaultFontSize: '14',
  defaultTextColor: '#000000'
};

// Configuration optimisée pour l'insertion d'images
export const imageConfig = {
  imageUploadEnabled: true,
  imageURLEnabled: true,
  imageSizeEnabled: true,
  imageAlignmentEnabled: true,
  defaultImageSize: { width: '100%', height: 'auto' },
  defaultImageAlignment: 'center',
  imageAccept: 'image/gif,image/jpeg,image/jpg,image/png,image/svg',
};

// Traductions pour l'interface de l'éditeur
export const editorLocalization = {
  locale: 'fr',
  translations: {
    'components.controls.blocktype.normal': 'Normal',
    'components.controls.blocktype.h1': 'Titre 1',
    'components.controls.blocktype.h2': 'Titre 2',
    'components.controls.blocktype.h3': 'Titre 3',
    'components.controls.blocktype.h4': 'Titre 4',
    'components.controls.blocktype.h5': 'Titre 5',
    'components.controls.blocktype.h6': 'Titre 6',
    'components.controls.blocktype.blockquote': 'Citation',
    'components.controls.blocktype.code': 'Code',
    'components.controls.blocktype.blocktype': 'Style',
    'components.controls.fontfamily.fontfamily': 'Police',
    'components.controls.fontsize.fontsize': 'Taille',
    'components.controls.image.image': 'Image',
    'components.controls.image.fileUpload': 'Téléverser',
    'components.controls.image.byURL': 'URL',
    'components.controls.image.dropFileText': 'Déposer un fichier ou cliquer pour téléverser',
    'components.controls.inline.bold': 'Gras',
    'components.controls.inline.italic': 'Italique',
    'components.controls.inline.underline': 'Souligné',
    'components.controls.inline.strikethrough': 'Barré',
    'components.controls.link.linkTitle': 'Titre du lien',
    'components.controls.link.linkTarget': 'Cible du lien',
    'components.controls.link.linkTargetOption': 'Ouvrir dans une nouvelle fenêtre',
    'components.controls.link.link': 'Lien',
    'components.controls.link.unlink': 'Supprimer le lien',
    'components.controls.list.list': 'Liste',
    'components.controls.list.unordered': 'Liste à puces',
    'components.controls.list.ordered': 'Liste numérotée',
    'components.controls.list.indent': 'Augmenter le retrait',
    'components.controls.list.outdent': 'Diminuer le retrait',
    'components.controls.textalign.textalign': 'Alignement du texte',
    'components.controls.textalign.left': 'Gauche',
    'components.controls.textalign.center': 'Centre',
    'components.controls.textalign.right': 'Droite',
    'components.controls.textalign.justify': 'Justifié',
    'components.controls.colorpicker.colorpicker': 'Couleur du texte'
  }
}; 