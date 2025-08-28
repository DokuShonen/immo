# --- START OF FILE app.py (FINAL VERSION) ---

import streamlit as st
import sys
import os
from datetime import datetime
from datetime import time as dt_time # Import 'time' as 'dt_time' to avoid conflict
import time # Import the 'time' module for sleep
import io
from PIL import Image
import pandas as pd
import plotly.express as px

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.auth import auth_manager
from utils.database import db_manager

# --- Fonctions d'affichage des vues (Pages) ---

def main():
    st.set_page_config(
        page_title="Gestion Immobilière",
        page_icon="🏠",
        layout="wide"
    )
    
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = "properties"
    
    if not auth_manager.is_authenticated():
        show_public_access()
    else:
        show_main_app()

def show_public_access():
    st.title("🏠 Plateforme de Gestion Immobilière")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### Consultez nos propriétés disponibles")
    with col2:
        if st.button("Se connecter", use_container_width=True):
            st.session_state.show_login = True
            st.rerun()
    with col3:
        if st.button("S'inscrire", use_container_width=True):
            st.session_state.show_register = True
            st.rerun()
    
    if st.session_state.get('show_login'):
        show_login_form()
        return
    if st.session_state.get('show_register'):
        show_register_form()
        return
    
    show_property_listings_public()

def show_login_form():
    st.subheader("Connexion")
    with st.form("public_login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        
        c1, c2 = st.columns(2)
        with c1:
            submitted = st.form_submit_button("Se connecter", use_container_width=True)
        with c2:
            if st.form_submit_button("Annuler", type="secondary", use_container_width=True):
                st.session_state.show_login = False
                st.rerun()
        
        if submitted:
            if username and password:
                user = auth_manager.login(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.show_login = False
                    st.success("Connexion réussie !")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect.")
            else:
                st.warning("Veuillez remplir tous les champs.")

def show_register_form():
    st.subheader("Créer un compte")
    with st.form("public_register_form"):
        role = st.selectbox("Type de compte", ["client", "bailleur"])
        c1, c2 = st.columns(2)
        with c1:
            username = st.text_input("Nom d'utilisateur*")
            nom = st.text_input("Nom*")
            email = st.text_input("Email*")
            telephone = st.text_input("Téléphone")
        with c2:
            password = st.text_input("Mot de passe*", type="password")
            prenom = st.text_input("Prénom")
            raison_sociale = st.text_input("Raison sociale") if role == "bailleur" else None
        
        adresse = st.text_area("Adresse")
        
        s1, s2 = st.columns(2)
        with s1:
            submitted = st.form_submit_button("Créer le compte", use_container_width=True)
        with s2:
            if st.form_submit_button("Annuler", type="secondary", use_container_width=True):
                st.session_state.show_register = False
                st.rerun()
        
        if submitted:
            if username and password and nom and email:
                result = auth_manager.register(username, email, password, role, nom, prenom, raison_sociale, telephone, adresse)
                if result['success']:
                    st.success(result['message'])
                    st.session_state.show_register = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(result['message'])
            else:
                st.error("Veuillez remplir tous les champs obligatoires (*).")

def show_main_app():
    user = st.session_state.user
    with st.sidebar:
        st.header(f"Bienvenue {user['nom']} {user['prenom'] or ''}")
        st.caption(f"Rôle: {user['role'].title()}")
        if st.button("Se déconnecter", use_container_width=True):
            auth_manager.logout()
            st.rerun()
        st.divider()
        
        if user['role'] == 'client': show_client_navigation()
        elif user['role'] == 'bailleur': show_bailleur_navigation()
        elif user['role'] == 'agent': show_agent_navigation()
        elif user['role'] == 'manager': show_manager_navigation()
    
    page = st.session_state.get('page', 'properties')
    
    if page == "properties": show_property_listings()
    elif page == "favorites" and user['role'] == 'client': show_favorites()
    elif page == "appointments": show_appointments()
    elif page == "add_property" and user['role'] in ['bailleur', 'agent', 'manager']: show_add_property()
    elif page == "my_properties" and user['role'] == 'bailleur': show_my_properties()
    elif page == "my_clients" and user['role'] in ['agent', 'manager']: show_my_clients()
    elif page == "manage_users" and user['role'] == 'manager': show_manage_users()
    elif page == "statistics" and user['role'] == 'manager': show_statistics()

# --- Fonctions de Navigation ---
def show_client_navigation():
    st.header("Menu Client")
    if st.button("🏠 Voir les propriétés", use_container_width=True): st.session_state.page = "properties"; st.rerun()
    if st.button("❤️ Mes favoris", use_container_width=True): st.session_state.page = "favorites"; st.rerun()
    if st.button("📅 Mes rendez-vous", use_container_width=True): st.session_state.page = "appointments"; st.rerun()

def show_bailleur_navigation():
    st.header("Menu Bailleur")
    if st.button("🏠 Voir les propriétés", use_container_width=True): st.session_state.page = "properties"; st.rerun()
    if st.button("➕ Ajouter une propriété", use_container_width=True): st.session_state.page = "add_property"; st.rerun()
    if st.button("📋 Mes propriétés", use_container_width=True): st.session_state.page = "my_properties"; st.rerun()

def show_agent_navigation():
    st.header("Menu Agent")
    if st.button("🏠 Voir les propriétés", use_container_width=True): st.session_state.page = "properties"; st.rerun()
    if st.button("➕ Ajouter une propriété", use_container_width=True): st.session_state.page = "add_property"; st.rerun()
    if st.button("👥 Mes clients", use_container_width=True): st.session_state.page = "my_clients"; st.rerun()
    if st.button("📅 Rendez-vous", use_container_width=True): st.session_state.page = "appointments"; st.rerun()

def show_manager_navigation():
    st.header("Menu Manager")
    if st.button("🏠 Voir les propriétés", use_container_width=True): st.session_state.page = "properties"; st.rerun()
    if st.button("➕ Ajouter une propriété", use_container_width=True): st.session_state.page = "add_property"; st.rerun()
    if st.button("👥 Gestion des utilisateurs", use_container_width=True): st.session_state.page = "manage_users"; st.rerun()
    if st.button("📊 Statistiques", use_container_width=True): st.session_state.page = "statistics"; st.rerun()

# --- Fonctions d'Affichage des Contenus ---

def display_property_card(prop, user_role=None, public_view=False):
    details_key = f"details_visible_{prop[0]}"
    appointment_key = f"appointment_form_visible_{prop[0]}"
    if details_key not in st.session_state: st.session_state[details_key] = False
    if appointment_key not in st.session_state: st.session_state[appointment_key] = False

    with st.container(border=True):
        if prop[11]: st.markdown("⭐ **MISE EN AVANT**")
        st.subheader(prop[3])
        st.write(f"**Localisation:** {prop[7]}")
        st.write(f"**Prix:** {prop[9]:,.0f} FCFA")
        
        if st.session_state[details_key]:
            st.markdown("---")
            st.write(f"**Type :** {prop[4]}")
            st.write(f"**Transaction :** {prop[6].title()}")
            if prop[8]: st.write(f"**Taille :** {prop[8]} m²")
            st.write(f"**Description :** {prop[10]}")

            if not public_view and user_role == 'client':
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("❤️ Ajouter aux favoris", key=f"fav_{prop[0]}", use_container_width=True):
                        db_manager.add_to_favorites(st.session_state.user['id'], prop[0])
                        st.toast(f"'{prop[3]}' ajouté à vos favoris !")
                with col2:
                    if st.button("📅 Prendre rendez-vous", key=f"appt_{prop[0]}", use_container_width=True):
                        st.session_state[appointment_key] = True
                        st.rerun()
            
            st.markdown("---")
            if st.button("Cacher les détails", key=f"hide_{prop[0]}", use_container_width=True, type="secondary"):
                st.session_state[details_key] = False
                st.session_state[appointment_key] = False
                st.rerun()
        else:
            if st.button("Voir les détails", key=f"view_{prop[0]}", use_container_width=True):
                st.session_state[details_key] = True
                st.rerun()
        
        if st.session_state[appointment_key]:
            st.markdown("---")
            show_appointment_form(prop[0], show_title=False)

def show_property_listings_public():
    st.subheader("🏠 Propriétés Disponibles")
    st.info("💡 Connectez-vous pour accéder aux fonctionnalités complètes.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: type_filter = st.selectbox("Type", ["Tous", "Appartement", "Maison", "Bureau", "Commercial", "Terrain"], key="pub_type")
    with col2: transaction_filter = st.selectbox("Transaction", ["Tous", "vente", "location"], key="pub_trans")
    with col3: prix_min = st.number_input("Prix min", min_value=0, value=0, key="pub_pmin")
    with col4: prix_max = st.number_input("Prix max", min_value=0, value=1000000, key="pub_pmax")
    
    filters = {'prix_min': prix_min, 'prix_max': prix_max}
    if type_filter != "Tous": filters['type_bien'] = type_filter
    if transaction_filter != "Tous": filters['transaction_type'] = transaction_filter
    
    try:
        properties = db_manager.get_properties(filters)
        if properties:
            cols = st.columns(3)
            for idx, prop in enumerate(properties):
                with cols[idx % 3]:
                    display_property_card(prop, public_view=True)
        else:
            st.info("Aucune propriété trouvée avec ces critères.")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

def show_property_listings():
    st.title("🏠 Propriétés Disponibles")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: type_filter = st.selectbox("Type", ["Tous", "Appartement", "Maison", "Bureau", "Commercial", "Terrain"], key="priv_type")
    with col2: transaction_filter = st.selectbox("Transaction", ["Tous", "vente", "location"], key="priv_trans")
    with col3: prix_min = st.number_input("Prix min", min_value=0, value=0, key="priv_pmin")
    with col4: prix_max = st.number_input("Prix max", min_value=0, value=1000000, key="priv_pmax")

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
            st.info("Aucune propriété trouvée avec ces critères.")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

def show_appointment_form(property_id, show_title=True):
    if show_title: st.subheader("Prendre un rendez-vous")
    
    date_rdv = st.date_input("Date du rendez-vous", min_value=datetime.now().date(), key=f"appt_date_{property_id}")
    time_rdv = st.time_input("Heure du rendez-vous", value=dt_time(14, 0), key=f"appt_time_{property_id}")
    type_rdv = st.selectbox("Type de rendez-vous", ["visite", "transaction"], key=f"appt_type_{property_id}")
    notes = st.text_area("Notes (optionnel)", key=f"appt_notes_{property_id}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Confirmer", use_container_width=True, type="primary", key=f"appt_confirm_{property_id}"):
            try:
                property_data = db_manager.get_property_by_id(property_id)
                if property_data and property_data[2]:
                    db_manager.create_appointment(st.session_state.user['id'], property_id, property_data[2], datetime.combine(date_rdv, time_rdv), type_rdv, notes)
                    st.success("Rendez-vous créé !")
                    st.session_state[f"appointment_form_visible_{property_id}"] = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Impossible de créer le rendez-vous (agent non assigné).")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
    with c2:
        if st.button("Annuler", use_container_width=True, key=f"appt_cancel_{property_id}"):
            st.session_state[f"appointment_form_visible_{property_id}"] = False
            st.rerun()

def show_favorites():
    st.title("❤️ Mes Propriétés Favorites")
    try:
        favorites = db_manager.get_user_favorites(st.session_state.user['id'])
        if favorites:
            for fav in favorites:
                with st.container(border=True):
                    st.subheader(fav[3])
                    st.write(f"{fav[4]} | {fav[6].title()} | {fav[9]:,.0f} FCFA")
                    if st.button("Retirer des favoris", key=f"remove_fav_{fav[0]}", use_container_width=True):
                        db_manager.remove_from_favorites(st.session_state.user['id'], fav[0])
                        st.success("Retiré des favoris!")
                        st.rerun()
        else:
            st.info("Vous n'avez aucune propriété favorite pour le moment.")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

def show_appointments():
    st.title("📅 Gestion des Rendez-vous")
    user = st.session_state.user
    if user['role'] == 'client': show_client_appointments_view()
    elif user['role'] in ['agent', 'manager']: show_agent_appointments_view()

def show_client_appointments_view():
    st.subheader("Mes Rendez-vous")
    try:
        appointments = db_manager.get_appointments(st.session_state.user['id'], 'client')
        if appointments:
            for apt in appointments:
                with st.container(border=True):
                    st.write(f"**Propriété:** {apt[10]}")
                    st.write(f"**Agent:** {apt[11]} {apt[12] or ''}")
                    st.write(f"**Date:** {apt[4].strftime('%d/%m/%Y %H:%M')} | **Type:** {apt[5].title()}")
                    st.write(f"**Statut:** {apt[7].title()}")
                    if apt[7] == 'pending':
                        if st.button("Annuler", key=f"cancel_{apt[0]}", use_container_width=True):
                            update_appointment_status(apt[0], 'cancelled')
                            st.success("Rendez-vous annulé")
                            st.rerun()
        else:
            st.info("Aucun rendez-vous planifié.")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

def show_agent_appointments_view():
    st.subheader("Rendez-vous de mes clients")
    try:
        appointments = db_manager.get_appointments(st.session_state.user['id'], 'agent')
        if appointments:
            for apt in appointments:
                with st.container(border=True):
                    st.write(f"**Client:** {apt[10]} {apt[11] or ''}")
                    st.write(f"**Propriété:** {apt[9]}")
                    st.write(f"**Date:** {apt[4].strftime('%d/%m/%Y %H:%M')}")
                    if apt[6]: st.write(f"**Notes:** {apt[6]}")
                    c1,c2 = st.columns(2)
                    with c1:
                        if apt[7] == 'pending':
                            if st.button("Confirmer", key=f"confirm_{apt[0]}", use_container_width=True):
                                update_appointment_status(apt[0], 'confirmed'); st.rerun()
                    with c2:
                        if apt[7] in ['pending', 'confirmed']:
                            if st.button("Marquer terminé", key=f"complete_{apt[0]}", use_container_width=True):
                                update_appointment_status(apt[0], 'completed'); st.rerun()
        else:
            st.info("Aucun rendez-vous pour cet agent.")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

def show_add_property():
    st.title("➕ Ajouter une Propriété")
    user = st.session_state.user
    with st.form("add_property_form"):
        c1, c2 = st.columns(2)
        with c1:
            titre = st.text_input("Titre*")
            type_bien = st.selectbox("Type*", ["Appartement", "Maison", "Bureau", "Commercial", "Terrain"])
            usage = st.selectbox("Usage*", ["Résidentiel", "Commercial", "Industriel", "Mixte"])
            transaction_type = st.selectbox("Transaction*", ["vente", "location"])
            situation_geo = st.text_input("Localisation*")
        with c2:
            taille = st.number_input("Taille (m²)", min_value=0)
            prix = st.number_input("Prix (FCFA)*", min_value=0)
            is_featured = st.checkbox("Mettre en avant")
            agent_id = user['id']
            if user['role'] == 'manager':
                agents = db_manager.get_all_users('agent')
                if agents:
                    agent_options = {f"{agent[5]} {agent[6] or ''}": agent[0] for agent in agents}
                    selected_agent = st.selectbox("Agent responsable", list(agent_options.keys()))
                    agent_id = agent_options[selected_agent]
        description = st.text_area("Description*")
        uploaded_files = st.file_uploader("Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        
        submitted = st.form_submit_button("Ajouter la propriété", use_container_width=True)
        if submitted:
            if all([titre, type_bien, usage, transaction_type, situation_geo, prix > 0, description]):
                bailleur_id = user['id'] if user['role'] == 'bailleur' else None
                property_id_tuple = db_manager.add_property(bailleur_id, agent_id, titre, type_bien, usage, transaction_type, situation_geo, taille, prix, description, is_featured)
                if property_id_tuple:
                    if uploaded_files:
                        save_property_images(property_id_tuple[0], uploaded_files)
                    st.success("Propriété ajoutée !")
                else:
                    st.error("Erreur lors de l'ajout.")
            else:
                st.error("Veuillez remplir tous les champs obligatoires (*).")

def save_property_images(property_id, uploaded_files):
    upload_dir = f"uploads/properties/{property_id}"
    os.makedirs(upload_dir, exist_ok=True)
    for i, uploaded_file in enumerate(uploaded_files):
        file_path = os.path.join(upload_dir, f"{i}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

def show_my_properties():
    st.title("📋 Mes Propriétés")
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
                        c1, c2, c3 = st.columns([2,1,1])
                        with c1:
                            st.subheader(prop[3])
                            st.write(f"Statut : {'Disponible' if prop[12] else 'Non disponible'}")
                        with c2:
                            if st.button("Modifier", key=f"edit_{prop[0]}", use_container_width=True):
                                st.session_state.editing_property_id = prop[0]; st.rerun()
                        with c3:
                            status_text = "Désactiver" if prop[12] else "Activer"
                            if st.button(status_text, key=f"toggle_{prop[0]}", use_container_width=True):
                                toggle_property_status(prop[0], not prop[12]); st.rerun()
            else:
                st.info("Vous n'avez aucune propriété enregistrée.")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

def show_edit_property_form(property_id):
    st.subheader("Modifier la propriété")
    property_data = db_manager.get_property_by_id(property_id)
    if not property_data:
        st.error("Propriété non trouvée."); st.session_state.editing_property_id = None; st.rerun(); return
    
    default_price = float(property_data[9]) if property_data[9] is not None else 0.0
    
    c1, c2 = st.columns(2)
    with c1:
        titre = st.text_input("Titre*", value=property_data[3], key=f"edit_titre_{property_id}")
        type_bien = st.selectbox("Type*", ["Appartement", "Maison", "Bureau", "Commercial", "Terrain"], index=["Appartement", "Maison", "Bureau", "Commercial", "Terrain"].index(property_data[4]), key=f"edit_type_{property_id}")
        transaction = st.selectbox("Transaction*", ["vente", "location"], index=["vente", "location"].index(property_data[6]), key=f"edit_trans_{property_id}")
    with c2:
        taille = st.number_input("Taille (m²)", value=property_data[8] or 0, key=f"edit_taille_{property_id}")
        prix = st.number_input("Prix (€)*", value=default_price, format="%.2f", key=f"edit_prix_{property_id}")
        is_featured = st.checkbox("Mettre en avant", value=property_data[11], key=f"edit_feat_{property_id}")
    description = st.text_area("Description*", value=property_data[10], key=f"edit_desc_{property_id}")
    
    st.divider()
    s1, s2 = st.columns(2)
    with s1:
        if st.button("Sauvegarder", use_container_width=True, type="primary"):
            if all([titre, type_bien, transaction, description]):
                update_property(property_id, titre, type_bien, transaction, property_data[7], taille, prix, description, is_featured)
                st.success("Modifié !"); st.session_state.editing_property_id = None; time.sleep(1); st.rerun()
            else: st.error("Champs requis manquants.")
    with s2:
        if st.button("Annuler", use_container_width=True):
            st.session_state.editing_property_id = None; st.rerun()

def show_my_clients():
    st.title("👥 Gestion des Clients")
    user = st.session_state.user
    try:
        query = "SELECT u.*, ca.created_at as assigned_date FROM users u JOIN client_assignments ca ON u.id = ca.client_id WHERE ca.agent_id = %s AND ca.is_active = TRUE AND u.role = 'client' ORDER BY ca.created_at DESC"
        clients = db_manager.execute_query(query, (user['id'],), fetch='all')
        if clients:
            st.subheader("Mes clients assignés")
            for client in clients:
                with st.container(border=True):
                    st.write(f"**{client[5]} {client[6] or ''}** | Assigné le: {client[-1].strftime('%d/%m/%Y')}")
        else:
            st.info("Aucun client assigné.")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

def show_manage_users():
    st.title("👥 Gestion des Utilisateurs")
    tab1, tab2 = st.tabs(["Utilisateurs", "Assignations"])
    with tab1:
        try:
            users = db_manager.execute_query("SELECT * FROM users ORDER BY role, nom", fetch='all')
            if users:
                for user in users:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2,1,1])
                        with c1: st.write(f"**{user[5]} {user[6] or ''}** ({user[4].title()})")
                        with c2: st.write(f"Statut : {'Actif' if user[11] else 'Inactif'}", unsafe_allow_html=True)
                        with c3:
                            if user[4] != 'manager':
                                action = "Désactiver" if user[11] else "Activer"
                                if st.button(action, key=f"toggle_user_{user[0]}", use_container_width=True):
                                    toggle_user_status(user[0], not user[11]); st.rerun()
            else: st.info("Aucun utilisateur.")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
    with tab2:
        st.subheader("Assigner un Client à un Agent")
        try:
            clients = db_manager.get_all_users('client')
            agents = db_manager.get_all_users('agent')
            if clients and agents:
                c_opts = {f"{c[5]} {c[6] or ''}": c[0] for c in clients}
                a_opts = {f"{a[5]} {a[6] or ''}": a[0] for a in agents}
                sel_c = st.selectbox("Client", list(c_opts.keys()))
                sel_a = st.selectbox("Agent", list(a_opts.keys()))
                if st.button("Assigner", use_container_width=True, type="primary"):
                    db_manager.assign_client_to_agent(c_opts[sel_c], a_opts[sel_a], st.session_state.user['id'])
                    st.success("Assignation réussie !"); st.balloons()
            else:
                st.warning("Il faut au moins un client et un agent actifs pour faire une assignation.")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

# Dans votre app.py actuel, remplacez cette fonction

def show_statistics():
    st.title("📊 Statistiques et Analyses de la Plateforme")
    
    # On importe les modules nécessaires ici pour ne pas alourdir le reste de l'app
    from utils.reporting import reporting_engine
    import pandas as pd
    import plotly.express as px

    try:
        # --- 1. Génération de toutes les données analytiques ---
        property_analytics = reporting_engine.generate_property_analytics()
        user_analytics = reporting_engine.generate_user_analytics()
        appointment_analytics = reporting_engine.generate_appointment_analytics()
        business_metrics = reporting_engine.generate_business_metrics()
        
        # --- 2. Affichage des Indicateurs Clés de Performance (KPIs) ---
        st.subheader("📈 Indicateurs Clés de Performance")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_properties = sum(property_analytics.get('property_types', {}).values())
            st.metric("Propriétés Totales", total_properties)
        
        with col2:
            total_users = sum(user_analytics.get('user_roles', {}).values())
            st.metric("Utilisateurs Actifs", total_users)
        
        with col3:
            total_appointments = sum(appointment_analytics.get('appointment_status', {}).values())
            st.metric("Rendez-vous Total", total_appointments)
        
        with col4:
            portfolio_value = business_metrics.get('portfolio_value', (0, 0))[0]
            if portfolio_value:
                st.metric("Valeur Portfolio", f"{portfolio_value:,.0f} FCFA")
            else:
                st.metric("Valeur Portfolio", "N/A")

        st.divider()

        # --- 3. Affichage des Graphiques Détaillés dans des Onglets ---
        tab1, tab2, tab3, tab4 = st.tabs(["Propriétés", "Utilisateurs", "Rendez-vous", "Analyse Commerciale"])
        
        with tab1:
            st.header("Analyse des Propriétés")
            df_prices = property_analytics.get('price_stats_df')
            if df_prices is not None and not df_prices.empty:
                fig = px.bar(df_prices, x='transaction_type', y='avg_price', title="Prix Moyen par Type de Transaction", labels={'transaction_type': 'Type', 'avg_price': 'Prix Moyen (FCFA)'})
                st.plotly_chart(fig, use_container_width=True)

            df_geo = property_analytics.get('geographic_distribution_df')
            if df_geo is not None and not df_geo.empty:
                fig = px.bar(df_geo, x='Localisation', y='Nombre', title="Top 10 des Localisations", labels={'Localisation': 'Zone', 'Nombre': 'Nombre de Propriétés'})
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.header("Analyse des Utilisateurs")
            if user_analytics.get('user_roles'):
                df = pd.DataFrame(list(user_analytics['user_roles'].items()), columns=['Rôle', 'Nombre'])
                fig = px.bar(df, x='Rôle', y='Nombre', title="Répartition des Utilisateurs par Rôle")
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.header("Analyse des Rendez-vous")
            c1, c2 = st.columns(2)
            with c1:
                if appointment_analytics.get('appointment_status'):
                    df = pd.DataFrame(list(appointment_analytics['appointment_status'].items()), columns=['Statut', 'Nombre'])
                    fig = px.pie(df, values='Nombre', names='Statut', title="Répartition par Statut")
                    st.plotly_chart(fig, use_container_width=True)
            with c2:
                 if appointment_analytics.get('appointment_types'):
                    df = pd.DataFrame(list(appointment_analytics['appointment_types'].items()), columns=['Type', 'Nombre'])
                    fig = px.pie(df, values='Nombre', names='Type', title="Répartition par Type de RDV")
                    st.plotly_chart(fig, use_container_width=True)
            
            df_perf = appointment_analytics.get('agent_performance_df')
            if df_perf is not None and not df_perf.empty:
                st.markdown("##### Performance des Agents")
                df_perf['Agent'] = df_perf['Nom'] + ' ' + df_perf['Prenom'].fillna('')
                fig = px.bar(df_perf.head(10), x='Agent', y='RDV_Gérés', title="Top 10 Agents par Nombre de RDV Gérés")
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

        with tab4:
            st.header("Analyse Commerciale")
            df_combo = business_metrics.get('popular_combinations_df')
            if df_combo is not None and not df_combo.empty:
                df_combo['Combinaison'] = df_combo['Type'] + ' - ' + df_combo['Transaction']
                fig = px.bar(df_combo.head(10), x='Combinaison', y='Nombre', title="Top 10 des Combinaisons Type/Transaction")
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            
            df_fav = business_metrics.get('most_favorited_df')
            if df_fav is not None and not df_fav.empty:
                st.markdown("##### Propriétés les Plus Favorites")
                fig = px.bar(df_fav.head(10), x='Propriété', y='Favoris', title="Top 10 des Propriétés Favorites")
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des statistiques: {str(e)}")
        st.exception(e) # Affiche la trace complète de l'erreur pour le débogage

# --- Fonctions Helpers ---
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

# --- END OF FILE app.py (FINAL VERSION) ---
# This is the final version of the app.py file for the real estate management platform.