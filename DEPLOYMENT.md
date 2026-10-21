# Mise en ligne d'ImmoPro

## Déploiement sur Streamlit Community Cloud

Le dépôt GitHub contient tout ce qu'il faut : `app.py` à la racine,
`requirements.txt`, et le schéma de la base dans `immo.sql`.

1. Se connecter sur <https://streamlit.io/cloud> et choisir
   **New app**, puis **Deploy from a GitHub repository**.
2. Choisir le dépôt `DokuShonen/immo`, la branche `main` et le fichier
   principal `app.py`. La version de Python est déjà épinglée dans
   `pyproject.toml` (3.12).
3. Ouvrir **Advanced settings > Secrets** et ajouter :

   ```toml
   DATABASE_URL = "postgresql://utilisateur:motdepasse@hote:5432/base"
   ```

   L'application lit d'abord la variable d'environnement `DATABASE_URL`, puis
   les secrets de Streamlit : les deux sont acceptés.
4. Cliquer **Deploy**. Le premier démarrage installe les dépendances, une
   à deux minutes suffisent.

### Base de données

La base PostgreSQL de démonstration est hébergée sur Alwaysdata, avec le
schéma et les données de `immo.sql` déjà importés. Les comptes de
démonstration partagent le mot de passe `ImmoPro2026!` :

| Compte | Rôle |
|---|---|
| `admin` | manager |
| `agent1` | agent |
| `bailleur1` | bailleur |
| `client1` | client |

Changez ces identifiants avant toute présentation publique.

### Ce que la plateforme ne fait pas encore

- Pas de paiement en ligne : la prise de rendez-vous est enregistrée, mais
  aucun règlement n'est encaissé.
- Pas d'envoi d'e-mail : les confirmations restent dans l'interface.
- Les photos importées sont conservées dans la base, sous forme d'octets :
  elles survivent donc au redémarrage de l'instance. Chaque image est
  limitée à 4 Mo et chaque annonce à 8 photos.

### Migrations

Le schéma évolue avec des scripts versionnés dans `migrations/`, appliqués
par `migrate.py`. Sur une base déjà en service :

```bash
./venv/bin/python migrate.py            # applique les migrations en attente
./venv/bin/python migrate.py --status   # affiche l'état sans rien modifier
```

La migration `002_images_en_base.sql` ajoute les colonnes qui stockent les
photos en base : elle est indispensable avant la mise en ligne, sinon les
images importées ne sont conservées que sur le disque de l'instance.

## Exécution en local

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env      # renseigner DATABASE_URL
psql immopro -f immo.sql  # schema et donnees de demonstration
./venv/bin/python migrate.py
./venv/bin/streamlit run app.py
```

## Tests

```bash
./venv/bin/python -m unittest discover -s tests -v
```

Les tests s'exécutent sur la base renseignée dans `DATABASE_URL` : ils
créent leurs propres lignes et les suppriment à la fin.
