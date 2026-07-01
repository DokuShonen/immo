import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement (si vous utilisez un .env)
load_dotenv()

# Ajouter le dossier utils au chemin pour pouvoir importer les modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.auth import auth_manager
from utils.database import db_manager

def seed_data():
    """
    Initialise la base de données avec des utilisateurs et des propriétés de test.
    Cette fonction est "idempotente", ce qui signifie que vous pouvez la lancer
    plusieurs fois sans créer de doublons.
    """
    print("Début du seeding de la base de données...")

    # --- 1. Création des utilisateurs de test ---
    users_to_create = [
        {'username': 'admin', 'email': 'admin@immo.com', 'role': 'manager', 'nom': 'Admin', 'prenom': 'Istrateur'},
        {'username': 'agent1', 'email': 'agent1@immo.com', 'role': 'agent', 'nom': 'Dupont', 'prenom': 'Jean'},
        {'username': 'bailleur1', 'email': 'bailleur1@immo.com', 'role': 'bailleur', 'nom': 'Martin', 'prenom': 'Sophie'},
        {'username': 'client1', 'email': 'client1@immo.com', 'role': 'client', 'nom': 'Durand', 'prenom': 'Paul'}
    ]

    created_users = {}
    for user_data in users_to_create:
        # Vérifier si l'utilisateur existe déjà
        existing_user = db_manager.get_user_by_username(user_data['username'])
        if existing_user:
            print(f"L'utilisateur '{user_data['username']}' existe déjà. On passe.")
            created_users[user_data['username']] = existing_user[0] # Stocker l'ID
        else:
            # Créer l'utilisateur via notre AuthManager (qui hache le mot de passe)
            print(f"Création de l'utilisateur '{user_data['username']}'...")
            result = auth_manager.register(
                username=user_data['username'],
                email=user_data['email'],
                password="password",  # Mot de passe en clair, le hachage se fait dans register()
                role=user_data['role'],
                nom=user_data['nom'],
                prenom=user_data['prenom']
            )
            if result.get('success'):
                created_users[user_data['username']] = result.get('user_id')
            else:
                print(f"ERREUR lors de la création de {user_data['username']}: {result.get('message')}")

    # --- 2. Création des propriétés de test ---
    # S'assurer que les IDs des utilisateurs ont été récupérés
    bailleur_id = created_users.get('bailleur1')
    agent_id = created_users.get('agent1')

    if bailleur_id and agent_id:
        properties_to_create = [
            {'titre': 'Superbe Appartement T3 Lumineux - Centre-ville', 'type_bien': 'Appartement', 'transaction_type': 'vente', 'situation_geo': 'Paris 15ème', 'prix': 680000.00, 'taille': 75, 'description': 'Description détaillée...', 'is_featured': True, 'usage_possible': 'Résidentiel'},
            {'titre': 'Maison Familiale avec Jardin', 'type_bien': 'Maison', 'transaction_type': 'location', 'situation_geo': 'Versailles', 'prix': 2500.00, 'taille': 150, 'description': 'Description détaillée...', 'is_featured': False, 'usage_possible': 'Résidentiel'},
        ]

        for prop_data in properties_to_create:
            # On pourrait ajouter une logique pour éviter les doublons si nécessaire
            print(f"Création de la propriété '{prop_data['titre']}'...")
            db_manager.add_property(
                bailleur_id=bailleur_id,
                agent_id=agent_id,
                titre=prop_data['titre'],
                type_bien=prop_data['type_bien'],
                usage_possible=prop_data['usage_possible'],
                transaction_type=prop_data['transaction_type'],
                situation_geo=prop_data['situation_geo'],
                taille=prop_data['taille'],
                prix=prop_data['prix'],
                description=prop_data['description'],
                is_featured=prop_data['is_featured']
            )
    
    print("\nSeeding terminé avec succès !")

if __name__ == "__main__":
    # Pour exécuter ce script, nous avons besoin d'une variable d'environnement DATABASE_URL.
    # Pour faciliter, nous allons l'ajouter à un fichier .env
    if not os.getenv('DATABASE_URL'):
        print("\nERREUR: La variable d'environnement DATABASE_URL n'est pas définie.")
        print("Veuillez la définir dans votre système ou dans un fichier .env à la racine du projet.")
        print("Exemple de .env:")
        print('DATABASE_URL="postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/postgres"')
    else:
        seed_data()