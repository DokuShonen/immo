# Fichier : utils/reporting.py
import pandas as pd
from utils.database import db_manager

class ReportingEngine:
    def __init__(self):
        self.db = db_manager
    
    def generate_property_analytics(self):
        analytics = {}
        
        query_types = "SELECT type_bien, COUNT(*) as count FROM properties WHERE is_available = TRUE GROUP BY type_bien"
        result_types = self.db.execute_query(query_types, fetch='all')
        analytics['property_types'] = dict(result_types) if result_types else {}
        
        query_prices = """
        SELECT transaction_type, AVG(prix) as avg_price, MIN(prix) as min_price, MAX(prix) as max_price
        FROM properties WHERE is_available = TRUE GROUP BY transaction_type
        """
        result_prices = self.db.execute_query(query_prices, fetch='all')
        if result_prices:
            analytics['price_stats_df'] = pd.DataFrame(result_prices, columns=['transaction_type', 'avg_price', 'min_price', 'max_price'])
        else:
            analytics['price_stats_df'] = pd.DataFrame() # DataFrame vide

        query_geo = "SELECT situation_geo, COUNT(*) as count FROM properties WHERE is_available = TRUE GROUP BY situation_geo ORDER BY count DESC LIMIT 10"
        result_geo = self.db.execute_query(query_geo, fetch='all')
        if result_geo:
            analytics['geographic_distribution_df'] = pd.DataFrame(result_geo, columns=['Localisation', 'Nombre'])
        else:
            analytics['geographic_distribution_df'] = pd.DataFrame()

        return analytics
    
    def generate_user_analytics(self):
        analytics = {}
        
        query_roles = "SELECT role, COUNT(*) as count FROM users WHERE is_active = TRUE GROUP BY role"
        result_roles = self.db.execute_query(query_roles, fetch='all')
        analytics['user_roles'] = dict(result_roles) if result_roles else {}
        
        query_assign = """
        SELECT COUNT(*) as total_assignments, COUNT(DISTINCT client_id) as unique_clients, COUNT(DISTINCT agent_id) as unique_agents
        FROM client_assignments WHERE is_active = TRUE
        """
        result_assign = self.db.execute_query(query_assign, fetch='one')
        analytics['assignment_stats'] = result_assign if result_assign else (0, 0, 0)
        
        # Pour le graphique manquant de registration_trends (on le simule pour éviter une erreur)
        analytics['registration_trends_df'] = pd.DataFrame(columns=['Mois', 'Inscriptions'])

        return analytics
    
    def generate_appointment_analytics(self):
        analytics = {}
        
        query_status = "SELECT status, COUNT(*) as count FROM appointments GROUP BY status"
        result_status = self.db.execute_query(query_status, fetch='all')
        analytics['appointment_status'] = dict(result_status) if result_status else {}
        
        query_types = "SELECT type_rdv, COUNT(*) as count FROM appointments GROUP BY type_rdv"
        result_types = self.db.execute_query(query_types, fetch='all')
        analytics['appointment_types'] = dict(result_types) if result_types else {}
        
        query_perf = """
        SELECT u.nom, u.prenom, COUNT(a.id) as appointments_handled
        FROM users u LEFT JOIN appointments a ON u.id = a.agent_id
        WHERE u.role IN ('agent', 'manager') AND u.is_active = TRUE
        GROUP BY u.id, u.nom, u.prenom ORDER BY appointments_handled DESC
        """
        result_perf = self.db.execute_query(query_perf, fetch='all')
        if result_perf:
            analytics['agent_performance_df'] = pd.DataFrame(result_perf, columns=['Nom', 'Prenom', 'RDV_Gérés'])
        else:
            analytics['agent_performance_df'] = pd.DataFrame()

        return analytics
    
    def generate_business_metrics(self):
        metrics = {}
        
        query_value = "SELECT SUM(prix) as total_value, AVG(prix) as avg_price FROM properties WHERE is_available = TRUE"
        result_value = self.db.execute_query(query_value, fetch='one')
        metrics['portfolio_value'] = result_value if result_value else (0, 0)
        
        query_conv = "SELECT COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed, COUNT(*) as total FROM appointments"
        result_conv = self.db.execute_query(query_conv, fetch='one')
        if result_conv and result_conv[1] > 0:
            metrics['conversion_rate'] = (result_conv[0] / result_conv[1]) * 100
        else:
            metrics['conversion_rate'] = 0
            
        query_combo = "SELECT type_bien, transaction_type, COUNT(*) as count FROM properties WHERE is_available = TRUE GROUP BY type_bien, transaction_type ORDER BY count DESC"
        result_combo = self.db.execute_query(query_combo, fetch='all')
        if result_combo:
            metrics['popular_combinations_df'] = pd.DataFrame(result_combo, columns=['Type', 'Transaction', 'Nombre'])
        else:
            metrics['popular_combinations_df'] = pd.DataFrame()
        
        query_fav = """
        SELECT p.titre, COUNT(f.id) as favorite_count
        FROM properties p LEFT JOIN favorites f ON p.id = f.property_id
        WHERE p.is_available = TRUE GROUP BY p.id, p.titre ORDER BY favorite_count DESC LIMIT 10
        """
        result_fav = self.db.execute_query(query_fav, fetch='all')
        if result_fav:
            metrics['most_favorited_df'] = pd.DataFrame(result_fav, columns=['Propriété', 'Favoris'])
        else:
            metrics['most_favorited_df'] = pd.DataFrame()
            
        return metrics

reporting_engine = ReportingEngine()