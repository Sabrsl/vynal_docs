import os
import logging
import datetime
import hashlib
import base64
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.x509 import load_pem_x509_certificate
from cryptography.fernet import Fernet
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io

logger = logging.getLogger(__name__)

class ElectronicSignature:
    """Classe pour gérer les signatures électroniques des documents PDF"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialise le gestionnaire de signatures électroniques
        
        Args:
            config: Configuration de l'application
        """
        self.config = config
        self.cert_path = os.path.join(config.get("data_dir", ""), "certificates", "signing_cert.pem")
        self.key_path = os.path.join(config.get("data_dir", ""), "certificates", "private_key.pem")
        self._ensure_certificates()
    
    def _ensure_certificates(self) -> None:
        """Vérifie et crée les certificats si nécessaire"""
        try:
            # Créer le dossier des certificats si nécessaire
            os.makedirs(os.path.dirname(self.cert_path), exist_ok=True)
            
            # Vérifier si les certificats existent
            if not (os.path.exists(self.cert_path) and os.path.exists(self.key_path)):
                self._generate_certificates()
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des certificats: {e}")
            raise
    
    def _generate_certificates(self) -> None:
        """Génère les certificats de signature"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives.asymmetric import rsa
            
            # Générer la clé privée
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Générer le certificat
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, u"VynalDocs Signing Certificate"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"VynalDocs"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=3650)
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            ).sign(private_key, hashes.SHA256())
            
            # Sauvegarder le certificat et la clé
            with open(self.cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open(self.key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info("Certificats de signature générés avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des certificats: {e}")
            raise
    
    def sign_document(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        """
        Signe un document PDF électroniquement
        
        Args:
            pdf_path: Chemin du document PDF à signer
            output_path: Chemin de sortie (optionnel)
            
        Returns:
            str: Chemin du document signé
        """
        try:
            # Vérifier que le fichier existe
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"Le fichier PDF n'existe pas: {pdf_path}")
            
            # Déterminer le chemin de sortie
            if output_path is None:
                base, ext = os.path.splitext(pdf_path)
                output_path = f"{base}_signed{ext}"
            
            # Lire le PDF original
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                pdf_writer = PyPDF2.PdfWriter()
                
                # Copier toutes les pages
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                
                # Ajouter la page de signature
                signature_page = self._create_signature_page()
                pdf_writer.add_page(signature_page)
                
                # Ajouter les métadonnées de signature
                self._add_signature_metadata(pdf_writer)
                
                # Sauvegarder le PDF signé
                with open(output_path, 'wb') as f:
                    pdf_writer.write(f)
            
            # Signer le fichier avec le certificat
            self._sign_file(output_path)
            
            logger.info(f"Document signé avec succès: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la signature du document: {e}")
            raise
    
    def _create_signature_page(self) -> PyPDF2.PageObject:
        """Crée une page de signature"""
        try:
            # Créer un buffer pour la page de signature
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Ajouter le texte de signature
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 100, "Signature électronique")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 150, f"Date de signature: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Ajouter les informations du certificat
            with open(self.cert_path, 'rb') as f:
                cert = load_pem_x509_certificate(f.read())
                subject = cert.subject
                c.drawString(50, height - 200, f"Signé par: {subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value}")
            
            c.save()
            
            # Créer la page PDF
            buffer.seek(0)
            signature_reader = PyPDF2.PdfReader(buffer)
            return signature_reader.pages[0]
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la page de signature: {e}")
            raise
    
    def _add_signature_metadata(self, pdf_writer: PyPDF2.PdfWriter) -> None:
        """Ajoute les métadonnées de signature au PDF"""
        try:
            # Créer les métadonnées
            metadata = {
                '/Signed': 'true',
                '/SignedBy': 'VynalDocs',
                '/SignedDate': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '/SignatureType': 'Electronic',
                '/SignatureAlgorithm': 'SHA256withRSA'
            }
            
            # Ajouter les métadonnées au PDF
            pdf_writer.metadata.update(metadata)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des métadonnées: {e}")
            raise
    
    def _sign_file(self, file_path: str) -> None:
        """Signe le fichier avec le certificat"""
        try:
            # Lire le fichier
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Calculer le hash du fichier
            file_hash = hashlib.sha256(file_content).digest()
            
            # Lire la clé privée
            with open(self.key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)
            
            # Signer le hash
            signature = private_key.sign(
                file_hash,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # Encoder la signature en base64
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            
            # Ajouter la signature au fichier
            with open(file_path, 'ab') as f:
                f.write(b'\n' + signature_b64.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Erreur lors de la signature du fichier: {e}")
            raise
    
    def verify_signature(self, file_path: str) -> bool:
        """
        Vérifie la signature d'un document
        
        Args:
            file_path: Chemin du document à vérifier
            
        Returns:
            bool: True si la signature est valide, False sinon
        """
        try:
            # Lire le fichier
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Séparer le contenu et la signature
            content_parts = content.split(b'\n')
            file_content = b'\n'.join(content_parts[:-1])
            signature_b64 = content_parts[-1].decode('utf-8')
            
            # Décoder la signature
            signature = base64.b64decode(signature_b64)
            
            # Calculer le hash du contenu
            file_hash = hashlib.sha256(file_content).digest()
            
            # Lire le certificat
            with open(self.cert_path, 'rb') as f:
                cert = load_pem_x509_certificate(f.read())
            
            # Vérifier la signature
            try:
                cert.public_key().verify(
                    signature,
                    file_hash,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                return True
            except:
                return False
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la signature: {e}")
            return False 