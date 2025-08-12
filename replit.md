# 🛠️ Documentation Technique - Plateforme de Gestion Immobilière

Ce document fournit les instructions techniques pour l'installation, la configuration et le déploiement de l'application de gestion immobilière.

---

## 🏗️ Structure du Projet
/
├── app.py # Application principale Streamlit
├── utils/
│ ├── auth.py # Système d'authentification (login, register, hash)
│ ├── database.py # Gestionnaire de base de données PostgreSQL (DAL)
│ └── reporting.py # Moteur d'analytics et reporting
├── uploads/properties/ # Dossier pour les images des propriétés
├── .streamlit/config.toml # Configuration Streamlit
├── pyproject.toml # Dépendances Python (pour UV ou PDM/Poetry)
├── README.md # Documentation utilisateur
└── replit.md # Documentation technique (ce fichier)


---

## ⚙️ Installation et Configuration

### Prérequis
- Python 3.9+
- Un serveur de base de données PostgreSQL accessible.
- L'outil de gestion de paquets `uv` (recommandé) ou `pip`.

### 1. Configuration de l'Environnement

Clonez le dépôt et naviguez dans le répertoire du projet.

Créez un environnement virtuel et activez-le :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Avec UV (recommandé)
uv pip install -r requirements.txt # (généré depuis pyproject.toml) ou directement depuis le toml

# Avec PIP
pip install streamlit psycopg2-binary bcrypt pandas plotly pillow

a. Créer la variable d'environnement DATABASE_URL
Dans votre environnement (par exemple, le fichier .env ou les secrets de Replit), définissez la variable :
Generated code

DATABASE_URL="postgresql://VOTRE_USER:VOTRE_MOT_DE_PASSE@VOTRE_HOTE:VOTRE_PORT/VOTRE_DB"