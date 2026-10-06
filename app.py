# --- START OF FILE app.py (REDESIGN v2) ---

import streamlit as st
import sys
import os
from datetime import datetime
from datetime import time as dt_time
import time
import pandas as pd
import plotly.express as px

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.auth import auth_manager
from utils.database import db_manager
from utils.media import fmt_fcfa, prix_affichage, property_image_uri, get_uploaded_images, save_image_set
from styles import inject_styles
from layout_utils import (
    show_public_hero, show_perks, show_section_title, show_result_bar, show_sidebar_brand,
    show_sidebar_user, show_header, show_footer,
)

# ----------------------------------------------------------------
# Palette Plotly cohérente avec le design system "Soleil"
# ----------------------------------------------------------------
PLOTLY_COLORS = ["#E9643B", "#0F7A68", "#F5A623", "#E0403B", "#12A07E", "#C46A9B", "#8A7566"]
PX_BASE = dict(
    template="plotly_white",
    color_discrete_sequence=PLOTLY_COLORS,
)


def _fig_layout(fig):
    fig.update_layout(
        font=dict(family="Nunito, sans-serif", color="#2E2016"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=16, r=16, t=64, b=16),
        title=dict(font=dict(size=17, color="#2E2016", family="Fredoka, sans-serif")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Nunito"),
    )
    fig.update_xaxes(gridcolor="#F6EBD9", linecolor="#F0E2CF")
    fig.update_yaxes(gridcolor="#F6EBD9", linecolor="#F0E2CF")
    return fig


TRANSACTION_LABELS = {"vente": "À vendre", "location": "À louer"}

ALERT_ICONS = {"success": ":material/task_alt:", "info": ":material/info:", "warning": ":material/warning:", "error": ":material/error:"}


def notify(level, message):
    """Message d'alerte affiché sous forme de popup (toast)."""
    st.toast(message, icon=ALERT_ICONS.get(level, ":material/info:"))


# --- Fonctions d'affichage des vues (Pages) ---

def main():
    st.set_page_config(
        page_title="ImmoPro – Gestion Immobilière",
        page_icon=":material/home:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_styles()
    show_header()

    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = "properties"

    if not auth_manager.is_authenticated():
        show_public_access()
    else:
        show_main_app()

    show_footer()


# ================================================================
# PARTIE PUBLIQUE
# ================================================================

def show_public_access():
    stats = db_manager.get_statistics()
    show_public_hero(
        stat_biens=stats.get('total_properties', 0),
        stat_villes=stats.get('total_cities', 0),
    )

    show_perks()

    c1, c2 = st.columns([2, 5])
    with c1:
        if st.button("Connexion", width='stretch', type="primary"):
            login_dialog()
    with c2:
        if st.button("Je crée mon compte", width='stretch', type="primary"):
            register_dialog()

    show_listings(filters_key_prefix="pub", role=None, public_view=True)


@st.dialog("Connexion", width="small", icon=":material/lock:")
def login_dialog():
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:1.2rem;">
            <div style="font-size:2.2rem;">🏠</div>
            <h2 style="margin:.3rem 0 .2rem; font-family:'Fredoka','Nunito',sans-serif;">Bon retour</h2>
            <p style="color:#8a7a6a; margin:0; font-size:.9rem;">Connectez-vous pour accéder à votre espace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("public_login_form"):
        username = st.text_input("Nom d'utilisateur", placeholder="Votre identifiant")
        password = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe")
        submitted = st.form_submit_button("Me connecter", width='stretch', type="primary")
        if submitted:
            if username and password:
                user = auth_manager.login(username, password)
                if user:
                    st.session_state.user = user
                    st.toast("Connexion réussie !", icon=":material/celebration:")
                    time.sleep(0.6)
                    st.rerun()
                else:
                    notify("error", "Nom d'utilisateur ou mot de passe incorrect.")
            else:
                notify("warning", "Veuillez remplir tous les champs.")


@st.dialog("Créer un compte", width="medium", icon=":material/star:")
def register_dialog():
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:1.2rem;">
            <div style="font-size:2.2rem;">✨</div>
            <h2 style="margin:.3rem 0 .2rem; font-family:'Fredoka','Nunito',sans-serif;">Créez votre compte</h2>
            <p style="color:#8a7a6a; margin:0; font-size:.9rem;">Rejoignez ImmoPro en moins d'une minute.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("public_register_form"):
        role = st.selectbox("Type de compte", ["client", "bailleur"],
                            help="Client : recherchez et réservez des biens. Bailleur : mettez vos biens en ligne.")
        c1, c2 = st.columns(2)
        with c1:
            username = st.text_input("Nom d'utilisateur*", placeholder="ex. martin12")
            nom = st.text_input("Nom*")
            email = st.text_input("Email*", placeholder="vous@exemple.com")
            telephone = st.text_input("Téléphone", placeholder="+33 6 12 34 56 78")
        with c2:
            password = st.text_input("Mot de passe*", type="password", help="Au moins 6 caractères.")
            prenom = st.text_input("Prénom")
            if role == "bailleur":
                raison_sociale = st.text_input("Raison sociale")
            else:
                raison_sociale = None

        adresse = st.text_area("Adresse", placeholder="Rue, ville, code postal")

        submitted = st.form_submit_button("C'est parti !", width='stretch', type="primary")
        if submitted:
            if not (username and password and nom and email):
                notify("error", "Veuillez remplir tous les champs obligatoires (*).")
            elif len(password) < 6:
                notify("error", "Le mot de passe doit contenir au moins 6 caractères.")
            elif "@" not in email or "." not in email:
                notify("error", "Veuillez saisir une adresse email valide.")
            else:
                result = auth_manager.register(username, email, password, role, nom, prenom, raison_sociale, telephone, adresse)
                if result['success']:
                    st.toast(result['message'], icon=":material/celebration:")
                    time.sleep(0.8)
                    st.rerun()
                else:
                    notify("error", result['message'])


def _liste_filtres(prefix):
    """Barre de filtres commune (publique et connectée)."""
    c1, c2, c3, c4, c5 = st.columns([1.4, 1.2, 1, 1, 1])
    with c1:
        q = st.text_input("Recherche", placeholder="Lieu, bien...", key=f"{prefix}_q")
    with c2:
        type_filter = st.selectbox("Type", ["Tous", "Appartement", "Maison", "Bureau", "Commercial", "Terrain"],
                                   key=f"{prefix}_type")
    with c3:
        transaction_filter = st.selectbox("Transaction", ["Tous", "vente", "location"],
                                          format_func=lambda x: "Toutes" if x == "Tous" else TRANSACTION_LABELS.get(x, x),
                                          key=f"{prefix}_trans")
    pmin, pmax = db_manager.get_price_bounds()
    with c4:
        prix_min = st.number_input("Prix min (FCFA)", min_value=0, value=pmin, step=50000, key=f"{prefix}_pmin")
    with c5:
        prix_max = st.number_input("Prix max (FCFA)", min_value=0, value=pmax, step=50000, key=f"{prefix}_pmax")

    if prix_min > prix_max:
        prix_min, prix_max = prix_max, prix_min

    filters = {'prix_min': prix_min, 'prix_max': prix_max}
    if type_filter != "Tous":
        filters['type_bien'] = type_filter
    if transaction_filter != "Tous":
        filters['transaction_type'] = transaction_filter
    if q and q.strip():
        filters['q'] = q
    return filters


def show_listings(filters_key_prefix, role=None, public_view=False):
    show_section_title("fa-search", "Propriétés disponibles")

    filters = _liste_filtres(filters_key_prefix)

    sort_map = {
        "Plus récents": "recent",
        "Prix croissant": "prix_asc",
        "Prix décroissant": "prix_desc",
        "Plus grandes surfaces": "taille_desc",
    }
    c_sort = st.selectbox("Trier par", list(sort_map.keys()), key=f"{filters_key_prefix}_sort")

    try:
        properties = db_manager.get_properties(filters, sort=sort_map[c_sort])
        if properties:
            show_result_bar(len(properties))
            cols = st.columns(3, gap="medium")
            for idx, prop in enumerate(properties):
                with cols[idx % 3]:
                    display_property_card(prop, user_role=role, public_view=public_view)
        else:
            st.info("Aucun bien ne correspond à ces critères. Modifiez vos filtres pour élargir la recherche.")
            if filters.get('q'):
                st.caption(f"Recherche : « {filters['q']} »")
    except Exception as e:
        st.error(f"Erreur : {str(e)}")


# ================================================================
# CARTE PROPRIÉTÉ
# ================================================================

def display_property_card(prop, user_role=None, public_view=False):
    pid = prop[0]
    dk = f"details_visible_{pid}"
    ak = f"appointment_form_visible_{pid}"
    if dk not in st.session_state:
        st.session_state[dk] = False
    if ak not in st.session_state:
        st.session_state[ak] = False

    is_featured = bool(prop[11])
    transaction = prop[6]
    trans_label = TRANSACTION_LABELS.get(transaction, transaction)
    price_html = prix_affichage(prop)
    m2 = f"{prop[8]:,.0f} m²" if prop[8] else "Surface n.c."

    tags = ""
    if is_featured:
        tags += '<span class="prop-tag featured"><i class="fas fa-star"></i> Mise en avant</span>'
    trans_cls = "vente" if transaction == "vente" else "location"
    tags += f'<span class="prop-tag {trans_cls}">{trans_label}</span>'

    st.markdown(f"""
    <div class="prop-card">
        <div class="prop-media">
            <img src="{property_image_uri(prop)}" alt="{prop[3]}" loading="lazy">
            <div class="prop-tags">{tags}</div>
            <div class="prop-price-badge">{price_html}</div>
        </div>
        <div class="prop-body">
            <div class="prop-title">{prop[3]}</div>
            <div class="prop-loc"><i class="fas fa-map-marker-alt"></i> {prop[7]}</div>
            <div class="prop-meta">
                <span class="prop-chip"><i class="fas fa-ruler-combined"></i> {m2}</span>
                <span class="prop-chip"><i class="fas fa-th-large"></i> {prop[4]}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="prop-actions">', unsafe_allow_html=True)
    if not st.session_state[dk]:
        if st.button("Découvrir ce bien", key=f"view_{pid}", width='stretch'):
            st.session_state[dk] = True
            st.rerun()
    else:
        _show_property_details(prop, pid, dk, ak, user_role, public_view)
    st.markdown('</div>', unsafe_allow_html=True)


def _show_property_details(prop, pid, dk, ak, user_role, public_view):
    is_featured = bool(prop[11])
    transaction = prop[6]
    trans_label = TRANSACTION_LABELS.get(transaction, transaction)
    m2 = f"{prop[8]:,.0f} m²" if prop[8] else "n.c."

    with st.container(border=True):
        st.markdown(f"""
        <div style="margin:-4px 0 8px;">
            <div style="font-size:0.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;font-weight:700;margin-bottom:6px;">Description</div>
            <div style="color:var(--ink);font-size:0.95rem;line-height:1.55;">{prop[10]}</div>
        </div>
        """, unsafe_allow_html=True)

        images = get_uploaded_images(pid)
        if images:
            st.markdown('<div style="font-size:0.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;font-weight:700;margin:4px 0 8px;">Photos</div>', unsafe_allow_html=True)
            img_cols = st.columns(min(len(images), 3))
            for i, img in enumerate(images[:3]):
                with img_cols[i]:
                    st.image(img, width='stretch')

        details_cols = st.columns(2)
        with details_cols[0]:
            st.markdown(f"**Type :** {prop[4]}")
            st.markdown(f"**Usage :** {prop[5]}")
            st.markdown(f"**Taille :** {m2}")
        with details_cols[1]:
            st.markdown(f"**Transaction :** {trans_label}")
            st.markdown(f"**Prix :** {fmt_fcfa(prop[9])}")
            if len(prop) > 15 and prop[14]:
                st.markdown(f"**Bailleur :** {prop[14]}" + (f" — {prop[15]}" if prop[15] else ""))
            if len(prop) > 17 and prop[16]:
                st.markdown(f"**Agent :** {prop[16]} {prop[17] or ''}".strip())

        if not public_view and user_role == 'client':
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Réserver une visite", key=f"appt_{pid}", width='stretch', type="primary"):
                    st.session_state[ak] = True
            with c2:
                is_fav = db_manager.is_favorite(st.session_state.user['id'], pid)
                label = "Retirer des favoris" if is_fav else "Garder en favori"
                if st.button(label, key=f"fav_{pid}", width='stretch'):
                    if is_fav:
                        db_manager.remove_from_favorites(st.session_state.user['id'], pid)
                        st.toast("Retiré des favoris")
                    else:
                        db_manager.add_to_favorites(st.session_state.user['id'], pid)
                        st.toast("Ajouté à vos favoris !")

    if st.button("Replier", key=f"hide_{pid}", width='stretch', type="secondary"):
        st.session_state[dk] = False
        st.session_state[ak] = False
        st.rerun()

    if st.session_state[ak] and user_role == 'client':
        show_appointment_form(pid, show_title=False)


# ================================================================
# APPLICATION CONNECTÉE
# ================================================================

def show_main_app():
    user = st.session_state.user

    menus = {
        'client': {"Voir les propriétés": "properties", "Mes favoris": "favorites", "Mes rendez-vous": "appointments"},
        'bailleur': {"Voir les propriétés": "properties", "Ajouter une propriété": "add_property", "Mes propriétés": "my_properties"},
        'agent': {"Voir les propriétés": "properties", "Ajouter une propriété": "add_property", "Mes clients": "my_clients", "Rendez-vous": "appointments"},
        'manager': {"Voir les propriétés": "properties", "Ajouter une propriété": "add_property", "Gestion des utilisateurs": "manage_users", "Statistiques": "statistics"},
    }

    MENU_ICONS = {
        "properties": "fa-home",
        "favorites": "fa-heart",
        "appointments": "fa-calendar-check",
        "add_property": "fa-plus-circle",
        "my_properties": "fa-list-alt",
        "my_clients": "fa-users",
        "manage_users": "fa-users-cog",
        "statistics": "fa-chart-bar",
        "dashboard": "fa-gauge-high",
    }

    current_menu = menus.get(user['role'], {})
    current_page = st.session_state.get('page', 'properties')

    if current_page not in current_menu.values():
        current_page = list(current_menu.values())[0]
        st.session_state.page = current_page

    default_index = list(current_menu.values()).index(current_page)

    with st.sidebar:
        show_sidebar_brand()
        st.divider()
        show_sidebar_user(user)
        st.caption(f"{user['email']} · {user['telephone'] or 'tél. non renseigné'}")
        st.divider()

        st.markdown('<div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.12em;color:rgba(255,255,255,0.55);font-weight:700;margin-bottom:6px;">Navigation</div>', unsafe_allow_html=True)
        labels = list(current_menu.keys())
        selection = st.radio("Navigation", labels, index=default_index, label_visibility="collapsed")
        st.session_state.page = current_menu[selection]

        st.divider()
        if st.button("Se déconnecter", width='stretch'):
            auth_manager.logout()
            st.rerun()

    page = st.session_state.get('page', 'properties')
    role = user['role']

    page_icon = MENU_ICONS.get(page, "fa-home")
    page_label = next((k for k, v in current_menu.items() if v == page), page)
    st.markdown(f'<div class="section-title"><span class="bar"></span><h2><i class="fas {page_icon}" style="color:var(--coral-strong);margin-right:8px;"></i>{page_label}</h2></div>', unsafe_allow_html=True)

    if page == "properties":
        show_listings(filters_key_prefix="priv", role=role, public_view=False)
    elif page == "favorites" and role == 'client':
        show_favorites()
    elif page == "appointments":
        show_appointments()
    elif page == "add_property" and role in ['bailleur', 'agent', 'manager']:
        show_add_property()
    elif page == "my_properties" and role == 'bailleur':
        show_my_properties()
    elif page == "my_clients" and role in ['agent', 'manager']:
        show_my_clients()
    elif page == "manage_users" and role == 'manager':
        show_manage_users()
    elif page == "statistics" and role == 'manager':
        show_statistics()


# ================================================================
# RENDEZ-VOUS
# ================================================================

def show_appointment_form(property_id, show_title=True):
    if show_title:
        show_section_title("fa-calendar-plus", "Prendre un rendez-vous")

    date_rdv = st.date_input("Date du rendez-vous", min_value=datetime.now().date(), key=f"appt_date_{property_id}")
    time_rdv = st.time_input("Heure du rendez-vous", value=dt_time(14, 0), key=f"appt_time_{property_id}")
    type_rdv = st.selectbox("Type de rendez-vous", ["visite", "transaction"],
                            format_func=lambda x: "Visite du bien" if x == "visite" else "Transaction",
                            key=f"appt_type_{property_id}")
    notes = st.text_area("Notes (optionnel)", placeholder="Précisez vos disponibilités ou vos questions...",
                         key=f"appt_notes_{property_id}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Confirmer", width='stretch', type="primary", key=f"appt_confirm_{property_id}"):
            try:
                property_data = db_manager.get_property_by_id(property_id)
                if property_data and property_data[2]:
                    db_manager.create_appointment(
                        st.session_state.user['id'], property_id, property_data[2],
                        datetime.combine(date_rdv, time_rdv), type_rdv, notes
                    )
                    st.toast("Rendez-vous créé !", icon=":material/celebration:")
                    st.session_state[f"appointment_form_visible_{property_id}"] = False
                    time.sleep(0.6)
                    st.rerun()
                else:
                    notify("error", "Impossible de créer le rendez-vous (agent non assigné).")
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
    with c2:
        if st.button("Annuler", width='stretch', key=f"appt_cancel_{property_id}"):
            st.session_state[f"appointment_form_visible_{property_id}"] = False
            st.rerun()


STATUS_BADGES = {
    "pending": '<span class="status-badge status-pending"><i class="fas fa-circle"></i> En attente</span>',
    "confirmed": '<span class="status-badge status-confirmed"><i class="fas fa-check-circle"></i> Confirmé</span>',
    "completed": '<span class="status-badge status-completed"><i class="fas fa-check-double"></i> Terminé</span>',
    "cancelled": '<span class="status-badge status-cancelled"><i class="fas fa-times-circle"></i> Annulé</span>',
}


def status_badge(status):
    return STATUS_BADGES.get(status, f"<span class='status-badge'>{status}</span>")


def show_appointments():
    user = st.session_state.user
    if user['role'] == 'client':
        show_client_appointments_view()
    elif user['role'] in ['agent', 'manager']:
        show_agent_appointments_view()


def show_client_appointments_view():
    try:
        appointments = db_manager.get_appointments(st.session_state.user['id'], 'client')
        if not appointments:
            st.info("Aucun rendez-vous planifié.")
            st.caption("Parcourez les propriétés et cliquez sur « Prendre rendez-vous » pour en créer un.")
            return
        for apt in appointments:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{apt[10]}**")
                    st.markdown(f"<span style='color:var(--muted);font-size:0.88rem;'>Agent : <b>{apt[11]} {apt[12] or ''}</b></span>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:0.9rem;margin-top:6px;'><i class='fas fa-calendar-day' style='color:var(--amber);'></i> {apt[4].strftime('%d/%m/%Y à %H:%M')} &nbsp;·&nbsp; {apt[5].title()}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(status_badge(apt[7]), unsafe_allow_html=True)
                if apt[7] == 'pending':
                    if st.button("Annuler ce rendez-vous", key=f"cancel_{apt[0]}", width='stretch'):
                        update_appointment_status(apt[0], 'cancelled')
                        notify("success", "Rendez-vous annulé")
                        st.rerun()
    except Exception as e:
        st.error(f"Erreur : {str(e)}")


def show_agent_appointments_view():
    try:
        appointments = db_manager.get_appointments(st.session_state.user['id'], 'agent')
        if not appointments:
            st.info("Aucun rendez-vous pour cet agent.")
            st.caption("Les demandes de rendez-vous de vos clients apparaîtront ici.")
            return
        for apt in appointments:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**Client : {apt[10]} {apt[11] or ''}**")
                    st.markdown(f"<span style='color:var(--muted);font-size:0.88rem;'>Propriété : <b>{apt[9]}</b></span>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:0.9rem;margin-top:6px;'><i class='fas fa-calendar-day' style='color:var(--amber);'></i> {apt[4].strftime('%d/%m/%Y à %H:%M')} &nbsp;·&nbsp; {apt[5].title()}</div>", unsafe_allow_html=True)
                    if apt[6]:
                        st.caption(f"Notes : {apt[6]}")
                with c2:
                    st.markdown(status_badge(apt[7]), unsafe_allow_html=True)
                if apt[7] == 'pending':
                    if st.button("Confirmer", key=f"confirm_{apt[0]}", width='stretch', type="primary"):
                        update_appointment_status(apt[0], 'confirmed')
                        st.rerun()
                if apt[7] in ['pending', 'confirmed']:
                    if st.button("Marquer terminé", key=f"complete_{apt[0]}", width='stretch'):
                        update_appointment_status(apt[0], 'completed')
                        st.rerun()
    except Exception as e:
        st.error(f"Erreur : {str(e)}")


# ================================================================
# FAVORIS
# ================================================================

def show_favorites():
    try:
        favorites = db_manager.get_user_favorites(st.session_state.user['id'])
        if not favorites:
            st.info("Vous n'avez aucune propriété favorite pour le moment.")
            st.caption("Ajoutez des biens à vos favoris depuis la page « Voir les propriétés ».")
            return
        show_result_bar(len(favorites))
        cols = st.columns(3, gap="medium")
        for idx, prop in enumerate(favorites):
            with cols[idx % 3]:
                display_property_card(prop, user_role='client', public_view=False)
    except Exception as e:
        st.error(f"Erreur : {str(e)}")


# ================================================================
# GESTION DES PROPRIÉTÉS
# ================================================================

def show_add_property():
    user = st.session_state.user
    with st.form("add_property_form"):
        c1, c2 = st.columns(2)
        with c1:
            titre = st.text_input("Titre*", placeholder="ex. Villa moderne avec piscine")
            type_bien = st.selectbox("Type*", ["Appartement", "Maison", "Bureau", "Commercial", "Terrain"])
            usage = st.selectbox("Usage*", ["Résidentiel", "Commercial", "Industriel", "Mixte"])
            transaction_type = st.selectbox("Transaction*", ["vente", "location"],
                                            format_func=lambda x: "À vendre" if x == "vente" else "À louer")
            situation_geo = st.text_input("Localisation*", placeholder="Quartier, ville")
        with c2:
            taille = st.number_input("Taille (m²)", min_value=0, step=1)
            prix = st.number_input("Prix (FCFA)*", min_value=0, step=10000)
            is_featured = st.checkbox("Mettre en avant")
            agent_id = user['id']
            if user['role'] == 'manager':
                agents = db_manager.get_all_users('agent')
                if agents:
                    agent_options = {f"{agent[5]} {agent[6] or ''}".strip(): agent[0] for agent in agents}
                    selected_agent = st.selectbox("Agent responsable", list(agent_options.keys()))
                    agent_id = agent_options[selected_agent]
        description = st.text_area("Description*", placeholder="Décrivez le bien : surface, pièces, équipements, environnement...")

        uploaded_files = st.file_uploader("Photos du bien", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

        submitted = st.form_submit_button("Ajouter la propriété", width='stretch', type="primary")
        if submitted:
            if all([titre, type_bien, usage, transaction_type, situation_geo, prix > 0, description]):
                bailleur_id = user['id'] if user['role'] == 'bailleur' else None
                property_id_tuple = db_manager.add_property(
                    bailleur_id, agent_id, titre, type_bien, usage,
                    transaction_type, situation_geo, taille, prix, description, is_featured
                )
                if property_id_tuple:
                    if uploaded_files:
                        save_image_set(property_id_tuple[0], uploaded_files)
                    notify("success", "Propriété ajoutée !")
                else:
                    notify("error", "Erreur lors de l'ajout.")
            else:
                notify("error", "Veuillez remplir tous les champs obligatoires (*).")


def show_my_properties():
    if 'editing_property_id' not in st.session_state:
        st.session_state.editing_property_id = None

    if st.session_state.editing_property_id:
        show_edit_property_form(st.session_state.editing_property_id)
        return

    user = st.session_state.user
    try:
        query = "SELECT p.* FROM properties p WHERE p.bailleur_id = %s ORDER BY p.created_at DESC"
        properties = db_manager.execute_query(query, (user['id'],), fetch='all')
        if not properties:
            st.info("Vous n'avez aucune propriété enregistrée.")
            st.caption("Utilisez « Ajouter une propriété » pour mettre en ligne votre premier bien.")
            return
        for prop in properties:
            with st.container(border=True):
                c1, c2 = st.columns([2.6, 1.4])
                with c1:
                    st.markdown(f"**{prop[3]}**")
                    st.markdown(f"<span style='color:var(--muted);font-size:0.88rem;'><i class='fas fa-map-marker-alt'></i> {prop[7]} · {fmt_fcfa(prop[9])}</span>", unsafe_allow_html=True)
                    badge_cls = "status-confirmed" if prop[12] else "status-cancelled"
                    libelle = "Actif" if prop[12] else "Masqué"
                    st.markdown(f"<span class='status-badge {badge_cls}'>• {libelle}</span>", unsafe_allow_html=True)
                with c2:
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("Modifier", key=f"edit_{prop[0]}", width='stretch'):
                            st.session_state.editing_property_id = prop[0]
                            st.rerun()
                    with b2:
                        status_text = "Masquer" if prop[12] else "Activer"
                        if st.button(status_text, key=f"toggle_{prop[0]}", width='stretch', type="secondary"):
                            toggle_property_status(prop[0], not prop[12])
                            st.rerun()
    except Exception as e:
        st.error(f"Erreur : {str(e)}")


def show_edit_property_form(property_id):
    st.subheader("Modifier la propriété")
    property_data = db_manager.get_property_by_id(property_id)
    if not property_data:
        notify("error", "Propriété non trouvée.")
        st.session_state.editing_property_id = None
        st.rerun()
        return

    default_price = float(property_data[9]) if property_data[9] is not None else 0.0

    with st.form(f"edit_property_{property_id}"):
        c1, c2 = st.columns(2)
        with c1:
            titre = st.text_input("Titre*", value=property_data[3], key=f"edit_titre_{property_id}")
            type_bien = st.selectbox(
                "Type*", ["Appartement", "Maison", "Bureau", "Commercial", "Terrain"],
                index=["Appartement", "Maison", "Bureau", "Commercial", "Terrain"].index(property_data[4]),
                key=f"edit_type_{property_id}")
            transaction = st.selectbox(
                "Transaction*", ["vente", "location"],
                index=["vente", "location"].index(property_data[6]),
                format_func=lambda x: "À vendre" if x == "vente" else "À louer",
                key=f"edit_trans_{property_id}")
        with c2:
            taille = st.number_input("Taille (m²)", value=property_data[8] or 0, key=f"edit_taille_{property_id}")
            prix = st.number_input("Prix (FCFA)*", value=default_price, format="%.0f", key=f"edit_prix_{property_id}")
            is_featured = st.checkbox("Mettre en avant", value=property_data[11], key=f"edit_feat_{property_id}")
        description = st.text_area("Description*", value=property_data[10], key=f"edit_desc_{property_id}")

        uploaded_files = st.file_uploader("Ajouter/Remplacer des photos", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

        s1, s2 = st.columns(2)
        with s1:
            submitted = st.form_submit_button("Sauvegarder", width='stretch', type="primary")
        with s2:
            cancelled = st.form_submit_button("Annuler", width='stretch', type="secondary")

        if submitted:
            if all([titre, type_bien, transaction, description]):
                update_property(property_id, titre, type_bien, transaction, property_data[7], taille, prix, description, is_featured)
                if uploaded_files:
                    save_image_set(property_id, uploaded_files)
                notify("success", "Modifié !")
                st.session_state.editing_property_id = None
                time.sleep(0.6)
                st.rerun()
            else:
                notify("error", "Champs requis manquants.")
        if cancelled:
            st.session_state.editing_property_id = None
            st.rerun()


# ================================================================
# GESTION DES CLIENTS & UTILISATEURS
# ================================================================

def show_my_clients():
    user = st.session_state.user
    try:
        query = """
        SELECT u.*, ca.created_at as assigned_date
        FROM users u
        JOIN client_assignments ca ON u.id = ca.client_id
        WHERE ca.agent_id = %s AND ca.is_active = TRUE AND u.role = 'client'
        ORDER BY ca.created_at DESC
        """
        clients = db_manager.execute_query(query, (user['id'],), fetch='all')
        if not clients:
            st.info("Aucun client assigné.")
            st.caption("Vos clients assignés par le manager apparaîtront ici.")
            return
        cols = st.columns(2, gap="medium")
        for idx, client in enumerate(clients):
            with cols[idx % 2]:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{client[5]} {client[6] or ''}**")
                        st.markdown(f"<span style='color:var(--muted);font-size:0.88rem;'>{client[2]} · {client[8] or 'tél. n.r.'}</span>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<span style='color:var(--faint);font-size:0.8rem;'>Assigné le<br><b>{client[-1].strftime('%d/%m/%Y')}</b></span>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur : {str(e)}")


def show_manage_users():
    tab1, tab2 = st.tabs(["Utilisateurs", "Assignations"])
    with tab1:
        try:
            users = db_manager.execute_query("SELECT * FROM users ORDER BY role, nom", fetch='all')
            if not users:
                st.info("Aucun utilisateur.")
                return
            roles = {"client": "Client", "bailleur": "Bailleur", "agent": "Agent", "manager": "Manager"}
            for user in users:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2.6, 1, 1.2])
                    with c1:
                        st.markdown(
                            f"**{user[5]} {user[6] or ''}** "
                            f"<span class='status-badge status-completed'>{roles.get(user[4], user[4])}</span>"
                            f"<br><span style='color:var(--muted);font-size:0.85rem;'>{user[1]} · {user[2]}</span>",
                            unsafe_allow_html=True
                        )
                    with c2:
                        badge_cls = "status-confirmed" if user[11] else "status-cancelled"
                        libelle = "Actif" if user[11] else "Inactif"
                        st.markdown(f"<span class='status-badge {badge_cls}'>• {libelle}</span>", unsafe_allow_html=True)
                    with c3:
                        if user[4] != 'manager':
                            action = "Désactiver" if user[11] else "Activer"
                            if st.button(action, key=f"toggle_user_{user[0]}", width='stretch', type="secondary"):
                                toggle_user_status(user[0], not user[11])
                                st.rerun()
        except Exception as e:
            st.error(f"Erreur : {str(e)}")
    with tab2:
        try:
            clients = db_manager.get_all_users('client')
            agents = db_manager.get_all_users('agent')
            if clients and agents:
                c_opts = {f"{c[5]} {c[6] or ''}".strip(): c[0] for c in clients}
                a_opts = {f"{a[5]} {a[6] or ''}".strip(): a[0] for a in agents}
                with st.container(border=True):
                    col_c, col_a, col_b = st.columns([1, 1, 0.8])
                    with col_c:
                        sel_c = st.selectbox("Client", list(c_opts.keys()))
                    with col_a:
                        sel_a = st.selectbox("Agent", list(a_opts.keys()))
                    with col_b:
                        st.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                        if st.button("Assigner", width='stretch', type="primary"):
                            db_manager.assign_client_to_agent(c_opts[sel_c], a_opts[sel_a], st.session_state.user['id'])
                            notify("success", "Assignation réussie !")
                            st.balloons()
            else:
                notify("warning", "Il faut au moins un client et un agent actifs pour faire une assignation.")
        except Exception as e:
            st.error(f"Erreur : {str(e)}")


# ================================================================
# STATISTIQUES MANAGER
# ================================================================

def show_statistics():
    from utils.reporting import reporting_engine

    try:
        property_analytics = reporting_engine.generate_property_analytics()
        user_analytics = reporting_engine.generate_user_analytics()
        appointment_analytics = reporting_engine.generate_appointment_analytics()
        business_metrics = reporting_engine.generate_business_metrics()

        c1, c2, c3, c4 = st.columns(4)
        total_properties = sum(property_analytics.get('property_types', {}).values())
        total_users = sum(user_analytics.get('user_roles', {}).values())
        total_appointments = sum(appointment_analytics.get('appointment_status', {}).values())
        portfolio_value = business_metrics.get('portfolio_value', (0, 0))[0]

        with c1:
            st.metric("Propriétés", total_properties)
        with c2:
            st.metric("Utilisateurs", total_users)
        with c3:
            st.metric("Rendez-vous", total_appointments)
        with c4:
            conversion = business_metrics.get('conversion_rate', 0)
            st.metric("Taux de conversion", f"{conversion:.1f}%" if total_appointments else "—")

        st.divider()

        tab1, tab2, tab3, tab4 = st.tabs(["Propriétés", "Utilisateurs", "Rendez-vous", "Analyse commerciale"])

        with tab1:
            df_prices = property_analytics.get('price_stats_df')
            if df_prices is not None and not df_prices.empty:
                df_prices['transaction_label'] = df_prices['transaction_type'].map(TRANSACTION_LABELS)
                fig = px.bar(df_prices, x='transaction_label', y='avg_price',
                             title="Prix moyen par type de transaction", **PX_BASE)
                fig.update_traces(marker_color=["#1B4A38", "#D19A2F"],
                                  texttemplate="%{y:,.0f}", textposition="outside", cliponaxis=False)
                fig.update_yaxes(tickformat=",")
                _fig_layout(fig)
                st.plotly_chart(fig, width='stretch')

            df_geo = property_analytics.get('geographic_distribution_df')
            if df_geo is not None and not df_geo.empty:
                fig = px.bar(df_geo, x='Localisation', y='Nombre', title="Top 10 des localisations", **PX_BASE)
                fig.update_traces(marker_color="#1B4A38")
                fig.update_xaxes(tickangle=25)
                _fig_layout(fig)
                st.plotly_chart(fig, width='stretch')

            if property_analytics.get('property_types'):
                df = pd.DataFrame(list(property_analytics['property_types'].items()), columns=['Type', 'Nombre'])
                fig = px.pie(df, names='Type', values='Nombre', title="Répartition par type de bien", hole=0.55, **PX_BASE)
                fig.update_traces(textposition="inside", textinfo="percent+label")
                _fig_layout(fig)
                st.plotly_chart(fig, width='stretch')

        with tab2:
            if user_analytics.get('user_roles'):
                labels = {"client": "Clients", "bailleur": "Bailleurs", "agent": "Agents", "manager": "Managers"}
                df = pd.DataFrame(list(user_analytics['user_roles'].items()), columns=['Rôle', 'Nombre'])
                df['Rôle'] = df['Rôle'].map(labels)
                fig = px.bar(df, x='Rôle', y='Nombre', title="Répartition des utilisateurs par rôle", **PX_BASE)
                fig.update_traces(marker_color="#D19A2F", text=df['Nombre'], textposition="outside", cliponaxis=False)
                _fig_layout(fig)
                st.plotly_chart(fig, width='stretch')

        with tab3:
            c1, c2 = st.columns(2)
            with c1:
                status_data = appointment_analytics.get('appointment_status')
                if status_data:
                    labels = {"pending": "En attente", "confirmed": "Confirmés", "completed": "Terminés", "cancelled": "Annulés"}
                    df = pd.DataFrame(list(status_data.items()), columns=['Statut', 'Nombre'])
                    df['Statut'] = df['Statut'].map(labels)
                    fig = px.pie(df, names='Statut', values='Nombre', title="Répartition par statut", hole=0.55, **PX_BASE)
                    fig.update_traces(textposition="inside", textinfo="percent+label")
                    _fig_layout(fig)
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.caption("Aucun rendez-vous enregistré.")
            with c2:
                types_data = appointment_analytics.get('appointment_types')
                if types_data:
                    labels = {"visite": "Visites", "transaction": "Transactions"}
                    df = pd.DataFrame(list(types_data.items()), columns=['Type', 'Nombre'])
                    df['Type'] = df['Type'].map(labels)
                    fig = px.pie(df, names='Type', values='Nombre', title="Répartition par type de RDV", hole=0.55, **PX_BASE)
                    fig.update_traces(textposition="inside", textinfo="percent+label")
                    _fig_layout(fig)
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.caption("Aucun rendez-vous enregistré.")

            df_perf = appointment_analytics.get('agent_performance_df')
            if df_perf is not None and not df_perf.empty:
                df_perf['Agent'] = df_perf['Nom'] + ' ' + df_perf['Prenom'].fillna('')
                fig = px.bar(df_perf.head(10), x='Agent', y='RDV_Gérés', title="Performance des agents (RDV gérés)", **PX_BASE)
                fig.update_traces(marker_color="#3A6B8A", text=df_perf['RDV_Gérés'].head(10), textposition="outside", cliponaxis=False)
                fig.update_xaxes(tickangle=25)
                _fig_layout(fig)
                st.plotly_chart(fig, width='stretch')

        with tab4:
            combos = business_metrics.get('popular_combinations_df')
            if combos is not None and not combos.empty:
                combos['Combinaison'] = combos['Type'] + ' — ' + combos['Transaction'].map(TRANSACTION_LABELS)
                fig = px.bar(combos.head(10), x='Combinaison', y='Nombre', title="Top des combinaisons type / transaction", **PX_BASE)
                fig.update_traces(marker_color="#B6482F", text=combos['Nombre'].head(10), textposition="outside", cliponaxis=False)
                fig.update_xaxes(tickangle=25)
                _fig_layout(fig)
                st.plotly_chart(fig, width='stretch')

            df_fav = business_metrics.get('most_favorited_df')
            if df_fav is not None and not df_fav.empty:
                fig = px.bar(df_fav.head(10), x='Propriété', y='Favoris', title="Propriétés les plus mises en favori", **PX_BASE)
                fig.update_traces(marker_color="#2E7D5B", text=df_fav['Favoris'].head(10), textposition="outside", cliponaxis=False)
                fig.update_xaxes(tickangle=30)
                _fig_layout(fig)
                st.plotly_chart(fig, width='stretch')

            if portfolio_value:
                avg_v = business_metrics.get('portfolio_value', (0, 0))[1]
                cA, cB = st.columns(2)
                with cA:
                    st.metric("Valeur totale du portefeuille", fmt_fcfa(portfolio_value))
                with cB:
                    st.metric("Prix moyen d'un bien", fmt_fcfa(avg_v) if avg_v else "N/A")

    except Exception as e:
        st.error(f"Erreur lors du chargement des statistiques : {str(e)}")
        st.exception(e)


# ================================================================
# Helpers
# ================================================================

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