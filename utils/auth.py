"""Authentification et gestion des comptes."""
import bcrypt
import streamlit as st

from utils.database import DatabaseError, db_manager, log_exception

# Roles accessibles a l'inscription publique.
ROLES_PUBLICS = ('client', 'bailleur')

# Limitation des tentatives de connexion.
MAX_TENTATIVES = 5
FENETRE_TENTATIVES = 15  # minutes


class AuthManager:
    def __init__(self):
        self.db = db_manager

    # ------------------------------------------------------------------
    # Mots de passe
    # ------------------------------------------------------------------
    def hash_password(self, password):
        """Hache un mot de passe pour le stockage."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password, hashed):
        """Verifie un mot de passe saisi contre l'empreinte stockee."""
        if not hashed:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except (ValueError, TypeError):
            return False

    # ------------------------------------------------------------------
    # Limitation des tentatives
    # ------------------------------------------------------------------
    @staticmethod
    def client_ip():
        """Adresse IP du visiteur, lue dans les en-tetes de la requete."""
        forwarded = st.context.headers.get("X-Forwarded-For", "") if hasattr(st, "context") else ""
        if forwarded:
            return forwarded.split(",")[0].strip()
        return st.context.headers.get("X-Real-IP", "127.0.0.1") if hasattr(st, "context") else "127.0.0.1"

    def est_bloque(self, username, ip_address):
        """Vrai si trop de tentatives ont echoue recemment."""
        try:
            echecs = self.db.count_recent_failures(username, ip_address, FENETRE_TENTATIVES)
        except DatabaseError:
            return False
        return echecs >= MAX_TENTATIVES

    def enregistrer_echec(self, username, ip_address):
        try:
            self.db.record_login_failure(username, ip_address)
        except DatabaseError:
            pass

    def effacer_echecs(self, username, ip_address):
        try:
            self.db.clear_login_failures(username, ip_address)
        except DatabaseError:
            pass

    # ------------------------------------------------------------------
    # Connexion et inscription
    # ------------------------------------------------------------------
    def login(self, username, password):
        """Authentifie un utilisateur et renvoie ses donnees, ou None.

        Un compte desactive ne peut plus se connecter, et les tentatives
        sont limitees pour freiner la force brute.
        """
        username = (username or '').strip()
        ip_address = self.client_ip()

        if not username or not password:
            return None

        if self.est_bloque(username, ip_address):
            return None

        try:
            user = self.db.get_user_by_username(username)
        except DatabaseError:
            return None

        if not user or not self.verify_password(password, user['password_hash']):
            self.enregistrer_echec(username, ip_address)
            return None

        if not user.get('is_active', True):
            # Compte desactive : on ne conserve pas la trace d'echec, ce
            # n'est pas une erreur de mot de passe.
            return None

        self.effacer_echecs(username, ip_address)

        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'nom': user['nom'],
            'prenom': user.get('prenom'),
            'raison_sociale': user.get('raison_sociale'),
            'telephone': user.get('telephone'),
            'adresse': user.get('adresse'),
            'is_active': user.get('is_active', True),
        }

    def register(self, username, email, password, role, nom, prenom=None,
                 raison_sociale=None, telephone=None, adresse=None):
        """Cree un compte. Ne renvoie jamais de detail technique."""
        username = (username or '').strip()
        email = (email or '').strip().lower()

        if role not in ROLES_PUBLICS:
            return {'success': False, 'message': "Ce type de compte n'est pas ouvert a l'inscription."}

        try:
            if self.db.get_user_by_username(username):
                return {'success': False, 'message': "Ce nom d'utilisateur est deja utilise."}
            if self.db.get_user_by_email(email):
                return {'success': False, 'message': "Cette adresse email est deja utilisee."}
        except DatabaseError:
            return {'success': False, 'message': "Inscription impossible pour le moment. Reessayez."}

        password_hash = self.hash_password(password)

        try:
            user = self.db.create_user(username, email, password_hash, role, nom,
                                       prenom, raison_sociale, telephone, adresse)
        except DatabaseError:
            return {'success': False, 'message': "Inscription impossible pour le moment. Reessayez."}
        except Exception as exc:  # pragma: no cover - filet de securite
            log_exception("creation de compte", exc)
            return {'success': False, 'message': "Inscription impossible pour le moment. Reessayez."}

        if user:
            return {'success': True, 'message': "Compte cree avec succes", 'user_id': user['id']}
        return {'success': False, 'message': "Erreur lors de la creation du compte"}

    def logout(self):
        """Vide la session."""
        for key in list(st.session_state.keys()):
            del st.session_state[key]

    def is_authenticated(self):
        return 'user' in st.session_state and st.session_state.user is not None

    def get_current_user(self):
        return st.session_state.get('user', None)

    def require_auth(self, allowed_roles=None):
        """Verifie l'authentification et le role, interrompt l'execution sinon."""
        if not self.is_authenticated():
            st.error("Vous devez etre connecte pour acceder a cette page")
            st.stop()

        if allowed_roles and st.session_state.user['role'] not in allowed_roles:
            st.error("Vous n'avez pas les permissions necessaires pour acceder a cette page")
            st.stop()

        return True


auth_manager = AuthManager()
