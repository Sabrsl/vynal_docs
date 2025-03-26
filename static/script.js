// Configuration
const API_URL = 'http://localhost:8000';
const fileInput = document.getElementById('fileInput');
const dropZone = document.getElementById('dropZone');
const uploadProgress = document.getElementById('uploadProgress');
const uploadStatus = document.getElementById('uploadStatus');
const fileList = document.getElementById('fileList');
const fileDetailsModal = new bootstrap.Modal(document.getElementById('fileDetailsModal'));

// Variables globales
let currentFiles = [];

// Gestion du drag & drop
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    dropZone.classList.add('dragover');
}

function unhighlight(e) {
    dropZone.classList.remove('dragover');
}

dropZone.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

// Gestion de la sélection de fichier
fileInput.addEventListener('change', function(e) {
    handleFiles(this.files);
});

function handleFiles(files) {
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
            uploadFile(file);
        } else {
            showStatus('Seuls les fichiers CSV sont acceptés', 'danger');
        }
    }
}

// Upload de fichier
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        showStatus('Upload en cours...', 'info');
        uploadProgress.classList.remove('d-none');
        uploadProgress.querySelector('.progress-bar').style.width = '0%';

        const response = await fetch(`${API_URL}/upload/`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showStatus('Fichier uploadé avec succès !', 'success');
            refreshFileList();
        } else {
            showStatus(data.detail || 'Erreur lors de l\'upload', 'danger');
        }
    } catch (error) {
        showStatus('Erreur de connexion au serveur', 'danger');
        console.error('Erreur:', error);
    } finally {
        uploadProgress.classList.add('d-none');
    }
}

// Affichage des messages de statut
function showStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `alert alert-${type} mt-3 fade-in`;
    uploadStatus.classList.remove('d-none');
    setTimeout(() => {
        uploadStatus.classList.add('d-none');
    }, 5000);
}

// Liste des fichiers
async function refreshFileList() {
    try {
        const response = await fetch(`${API_URL}/files/`);
        const data = await response.json();

        fileList.innerHTML = '';
        data.files.forEach(file => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${file.filename}</td>
                <td>${formatFileSize(file.size)}</td>
                <td>${formatDate(file.upload_date)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary btn-action" onclick="showFileDetails('${file.filename}')">
                        <i class="bi bi-info-circle"></i>
                    </button>
                </td>
            `;
            fileList.appendChild(row);
        });
    } catch (error) {
        console.error('Erreur:', error);
        showStatus('Erreur lors de la récupération de la liste des fichiers', 'danger');
    }
}

// Détails du fichier
async function showFileDetails(filename) {
    try {
        const response = await fetch(`${API_URL}/files/${filename}`);
        const data = await response.json();

        const details = document.getElementById('fileDetails');
        details.innerHTML = `
            <div class="mb-3">
                <strong>Nom du fichier:</strong> ${data.filename}
            </div>
            <div class="mb-3">
                <strong>Taille:</strong> ${formatFileSize(data.size)}
            </div>
            <div class="mb-3">
                <strong>Date d'upload:</strong> ${formatDate(data.upload_date)}
            </div>
            <div class="mb-3">
                <strong>Chemin:</strong> ${data.path}
            </div>
        `;

        fileDetailsModal.show();
    } catch (error) {
        console.error('Erreur:', error);
        showStatus('Erreur lors de la récupération des détails du fichier', 'danger');
    }
}

// Utilitaires
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser la zone de drop
    initDropZone();
    
    // Charger la liste des fichiers
    refreshFileList();
    
    // Initialiser les tooltips Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Ajouter un exemple de notification
    setTimeout(() => {
        showNotification('Bienvenue sur Vynal Docs', 'info');
    }, 1000);
});

// Initialisation de la zone de glisser-déposer
function initDropZone() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    if (!dropZone || !fileInput) return;
    
    // Gérer le drag & drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Ajouter des classes visuelles pendant le drag
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('dragover');
        }, false);
    });
    
    // Gérer le drop
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }, false);
    
    // Gérer la sélection de fichier via l'input
    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        handleFiles(files);
    });
}

// Gestion des fichiers uploadés
function handleFiles(files) {
    if (files.length === 0) return;
    
    // Afficher la barre de progression
    const progressBar = document.getElementById('uploadProgress');
    const progressBarInner = progressBar.querySelector('.progress-bar');
    const statusContainer = document.getElementById('uploadStatus');
    
    progressBar.classList.remove('d-none');
    progressBarInner.style.width = '0%';
    statusContainer.classList.remove('d-none', 'alert-success', 'alert-danger');
    statusContainer.textContent = 'Upload en cours...';
    
    // Simuler un upload
    let progress = 0;
    const interval = setInterval(() => {
        progress += 5;
        progressBarInner.style.width = `${progress}%`;
        progressBarInner.setAttribute('aria-valuenow', progress);
        
        if (progress >= 100) {
            clearInterval(interval);
            
            // Simuler un délai de traitement
            setTimeout(() => {
                progressBar.classList.add('d-none');
                statusContainer.classList.add('alert-success');
                statusContainer.textContent = 'Upload réussi!';
                
                // Ajouter le fichier à la liste
                for (let i = 0; i < files.length; i++) {
                    addFileToList(files[i]);
                }
                
                // Mettre à jour la liste des fichiers
                refreshFileList();
                
                // Notification
                showNotification('Fichier ajouté avec succès', 'success');
                
                // Cacher le message après 3 secondes
                setTimeout(() => {
                    statusContainer.classList.add('d-none');
                }, 3000);
            }, 500);
        }
    }, 100);
}

// Ajouter un fichier à la liste (simulation)
function addFileToList(file) {
    // Dans une application réelle, vous enverriez le fichier au serveur
    // Ici nous simulons juste l'ajout
    const fileObj = {
        id: Date.now(), // Utiliser l'horodatage comme ID unique
        name: file.name,
        size: formatFileSize(file.size),
        type: file.type,
        date: new Date().toLocaleDateString(),
        progress: 100
    };
    
    currentFiles.push(fileObj);
}

// Afficher une notification
function showNotification(message, type = 'info') {
    // Vérifier si le conteneur existe déjà
    let notifContainer = document.getElementById('notificationContainer');
    
    // Créer le conteneur s'il n'existe pas
    if (!notifContainer) {
        notifContainer = document.createElement('div');
        notifContainer.id = 'notificationContainer';
        notifContainer.style.position = 'fixed';
        notifContainer.style.top = '20px';
        notifContainer.style.right = '20px';
        notifContainer.style.zIndex = '1050';
        document.body.appendChild(notifContainer);
    }
    
    // Créer la notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fade-in shadow-sm`;
    notification.style.minWidth = '250px';
    notification.style.marginBottom = '10px';
    notification.style.opacity = '0';
    notification.style.transition = 'opacity 0.3s ease-in-out';
    
    // Ajouter l'icône en fonction du type
    let icon = 'bi-info-circle';
    if (type === 'success') icon = 'bi-check-circle';
    else if (type === 'warning') icon = 'bi-exclamation-triangle';
    else if (type === 'danger') icon = 'bi-x-circle';
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi ${icon} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    // Ajouter au conteneur
    notifContainer.appendChild(notification);
    
    // Afficher avec une animation
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 10);
    
    // Supprimer après 5 secondes
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Fonctions supplémentaires pour l'interface de workflow
function toggleNodeDetails(nodeId) {
    const node = document.getElementById(nodeId);
    if (node) {
        node.querySelector('.node-body').classList.toggle('d-none');
    }
} 