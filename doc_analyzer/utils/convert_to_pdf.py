import os
import shutil
from pathlib import Path
from docx import Document
from PyPDF2 import PdfWriter
import logging
import subprocess
import tempfile

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def convert_docx_to_pdf(input_path, output_path):
    """Convertit un fichier DOCX en PDF en utilisant LibreOffice."""
    try:
        # Créer un dossier temporaire pour la conversion
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convertir en utilisant LibreOffice
            cmd = [
                'soffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', temp_dir,
                str(input_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Erreur lors de la conversion avec LibreOffice: {result.stderr}")
                return False
                
            # Déplacer le fichier PDF généré
            pdf_name = input_path.stem + '.pdf'
            temp_pdf = Path(temp_dir) / pdf_name
            if temp_pdf.exists():
                shutil.move(str(temp_pdf), str(output_path))
                return True
            else:
                logger.error(f"Le fichier PDF n'a pas été généré dans {temp_dir}")
                return False
    except Exception as e:
        logger.error(f"Erreur lors de la conversion DOCX vers PDF: {str(e)}")
        return False

def convert_to_pdf():
    """Convertit tous les documents en PDF et les déplace dans les bons dossiers."""
    # Chemins des dossiers
    base_dir = Path("data/documents")
    types_dir = base_dir / "types"
    
    # Créer les dossiers de types s'ils n'existent pas
    for type_dir in ["factures", "devis", "contrats"]:
        (types_dir / type_dir).mkdir(parents=True, exist_ok=True)
    
    # Déplacer et convertir les fichiers
    files_to_convert = {
        "facture_client1.txt": ("factures", "facture_client1.pdf"),
        "facture_incomplete.txt": ("factures", "facture_incomplete.pdf"),
        "devis.pdf": ("devis", "devis.pdf"),
        "contrat.docx": ("contrats", "contrat.pdf")
    }
    
    for source_file, (type_dir, target_file) in files_to_convert.items():
        source_path = base_dir / source_file
        target_path = types_dir / type_dir / target_file
        
        if not source_path.exists():
            logger.warning(f"Fichier source non trouvé : {source_file}")
            continue
            
        try:
            if source_file.endswith('.txt'):
                # Créer un PDF vide pour les fichiers texte
                writer = PdfWriter()
                writer.add_blank_page(width=72, height=72)
                with open(target_path, 'wb') as f:
                    writer.write(f)
                logger.info(f"Créé PDF vide pour : {source_file} -> {target_file}")
                
            elif source_file.endswith('.docx'):
                # Convertir DOCX en PDF
                if convert_docx_to_pdf(source_path, target_path):
                    logger.info(f"Converti DOCX en PDF : {source_file} -> {target_file}")
                else:
                    # Créer un PDF vide en cas d'échec
                    writer = PdfWriter()
                    writer.add_blank_page(width=72, height=72)
                    with open(target_path, 'wb') as f:
                        writer.write(f)
                    logger.warning(f"Échec de la conversion DOCX, créé PDF vide : {target_file}")
                    
            else:
                # Déplacer le fichier PDF existant
                shutil.copy2(source_path, target_path)
                logger.info(f"Déplacé PDF : {source_file} -> {target_file}")
            
            # Supprimer le fichier source
            source_path.unlink()
            logger.info(f"Supprimé le fichier source : {source_file}")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {source_file}: {str(e)}")

if __name__ == "__main__":
    convert_to_pdf() 