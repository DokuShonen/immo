# Documentation Graphique Exhaustive du Projet Immo (PlantUML)

Ce document fournit une modélisation complète et détaillée du système, basée sur l'implémentation technique réelle. Tous les diagrammes sont conçus pour être rendus via PlantUML.

---

## 1. Diagramme Entité-Relation (ERD) Détaillé
Ce diagramme représente la structure physique et logique de la base de données PostgreSQL.

```plantuml
@startuml
!theme plain
title Modèle de Données Détaillé - Gestion Immobilière

entity "Utilisateurs (users)" as users {
  * id : SERIAL <<PK>>
  --
  username : VARCHAR(50) <<UNIQUE>>
  email : VARCHAR(255) <<UNIQUE>>
  password_hash : VARCHAR(255)
  role : VARCHAR(20) [client, bailleur, agent, manager]
  nom : VARCHAR(100)
  prenom : VARCHAR(100)
  raison_sociale : VARCHAR(255)
  telephone : VARCHAR(20)
  adresse : TEXT
  created_at : TIMESTAMP
  is_active : BOOLEAN
}

entity "Biens (properties)" as properties {
  * id : SERIAL <<PK>>
  --
  bailleur_id : INTEGER <<FK>>
  agent_id : INTEGER <<FK>>
  titre : VARCHAR(255)
  type_bien : VARCHAR(50)
  usage_possible : VARCHAR(50)
  transaction_type : VARCHAR(20) [vente, location]
  situation_geo : VARCHAR(255)
  taille : INTEGER
  prix : DECIMAL(15,2)
  description : TEXT
  is_featured : BOOLEAN
  is_available : BOOLEAN
  created_at : TIMESTAMP
}

entity "Images (property_images)" as images {
  * id : SERIAL <<PK>>
  --
  property_id : INTEGER <<FK>>
  image_path : VARCHAR(500)
  created_at : TIMESTAMP
}

entity "Favoris (favorites)" as favorites {
  * id : SERIAL <<PK>>
  --
  client_id : INTEGER <<FK>>
  property_id : INTEGER <<FK>>
  created_at : TIMESTAMP
}

entity "Rendez-vous (appointments)" as appointments {
  * id : SERIAL <<PK>>
  --
  client_id : INTEGER <<FK>>
  property_id : INTEGER <<FK>>
  agent_id : INTEGER <<FK>>
  date_rdv : TIMESTAMP
  type_rdv : VARCHAR(20) [visite, transaction]
  status : VARCHAR(20) [pending, confirmed, cancelled, completed]
  notes : TEXT
  created_at : TIMESTAMP
}

entity "Assignations (client_assignments)" as assignments {
  * id : SERIAL <<PK>>
  --
  client_id : INTEGER <<FK>>
  agent_id : INTEGER <<FK>>
  assigned_by : INTEGER <<FK>>
  created_at : TIMESTAMP
  is_active : BOOLEAN
}

' Relations avec cardinalités
users ||--o{ properties : "est propriétaire (bailleur)"
users ||--o{ properties : "est responsable (agent)"
properties ||--o{ images : "possède"
users ||--o{ favorites : "ajoute (client)"
properties ||--o{ favorites : "est ajouté"
users ||--o{ appointments : "sollicite (client)"
properties ||--o{ appointments : "fait l'objet de"
users ||--o{ appointments : "gère (agent)"
users ||--o{ assignments : "est affecté (client)"
users ||--o{ assignments : "est assigné (agent)"
users ||--o{ assignments : "ordonne l'affectation (manager)"

@enduml
```

**Légende du Diagramme ERD :**
- `*` : Attribut obligatoire (NOT NULL).
- `<<PK>>` : Clé Primaire (Primary Key), identifiant unique de l'entité.
- `<<FK>>` : Clé Étrangère (Foreign Key), lien vers une clé primaire d'une autre table.
- `||--o{` : Relation "Un à Plusieurs" (1:N). Le côté `||` signifie "exactement un" et le côté `o{` signifie "zéro ou plusieurs".
- `VARCHAR/INTEGER/DECIMAL` : Types de données SQL utilisés.

---

## 2. Diagramme de Cas d'Utilisation
Ce diagramme détaille les fonctionnalités accessibles selon le rôle de l'utilisateur.

```plantuml
@startuml
!theme blueprint
left to right direction
title Cas d'Utilisation par Rôle

actor "Utilisateur" as Public
actor "Client" as Client
actor "Bailleur" as Bailleur
actor "Agent" as Agent
actor "Manager" as Manager

Public <|-- Client
Public <|-- Bailleur
Public <|-- Agent
Public <|-- Manager

package "Système Immo" {
  usecase "Rechercher des biens" as UC_Search
  usecase "S'inscrire / Se connecter" as UC_Auth
  
  usecase "Gérer ses favoris" as UC_Fav
  usecase "Prendre RDV de visite" as UC_Appt_Req
  usecase "Consulter ses RDV" as UC_Appt_View
  
  usecase "Publier un bien" as UC_Prop_Add
  usecase "Gérer ses propres biens" as UC_Prop_Manage
  
  usecase "Gérer son portefeuille clients" as UC_Client_Manage
  usecase "Valider/Gérer les RDV" as UC_Appt_Manage
  
  usecase "Administrer les utilisateurs" as UC_User_Admin
  usecase "Assigner Client -> Agent" as UC_Assign
  usecase "Analyser les statistiques (BI)" as UC_Stats
}

Public --> UC_Search
Public --> UC_Auth

Client --> UC_Fav
Client --> UC_Appt_Req
Client --> UC_Appt_View

Bailleur --> UC_Prop_Add
Bailleur --> UC_Prop_Manage

Agent --> UC_Prop_Add
Agent --> UC_Client_Manage
Agent --> UC_Appt_Manage

Manager --> UC_User_Admin
Manager --> UC_Assign
Manager --> UC_Stats
Manager --> UC_Prop_Add
@enduml
```

**Légende du Diagramme de Cas d'Utilisation :**
- **Bonhomme (Actor)** : Représente un rôle utilisateur externe au système.
- **Ovale (Usecase)** : Représente une fonctionnalité ou un objectif métier du système.
- **Rectangle (Package)** : Délimite le périmètre du système ("Système Immo").
- `-->` : Lien d'interaction. L'acteur déclenche le cas d'utilisation.
- `<|--` : Relation d'héritage/spécialisation. Par exemple, un "Client" hérite de toutes les capacités de l' "Utilisateur Public".

---

## 3. Diagramme de Classes (Architecture Détaillée)
Ce diagramme présente la structure complète du système : le modèle de données (entités), les services de gestion (managers) et l'interface utilisateur.

```plantuml
@startuml
!theme plain
skinparam classAttributeIconSize 0
title Architecture Logicielle Détaillée - Système Immo

' --- Couche Entités (Domaine) ---
package "Modèle de Données" {
  abstract class Utilisateur {
    + id : int
    + username : String
    + email : String
    + password_hash : String
    + nom : String
    + prenom : String
    + telephone : String
    + adresse : String
    + is_active : boolean
  }

  class Client {
    + ajouterFavori(bienId)
    + demanderRendezVous(bienId, date)
  }

  class Bailleur {
    + raison_sociale : String
    + publierBien()
    + modifierBien()
  }

  class Agent {
    + gererPortefeuilleClients()
    + validerRendezVous()
  }

  class Manager {
    + administrerUtilisateurs()
    + assignerAgentClient()
    + consulterStatistiques()
  }

  class Bien {
    + id : int
    + titre : String
    + type_bien : String
    + usage_possible : String
    + transaction_type : String
    + situation_geo : String
    + taille : int
    + prix : double
    + description : String
    + is_featured : boolean
    + is_available : boolean
  }

  class ImageBien {
    + id : int
    + image_path : String
  }

  class RendezVous {
    + id : int
    + date_rdv : DateTime
    + type_rdv : String
    + status : String
    + notes : String
  }

  class Favori {
    + id : int
    + date_ajout : DateTime
  }

  class Assignation {
    + id : int
    + date_assignation : DateTime
    + is_active : boolean
  }

  ' Relations Entités
  Utilisateur <|-- Client
  Utilisateur <|-- Bailleur
  Utilisateur <|-- Agent
  Utilisateur <|-- Manager

  Bailleur "1" -- "0..*" Bien : possède >
  Agent "1" -- "0..*" Bien : gère >
  Bien "1" -- "0..*" ImageBien : possède >
  
  Client "1" -- "0..*" Favori : marque >
  Bien "1" -- "0..*" Favori : est favori >
  
  Client "1" -- "0..*" RendezVous : demande >
  Agent "1" -- "0..*" RendezVous : anime >
  Bien "1" -- "0..*" RendezVous : fait l'objet de >
  
  Client "1" -- "0..*" Assignation : est assigné >
  Agent "1" -- "0..*" Assignation : est responsable >
  Manager "1" -- "0..*" Assignation : effectue l'assignation >
}

' --- Couche Services (Logique Métier) ---
package "Services de Gestion" {
  class GestionnaireBaseDeDonnees {
    - connection_string : String
    + execute_query(requete, params, fetch) : Any
    + get_user_by_username(username) : tuple
    + create_user(...) : tuple
    + get_properties(filtres) : list
    + get_property_by_id(id) : tuple
    + add_property(...) : tuple
    + add_to_favorites(clientId, propId) : bool
    + remove_from_favorites(clientId, propId) : bool
    + get_user_favorites(clientId) : list
    + create_appointment(...) : tuple
    + get_appointments(userId, role) : list
    + get_all_users(role) : list
    + assign_client_to_agent(...) : bool
    + get_statistics() : dict
  }

  class GestionnaireAuthentification {
    - db : GestionnaireBaseDeDonnees
    + hash_password(password) : String
    + verify_password(password, hashed) : bool
    + login(username, password) : dict
    + register(...) : dict
    + logout() : void
    + is_authenticated() : bool
    + require_auth(roles_autorises) : bool
  }

  class MoteurReporting {
    - db : GestionnaireBaseDeDonnees
    + generate_property_analytics() : dict
    + generate_user_analytics() : dict
    + generate_appointment_analytics() : dict
    + generate_business_metrics() : dict
  }
}

' --- Couche Interface ---
package "Interface Utilisateur" {
  class ApplicationStreamlit {
    + main()
    + show_public_access()
    + show_main_app()
    + show_property_listings()
    + show_favorites()
    + show_appointments()
    + show_add_property()
    + show_my_properties()
    + show_my_clients()
    + show_manage_users()
    + show_statistics()
  }
}

' Dépendances Inter-Couches
ApplicationStreamlit ..> GestionnaireAuthentification : utilise
ApplicationStreamlit ..> GestionnaireBaseDeDonnees : utilise
ApplicationStreamlit ..> MoteurReporting : utilise

GestionnaireAuthentification --> GestionnaireBaseDeDonnees : délègue
MoteurReporting --> GestionnaireBaseDeDonnees : délègue

@enduml
```

**Légende du Diagramme de Classes :**
- `+` : Membre public (accessible depuis l'extérieur de la classe).
- `-` : Membre privé (accessible uniquement à l'intérieur de la classe).
- `<|--` : Héritage. La classe fille hérite des attributs et méthodes de la classe parente.
- `--` : Association simple. Représente un lien logique entre deux classes.
- `"1" -- "0..*"` : Multiplicité. Indique qu'un élément de la classe A est lié à zéro ou plusieurs éléments de la classe B.
- `..>` : Dépendance. Indique qu'une classe utilise une autre classe temporairement (ex: appel d'une méthode).
- `-->` : Association dirigée. La classe A connaît la classe B, mais pas forcément l'inverse.

---

## 4. Diagrammes de Séquence (Flux Métier Détaillés)

### A. Authentification et Accès Sécurisé
```plantuml
@startuml
!theme blueprint
title Flux de Connexion et Session

actor Utilisateur
participant "Interface Streamlit" as App
participant "GestionnaireAuthentification" as Auth
participant "GestionnaireBaseDeDonnees" as DB
database "PostgreSQL" as DB_Store

Utilisateur -> App : Saisit identifiants (username, password)
App -> Auth : login(username, password)
Auth -> DB : get_user_by_username(username)
DB -> DB_Store : SELECT * FROM users WHERE username = ...
DB_Store --> DB : Retourne le tuple utilisateur (inclut password_hash)
DB --> Auth : Données utilisateur
Auth -> Auth : verify_password(password, hash)
alt Authentification Réussie
    Auth --> App : Retourne dictionnaire utilisateur
    App -> App : st.session_state.user = user
    App --> Utilisateur : Redirection vers le tableau de bord (rôle spécifique)
else Authentification Échouée
    Auth --> App : Retourne None
    App --> Utilisateur : Affiche "Identifiants incorrects"
end
@enduml
```

### B. Publication d'un Bien Immobilier
```plantuml
@startuml
!theme blueprint
title Flux de Publication d'un Bien

actor "Bailleur / Agent" as User
participant "Interface Streamlit" as App
participant "GestionnaireBaseDeDonnees" as DB
participant "Système de Fichiers" as FS
database "PostgreSQL" as DB_Store

User -> App : Remplit le formulaire de publication
User -> App : Télécharge les photos du bien
App -> DB : add_property(bailleur_id, agent_id, titre, prix, ...)
DB -> DB_Store : INSERT INTO properties ... RETURNING id
DB_Store --> DB : Retourne property_id
DB --> App : Retourne property_id

App -> FS : Crée dossier /uploads/properties/{property_id}/
App -> FS : Sauvegarde les fichiers images
FS --> App : Confirmation sauvegarde

App --> User : Affiche "La fiche immobilière a bien été créée"
@enduml
```

### C. Assignation d'un Client à un Agent (Action Manager)
```plantuml
@startuml
!theme blueprint
title Flux d'Assignation Client -> Agent

actor Manager
participant "Interface Streamlit" as App
participant "GestionnaireBaseDeDonnees" as DB
database "PostgreSQL" as DB_Store

Manager -> App : Sélectionne Client X et Agent Y
Manager -> App : Clique sur "Confirmer l'attribution"
App -> DB : assign_client_to_agent(clientId, agentId, managerId)

DB -> DB_Store : UPDATE client_assignments SET is_active = FALSE WHERE client_id = clientId
DB_Store --> DB : OK

DB -> DB_Store : INSERT INTO client_assignments (client_id, agent_id, assigned_by) ...
DB_Store --> DB : OK

DB --> App : Retourne succès
App --> Manager : Affiche "L'attribution a bien été modifiée"
@enduml
```

### D. Génération de Statistiques BI (Business Intelligence)
```plantuml
@startuml
!theme blueprint
title Flux de Génération d'Analyses (BI)

actor Manager
participant "Interface Streamlit" as App
participant "MoteurReporting" as Reporting
participant "GestionnaireBaseDeDonnees" as DB
database "PostgreSQL" as DB_Store

Manager -> App : Accède à la page "Statistiques"
App -> Reporting : generate_property_analytics()
Reporting -> DB : execute_query("SELECT type_bien, COUNT(*) ...")
DB -> DB_Store : Exécute requêtes d'agrégation
DB_Store --> DB : Résultats bruts
DB --> Reporting : Données
Reporting -> Reporting : Transforme en DataFrames Pandas
Reporting --> App : Retourne dictionnaires d'analyses

App -> Reporting : generate_business_metrics()
Reporting -> DB : execute_query("SELECT SUM(prix) ...")
DB --> Reporting : Valeur totale du portefeuille
Reporting --> App : Métriques financières

App -> App : Génère graphiques Plotly (Bar, Pie)
App --> Manager : Affiche le tableau de bord analytique
@enduml
```

**Légende des Diagrammes de Séquence :**
- **Ligne de vie (Rectangle vertical)** : Représente la durée de vie d'un objet ou acteur pendant l'interaction.
- **Rectangle d'activation (Barre blanche sur la ligne)** : Indique que l'objet est actuellement actif et exécute une opération.
- `->` (Flèche pleine) : Message synchrone. L'émetteur attend une réponse avant de continuer.
- `-->` (Flèche pointillée) : Message de retour. Retourne le résultat d'une opération précédente.
- `alt / else` : Bloc conditionnel (équivalent à un If/Else).
- `Self-call` (Flèche revenant vers soi) : Opération interne à l'objet.

---

## 5. Diagrammes d'État (Cycles de Vie)

### A. Cycle de Vie d'un Rendez-vous
Ce diagramme détaille les transitions de statut pour les rendez-vous, conformément aux contraintes de la base de données.

```plantuml
@startuml
!theme plain
title Cycle de Vie Détaillé d'un Rendez-vous

[*] --> Pending : Création (Client demande une visite)

state Pending : Statut 'pending'\nEn attente de validation par l'Agent
state Confirmed : Statut 'confirmed'\nVisite officiellement planifiée
state Cancelled : Statut 'cancelled'\nRendez-vous annulé, conservé pour historique
state Completed : Statut 'completed'\nVisite terminée, peut mener à une transaction

Pending --> Confirmed : Agent accepte la date/heure
Pending --> Cancelled : Annulé par le client ou l'agent

Confirmed --> Completed : Visite effectuée avec succès
Confirmed --> Cancelled : Annulation de dernière minute

Completed --> [*]
Cancelled --> [*]

note right of Pending : Le client peut annuler tant\nque l'agent n'a pas confirmé.
note right of Confirmed : L'agent marque comme effectué\nune fois la visite terminée.
@enduml
```

### B. Cycle de Vie d'un Bien Immobilier
Ce diagramme représente la gestion de la disponibilité d'un bien sur le marché.

```plantuml
@startuml
!theme plain
title Cycle de Vie de la Disponibilité d'un Bien

[*] --> Disponible : Publication de la fiche

state Disponible : is_available = TRUE\nLe bien est visible dans le catalogue
state Indisponible : is_available = FALSE\nLe bien est masqué (vendu, loué ou retiré)

Disponible --> Indisponible : Retrait du marché / Vente / Location
Indisponible --> Disponible : Remise sur le marché / Nouvelle offre

Disponible --> [*] : Suppression définitive
Indisponible --> [*] : Suppression définitive

note right of Disponible : Le bien peut être mis en avant\n(is_featured = TRUE) pour plus de visibilité.
@enduml
```

### C. Cycle de Vie d'un Utilisateur
Ce diagramme représente la gestion du statut d'activation d'un compte utilisateur.

```plantuml
@startuml
!theme plain
title Cycle de Vie du Compte Utilisateur

[*] --> Actif : Inscription / Création du compte

state Actif : is_active = TRUE\nAccès autorisé aux services
state Inactif : is_active = FALSE\nAccès refusé (compte suspendu ou désactivé)

Actif --> Inactif : Suspension par le Manager
Inactif --> Actif : Réactivation par le Manager

Actif --> [*] : Suppression du compte
Inactif --> [*] : Suppression du compte

note right of Inactif : Un utilisateur inactif ne peut plus\nse connecter même avec des identifiants valides.
@enduml
```

**Légende des Diagrammes d'État :**
- `[*]` (Cercle plein) : Point de départ (Initial State).
- `[*]` (Cercle avec contour) : Point final (Final State).
- **Rectangle arrondi** : Un état du système.
- `-->` : Transition. Représente le changement d'un état à un autre suite à un événement.
- **Note (Rectangle jaune)** : Commentaire explicatif sur le comportement de l'état ou de la transition.
