# Installation et Exécution du Projet

Ce guide explique comment installer et exécuter la plateforme de gestion immobilière en mode développement sur votre machine.

---

## 🛠️ Prérequis
- **Python 3.11+** installé.
- **pip** installé.

---

## 🚀 Installation

Ouvrez un terminal ou une invite de commande à la racine du projet et suivez ces étapes :

### 1. Création de l'environnement virtuel
L'utilisation d'un environnement virtuel est fortement recommandée pour isoler les dépendances.

**Sur Linux (Debian) :**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Sur Windows :**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 2. Installation des dépendances
```bash
pip install -r pyproject.toml
```

---

## 🖥️ Exécution en Mode Développement

Une fois l'environnement configuré, vous pouvez lancer l'application directement :

1. **Dans votre IDE (VS Code, PyCharm, etc.) :**
   - Assurez-vous que l'interpréteur Python sélectionné est celui de l'environnement virtuel (`venv/bin/python` sur Linux ou `venv\Scripts\python.exe` sur Windows).
   - Lancez le script `run_app.py`.

2. **En ligne de commande :**
   ```bash
   # Assurez-vous que l'environnement virtuel est activé
   python run_app.py
   ```

L'application sera accessible dans votre navigateur à l'adresse : **http://localhost:5000**
