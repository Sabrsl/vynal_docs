# Module de Configuration Distante

Ce module a été restructuré et déplacé de `utils/` vers `admin/remote_config/` pour une meilleure organisation du code.

## Structure des fichiers

- `admin/remote_config/remote_config_admin.py` - Interface d'administration pour gérer les configurations
- `admin/remote_config/remote_config_manager.py` - Gestionnaire de configuration distante
- `admin/remote_config/remote_config_ui.py` - Interface utilisateur pour afficher les mises à jour et messages
- `admin/remote_config/__init__.py` - Exporte les classes principales

## Mise à jour des importations

Si vous utilisiez les anciens modules, vous devez mettre à jour vos importations comme suit :

### Anciennes importations

```python
from utils.remote_config_admin import RemoteConfigAdmin
from utils.remote_config_manager import RemoteConfigManager
from utils.remote_config_ui import RemoteConfigUI
```

### Nouvelles importations

```python
from admin.remote_config import RemoteConfigAdmin, RemoteConfigManager, RemoteConfigUI
```

Ou si vous préférez des importations spécifiques :

```python
from admin.remote_config.remote_config_admin import RemoteConfigAdmin
from admin.remote_config.remote_config_manager import RemoteConfigManager
from admin.remote_config.remote_config_ui import RemoteConfigUI
```

## Intégration avec l'Interface d'Administration

Le module est désormais intégré à l'interface d'administration principale via un nouvel onglet "Config. Distante". 
Cette intégration permet d'accéder facilement à toutes les fonctionnalités de gestion de la configuration à distance.

## Utilisation

L'utilisation des classes reste identique - seul le chemin d'importation a changé.

### Exemple d'utilisation du gestionnaire de configuration

```python
from admin.remote_config import RemoteConfigManager

config_manager = RemoteConfigManager(
    config_url="https://example.com/app_config.json",
    local_cache_dir="./config_cache"
)

# Vérifier les mises à jour
is_update_available, update_info = config_manager.update_is_available()
```

### Exemple d'utilisation de l'UI

```python
from admin.remote_config import RemoteConfigManager, RemoteConfigUI
import tkinter as tk

root = tk.Tk()
config_manager = RemoteConfigManager(
    config_url="https://example.com/app_config.json",
    local_cache_dir="./config_cache"
)

ui = RemoteConfigUI(root, config_manager)
root.mainloop()
```

### Exemple d'utilisation de l'administration

```python
from admin.remote_config import RemoteConfigAdmin

# Lancer l'interface d'administration en mode autonome
admin = RemoteConfigAdmin() 