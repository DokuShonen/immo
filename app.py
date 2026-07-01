# --- START OF FILE app.py ---

import streamlit as st
import sys
import os
from datetime import datetime
from datetime import time as dt_time
import time
import io
from PIL import Image
import pandas as pd
import plotly.express as px

# Ajout des utilitaires au chemin système
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.auth import auth_manager
from utils.database import db_manager
from layout_utils import show_header, show_footer

# Dictionnaire d'images d'illustration de haute qualité par type de bien
DEFAULT_IMAGES = {
    "Maison": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",       # Villa moderne de prestige
    "Appartement": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80",  # Intérieur d'appartement chic
    "Bureau": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80",       # Espace de travail/bureau moderne
    "Commercial": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=800&q=80",   # Local commercial/boutique
    "Terrain": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80"       # Beau terrain verdoyant
}

def main():
    st.set_page_config(
        page_title="Gestion Immobilière de Prestige",
        page_icon="🏢",  # Icône de l'onglet professionnelle
        layout="wide"
    )
    
    # CSS Personnalisé - Thème Premium & Épuré
    st.markdown("""
        <style>
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
        
        /* Application globale de la police */
        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            background-color: #f8fafc !important;
        }

        /* Personnalisation de la barre latérale */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important;
            border-right: 1px solid #1e293b !important;
        }

        /* Titres & Labels de la Sidebar */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] h4, 
        [data-testid="stSidebar"] h5, 
        [data-testid="stSidebar"] h6,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #f1f5f9 !important;
        }

        /* --- CORRECTION ULTRA-ROBUSTE CONTRASTE SELECTBOX BARRE LATÉRALE --- */
        [data-testid="stSidebar"] .stSelectbox > div {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
        }
        [data-testid="stSidebar"] .stSelectbox > div * {
            background-color: transparent !important; /* Force la transparence pour garder le fond sombre */
            color: #f8fafc !important;                 /* Force le texte en blanc/clair */
        }
        [data-testid="stSidebar"] .stSelectbox label {
            color: #94a3b8 !important;
            font-weight: 500;
        }

        /* --- CORRECTION ULTRA-ROBUSTE BOUTON SE DÉCONNECTER --- */
        [data-testid="stSidebar"] div.stButton > button {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease-in-out !important;
            width: 100% !important;
        }
        [data-testid="stSidebar"] div.stButton > button * {
            background-color: transparent !important;
            color: #f8fafc !important;
            font-weight: 600 !important;
        }
        [data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #ef4444 !important; /* Rouge élégant au survol pour la déconnexion */
            border-color: #f87171 !important;
        }
        [data-testid="stSidebar"] div.stButton > button:hover * {
            background-color: transparent !important;
            color: #ffffff !important;
        }

        /* Cartes de propriétés modernisées */
        .premium-card {
            background-color: #ffffff;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            margin-bottom: 24px;
        }
        .premium-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 30px -4px rgba(15, 23, 42, 0.08);
            border-color: #cbd5e1;
        }
        
        .premium-card-body {
            padding: 24px;
        }

        .premium-card-title {
            color: #0f172a;
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }
        
        /* Badges de statut */
        .badge-sale {
            background-color: #fef3c7;
            color: #d97706;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: inline-block;
        }
        .badge-rent {
            background-color: #e0f2fe;
            color: #0369a1;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: inline-block;
        }
        .badge-featured {
            background-color: #f0fdf4;
            color: #15803d;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: inline-block;
            margin-bottom: 8px;
        }

        /* Personnalisation globale des boutons principaux */
        div.stButton > button {
            border-radius: 10px !important;
            font-weight: 500 !important;
            padding: 8px 18px !important;
            transition: all 0.2s ease !important;
            border: 1px solid #cbd5e1 !important;
            background-color: #ffffff !important;
            color: #0f172a !important;
        }
        div.stButton > button:hover {
            border-color: #0f172a !important;
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }
        
        /* Bouton primaire (Action forte) */
        div.stButton > button[kind="primary"] {
            background: #0f172a !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.1) !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background: #1e293b !important;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.15) !important;
            color: #ffffff !important;
        }
        
        /* En-tête des sous-pages */
        .section-header {
            font-size: 1.75rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 25px;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    show_header()
    
    # Initialisation du session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = "properties"
    
    if not auth_manager.is_authenticated():
        show_public_access()
    else:
        show_main_app()
        
    show_footer()

# --- POPUPS (DIALOGS) DE CONNEXION ET D'INSCRIPTION ---

@st.dialog("Connexion Partenaire", width="small")
def show_login_dialog():
    st.markdown("<p style='color: #64748b; margin-top:-10px; margin-bottom: 20px;'>Renseignez vos identifiants pour accéder à votre espace sécurisé.</p>", unsafe_allow_html=True)
    username = st.text_input("Nom d'utilisateur", key="diag_login_user")
    password = st.text_input("Mot de passe", type="password", key="diag_login_pass")
    
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    if st.button("Se connecter", use_container_width=True, type="primary"):
        if username and password:
            user = auth_manager.login(username, password)
            if user:
                st.session_state.user = user
                st.success("Connexion réussie.")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Identifiants incorrects.")
        else:
            st.warning("Veuillez renseigner tous les champs.")

@st.dialog("Créer un compte", width="medium")
def show_register_dialog():
    st.markdown("<p style='color: #64748b; margin-top:-10px; margin-bottom: 20px;'>Rejoignez notre réseau immobilier exclusif en remplissant ce formulaire.</p>", unsafe_allow_html=True)
    role = st.selectbox("Type de compte", ["client", "bailleur"], key="diag_reg_role")
    
    c1, c2 = st.columns(2)
    with c1:
        username = st.text_input("Nom d'utilisateur*", key="diag_reg_user")
        nom = st.text_input("Nom*", key="diag_reg_nom")
        email = st.text_input("Adresse email*", key="diag_reg_email")
        telephone = st.text_input("Numéro de téléphone", key="diag_reg_phone")
    with c2:
        password = st.text_input("Mot de passe*", type="password", key="diag_reg_pass")
        prenom = st.text_input("Prénom", key="diag_reg_prenom")
        raison_sociale = st.text_input("Raison sociale", key="diag_reg_raison") if role == "bailleur" else None
    
    adresse = st.text_area("Adresse postale", key="diag_reg_address")
    
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    if st.button("Créer mon compte", use_container_width=True, type="primary"):
        if username and password and nom and email:
            result = auth_manager.register(username, email, password, role, nom, prenom, raison_sociale, telephone, adresse)
            if result['success']:
                st.success(result['message'])
                time.sleep(1)
                st.rerun()
            else:
                st.error(result['message'])
        else:
            st.error("Veuillez remplir tous les champs obligatoires (*).")

# ----------------------------------------------------

def show_public_access():
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("<div class='section-header'><i class='fas fa-search'></i> Découvrez notre catalogue d'exception</div>", unsafe_allow_html=True)
    with col2:
        if st.button("Se connecter", use_container_width=True, type="primary"):
            show_login_dialog()
    with col3:
        if st.button("S'inscrire", use_container_width=True):
            show_register_dialog()
    
    show_property_listings_public()

def show_main_app():
    user = st.session_state.user
    
    # Définition des menus
    menus = {
        'client': {"Voir les propriétés": "properties", "Mes favoris": "favorites", "Mes rendez-vous": "appointments"},
        'bailleur': {"Voir les propriétés": "properties", "Ajouter une propriété": "add_property", "Mes propriétés": "my_properties"},
        'agent': {"Voir les propriétés": "properties", "Ajouter une propriété": "add_property", "Mes clients": "my_clients", "Rendez-vous": "appointments"},
        'manager': {"Voir les propriétés": "properties", "Ajouter une propriété": "add_property", "Gestion des utilisateurs": "manage_users", "Statistiques": "statistics"}
    }
    
    current_menu = menus.get(user['role'], {})
    current_page = st.session_state.get('page', 'properties')
    
    if current_page in current_menu.values():
        default_index = list(current_menu.values()).index(current_page)
    else:
        default_index = 0
        st.session_state.page = list(current_menu.values())[0]

    with st.sidebar:
        # Encadré de profil
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                        padding: 20px; 
                        border-radius: 12px; 
                        border: 1px solid #334155; 
                        margin-bottom: 25px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; font-weight: 600;">Espace de</div>
                <div style="font-size: 1.15rem; font-weight: 600; color: #f8fafc; margin-top: 2px;">{user['nom']} {user['prenom'] or ''}</div>
                <span style="display: inline-block; background-color: #b45309; color: #fef3c7; font-size: 0.7rem; padding: 2px 8px; border-radius: 4px; margin-top: 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                    {user['role']}
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        selection = st.selectbox("Navigation", list(current_menu.keys()), index=default_index)
        st.session_state.page = current_menu[selection]
        
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        if st.button("Se déconnecter", use_container_width=True):
            auth_manager.logout()
            st.rerun()
            
    page = st.session_state.get('page', 'properties')
    
    if page == "properties": show_property_listings()
    elif page == "favorites" and user['role'] == 'client': show_favorites()
    elif page == "appointments": show_appointments()
    elif page == "add_property" and user['role'] in ['bailleur', 'agent', 'manager']: show_add_property()
    elif page == "my_properties" and user['role'] == 'bailleur': show_my_properties()
    elif page == "my_clients" and user['role'] in ['agent', 'manager']: show_my_clients()
    elif page == "manage_users" and user['role'] == 'manager': show_manage_users()
    elif page == "statistics" and user['role'] == 'manager': show_statistics()

def display_property_card(prop, user_role=None, public_view=False):
    """Affiche une carte de propriété au design haut de gamme avec image."""
    details_key = f"details_visible_{prop[0]}"
    appointment_key = f"appointment_form_visible_{prop[0]}"
    if details_key not in st.session_state: st.session_state[details_key] = False
    if appointment_key not in st.session_state: st.session_state[appointment_key] = False

    # Détection des images
    images = get_property_images(prop[0])
    
    with st.container():
        # Début de la carte premium
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        
        # Affichage de l'image de couverture
        if images:
            st.image(images[0], use_container_width=True)
        else:
            # Image de prestige par défaut
            type_bien = prop[4]
            # Choix dynamique de l'image de substitution en fonction du type de propriété
            default_img_url = DEFAULT_IMAGES.get(type_bien, DEFAULT_IMAGES["Maison"])
            st.image(default_img_url, use_container_width=True)
            
        st.markdown('<div class="premium-card-body">', unsafe_allow_html=True)
        
        # Badges d'état de la propriété
        badge_html = ""
        if prop[11]:  # is_featured
            badge_html += '<span class="badge-featured"><i class="fas fa-star"></i> Sélection Premium</span> '
        if prop[6] == "vente":
            badge_html += '<span class="badge-sale">Acheter</span>'
        else:
            badge_html += '<span class="badge-rent">Louer</span>'
            
        st.markdown(badge_html, unsafe_allow_html=True)
        st.markdown(f'<div class="premium-card-title">{prop[3]}</div>', unsafe_allow_html=True)
        
        # Métadonnées
        st.markdown(f"""
            <div style="font-size: 0.9rem; color: #475569; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
                <i class="fas fa-map-marker-alt" style="color: #64748b;"></i> {prop[7]}
            </div>
            <div style="font-size: 1.3rem; font-weight: 700; color: #0f172a; margin-bottom: 15px;">
                {prop[9]:,.0f} <span style="font-size: 0.9rem; font-weight: 500; color: #475569;">FCFA</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Détails extensibles
        if st.session_state[details_key]:
            st.markdown("""<div style="border-top: 1px solid #f1f5f9; padding-top: 15px; margin-top: 15px;"></div>""", unsafe_allow_html=True)
            st.write(f"**Type de bien :** {prop[4]}")
            if prop[8]: st.write(f"**Superficie :** {prop[8]} m²")
            st.write(f"**Description :** {prop[10]}")

            if not public_view and user_role == 'client':
                st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Ajouter aux favoris", key=f"fav_{prop[0]}", use_container_width=True):
                        db_manager.add_to_favorites(st.session_state.user['id'], prop[0])
                        st.toast(f"'{prop[3]}' ajouté à vos favoris.")
                with col2:
                    if st.button("Prendre RDV", key=f"appt_{prop[0]}", use_container_width=True, type="primary"):
                        st.session_state[appointment_key] = True
                        st.rerun()
            
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            if st.button("Masquer les détails", key=f"hide_{prop[0]}", use_container_width=True):
                st.session_state[details_key] = False
                st.session_state[appointment_key] = False
                st.rerun()
        else:
            if st.button("Voir la fiche complète", key=f"view_{prop[0]}", use_container_width=True, type="primary"):
                st.session_state[details_key] = True
                st.rerun()

        st.markdown('</div></div>', unsafe_allow_html=True)

        if st.session_state[appointment_key]:
            with st.container(border=True):
                show_appointment_form(prop[0], show_title=True)

def show_property_listings_public():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("<h4 style='margin-top:0;'>Filtres de recherche</h4>", unsafe_allow_html=True)
        type_filter = st.selectbox("Type de propriété", ["Tous", "Appartement", "Maison", "Bureau", "Commercial", "Terrain"], key="pub_type")
        transaction_filter = st.selectbox("Transaction", ["Tous", "vente", "location"], key="pub_trans")
        prix_min = st.number_input("Budget minimum (FCFA)", min_value=0, value=0, key="pub_pmin")
        prix_max = st.number_input("Budget maximum (FCFA)", min_value=0, value=100000000, key="pub_pmax")
    
    with col2:
        filters = {'prix_min': prix_min, 'prix_max': prix_max}
        if type_filter != "Tous": filters['type_bien'] = type_filter
        if transaction_filter != "Tous": filters['transaction_type'] = transaction_filter
        
        try:
            properties = db_manager.get_properties(filters)
            if properties:
                cols = st.columns(2)
                for idx, prop in enumerate(properties):
                    with cols[idx % 2]:
                        display_property_card(prop, public_view=True)
            else:
                st.info("Aucun bien ne correspond aux critères sélectionnés.")
        except Exception as e:
            st.error(f"Une erreur est survenue lors de la récupération des données : {str(e)}")

def show_property_listings():
    st.markdown("<div class='section-header'><i class='fas fa-home'></i> Catalogue Immobilier</div>", unsafe_allow_html=True)
    
    with st.expander("🔍 Critères de recherche avancée", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1: type_filter = st.selectbox("Type de bien", ["Tous", "Appartement", "Maison", "Bureau", "Commercial", "Terrain"], key="priv_type")
        with col2: transaction_filter = st.selectbox("Type d'offre", ["Tous", "vente", "location"], key="priv_trans")
        with col3: prix_min = st.number_input("Prix minimum (FCFA)", min_value=0, value=0, key="priv_pmin")
        with col4: prix_max = st.number_input("Prix maximum (FCFA)", min_value=0, value=150000000, key="priv_pmax")

    filters = {'prix_min': prix_min, 'prix_max': prix_max}
    if type_filter != "Tous": filters['type_bien'] = type_filter
    if transaction_filter != "Tous": filters['transaction_type'] = transaction_filter
    
    try:
        properties = db_manager.get_properties(filters)
        if properties:
            cols = st.columns(3)
            for idx, prop in enumerate(properties):
                with cols[idx % 3]:
                    display_property_card(prop, user_role=st.session_state.user['role'])
        else:
            st.info("Aucune propriété disponible avec ces critères.")
    except Exception as e:
        st.error(f"Erreur de communication de la base de données : {str(e)}")

def show_appointment_form(property_id, show_title=True):
    if show_title: st.subheader("Planifier une visite officielle")
    
    date_rdv = st.date_input("Date souhaitée", min_value=datetime.now().date(), key=f"appt_date_{property_id}")
    time_rdv = st.time_input("Créneau horaire", value=dt_time(10, 0), key=f"appt_time_{property_id}")
    type_rdv = st.selectbox("Nature du rendez-vous", ["visite", "transaction"], key=f"appt_type_{property_id}")
    notes = st.text_area("Instructions ou demandes spécifiques", key=f"appt_notes_{property_id}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Confirmer la demande", use_container_width=True, type="primary", key=f"appt_confirm_{property_id}"):
            try:
                property_data = db_manager.get_property_by_id(property_id)
                if property_data and property_data[2]:
                    db_manager.create_appointment(st.session_state.user['id'], property_id, property_data[2], datetime.combine(date_rdv, time_rdv), type_rdv, notes)
                    st.success("La demande de rendez-vous a bien été transmise à notre conseiller.")
                    st.session_state[f"appointment_form_visible_{property_id}"] = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Impossible de finaliser la demande (aucun agent attitré à ce dossier).")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
    with c2:
        if st.button("Annuler", use_container_width=True, key=f"appt_cancel_{property_id}"):
            st.session_state[f"appointment_form_visible_{property_id}"] = False
            st.rerun()

def show_favorites():
    st.markdown("<div class='section-header'><i class='fas fa-heart'></i> Mes Propriétés Favorites</div>", unsafe_allow_html=True)
    try:
        favorites = db_manager.get_user_favorites(st.session_state.user['id'])
        if favorites:
            cols = st.columns(3)
            for idx, fav in enumerate(favorites):
                with cols[idx % 3]:
                    with st.container(border=True):
                        images = get_property_images(fav[0])
                        if images:
                            st.image(images[0], use_container_width=True)
                        else:
                            type_bien = fav[4]
                            default_img_url = DEFAULT_IMAGES.get(type_bien, DEFAULT_IMAGES["Maison"])
                            st.image(default_img_url, use_container_width=True)
                            
                        st.subheader(fav[3])
                        st.write(f"**Type:** {fav[4]} | **Transaction:** {fav[6].title()}")
                        st.write(f"**Prix:** {fav[9]:,.0f} FCFA")
                        if st.button("Retirer de ma sélection", key=f"remove_fav_{fav[0]}", use_container_width=True):
                            db_manager.remove_from_favorites(st.session_state.user['id'], fav[0])
                            st.success("Propriété retirée de vos favoris.")
                            st.rerun()
        else:
            st.info("Vous n'avez aucun coup de cœur enregistré pour le moment.")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

def show_appointments():
    st.markdown("<div class='section-header'><i class='fas fa-calendar-alt'></i> Vos Rendez-vous et Visites</div>", unsafe_allow_html=True)
    user = st.session_state.user
    if user['role'] == 'client': show_client_appointments_view()
    elif user['role'] in ['agent', 'manager']: show_agent_appointments_view()

def show_client_appointments_view():
    try:
        appointments = db_manager.get_appointments(st.session_state.user['id'], 'client')
        if appointments:
            for apt in appointments:
                with st.container(border=True):
                    st.markdown(f"<h5>Demande de RDV pour : {apt[10]}</h5>", unsafe_allow_html=True)
                    st.write(f"**Conseiller immobilier chargé :** {apt[11]} {apt[12] or ''}")
                    st.write(f"**Date planifiée :** {apt[4].strftime('%d/%m/%Y à %H:%M')} | **Type :** {apt[5].title()}")
                    st.write(f"**Statut de la demande :** `{apt[7].upper()}`")
                    if apt[7] == 'pending':
                        if st.button("Annuler le rendez-vous", key=f"cancel_{apt[0]}", use_container_width=True):
                            update_appointment_status(apt[0], 'cancelled')
                            st.toast("Rendez-vous annulé.")
                            st.rerun()
        else:
            st.info("Aucun rendez-vous planifié.")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

def show_agent_appointments_view():
    try:
        appointments = db_manager.get_appointments(st.session_state.user['id'], 'agent')
        if appointments:
            for apt in appointments:
                with st.container(border=True):
                    st.write(f"**Client concerné :** {apt[10]} {apt[11] or ''}")
                    st.write(f"**Propriété cible :** {apt[9]}")
                    st.write(f"**Date & Heure :** {apt[4].strftime('%d/%m/%Y à %H:%M')}")
                    if apt[6]: st.write(f"**Remarques client :** *{apt[6]}*")
                    st.write(f"**Statut actuel :** `{apt[7].upper()}`")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if apt[7] == 'pending':
                            if st.button("Confirmer la visite", key=f"confirm_{apt[0]}", use_container_width=True, type="primary"):
                                update_appointment_status(apt[0], 'confirmed')
                                st.rerun()
                    with c2:
                        if apt[7] in ['pending', 'confirmed']:
                            if st.button("Marquer comme effectué", key=f"complete_{apt[0]}", use_container_width=True):
                                update_appointment_status(apt[0], 'completed')
                                st.rerun()
        else:
            st.info("Aucune activité planifiée à ce jour.")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

def show_add_property():
    st.markdown("<div class='section-header'><i class='fas fa-plus-circle'></i> Référencer une Nouvelle Propriété</div>", unsafe_allow_html=True)
    user = st.session_state.user
    with st.form("add_property_form"):
        c1, c2 = st.columns(2)
        with c1:
            titre = st.text_input("Titre de la fiche*")
            type_bien = st.selectbox("Type d'actif*", ["Appartement", "Maison", "Bureau", "Commercial", "Terrain"])
            usage = st.selectbox("Usage autorisé*", ["Résidentiel", "Commercial", "Industriel", "Mixte"])
            transaction_type = st.selectbox("Régime*", ["vente", "location"])
            situation_geo = st.text_input("Situation géographique complète*")
        with c2:
            taille = st.number_input("Superficie habitable/terrain (m²)", min_value=0)
            prix = st.number_input("Valeur marchande/Loyer (FCFA)*", min_value=0)
            is_featured = st.checkbox("Mettre ce bien en avant")
            agent_id = user['id']
            if user['role'] == 'manager':
                agents = db_manager.get_all_users('agent')
                if agents:
                    agent_options = {f"{agent[5]} {agent[6] or ''}": agent[0] for agent in agents}
                    selected_agent = st.selectbox("Conseiller en charge", list(agent_options.keys()))
                    agent_id = agent_options[selected_agent]
        
        description = st.text_area("Descriptif marketing*")
        uploaded_files = st.file_uploader("Fichiers multimédias (Photos du bien)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        
        submitted = st.form_submit_button("Publier l'annonce officielle", use_container_width=True)
        if submitted:
            if all([titre, type_bien, usage, transaction_type, situation_geo, prix > 0, description]):
                bailleur_id = user['id'] if user['role'] == 'bailleur' else None
                property_id_tuple = db_manager.add_property(bailleur_id, agent_id, titre, type_bien, usage, transaction_type, situation_geo, taille, prix, description, is_featured)
                if property_id_tuple:
                    if uploaded_files:
                        save_property_images(property_id_tuple[0], uploaded_files)
                    st.success("La fiche immobilière a bien été créée et diffusée.")
                else:
                    st.error("Une erreur technique s'est produite lors de l'enregistrement.")
            else:
                st.error("Veuillez renseigner l'ensemble des champs requis (*).")

def save_property_images(property_id, uploaded_files):
    upload_dir = f"uploads/properties/{property_id}"
    os.makedirs(upload_dir, exist_ok=True)
    for i, uploaded_file in enumerate(uploaded_files):
        file_path = os.path.join(upload_dir, f"{i}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

def show_my_properties():
    st.markdown("<div class='section-header'><i class='fas fa-list-alt'></i> Mon Portefeuille d'Actifs</div>", unsafe_allow_html=True)
    if 'editing_property_id' not in st.session_state:
        st.session_state.editing_property_id = None
        
    if st.session_state.editing_property_id:
        show_edit_property_form(st.session_state.editing_property_id)
    else:
        user = st.session_state.user
        try:
            query = "SELECT p.* FROM properties p WHERE p.bailleur_id = %s ORDER BY p.created_at DESC"
            properties = db_manager.execute_query(query, (user['id'],), fetch='all')
            if properties:
                for prop in properties:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        with c1:
                            st.subheader(prop[3])
                            st.write(f"**Disponibilité :** {'Disponible' if prop[12] else 'Hors-ligne'}")
                        with c2:
                            if st.button("Éditer la fiche", key=f"edit_{prop[0]}", use_container_width=True):
                                st.session_state.editing_property_id = prop[0]
                                st.rerun()
                        with c3:
                            status_text = "Retirer du marché" if prop[12] else "Remettre sur le marché"
                            if st.button(status_text, key=f"toggle_{prop[0]}", use_container_width=True):
                                toggle_property_status(prop[0], not prop[12])
                                st.rerun()
            else:
                st.info("Aucun actif n'est actuellement rattaché à votre compte.")
        except Exception as e:
            st.error(f"Erreur de traitement : {str(e)}")

def show_edit_property_form(property_id):
    st.subheader("Modification de la fiche immobilière")
    property_data = db_manager.get_property_by_id(property_id)
    if not property_data:
        st.error("Document introuvable.")
        st.session_state.editing_property_id = None
        st.rerun()
        return
    
    default_price = float(property_data[9]) if property_data[9] is not None else 0.0
    
    c1, c2 = st.columns(2)
    with c1:
        titre = st.text_input("Titre*", value=property_data[3], key=f"edit_titre_{property_id}")
        type_bien = st.selectbox("Type*", ["Appartement", "Maison", "Bureau", "Commercial", "Terrain"], index=["Appartement", "Maison", "Bureau", "Commercial", "Terrain"].index(property_data[4]), key=f"edit_type_{property_id}")
        transaction = st.selectbox("Transaction*", ["vente", "location"], index=["vente", "location"].index(property_data[6]), key=f"edit_trans_{property_id}")
    with c2:
        taille = st.number_input("Taille (m²)", value=property_data[8] or 0, key=f"edit_taille_{property_id}")
        prix = st.number_input("Prix (FCFA)*", value=default_price, format="%.2f", key=f"edit_prix_{property_id}")
        is_featured = st.checkbox("Mettre en avant", value=property_data[11], key=f"edit_feat_{property_id}")
    
    description = st.text_area("Description*", value=property_data[10], key=f"edit_desc_{property_id}")
    uploaded_files = st.file_uploader("Ajouter ou remplacer des images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

    st.divider()
    s1, s2 = st.columns(2)
    with s1:
        if st.button("Enregistrer les modifications", use_container_width=True, type="primary"):
            if all([titre, type_bien, transaction, description]):
                update_property(property_id, titre, type_bien, transaction, property_data[7], taille, prix, description, is_featured)
                if uploaded_files:
                    save_property_images(property_id, uploaded_files)
                st.success("La fiche immobilière a bien été mise à jour.")
                st.session_state.editing_property_id = None
                time.sleep(1)
                st.rerun()
            else:
                st.error("Champs requis manquants.")
    with s2:
        if st.button("Annuler", use_container_width=True):
            st.session_state.editing_property_id = None
            st.rerun()

def show_my_clients():
    st.markdown("<div class='section-header'><i class='fas fa-users'></i> Votre Portefeuille Clients</div>", unsafe_allow_html=True)
    user = st.session_state.user
    try:
        query = "SELECT u.*, ca.created_at as assigned_date FROM users u JOIN client_assignments ca ON u.id = ca.client_id WHERE ca.agent_id = %s AND ca.is_active = TRUE AND u.role = 'client' ORDER BY ca.created_at DESC"
        clients = db_manager.execute_query(query, (user['id'],), fetch='all')
        if clients:
            for client in clients:
                with st.container(border=True):
                    st.write(f"**Client :** {client[5]} {client[6] or ''}")
                    st.write(f"**Email :** {client[2]} | **Téléphone :** {client[8] or 'Non communiqué'}")
                    st.write(f"*Assigné à votre portefeuille le : {client[-1].strftime('%d/%m/%Y')}*")
        else:
            st.info("Aucun client n'est actuellement rattaché à votre compte.")
    except Exception as e:
        st.error(f"Erreur lors du chargement des clients : {str(e)}")

def show_manage_users():
    st.markdown("<div class='section-header'><i class='fas fa-users-cog'></i> Administration des Utilisateurs</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Comptes Utilisateurs", "Assignation Conseillers"])
    
    with tab1:
        try:
            users = db_manager.execute_query("SELECT * FROM users ORDER BY role, nom", fetch='all')
            if users:
                for user in users:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        with c1:
                            st.write(f"**{user[5]} {user[6] or ''}** | {user[2]}")
                            st.write(f"Rôle : `{user[4].upper()}`")
                        with c2:
                            st.write(f"Statut : `{'ACTIF' if user[11] else 'INACTIF'}`")
                        with c3:
                            if user[4] != 'manager':
                                action = "Désactiver" if user[11] else "Activer"
                                if st.button(action, key=f"toggle_user_{user[0]}", use_container_width=True):
                                    toggle_user_status(user[0], not user[11])
                                    st.rerun()
            else:
                st.info("Aucun compte utilisateur trouvé.")
        except Exception as e:
            st.error(f"Erreur de synchronisation : {str(e)}")
            
    with tab2:
        st.subheader("Associer un client à un conseiller d'affaires")
        try:
            clients = db_manager.get_all_users('client')
            agents = db_manager.get_all_users('agent')
            if clients and agents:
                c_opts = {f"{c[5]} {c[6] or ''} ({c[2]})": c[0] for c in clients}
                a_opts = {f"{a[5]} {a[6] or ''}": a[0] for a in agents}
                sel_c = st.selectbox("Sélectionner le client", list(c_opts.keys()))
                sel_a = st.selectbox("Attribuer à l'agent", list(a_opts.keys()))
                if st.button("Confirmer l'attribution", use_container_width=True, type="primary"):
                    db_manager.assign_client_to_agent(c_opts[sel_c], a_opts[sel_a], st.session_state.user['id'])
                    st.success("L'attribution a bien été modifiée.")
            else:
                st.warning("Un agent et un client actifs minimum sont requis pour initier l'assignation.")
        except Exception as e:
            st.error(f"Erreur lors du traitement de l'attribution : {str(e)}")

def show_statistics():
    st.markdown("<div class='section-header'><i class='fas fa-chart-pie'></i> Business Intelligence & Analytics</div>", unsafe_allow_html=True)
    
    from utils.reporting import reporting_engine
    
    try:
        property_analytics = reporting_engine.generate_property_analytics()
        user_analytics = reporting_engine.generate_user_analytics()
        appointment_analytics = reporting_engine.generate_appointment_analytics()
        business_metrics = reporting_engine.generate_business_metrics()
        
        # Section KPI
        st.subheader("Indicateurs Clés de l'Activité")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_properties = sum(property_analytics.get('property_types', {}).values())
            st.metric("Actifs Référencés", total_properties)
        
        with col2:
            total_users = sum(user_analytics.get('user_roles', {}).values())
            st.metric("Partenaires Actifs", total_users)
        
        with col3:
            total_appointments = sum(appointment_analytics.get('appointment_status', {}).values())
            st.metric("Total des Visites", total_appointments)
        
        with col4:
            portfolio_value = business_metrics.get('portfolio_value', (0, 0))[0]
            if portfolio_value:
                st.metric("Valeur du Portefeuille", f"{portfolio_value:,.0f} FCFA")
            else:
                st.metric("Valeur du Portefeuille", "Non disponible")

        st.markdown("<hr style='margin: 40px 0;'>", unsafe_allow_html=True)

        # Onglets Analytiques
        tab1, tab2, tab3, tab4 = st.tabs(["Actifs & Offre", "Données Utilisateurs", "Suivi des Échéances", "Performance Commerciale"])
        
        # Paramétrage thématique Plotly pour la cohérence visuelle
        plotly_colors = ['#0f172a', '#b45309', '#334155', '#d97706', '#64748b']
        
        with tab1:
            st.subheader("Analyse Sectorielle de l'Offre")
            df_prices = property_analytics.get('price_stats_df')
            if df_prices is not None and not df_prices.empty:
                fig = px.bar(df_prices, x='transaction_type', y='avg_price', 
                             title="Valorisation Moyenne par Type de Transaction", 
                             labels={'transaction_type': 'Régime', 'avg_price': 'Moyenne (FCFA)'},
                             color_discrete_sequence=['#b45309'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

            df_geo = property_analytics.get('geographic_distribution_df')
            if df_geo is not None and not df_geo.empty:
                fig = px.bar(df_geo, x='Localisation', y='Nombre', 
                             title="Concentration Géographique des Biens", 
                             labels={'Localisation': 'Ville/Région', 'Nombre': 'Nombre de biens'},
                             color_discrete_sequence=['#0f172a'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("Composition de notre réseau d'affaires")
            if user_analytics.get('user_roles'):
                df = pd.DataFrame(list(user_analytics['user_roles'].items()), columns=['Rôle', 'Nombre'])
                fig = px.pie(df, values='Nombre', names='Rôle', 
                             title="Structure de l'Écosystème Partenaire",
                             color_discrete_sequence=plotly_colors)
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.subheader("Statistiques d'Activité et Visites")
            c1, c2 = st.columns(2)
            with c1:
                if appointment_analytics.get('appointment_status'):
                    df = pd.DataFrame(list(appointment_analytics['appointment_status'].items()), columns=['Statut', 'Nombre'])
                    fig = px.pie(df, values='Nombre', names='Statut', 
                                 title="Taux de conversion des Visites",
                                 color_discrete_sequence=plotly_colors)
                    st.plotly_chart(fig, use_container_width=True)
            with c2:
                if appointment_analytics.get('appointment_types'):
                    df = pd.DataFrame(list(appointment_analytics['appointment_types'].items()), columns=['Type', 'Nombre'])
                    fig = px.pie(df, values='Nombre', names='Type', 
                                 title="Typologie de Contact Réalisé",
                                 color_discrete_sequence=plotly_colors)
                    st.plotly_chart(fig, use_container_width=True)
            
            df_perf = appointment_analytics.get('agent_performance_df')
            if df_perf is not None and not df_perf.empty:
                st.markdown("##### Performance Conseillers")
                df_perf['Agent'] = df_perf['Nom'] + ' ' + df_perf['Prenom'].fillna('')
                fig = px.bar(df_perf.head(10), x='Agent', y='RDV_Gérés', 
                             title="Top 10 Conseillers par Volume d'Activité",
                             color_discrete_sequence=['#b45309'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

        with tab4:
            st.subheader("Indicateurs de Demande")
            df_combo = business_metrics.get('popular_combinations_df')
            if df_combo is not None and not df_combo.empty:
                df_combo['Combinaison'] = df_combo['Type'] + ' - ' + df_combo['Transaction']
                fig = px.bar(df_combo.head(10), x='Combinaison', y='Nombre', 
                             title="Segments Offre les Plus Sollicités",
                             color_discrete_sequence=['#0f172a'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            df_fav = business_metrics.get('most_favorited_df')
            if df_fav is not None and not df_fav.empty:
                st.markdown("##### Classement d'Intérêt (Coup de Cœur)")
                fig = px.bar(df_fav.head(10), x='Propriété', y='Favoris', 
                             title="Propriétés les Plus Plébiscitées (Favoris)",
                             color_discrete_sequence=['#b45309'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Erreur d'accès à la base décisionnelle : {str(e)}")

# --- Fonctions Auxiliaires de l'Interface ---
def get_property_images(property_id):
    upload_dir = f"uploads/properties/{property_id}"
    if os.path.exists(upload_dir):
        return [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return []

def update_appointment_status(appointment_id, status):
    return db_manager.execute_query("UPDATE appointments SET status = %s WHERE id = %s", (status, appointment_id))

def toggle_property_status(property_id, is_available):
    return db_manager.execute_query("UPDATE properties SET is_available = %s WHERE id = %s", (is_available, property_id))

def toggle_user_status(user_id, is_active):
    return db_manager.execute_query("UPDATE users SET is_active = %s WHERE id = %s", (is_active, user_id))

def update_property(property_id, titre, type_bien, transaction_type, situation_geo, taille, prix, description, is_featured):
    query = "UPDATE properties SET titre = %s, type_bien = %s, transaction_type = %s, situation_geo = %s, taille = %s, prix = %s, description = %s, is_featured = %s WHERE id = %s"
    return db_manager.execute_query(query, (titre, type_bien, transaction_type, situation_geo, taille, prix, description, is_featured, property_id))

if __name__ == "__main__":
    main()

# --- END OF FILE app.py ---
