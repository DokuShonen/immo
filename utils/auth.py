import bcrypt
import streamlit as st
from utils.database import db_manager

class AuthManager:
    def __init__(self):
        self.db = db_manager
    
    def hash_password(self, password):
        """Hash a password for storing."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Verify a stored password against one provided by user"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def login(self, username, password):
        """Authenticate user and return user data if successful"""
        user = self.db.get_user_by_username(username)
        if user and self.verify_password(password, user[3]):  # password_hash is at index 3
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[4],
                'nom': user[5],
                'prenom': user[6],
                'raison_sociale': user[7],
                'telephone': user[8],
                'adresse': user[9],
                'is_active': user[11]
            }
        return None
    
    def register(self, username, email, password, role, nom, prenom=None, raison_sociale=None, telephone=None, adresse=None):
        """Register a new user"""
        # Check if username or email already exists
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            return {'success': False, 'message': 'Nom d\'utilisateur déjà utilisé'}
        
        # Hash password
        password_hash = self.hash_password(password)
        
        try:
            user_id = self.db.create_user(username, email, password_hash, role, nom, prenom, raison_sociale, telephone, adresse)
            if user_id:
                return {'success': True, 'message': 'Compte créé avec succès', 'user_id': user_id[0]}
            else:
                return {'success': False, 'message': 'Erreur lors de la création du compte'}
        except Exception as e:
            return {'success': False, 'message': f'Erreur: {str(e)}'}
    
    def logout(self):
        """Clear session state"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    def is_authenticated(self):
        """Check if user is logged in"""
        return 'user' in st.session_state and st.session_state.user is not None
    
    def get_current_user(self):
        """Get current logged in user"""
        return st.session_state.get('user', None)
    
    def require_auth(self, allowed_roles=None):
        """Decorator/function to require authentication"""
        if not self.is_authenticated():
            st.error("Vous devez être connecté pour accéder à cette page")
            st.stop()
        
        if allowed_roles and st.session_state.user['role'] not in allowed_roles:
            st.error("Vous n'avez pas les permissions nécessaires pour accéder à cette page")
            st.stop()
        
        return True

auth_manager = AuthManager()