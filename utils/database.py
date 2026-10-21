"""Acces aux donnees de la plateforme ImmoPro.

Toutes les requetes sont parametrees. Les lignes sont retournees sous forme
de dictionnaires : l'acces par nom de colonne evite qu'un simple
reordonnancement du schema casse silencieusement l'application.
"""
import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


class DatabaseError(RuntimeError):
    """Erreur de base de donnees destinee a l'utilisateur.

    Le detail technique est journalise cote serveur, jamais affiche.
    """


class DatabaseManager:
    def __init__(self):
        self.connection_string = os.getenv('DATABASE_URL')
        if not self.connection_string:
            try:
                self.connection_string = st.secrets["DATABASE_URL"]
            except Exception:
                pass
        if not self.connection_string:
            raise ValueError(
                "DATABASE_URL non définie dans les variables d'environnement ou st.secrets"
            )

    # ------------------------------------------------------------------
    # Connexion
    # ------------------------------------------------------------------
    @contextmanager
    def get_db_connection(self):
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
        except psycopg2.Error as exc:
            if conn:
                conn.rollback()
            log_exception("connexion à la base", exc)
            raise DatabaseError(
                "La base de données est momentanément indisponible. Réessayez dans un instant."
            ) from exc
        finally:
            if conn:
                conn.close()

    def execute_query(self, query, params=None, fetch=None, commit=None):
        """Execute une requete et renvoie les lignes demandees.

        fetch : None (defaut), 'one' ou 'all'.
        commit : None pour déduire de la requete, True ou False pour forcer.
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            try:
                cursor.execute(query, params)
            except psycopg2.Error as exc:
                conn.rollback()
                log_exception("exécution de la requête", exc)
                raise DatabaseError(
                    "L'opération n'a pas pu aboutir. Réessayez dans un instant."
                ) from exc

            result = None
            if fetch == 'one':
                result = cursor.fetchone()
            elif fetch == 'all':
                result = cursor.fetchall()

            if commit is None:
                commit = query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE'))
            if commit:
                conn.commit()

            cursor.close()

            if fetch:
                return result
            return True

    def execute_transaction(self, operations):
        """Execute une suite d'operations dans une seule transaction.

        operations : liste de tuples (query, params). Si une operation
        echoue, rien n'est conserve.
        """
        with self.get_db_connection() as conn:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            try:
                for query, params in operations:
                    cursor.execute(query, params)
                conn.commit()
            except psycopg2.Error as exc:
                conn.rollback()
                log_exception("transaction", exc)
                raise DatabaseError(
                    "L'opération n'a pas pu aboutir. Réessayez dans un instant."
                ) from exc
            finally:
                cursor.close()
        return True

    # ------------------------------------------------------------------
    # Utilisateurs
    # ------------------------------------------------------------------
    def get_user_by_username(self, username):
        return self.execute_query(
            "SELECT * FROM users WHERE username = %s", (username,), fetch='one'
        )

    def get_user_by_email(self, email):
        return self.execute_query(
            "SELECT * FROM users WHERE email = %s", (email,), fetch='one'
        )

    def create_user(self, username, email, password_hash, role, nom, prenom=None,
                    raison_sociale=None, telephone=None, adresse=None):
        return self.execute_query(
            """
            INSERT INTO users (username, email, password_hash, role, nom, prenom,
                               raison_sociale, telephone, adresse)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (username, email, password_hash, role, nom, prenom, raison_sociale,
             telephone, adresse),
            fetch='one',
        )

    def set_user_active(self, user_id, is_active):
        return self.execute_query(
            "UPDATE users SET is_active = %s WHERE id = %s", (is_active, user_id)
        )

    # ------------------------------------------------------------------
    # Tentatives de connexion
    # ------------------------------------------------------------------
    def count_recent_failures(self, username, ip_address, minutes=15):
        """Nombre d'echecs recents pour un couple identifiant + adresse IP."""
        try:
            result = self.execute_query(
                """
                SELECT COUNT(*) AS nb FROM login_attempts
                WHERE username = %s AND ip_address = %s
                  AND created_at >= NOW() - (%s * INTERVAL '1 minute')
                """,
                (username, ip_address, minutes),
                fetch='one',
            )
            return int(result['nb']) if result else 0
        except DatabaseError:
            return 0

    def record_login_failure(self, username, ip_address):
        try:
            self.execute_query(
                "INSERT INTO login_attempts (username, ip_address) VALUES (%s, %s)",
                (username, ip_address),
            )
            # Purge des traces anciennes pour que la table ne grossisse pas.
            self.execute_query(
                "DELETE FROM login_attempts WHERE created_at < NOW() - INTERVAL '2 day'"
            )
        except DatabaseError:
            pass

    def clear_login_failures(self, username, ip_address):
        try:
            self.execute_query(
                "DELETE FROM login_attempts WHERE username = %s AND ip_address = %s",
                (username, ip_address),
            )
        except DatabaseError:
            pass

    # ------------------------------------------------------------------
    # Biens
    # ------------------------------------------------------------------
    SORTS = {
        'recent': "p.created_at DESC, p.id DESC",
        'featured': "p.is_featured DESC, p.created_at DESC",
        'prix_asc': "p.prix ASC",
        'prix_desc': "p.prix DESC",
        'taille_desc': "p.taille DESC",
    }

    def get_price_bounds(self):
        """Bornes de prix des biens disponibles (servent au filtre prix)."""
        result = self.execute_query(
            "SELECT MIN(prix) AS min_prix, MAX(prix) AS max_prix "
            "FROM properties WHERE is_available = TRUE",
            fetch='one',
        )
        if not result or result['min_prix'] is None:
            return 0, 1_000_000
        return int(result['min_prix']), int(result['max_prix'])

    def get_properties(self, filters=None, sort='recent', bailleur_id=None,
                       limit=12, offset=0, count_only=False):
        """Biens disponibles, filtres appliques, pagines.

        bailleur_id : restreint la liste au portefeuille d'un bailleur.
        """
        conditions = ["p.is_available = TRUE"]
        params = []

        if bailleur_id:
            conditions.append("p.bailleur_id = %s")
            params.append(bailleur_id)

        if filters:
            if filters.get('type_bien'):
                conditions.append("p.type_bien = %s")
                params.append(filters['type_bien'])
            if filters.get('transaction_type'):
                conditions.append("p.transaction_type = %s")
                params.append(filters['transaction_type'])
            if filters.get('prix_min') is not None:
                conditions.append("p.prix >= %s")
                params.append(filters['prix_min'])
            if filters.get('prix_max') is not None:
                conditions.append("p.prix <= %s")
                params.append(filters['prix_max'])
            if filters.get('q'):
                conditions.append("(p.titre ILIKE %s OR p.situation_geo ILIKE %s)")
                like = f"%{filters['q'].strip()}%"
                params.extend([like, like])

        where = " AND ".join(conditions)

        if count_only:
            result = self.execute_query(
                f"SELECT COUNT(*) AS nb FROM properties p WHERE {where}",
                params or None,
                fetch='one',
            )
            return int(result['nb']) if result else 0

        query = f"""
        SELECT p.*, u.nom as bailleur_nom, u.raison_sociale as bailleur_raison_sociale,
               a.nom as agent_nom, a.prenom as agent_prenom
        FROM properties p
        LEFT JOIN users u ON p.bailleur_id = u.id
        LEFT JOIN users a ON p.agent_id = a.id
        WHERE {where}
        ORDER BY {self.SORTS.get(sort, self.SORTS['recent'])}
        LIMIT %s OFFSET %s
        """
        query_params = (params or []) + [limit, offset]
        return self.execute_query(query, query_params, fetch='all')

    def get_property_by_id(self, property_id):
        return self.execute_query(
            """
            SELECT p.*, u.nom as bailleur_nom, u.raison_sociale as bailleur_raison_sociale,
                   a.nom as agent_nom, a.prenom as agent_prenom
            FROM properties p
            LEFT JOIN users u ON p.bailleur_id = u.id
            LEFT JOIN users a ON p.agent_id = a.id
            WHERE p.id = %s
            """,
            (property_id,),
            fetch='one',
        )

    def get_properties_by_bailleur(self, bailleur_id, limit=50, offset=0):
        """Portefeuille d'un bailleur, toutes visibilites confondues."""
        return self.execute_query(
            """
            SELECT p.*, u.nom as bailleur_nom, u.raison_sociale as bailleur_raison_sociale,
                   a.nom as agent_nom, a.prenom as agent_prenom
            FROM properties p
            LEFT JOIN users u ON p.bailleur_id = u.id
            LEFT JOIN users a ON p.agent_id = a.id
            WHERE p.bailleur_id = %s
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (bailleur_id, limit, offset),
            fetch='all',
        )

    def add_property(self, bailleur_id, agent_id, titre, type_bien, usage_possible,
                     transaction_type, situation_geo, taille, prix, description,
                     is_featured=False):
        return self.execute_query(
            """
            INSERT INTO properties (bailleur_id, agent_id, titre, type_bien,
                usage_possible, transaction_type, situation_geo, taille, prix,
                description, is_featured)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (bailleur_id, agent_id, titre, type_bien, usage_possible,
             transaction_type, situation_geo, taille, prix, description, is_featured),
            fetch='one',
        )

    def update_property(self, property_id, titre, type_bien, transaction_type,
                        situation_geo, taille, prix, description, is_featured):
        return self.execute_query(
            """
            UPDATE properties
            SET titre = %s, type_bien = %s, transaction_type = %s,
                situation_geo = %s, taille = %s, prix = %s, description = %s,
                is_featured = %s
            WHERE id = %s
            """,
            (titre, type_bien, transaction_type, situation_geo, taille, prix,
             description, is_featured, property_id),
        )

    def toggle_property_status(self, property_id, is_available):
        return self.execute_query(
            "UPDATE properties SET is_available = %s WHERE id = %s",
            (is_available, property_id),
        )

    # ------------------------------------------------------------------
    # Favoris
    # ------------------------------------------------------------------
    def add_to_favorites(self, client_id, property_id):
        return self.execute_query(
            "INSERT INTO favorites (client_id, property_id) VALUES (%s, %s) "
            "ON CONFLICT (client_id, property_id) DO NOTHING",
            (client_id, property_id),
        )

    def is_favorite(self, client_id, property_id):
        result = self.execute_query(
            "SELECT 1 AS present FROM favorites WHERE client_id = %s AND property_id = %s",
            (client_id, property_id),
            fetch='one',
        )
        return result is not None

    def remove_from_favorites(self, client_id, property_id):
        return self.execute_query(
            "DELETE FROM favorites WHERE client_id = %s AND property_id = %s",
            (client_id, property_id),
        )

    def get_user_favorites(self, client_id):
        return self.execute_query(
            """
            SELECT p.*, f.created_at as favorited_at,
                   u.nom as bailleur_nom, a.nom as agent_nom
            FROM favorites f
            JOIN properties p ON p.id = f.property_id
            LEFT JOIN users u ON p.bailleur_id = u.id
            LEFT JOIN users a ON p.agent_id = a.id
            WHERE f.client_id = %s
            ORDER BY f.created_at DESC
            """,
            (client_id,),
            fetch='all',
        )

    # ------------------------------------------------------------------
    # Rendez-vous
    # ------------------------------------------------------------------
    def create_appointment(self, client_id, property_id, agent_id, date_rdv,
                           type_rdv, notes=None):
        return self.execute_query(
            """
            INSERT INTO appointments (client_id, property_id, agent_id, date_rdv,
                                      type_rdv, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (client_id, property_id, agent_id, date_rdv, type_rdv, notes),
            fetch='one',
        )

    def get_appointments(self, user_id, role):
        """Rendez-vous d'un client, ou d'un agent, ou tous pour un manager."""
        if role == 'client':
            query = """
            SELECT a.*, p.titre as property_titre,
                   u.nom as agent_nom, u.prenom as agent_prenom
            FROM appointments a
            JOIN properties p ON a.property_id = p.id
            JOIN users u ON a.agent_id = u.id
            WHERE a.client_id = %s
            ORDER BY a.date_rdv DESC
            """
            params = (user_id,)
        else:
            conditions = []
            params = []
            if role == 'agent':
                conditions.append("a.agent_id = %s")
                params.append(user_id)
            query = """
            SELECT a.*, p.titre as property_titre,
                   c.nom as client_nom, c.prenom as client_prenom,
                   ag.nom as agent_nom, ag.prenom as agent_prenom
            FROM appointments a
            JOIN properties p ON a.property_id = p.id
            JOIN users c ON a.client_id = c.id
            JOIN users ag ON a.agent_id = ag.id
            {where}
            ORDER BY a.date_rdv DESC
            """.format(where="WHERE " + " AND ".join(conditions) if conditions else "")
        return self.execute_query(query, params or None, fetch='all')

    def get_appointment_by_id(self, appointment_id):
        return self.execute_query(
            "SELECT * FROM appointments WHERE id = %s", (appointment_id,), fetch='one'
        )

    def get_conflicting_appointments(self, agent_id, date_rdv, exclude_id=None,
                                    minutes=60):
        """Rendez-vous de l'agent autour du meme creneau."""
        conditions = [
            "agent_id = %s",
            "status IN ('pending', 'confirmed')",
            "date_rdv >= %s - (%s * INTERVAL '1 minute')",
            "date_rdv < %s + (%s * INTERVAL '1 minute')",
        ]
        params = [agent_id, date_rdv, minutes, date_rdv, minutes]
        if exclude_id:
            conditions.append("id <> %s")
            params.append(exclude_id)
        return self.execute_query(
            "SELECT * FROM appointments WHERE " + " AND ".join(conditions) + " ORDER BY date_rdv",
            params,
            fetch='all',
        )

    def update_appointment_status(self, appointment_id, status):
        return self.execute_query(
            "UPDATE appointments SET status = %s WHERE id = %s", (status, appointment_id)
        )

    def delete_appointment(self, appointment_id):
        return self.execute_query(
            "DELETE FROM appointments WHERE id = %s", (appointment_id,)
        )

    # ------------------------------------------------------------------
    # Assignations clients / agents
    # ------------------------------------------------------------------
    def assign_client_to_agent(self, client_id, agent_id, assigned_by):
        """Affecte un client a un agent. Les deux ecritures sont atomiques."""
        return self.execute_transaction([
            (
                "UPDATE client_assignments SET is_active = FALSE "
                "WHERE client_id = %s AND is_active = TRUE",
                (client_id,),
            ),
            (
                "INSERT INTO client_assignments (client_id, agent_id, assigned_by) "
                "VALUES (%s, %s, %s)",
                (client_id, agent_id, assigned_by),
            ),
        ])

    def get_clients_for_agent(self, agent_id, role='agent'):
        """Clients assignes a un agent ; un manager voit tous les clients."""
        conditions = ["u.role = 'client'"]
        params = []
        if role == 'agent':
            conditions.append("ca.agent_id = %s")
            params.append(agent_id)
        query = """
        SELECT u.*, ca.created_at as assigned_date, ca.agent_id as assigned_agent_id,
               ag.nom as agent_nom, ag.prenom as agent_prenom
        FROM users u
        JOIN client_assignments ca ON u.id = ca.client_id
        LEFT JOIN users ag ON ca.agent_id = ag.id
        WHERE ca.is_active = TRUE AND {conditions}
        ORDER BY ca.created_at DESC
        """.format(conditions=" AND ".join(conditions))
        return self.execute_query(query, params or None, fetch='all')

    # ------------------------------------------------------------------
    # Utilisateurs
    # ------------------------------------------------------------------
    def get_all_users(self, role=None, include_inactive=False):
        conditions = []
        params = []
        if role:
            conditions.append("role = %s")
            params.append(role)
        if not include_inactive:
            conditions.append("is_active = TRUE")
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        return self.execute_query(
            f"SELECT * FROM users {where} ORDER BY role, nom", params or None, fetch='all'
        )

    # ------------------------------------------------------------------
    # Statistiques
    # ------------------------------------------------------------------
    def get_statistics(self):
        stats = {}

        result = self.execute_query(
            "SELECT COUNT(*) AS nb FROM properties WHERE is_available = TRUE", fetch='one')
        stats['total_properties'] = int(result['nb']) if result else 0

        result = self.execute_query(
            "SELECT COUNT(DISTINCT situation_geo) AS nb FROM properties WHERE is_available = TRUE",
            fetch='one')
        stats['total_cities'] = int(result['nb']) if result else 0

        result = self.execute_query(
            "SELECT type_bien, COUNT(*) AS nb FROM properties WHERE is_available = TRUE "
            "GROUP BY type_bien", fetch='all')
        stats['properties_by_type'] = {r['type_bien']: int(r['nb']) for r in result} if result else {}

        result = self.execute_query(
            "SELECT transaction_type, COUNT(*) AS nb FROM properties WHERE is_available = TRUE "
            "GROUP BY transaction_type", fetch='all')
        stats['properties_by_transaction'] = {
            r['transaction_type']: int(r['nb']) for r in result} if result else {}

        result = self.execute_query(
            "SELECT role, COUNT(*) AS nb FROM users WHERE is_active = TRUE GROUP BY role",
            fetch='all')
        stats['users_by_role'] = {r['role']: int(r['nb']) for r in result} if result else {}

        result = self.execute_query(
            "SELECT COUNT(*) AS nb FROM appointments", fetch='one')
        stats['total_appointments'] = int(result['nb']) if result else 0

        return stats


def log_exception(contexte, exc):
    """Journalise une erreur technique sans l'exposer a l'utilisateur."""
    import traceback
    traceback.print_exc()
    print(f"[ImmoPro] Erreur lors de {contexte} : {exc}")


db_manager = DatabaseManager()
