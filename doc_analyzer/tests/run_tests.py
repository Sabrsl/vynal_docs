import os
import sys
import unittest
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_all_tests():
    """Lance tous les tests du projet."""
    # Ajouter le répertoire parent au PYTHONPATH
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Découvrir et lancer tous les tests
    loader = unittest.TestLoader()
    start_dir = str(project_root / "tests")
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Lancer les tests avec un affichage détaillé
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Afficher un résumé des résultats
    logger.info("\nRésumé des tests :")
    logger.info(f"Tests exécutés : {result.testsRun}")
    logger.info(f"Échecs : {len(result.failures)}")
    logger.info(f"Erreurs : {len(result.errors)}")
    
    # Afficher les détails des échecs et erreurs
    if result.failures:
        logger.error("\nÉchecs des tests :")
        for failure in result.failures:
            logger.error(f"\n{failure[1]}")
    
    if result.errors:
        logger.error("\nErreurs des tests :")
        for error in result.errors:
            logger.error(f"\n{error[1]}")
    
    # Retourner le code de sortie approprié
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_all_tests()) 