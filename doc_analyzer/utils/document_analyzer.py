import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    """
    Classe pour l'analyse de documents texte avec extraction d'informations clés.
    """
    
    def __init__(self):
        """Initialise l'analyseur de documents."""
        logger.info("Initialisation du DocumentAnalyzer")
        
        # Patterns pour les dates
        self.date_patterns = [
            r"\b\d{2}/\d{2}/\d{4}\b",               # 12/03/2025
            r"\b\d{4}-\d{2}-\d{2}\b",               # 2025-03-12
            r"\b\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}\b",  # 12 mars 2025
            r"\b\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b"  # 12 mars
        ]
        
        # Patterns pour les informations clés
        self.info_patterns = {
            'siret': r"SIRET[:\s]*([0-9]{14})",
            'montant': r"(\d+[\s.,]?\d*)\s?€",
            'adresse': r"\d{1,3} [\w\s]+,\s?\d{5} [\w\s]+",
            'email': r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            'telephone': r"(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}",
            'iban': r"FR\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{3}"
        }
        
        # Patterns pour les champs vides
        self.empty_field_patterns = [
            r"(XXX+|__+|\.\.\.+)",  # Champs vides classiques
            r"\[.*?\]",             # Crochets vides
            r"\(\s*\)",             # Parenthèses vides
            r"\{\s*\}",             # Accolades vides
            r"<.*?>"                # Balises vides
        ]
    
    def extraire_dates(self, texte: str) -> List[str]:
        """
        Extrait les dates du texte.
        
        Args:
            texte (str): Texte à analyser
            
        Returns:
            List[str]: Liste des dates trouvées
        """
        dates = []
        for pattern in self.date_patterns:
            dates.extend(re.findall(pattern, texte))
        return dates
    
    def extraire_infos(self, texte: str) -> Dict[str, str]:
        """
        Extrait les informations clés du texte.
        
        Args:
            texte (str): Texte à analyser
            
        Returns:
            Dict[str, str]: Informations extraites
        """
        infos = {}
        for key, pattern in self.info_patterns.items():
            match = re.search(pattern, texte)
            if match:
                infos[key] = match.group(1) if len(match.groups()) > 0 else match.group(0)
        return infos
    
    def detecter_champs_vides(self, texte: str) -> List[str]:
        """
        Détecte les champs vides dans le texte.
        
        Args:
            texte (str): Texte à analyser
            
        Returns:
            List[str]: Liste des champs vides trouvés
        """
        vides = []
        for pattern in self.empty_field_patterns:
            vides.extend(re.findall(pattern, texte))
        return vides
    
    def verifier_echeance(self, dates: List[str]) -> List[str]:
        """
        Vérifie les dates proches de la date actuelle.
        
        Args:
            dates (List[str]): Liste des dates à vérifier
            
        Returns:
            List[str]: Liste des alertes d'échéance
        """
        alertes = []
        aujourd_hui = datetime.now()
        
        for date_str in dates:
            try:
                # Gestion des différents formats de date
                if '/' in date_str:
                    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                elif '-' in date_str:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    # Format avec mois en lettres
                    mois_fr = {
                        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
                        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
                        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
                    }
                    
                    # Si l'année n'est pas présente, on suppose l'année en cours
                    if len(date_str.split()) == 2:
                        jour, mois = date_str.split()
                        date_str = f"{jour} {mois} {aujourd_hui.year}"
                    
                    for mois_fr, mois_num in mois_fr.items():
                        if mois_fr in date_str.lower():
                            date_str = date_str.replace(mois_fr, mois_num)
                            break
                    
                    date_obj = datetime.strptime(date_str, "%d %m %Y")
                
                # Vérifier si la date est dans les 30 prochains jours
                if 0 <= (date_obj - aujourd_hui).days <= 30:
                    alertes.append(f"📌 Échéance proche : {date_str}")
            except ValueError as e:
                logger.warning(f"Date invalide ignorée : {date_str} - {str(e)}")
                continue
        
        return alertes
    
    def analyser_document(self, texte: str) -> Dict[str, Any]:
        """
        Analyse un document et extrait toutes les informations pertinentes.
        
        Args:
            texte (str): Texte du document à analyser
            
        Returns:
            Dict[str, Any]: Résultats de l'analyse
        """
        try:
            # Extraire les informations
            dates = self.extraire_dates(texte)
            infos = self.extraire_infos(texte)
            vides = self.detecter_champs_vides(texte)
            alertes = self.verifier_echeance(dates)
            
            # Déterminer le type de document
            type_doc = self._determiner_type_document(texte)
            
            # Générer les suggestions
            suggestions = self._generer_suggestions(texte, infos, vides)
            
            # Organiser les résultats
            resultat = {
                "type_de_document": type_doc,
                "informations_extraites": infos,
                "dates_trouvees": dates,
                "zones_incomplètes": vides,
                "alertes": alertes,
                "suggestions": suggestions,
                "metadata": {
                    "date_analyse": datetime.now().isoformat(),
                    "nombre_dates": len(dates),
                    "nombre_infos": len(infos),
                    "nombre_zones_vides": len(vides),
                    "nombre_alertes": len(alertes)
                }
            }
            
            logger.info("Analyse du document terminée avec succès")
            return resultat
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du document : {str(e)}")
            return {
                "error": str(e),
                "type_de_document": "erreur",
                "informations_extraites": {},
                "dates_trouvees": [],
                "zones_incomplètes": [],
                "alertes": [],
                "suggestions": ["Une erreur est survenue lors de l'analyse"]
            }
    
    def _determiner_type_document(self, texte: str) -> str:
        """
        Détermine le type de document en fonction de son contenu.
        
        Args:
            texte (str): Texte du document
            
        Returns:
            str: Type de document déterminé
        """
        texte_lower = texte.lower()
        
        # Patterns pour différents types de documents
        patterns = {
            "contrat": [
                r"contrat",
                r"convention",
                r"accord",
                r"entre les soussignés",
                r"s'engage à",
                r"obligations",
                r"signataires"
            ],
            "facture": [
                r"facture",
                r"montant",
                r"total",
                r"ht",
                r"tva",
                r"ttc",
                r"règlement"
            ],
            "devis": [
                r"devis",
                r"estimation",
                r"proposition",
                r"validité",
                r"acceptation"
            ],
            "lettre": [
                r"madame",
                r"monsieur",
                r"cordialement",
                r"salutations"
            ]
        }
        
        # Calculer les scores pour chaque type
        scores = {doc_type: 0 for doc_type in patterns}
        
        for doc_type, doc_patterns in patterns.items():
            for pattern in doc_patterns:
                if re.search(pattern, texte_lower):
                    scores[doc_type] += 1
        
        # Déterminer le type avec le score le plus élevé
        max_score = max(scores.values())
        if max_score == 0:
            return "document_general"
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _generer_suggestions(self, texte: str, infos: Dict[str, str], vides: List[str]) -> List[str]:
        """
        Génère des suggestions basées sur l'analyse du document.
        
        Args:
            texte (str): Texte du document
            infos (Dict[str, str]): Informations extraites
            vides (List[str]): Champs vides trouvés
            
        Returns:
            List[str]: Liste des suggestions
        """
        suggestions = []
        
        # Vérifier les champs vides
        if vides:
            suggestions.append("Vérifier les champs vides avant envoi")
        
        # Vérifier la présence d'informations essentielles
        if not infos.get('siret'):
            suggestions.append("Ajouter le numéro SIRET si applicable")
        
        if not infos.get('adresse'):
            suggestions.append("Vérifier la présence de l'adresse complète")
        
        # Vérifier la présence de clauses importantes
        if "contrat" in self._determiner_type_document(texte).lower():
            if "confidentialité" not in texte.lower():
                suggestions.append("Ajouter une clause de confidentialité si nécessaire")
            if "rgpd" not in texte.lower():
                suggestions.append("Ajouter une clause RGPD si nécessaire")
        
        return suggestions 