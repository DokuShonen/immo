"""Agregations et statistiques destinees au tableau de bord du manager."""
import pandas as pd

from utils.database import db_manager


class ReportingEngine:
    def __init__(self):
        self.db = db_manager

    def generate_property_analytics(self):
        analytics = {}

        result = self.db.execute_query(
            "SELECT type_bien, COUNT(*) AS nb FROM properties "
            "WHERE is_available = TRUE GROUP BY type_bien",
            fetch='all',
        )
        analytics['property_types'] = {r['type_bien']: int(r['nb']) for r in result} if result else {}

        result = self.db.execute_query(
            """
            SELECT transaction_type, AVG(prix) AS prix_moyen,
                   MIN(prix) AS prix_min, MAX(prix) AS prix_max
            FROM properties WHERE is_available = TRUE GROUP BY transaction_type
            """,
            fetch='all',
        )
        analytics['price_stats_df'] = (
            pd.DataFrame(result).rename(columns={
                'transaction_type': 'transaction_type',
                'prix_moyen': 'prix_moyen',
                'prix_min': 'prix_min',
                'prix_max': 'prix_max',
            }) if result else pd.DataFrame()
        )

        result = self.db.execute_query(
            "SELECT situation_geo, COUNT(*) AS nb FROM properties "
            "WHERE is_available = TRUE GROUP BY situation_geo ORDER BY nb DESC LIMIT 10",
            fetch='all',
        )
        analytics['geographic_distribution_df'] = (
            pd.DataFrame(result).rename(columns={
                'situation_geo': 'Localisation',
                'nb': 'Nombre',
            }) if result else pd.DataFrame()
        )

        return analytics

    def generate_user_analytics(self):
        analytics = {}

        result = self.db.execute_query(
            "SELECT role, COUNT(*) AS nb FROM users WHERE is_active = TRUE GROUP BY role",
            fetch='all',
        )
        analytics['user_roles'] = {r['role']: int(r['nb']) for r in result} if result else {}

        result = self.db.execute_query(
            """
            SELECT COUNT(*) AS total_assignments,
                   COUNT(DISTINCT client_id) AS unique_clients,
                   COUNT(DISTINCT agent_id) AS unique_agents
            FROM client_assignments WHERE is_active = TRUE
            """,
            fetch='one',
        )
        analytics['assignment_stats'] = result if result else (0, 0, 0)

        analytics['registration_trends_df'] = pd.DataFrame(columns=['Mois', 'Inscriptions'])

        return analytics

    def generate_appointment_analytics(self):
        analytics = {}

        result = self.db.execute_query(
            "SELECT status, COUNT(*) AS nb FROM appointments GROUP BY status",
            fetch='all',
        )
        analytics['appointment_status'] = {r['status']: int(r['nb']) for r in result} if result else {}

        result = self.db.execute_query(
            "SELECT type_rdv, COUNT(*) AS nb FROM appointments GROUP BY type_rdv",
            fetch='all',
        )
        analytics['appointment_types'] = {r['type_rdv']: int(r['nb']) for r in result} if result else {}

        # Le manager suit tous les agents, pas seulement lui-meme.
        result = self.db.execute_query(
            """
            SELECT u.nom, u.prenom, COUNT(a.id) AS appointments_handled
            FROM users u LEFT JOIN appointments a ON u.id = a.agent_id
            WHERE u.role IN ('agent', 'manager') AND u.is_active = TRUE
            GROUP BY u.id, u.nom, u.prenom ORDER BY appointments_handled DESC
            """,
            fetch='all',
        )
        analytics['agent_performance_df'] = (
            pd.DataFrame(result).rename(columns={
                'nom': 'Nom',
                'prenom': 'Prenom',
                'appointments_handled': 'RDV_Geres',
            }) if result else pd.DataFrame()
        )

        return analytics

    def generate_business_metrics(self):
        metrics = {}

        # La valeur du portefeuille et le revenu locatif ne se melangent pas :
        # additionner un prix de vente et un loyer mensuel n'a aucun sens.
        result = self.db.execute_query(
            "SELECT COALESCE(SUM(prix), 0) AS total, COALESCE(AVG(prix), 0) AS moyenne "
            "FROM properties WHERE is_available = TRUE AND transaction_type = 'vente'",
            fetch='one',
        )
        metrics['portfolio_value'] = (
            (float(result['total']), float(result['moyenne'])) if result else (0.0, 0.0)
        )

        result = self.db.execute_query(
            "SELECT COALESCE(SUM(prix), 0) AS total, COUNT(*) AS nb "
            "FROM properties WHERE is_available = TRUE AND transaction_type = 'location'",
            fetch='one',
        )
        metrics['rental_income'] = (
            (float(result['total']), int(result['nb'])) if result else (0.0, 0)
        )

        # Taux de conversion : les rendez-vous annules ne comptent pas.
        result = self.db.execute_query(
            """
            SELECT COUNT(*) FILTER (WHERE status = 'completed') AS aboutis,
                   COUNT(*) FILTER (WHERE status <> 'cancelled') AS total
            FROM appointments
            """,
            fetch='one',
        )
        if result and result['total'] > 0:
            metrics['conversion_rate'] = (result['aboutis'] / result['total']) * 100
        else:
            metrics['conversion_rate'] = 0.0

        result = self.db.execute_query(
            "SELECT type_bien, transaction_type, COUNT(*) AS nb FROM properties "
            "WHERE is_available = TRUE GROUP BY type_bien, transaction_type ORDER BY nb DESC",
            fetch='all',
        )
        metrics['popular_combinations_df'] = (
            pd.DataFrame(result).rename(columns={
                'type_bien': 'Type',
                'transaction_type': 'Transaction',
                'nb': 'Nombre',
            }) if result else pd.DataFrame()
        )

        result = self.db.execute_query(
            """
            SELECT p.titre, COUNT(f.id) AS favorite_count
            FROM properties p LEFT JOIN favorites f ON p.id = f.property_id
            WHERE p.is_available = TRUE
            GROUP BY p.id, p.titre ORDER BY favorite_count DESC LIMIT 10
            """,
            fetch='all',
        )
        metrics['most_favorited_df'] = (
            pd.DataFrame(result).rename(columns={
                'titre': 'Propriete',
                'favorite_count': 'Favoris',
            }) if result else pd.DataFrame()
        )

        return metrics


reporting_engine = ReportingEngine()
