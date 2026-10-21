# ImmoPro : Plateforme de Gestion Immobilière

Bienvenue sur la Plateforme de Gestion Immobilière, une solution web complète conçue pour simplifier et optimiser toutes les facettes de la gestion de biens immobiliers. Que vous soyez un client à la recherche de la maison de vos rêves, un bailleur souhaitant lister ses propriétés, un agent gérant un portefeuille ou un manager supervisant l'ensemble des opérations, notre plateforme offre des outils puissants et intuitifs adaptés à chaque rôle.

---

## Fonctionnalités Principales

Notre plateforme est conçue autour d'un système de rôles robuste, offrant une expérience personnalisée pour chaque type d'utilisateur.

### Accès Public (Visiteurs)
- **Consultation des Biens :** Parcourez librement l'ensemble des propriétés disponibles à la vente ou à la location.
- **Filtres Avancés :** Affinez votre recherche par type de bien, type de transaction (vente/location), et fourchette de prix.
- **Détails des Propriétés :** Accédez aux fiches détaillées des biens avec description, photos, caractéristiques et prix.
- **Inscription et Connexion :** Créez un compte client ou bailleur, ou connectez-vous à un compte existant.

##### Rôle Client
*Toutes les fonctionnalités publiques, plus :*
- **Gestion des Favoris :** Sauvegardez les propriétés qui vous intéressent pour les retrouver facilement.
- **Prise de Rendez-vous :** Planifiez une visite ou un rendez-vous de transaction directement depuis la fiche d'une propriété.
- **Espace Personnel :** Consultez et gérez vos rendez-vous (modification, annulation).

### Rôle Bailleur
*Toutes les fonctionnalités publiques, plus :*
- **Ajout de Propriétés :** Mettez en ligne vos biens en remplissant un formulaire détaillé (description, photos, prix, etc.).
- **Gestion de Portefeuille :** Suivez l'état de vos propriétés, modifiez leurs informations et activez/désactivez leur disponibilité.
- **Suivi des Agents :** Visualisez l'agent immobilier assigné à la gestion de votre bien.

### Rôle Agent Immobilier
- **Gestion Complète des Propriétés :** Ajoutez, modifiez et gérez l'ensemble des biens de l'agence.
- **Gestion des Clients :** Accédez aux fiches de vos clients assignés et suivez leurs activités.
- **Gestion des Rendez-vous :** Confirmez, gérez et suivez les rendez-vous de votre portefeuille de clients.

### Rôle Manager
*Toutes les fonctionnalités des agents, plus :*
- **Tableau de Bord Analytique :** Accédez à des statistiques et visualisations de données complètes sur les performances de la plateforme :
    - Indicateurs clés de performance (KPIs).
    - Analyse des propriétés (répartition, prix moyens).
    - Analyse des utilisateurs (rôles, inscriptions).
    - Analyse des rendez-vous (statuts, performances des agents).
    - Métriques business (valeur du portefeuille, taux de conversion).
- **Gestion des Utilisateurs :** Supervisez tous les comptes, activez ou désactivez des utilisateurs.
- **Assignation Stratégique :** Assigne-les clients aux agents immobiliers pour optimiser la charge de travail et l'efficacité.

---

## Installation

```bash
# 1. Dependances
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 2. Base de donnees
cp .env.example .env      # puis renseignez DATABASE_URL
createdb immopro          # ou CREATE DATABASE immopro;
psql immopro -f immo.sql  # schema et donnees de demonstration

# 3. Migrations (sur une base deja en service)
./venv/bin/python migrate.py

# 4. Lancement
./venv/bin/streamlit run app.py
```

### Comptes de démonstration

Les quatre comptes partagent le mot de passe `ImmoPro2026!` :
`admin` (manager), `agent1` (agent), `bailleur1` (bailleur), `client1` (client).
Ce sont des exemples : changez-les avant toute mise en ligne.

### Tests

```bash
./venv/bin/python -m unittest discover -s tests -v
```

La suite couvre la logique metier (authentification, limitation des tentatives,
droits du manager, conflits de rendez-vous, pagination, transactions) et le
rendu de chaque espace de l'interface.

---

## Comment Démarrer

1. **Visitez la page d'accueil** pour commencer à explorer les propriétés.
2. **Utilisez les filtres** en haut de la page pour trouver ce que vous cherchez.
3. **Inscrivez-vous** en cliquant sur le bouton "S'inscrire" pour débloquer les fonctionnalités de prise de rendez-vous et de gestion des favoris.
4. **Connectez-vous** pour accéder à votre espace personnel.

---

## Sécurité

- Mots de passe hachés avec bcrypt, jamais stockés en clair.
- Toute donnée saisie par un utilisateur est échappée avant d'être injectée
  en HTML : une annonce ne peut plus transporter de code exécutable.
- Un compte désactivé ne peut plus se connecter.
- Les tentatives de connexion sont limitées à cinq échecs par identifiant et
  par adresse IP sur quinze minutes.
- Les messages d'erreur techniques ne sont jamais affichés : ils sont
  journalisés côté serveur, l'utilisateur reçoit un message générique.
- L'inscription publique n'accepte que les rôles `client` et `bailleur`.
- Toutes les requêtes SQL sont paramétrées, y compris les tris et les
  filtres.
- Les photos importées sont stockées en base sous forme d'octets, avec un
  format et un poids contrôlés : elles survivent au redémarrage de
  l'instance et ne peuvent pas provenir d'un type de fichier non prévu.

---

## Technologies Utilisées
- **Frontend :** Streamlit
- **Backend :** Python
- **Base de données :** PostgreSQL
- **Dépendances clés :** Pandas, Plotly, Bcrypt, Psycopg2