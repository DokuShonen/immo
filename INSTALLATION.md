# Guide Complet d'Installation et d'Exécution

Ce guide vous accompagne dans l'installation du projet, étape par étape, depuis la réception de l'archive ZIP jusqu'au lancement de l'application, sur Windows ou Linux.

---

## 1. Outils nécessaires (Prérequis système)

Avant de commencer, assurez-vous d'avoir installé les logiciels suivants sur votre machine :

| Outil | Description | Lien/Commande d'installation |
| :--- | :--- | :--- |
| **Python 3.10+** | Langage du projet. | [python.org](https://www.python.org/) |
| **PostgreSQL** | Serveur de base de données. | [postgresql.org](https://www.postgresql.org/download/) |

---

## 2. Configuration de la base de données (PostgreSQL)

L'application a besoin d'une base de données PostgreSQL pour fonctionner.

1. **Installez PostgreSQL** : Suivez l'installeur correspondant à votre OS.
2. **Créez un utilisateur et une base de données** :
   - Ouvrez `pgAdmin` ou le terminal `psql`.
   - Créez un utilisateur (ex: `postgres`) avec un mot de passe (ex: `mysecretpassword`).
   - Créez une base de données nommée `postgres` (ou une autre, mais il faudra adapter le `.env`).
   - *Note :* Notez bien ces informations, elles sont cruciales pour l'étape suivante.

---

## 3. Préparation du projet depuis le ZIP

1. **Extraction :** Décompressez l'archive ZIP.
2. **Accès au dossier :** Ouvrez un terminal dans le dossier extrait.
3. **Configuration (`.env`) :**
   - Créez un fichier nommé `.env` (sans extension .txt) à la racine du projet.
   - Ajoutez-y la ligne suivante, **sans guillemets**, en remplaçant les valeurs :
     ```env
     DATABASE_URL=postgresql://utilisateur:motdepasse@localhost:5432/nom_de_la_base
     ```
     *Exemple correct : `DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/postgres`*

---

## 4. Installation de l'environnement Python

Il est fortement conseillé d'utiliser un environnement virtuel.

### Sur Windows
```bash
python -m venv venv
.\venv\Scripts\activate
```

### Sur Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### Installation des dépendances
```bash
pip install -r requirements.txt
# Si vous n'avez pas de requirements.txt, installez :
pip install streamlit psycopg2-binary bcrypt pandas plotly pillow
```

---

## 5. Initialisation de la base de données

Une fois la base de données créée et le fichier `.env` configuré, initialisez les tables :

```bash
python seed_database.py
```

---

## 6. Lancement de l'application

Activez votre environnement virtuel, puis lancez :

```bash
python run_app.py
```

L'application sera accessible sur : **`http://localhost:5000`**

---

## 7. Comptes utilisateurs par défaut

Le mot de passe par défaut pour tous les comptes est : **`password`**

| Username | Rôle | Email |
| :--- | :--- | :--- |
| **admin** | manager | admin@immo.com |
| **agent1** | agent | agent1@immo.com |
| **bailleur1** | bailleur | bailleur1@immo.com |
| **client1** | client | client1@immo.com |

*Sécurité : Changez ces mots de passe après la première connexion.*

---

## 8. Dépannage rapide (FAQ)

- **Erreur "Module not found" :** Vérifiez que vous avez bien activé l'environnement virtuel (`source venv/bin/activate` ou `.\venv\Scripts\activate`) avant de lancer les commandes.
- **Erreur de base de données (FATAL) :** Vérifiez votre `.env`. L'utilisateur ou le mot de passe sont probablement incorrects, ou le serveur PostgreSQL n'est pas lancé.
- **Port 5000 déjà utilisé :** Une autre instance de l'application est probablement ouverte. Fermez-la ou redémarrez votre machine.
