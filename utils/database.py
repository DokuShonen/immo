import psycopg2
import os
from contextlib import contextmanager
import streamlit as st

# DANS utils/database.py, REMPLACEZ LA CLASSE EXISTANTE PAR CELLE-CI

class DatabaseManager:
    def __init__(self):
        self.connection_string = os.getenv('DATABASE_URL')
    
    @contextmanager
    def get_db_connection(self):
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            st.error(f"Erreur de base de données: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query, params=None, fetch=None):
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            result = None
            if fetch == 'one':
                result = cursor.fetchone()
            elif fetch == 'all':
                result = cursor.fetchall()
            
            # Si c'était une opération d'écriture, on valide la transaction.
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                conn.commit()
            
            cursor.close()
            
            if fetch:
                return result
            else:
                return True

    # --- FONCTION MANQUANTE RESTAURÉE ICI ---
    def get_user_by_username(self, username):
        query = "SELECT * FROM users WHERE username = %s"
        return self.execute_query(query, (username,), fetch='one')
    
    def create_user(self, username, email, password_hash, role, nom, prenom=None, raison_sociale=None, telephone=None, adresse=None):
        query = """
        INSERT INTO users (username, email, password_hash, role, nom, prenom, raison_sociale, telephone, adresse)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        return self.execute_query(query, (username, email, password_hash, role, nom, prenom, raison_sociale, telephone, adresse), fetch='one')
    
    def get_properties(self, filters=None):
        query = """
        SELECT p.*, u.nom as bailleur_nom, u.raison_sociale as bailleur_raison_sociale,
               a.nom as agent_nom, a.prenom as agent_prenom
        FROM properties p
        LEFT JOIN users u ON p.bailleur_id = u.id
        LEFT JOIN users a ON p.agent_id = a.id
        WHERE p.is_available = TRUE
        """
        params = []
        
        if filters:
            if filters.get('type_bien'):
                query += " AND p.type_bien = %s"
                params.append(filters['type_bien'])
            if filters.get('transaction_type'):
                query += " AND p.transaction_type = %s"
                params.append(filters['transaction_type'])
            if filters.get('prix_min'):
                query += " AND p.prix >= %s"
                params.append(filters['prix_min'])
            if filters.get('prix_max'):
                query += " AND p.prix <= %s"
                params.append(filters['prix_max'])
        
        query += " ORDER BY p.is_featured DESC, p.created_at DESC"
        return self.execute_query(query, params if params else None, fetch='all')
    
    def get_property_by_id(self, property_id):
        query = """
        SELECT p.*, u.nom as bailleur_nom, u.raison_sociale as bailleur_raison_sociale,
               a.nom as agent_nom, a.prenom as agent_prenom
        FROM properties p
        LEFT JOIN users u ON p.bailleur_id = u.id
        LEFT JOIN users a ON p.agent_id = a.id
        WHERE p.id = %s
        """
        return self.execute_query(query, (property_id,), fetch='one')
    
    def add_property(self, bailleur_id, agent_id, titre, type_bien, usage_possible, transaction_type, situation_geo, taille, prix, description, is_featured=False):
        query = """
        INSERT INTO properties (bailleur_id, agent_id, titre, type_bien, usage_possible, transaction_type, situation_geo, taille, prix, description, is_featured)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        return self.execute_query(query, (bailleur_id, agent_id, titre, type_bien, usage_possible, transaction_type, situation_geo, taille, prix, description, is_featured), fetch='one')
    
    def add_to_favorites(self, client_id, property_id):
        query = "INSERT INTO favorites (client_id, property_id) VALUES (%s, %s) ON CONFLICT (client_id, property_id) DO NOTHING"
        return self.execute_query(query, (client_id, property_id))
    
    def remove_from_favorites(self, client_id, property_id):
        query = "DELETE FROM favorites WHERE client_id = %s AND property_id = %s"
        return self.execute_query(query, (client_id, property_id))
    
    def get_user_favorites(self, client_id):
        query = """
        SELECT p.*, f.created_at as favorited_at
        FROM properties p
        JOIN favorites f ON p.id = f.property_id
        WHERE f.client_id = %s
        ORDER BY f.created_at DESC
        """
        return self.execute_query(query, (client_id,), fetch='all')
    
    def create_appointment(self, client_id, property_id, agent_id, date_rdv, type_rdv, notes=None):
        query = """
        INSERT INTO appointments (client_id, property_id, agent_id, date_rdv, type_rdv, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        return self.execute_query(query, (client_id, property_id, agent_id, date_rdv, type_rdv, notes), fetch='one')
    
    def get_appointments(self, user_id, role):
        if role == 'client':
            query = """
            SELECT a.*, p.titre as property_titre, u.nom as agent_nom, u.prenom as agent_prenom
            FROM appointments a
            JOIN properties p ON a.property_id = p.id
            JOIN users u ON a.agent_id = u.id
            WHERE a.client_id = %s
            ORDER BY a.date_rdv DESC
            """
            return self.execute_query(query, (user_id,), fetch='all')
        elif role in ['agent', 'manager']:
            query = """
            SELECT a.*, p.titre as property_titre, c.nom as client_nom, c.prenom as client_prenom
            FROM appointments a
            JOIN properties p ON a.property_id = p.id
            JOIN users c ON a.client_id = c.id
            WHERE a.agent_id = %s
            ORDER BY a.date_rdv DESC
            """
            return self.execute_query(query, (user_id,), fetch='all')
    
    def get_statistics(self):
        stats = {}
        
        # Total properties
        result = self.execute_query("SELECT COUNT(*) FROM properties WHERE is_available = TRUE", fetch='one')
        stats['total_properties'] = result[0] if result else 0
        
        # Properties by type
        result = self.execute_query("SELECT type_bien, COUNT(*) FROM properties WHERE is_available = TRUE GROUP BY type_bien", fetch='all')
        stats['properties_by_type'] = dict(result) if result else {}
        
        # Properties by transaction type
        result = self.execute_query("SELECT transaction_type, COUNT(*) FROM properties WHERE is_available = TRUE GROUP BY transaction_type", fetch='all')
        stats['properties_by_transaction'] = dict(result) if result else {}
        
        # Total users by role
        result = self.execute_query("SELECT role, COUNT(*) FROM users WHERE is_active = TRUE GROUP BY role", fetch='all')
        stats['users_by_role'] = dict(result) if result else {}
        
        # Total appointments
        result = self.execute_query("SELECT COUNT(*) FROM appointments", fetch='one')
        stats['total_appointments'] = result[0] if result else 0
        
        return stats
    
    def get_all_users(self, role=None):
        if role:
            query = "SELECT * FROM users WHERE role = %s AND is_active = TRUE ORDER BY nom"
            return self.execute_query(query, (role,), fetch='all')
        else:
            query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY role, nom"
            return self.execute_query(query, fetch='all')
    
    def assign_client_to_agent(self, client_id, agent_id, assigned_by):
        # Deactivate previous assignments
        self.execute_query("UPDATE client_assignments SET is_active = FALSE WHERE client_id = %s", (client_id,))
        
        # Create new assignment
        query = """
        INSERT INTO client_assignments (client_id, agent_id, assigned_by)
        VALUES (%s, %s, %s)
        """
        return self.execute_query(query, (client_id, agent_id, assigned_by))
    
    # COLLEZ CETTE VERSION CORRIGÉE DANS utils/database.py

def execute_query(self, query, params=None, fetch=None):
    with self.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        result = None
        if fetch == 'one':
            result = cursor.fetchone()
        elif fetch == 'all':
            result = cursor.fetchall()
        
        # Si ce n'était pas une simple lecture, on valide la transaction.
        # Une requête avec RETURNING (comme notre INSERT) aura un fetch='one'.
        # On se base sur le type de requête. Si elle commence par INSERT, UPDATE, ou DELETE, on commit.
        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            conn.commit()
        
        cursor.close()
        
        if fetch:
            return result
        else:
            return True
    
    def get_user_by_username(self, username):
        query = "SELECT * FROM users WHERE username = %s"
        return self.execute_query(query, (username,), fetch='one')
    
    def create_user(self, username, email, password_hash, role, nom, prenom=None, raison_sociale=None, telephone=None, adresse=None):
        query = """
        INSERT INTO users (username, email, password_hash, role, nom, prenom, raison_sociale, telephone, adresse)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        return self.execute_query(query, (username, email, password_hash, role, nom, prenom, raison_sociale, telephone, adresse), fetch='one')
    
    def get_properties(self, filters=None):
        query = """
        SELECT p.*, u.nom as bailleur_nom, u.raison_sociale as bailleur_raison_sociale,
               a.nom as agent_nom, a.prenom as agent_prenom
        FROM properties p
        LEFT JOIN users u ON p.bailleur_id = u.id
        LEFT JOIN users a ON p.agent_id = a.id
        WHERE p.is_available = TRUE
        """
        params = []
        
        if filters:
            if filters.get('type_bien'):
                query += " AND p.type_bien = %s"
                params.append(filters['type_bien'])
            if filters.get('transaction_type'):
                query += " AND p.transaction_type = %s"
                params.append(filters['transaction_type'])
            if filters.get('prix_min'):
                query += " AND p.prix >= %s"
                params.append(filters['prix_min'])
            if filters.get('prix_max'):
                query += " AND p.prix <= %s"
                params.append(filters['prix_max'])
        
        query += " ORDER BY p.is_featured DESC, p.created_at DESC"
        return self.execute_query(query, params if params else None, fetch='all')
    
    def get_property_by_id(self, property_id):
        query = """
        SELECT p.*, u.nom as bailleur_nom, u.raison_sociale as bailleur_raison_sociale,
               a.nom as agent_nom, a.prenom as agent_prenom
        FROM properties p
        LEFT JOIN users u ON p.bailleur_id = u.id
        LEFT JOIN users a ON p.agent_id = a.id
        WHERE p.id = %s
        """
        return self.execute_query(query, (property_id,), fetch='one')
    
    def add_property(self, bailleur_id, agent_id, titre, type_bien, usage_possible, transaction_type, situation_geo, taille, prix, description, is_featured=False):
        query = """
        INSERT INTO properties (bailleur_id, agent_id, titre, type_bien, usage_possible, transaction_type, situation_geo, taille, prix, description, is_featured)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        return self.execute_query(query, (bailleur_id, agent_id, titre, type_bien, usage_possible, transaction_type, situation_geo, taille, prix, description, is_featured), fetch='one')
    
    def add_to_favorites(self, client_id, property_id):
        query = "INSERT INTO favorites (client_id, property_id) VALUES (%s, %s) ON CONFLICT (client_id, property_id) DO NOTHING"
        return self.execute_query(query, (client_id, property_id))
    
    def remove_from_favorites(self, client_id, property_id):
        query = "DELETE FROM favorites WHERE client_id = %s AND property_id = %s"
        return self.execute_query(query, (client_id, property_id))
    
    def get_user_favorites(self, client_id):
        query = """
        SELECT p.*, f.created_at as favorited_at
        FROM properties p
        JOIN favorites f ON p.id = f.property_id
        WHERE f.client_id = %s
        ORDER BY f.created_at DESC
        """
        return self.execute_query(query, (client_id,), fetch='all')
    
    def create_appointment(self, client_id, property_id, agent_id, date_rdv, type_rdv, notes=None):
        query = """
        INSERT INTO appointments (client_id, property_id, agent_id, date_rdv, type_rdv, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        return self.execute_query(query, (client_id, property_id, agent_id, date_rdv, type_rdv, notes), fetch='one')
    
    def get_appointments(self, user_id, role):
        if role == 'client':
            query = """
            SELECT a.*, p.titre as property_titre, u.nom as agent_nom, u.prenom as agent_prenom
            FROM appointments a
            JOIN properties p ON a.property_id = p.id
            JOIN users u ON a.agent_id = u.id
            WHERE a.client_id = %s
            ORDER BY a.date_rdv DESC
            """
            return self.execute_query(query, (user_id,), fetch='all')
        elif role in ['agent', 'manager']:
            query = """
            SELECT a.*, p.titre as property_titre, c.nom as client_nom, c.prenom as client_prenom
            FROM appointments a
            JOIN properties p ON a.property_id = p.id
            JOIN users c ON a.client_id = c.id
            WHERE a.agent_id = %s
            ORDER BY a.date_rdv DESC
            """
            return self.execute_query(query, (user_id,), fetch='all')
    
    def get_statistics(self):
        stats = {}
        
        # Total properties
        result = self.execute_query("SELECT COUNT(*) FROM properties WHERE is_available = TRUE", fetch='one')
        stats['total_properties'] = result[0] if result else 0
        
        # Properties by type
        result = self.execute_query("SELECT type_bien, COUNT(*) FROM properties WHERE is_available = TRUE GROUP BY type_bien", fetch='all')
        stats['properties_by_type'] = dict(result) if result else {}
        
        # Properties by transaction type
        result = self.execute_query("SELECT transaction_type, COUNT(*) FROM properties WHERE is_available = TRUE GROUP BY transaction_type", fetch='all')
        stats['properties_by_transaction'] = dict(result) if result else {}
        
        # Total users by role
        result = self.execute_query("SELECT role, COUNT(*) FROM users WHERE is_active = TRUE GROUP BY role", fetch='all')
        stats['users_by_role'] = dict(result) if result else {}
        
        # Total appointments
        result = self.execute_query("SELECT COUNT(*) FROM appointments", fetch='one')
        stats['total_appointments'] = result[0] if result else 0
        
        return stats
    
    def get_all_users(self, role=None):
        if role:
            query = "SELECT * FROM users WHERE role = %s AND is_active = TRUE ORDER BY nom"
            return self.execute_query(query, (role,), fetch='all')
        else:
            query = "SELECT * FROM users WHERE is_active = TRUE ORDER BY role, nom"
            return self.execute_query(query, fetch='all')
    
    def assign_client_to_agent(self, client_id, agent_id, assigned_by):
        # Deactivate previous assignments
        self.execute_query("UPDATE client_assignments SET is_active = FALSE WHERE client_id = %s", (client_id,))
        
        # Create new assignment
        query = """
        INSERT INTO client_assignments (client_id, agent_id, assigned_by)
        VALUES (%s, %s, %s)
        """
        return self.execute_query(query, (client_id, agent_id, assigned_by))

db_manager = DatabaseManager()