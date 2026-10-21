# --- ImmoPro - application de gestion immobiliere ---

import streamlit as st
import sys
import os
from datetime import datetime
from datetime import time as dt_time
from html import escape
import time
import pandas as pd
import plotly.express as px

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.auth import auth_manager
from utils.database import (
    DatabaseError, biens_en_cache, bornes_prix_en_cache, compte_biens_en_cache,
    db_manager, log_exception, statistiques_en_cache, vider_cache,
)
from utils.media import (
    fmt_prix, get_uploaded_images_map, prix_affichage, property_image_uri,
    save_image_set,
)
from styles import inject_styles
from layout_utils import (
    show_public_hero, show_perks, show_section_title, show_result_bar, show_sidebar_brand,
    show_sidebar_user, show_header, show_footer,
)

# ----------------------------------------------------------------
# Palette Plotly coherente avec le design system "Soleil"
# ----------------------------------------------------------------
PLOTLY_COLORS = ["#E9643B", "#0F7A68", "#F5A623", "#E0403B", "#12A07E", "#C46A9B", "#8A7566"]
PX_BASE = dict(
    template="plotly_white",
    color_discrete_sequence=PLOTLY_COLORS,
)

# Nombre de biens affiches par page.
BIENS_PAR_PAGE = 9


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


TRANSACTION_LABELS = {"vente": "A vendre", "location": "A louer"}

ALERT_ICONS = {"success": ":material/task_alt:", "info": ":material/info:", "warning": ":material/warning:", "error": ":material/error:"}


def notify(level, message):
    """Message d'alerte affiche sous forme de popup (toast)."""
    st.toast(message, icon=ALERT_ICONS.get(level, ":material/info:"))


def e(valeur):
    """Echappe une valeur destinee a etre injectee en HTML.

    Sans cet appel, un titre de bien contenant du code HTML serait
    interprete par le navigateur.
    """
    if valeur is None:
        return ""
    return escape(str(valeur), quote=True)


def erreur_attendue(exc, message="L operation n a pas pu aboutir. Reessayez dans un instant."):
    """Trace l'erreur cote serveur et affiche un message generique."""
    log_exception("application", exc)
    st.error(message)


# --- Fonctions d'affichage des vues (Pages) ---

def main():
    st.set_page_config(
        page_title="ImmoPro - Gestion Immobiliere",
        page_icon=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "logo.png"),
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
    try:
        stats = statistiques_en_cache()
    except DatabaseError:
        stats = {}

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
        if st.button("Je cree mon compte", width='stretch', type="primary"):
            register_dialog()

    show_listings(filters_key_prefix="pub", role=None, public_view=True)


@st.dialog("Connexion", width="small", icon=":material/lock:")
def login_dialog():
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:1.2rem;">
            <svg width="44" height="44" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#E9643B"/><path d="M14 34 L32 18 L50 34" fill="none" stroke="#FBF1E4" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><path d="M20 31 V46 H44 V31" fill="none" stroke="#FBF1E4" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="46" cy="15" r="4.5" fill="#FBF1E4"/></svg>
            <h2 style="margin:.3rem 0 .2rem; font-family:'Fredoka','Nunito',sans-serif;">Bon retour</h2>
            <p style="color:#8a7a6a; margin:0; font-size:.9rem;">Connectez-vous pour acceder a votre espace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("public_login_form"):
        username = st.text_input("Nom d'utilisateur", placeholder="Votre identifiant")
        password = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe")
        submitted = st.form_submit_button("Me connecter", width='stretch', type="primary")
        if submitted:
            if not (username and password):
                notify("warning", "Veuillez remplir tous les champs.")
            else:
                user = auth_manager.login(username, password)
                if user:
                    st.session_state.user = user
                    st.toast("Connexion reussie !", icon=":material/celebration:")
                    time.sleep(0.6)
                    st.rerun()
                elif auth_manager.est_bloque(username, auth_manager.client_ip()):
                    notify("error", "Trop de tentatives. Reessayez dans quinze minutes.")
                else:
                    notify("error", "Nom d'utilisateur ou mot de passe incorrect.")


@st.dialog("Creer un compte", width="medium", icon=":material/star:")
def register_dialog():
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:1.2rem;">
            <svg width="44" height="44" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#E9643B"/><path d="M14 34 L32 18 L50 34" fill="none" stroke="#FBF1E4" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><path d="M20 31 V46 H44 V31" fill="none" stroke="#FBF1E4" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="46" cy="15" r="4.5" fill="#FBF1E4"/></svg>
            <h2 style="margin:.3rem 0 .2rem; font-family:'Fredoka','Nunito',sans-serif;">Creez votre compte</h2>
            <p style="color:#8a7a6a; margin:0; font-size:.9rem;">Rejoignez ImmoPro en moins d'une minute.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("public_register_form"):
        role = st.selectbox("Type de compte", ["client", "bailleur"],
                            help="Client : recherchez des biens. Bailleur : mettez vos biens en ligne.")
        c1, c2 = st.columns(2)
        with c1:
            username = st.text_input("Nom d'utilisateur*", placeholder="ex. martin12")
            nom = st.text_input("Nom*")
            email = st.text_input("Email*", placeholder="vous@exemple.com")
            telephone = st.text_input("Telephone", placeholder="+33 6 12 34 56 78")
        with c2:
            password = st.text_input("Mot de passe*", type="password", help="Au moins 8 caracteres.")
            prenom = st.text_input("Prenom")
            if role == "bailleur":
                raison_sociale = st.text_input("Raison sociale")
            else:
                raison_sociale = None

        adresse = st.text_area("Adresse", placeholder="Rue, ville, code postal")

        submitted = st.form_submit_button("C'est parti !", width='stretch', type="primary")
        if submitted:
            if not (username and password and nom and email):
                notify("error", "Veuillez remplir tous les champs obligatoires (*).")
            elif len(password) < 8:
                notify("error", "Le mot de passe doit contenir au moins 8 caracteres.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                notify("error", "Veuillez saisir une adresse email valide.")
            else:
                result = auth_manager.register(username, email, password, role, nom,
                                               prenom, raison_sociale, telephone, adresse)
                if result['success']:
                    st.toast(result['message'], icon=":material/celebration:")
                    time.sleep(0.8)
                    st.rerun()
                else:
                    notify("error", result['message'])


def _liste_filtres(prefix):
    """Barre de filtres commune (publique et connectee)."""
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
    pmin, pmax = bornes_prix_en_cache()
    with c4:
        prix_min = st.number_input("Prix min (EUR)", min_value=0, value=pmin, step=50000, key=f"{prefix}_pmin")
    with c5:
        prix_max = st.number_input("Prix max (EUR)", min_value=0, value=pmax, step=50000, key=f"{prefix}_pmax")

    if prix_min > prix_max:
        prix_min, prix_max = prix_max, prix_min

    return {
        'q': q,
        'type_bien': None if type_filter == "Tous" else type_filter,
        'transaction_type': None if transaction_filter == "Tous" else transaction_filter,
        'prix_min': prix_min,
        'prix_max': prix_max,
    }


def show_listings(filters_key_prefix, role=None, public_view=False):
    show_section_title("fa-search", "Proprietes disponibles")

    try:
        filters = _liste_filtres(filters_key_prefix)
    except DatabaseError as exc:
        erreur_attendue(exc)
        return

    sort_map = {
        "Plus recents": "recent",
        "Prix croissant": "prix_asc",
        "Prix decroissant": "prix_desc",
        "Plus grandes surfaces": "taille_desc",
    }
    c_sort = st.selectbox("Trier par", list(sort_map.keys()), key=f"{filters_key_prefix}_sort")

    page_key = f"{filters_key_prefix}_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    try:
        total = compte_biens_en_cache(filters)
        nb_pages = max(1, (total + BIENS_PAR_PAGE - 1) // BIENS_PAR_PAGE)
        if st.session_state[page_key] >= nb_pages:
            st.session_state[page_key] = nb_pages - 1

        properties = biens_en_cache(
            filters,
            sort=sort_map[c_sort],
            limit=BIENS_PAR_PAGE,
            offset=st.session_state[page_key] * BIENS_PAR_PAGE,
        )
    except DatabaseError as exc:
        erreur_attendue(exc)
        return

    if properties:
        show_result_bar(total)
        images = get_uploaded_images_map([p['id'] for p in properties])
        cols = st.columns(3, gap="medium")
        for idx, prop in enumerate(properties):
            with cols[idx % 3]:
                display_property_card(prop, user_role=role, public_view=public_view,
                                      images=images.get(prop['id'], []))

        if nb_pages > 1:
            c_prec, c_info, c_suiv = st.columns([1, 2, 1])
            with c_prec:
                if st.button("Precedent", width='stretch', disabled=st.session_state[page_key] == 0):
                    st.session_state[page_key] = max(0, st.session_state[page_key] - 1)
                    st.rerun()
            with c_info:
                st.caption(f"Page {st.session_state[page_key] + 1} sur {nb_pages} - {total} biens")
            with c_suiv:
                if st.button("Suivant", width='stretch', disabled=st.session_state[page_key] >= nb_pages - 1):
                    st.session_state[page_key] = min(nb_pages - 1, st.session_state[page_key] + 1)
                    st.rerun()
    else:
        st.info("Aucun bien ne correspond a ces criteres. Modifiez vos filtres pour elargir la recherche.")
        if filters.get('q'):
            st.caption(f"Recherche : « {filters['q']} »")


# ================================================================
# CARTE PROPRIETE
# ================================================================

def display_property_card(prop, user_role=None, public_view=False, images=None):
    pid = prop['id']
    dk = f"details_visible_{pid}"
    ak = f"appointment_form_visible_{pid}"
    if dk not in st.session_state:
        st.session_state[dk] = False
    if ak not in st.session_state:
        st.session_state[ak] = False

    is_featured = bool(prop.get('is_featured'))
    transaction = prop.get('transaction_type')
    trans_label = TRANSACTION_LABELS.get(transaction, transaction)
    price_html = prix_affichage(prop)
    taille = prop.get('taille')
    m2 = f"{taille:,.0f} m2" if taille else "Surface n.c."

    tags = ""
    if is_featured:
        tags += '<span class="prop-tag featured"><i class="fas fa-star"></i> Mise en avant</span>'
    trans_cls = "vente" if transaction == "vente" else "location"
    tags += f'<span class="prop-tag {trans_cls}">{e(trans_label)}</span>'

    st.markdown(f"""
    <div class="prop-card">
        <div class="prop-media">
            <img src="{e(property_image_uri(prop, images=images))}" alt="{e(prop.get('titre'))}" loading="lazy">
            <div class="prop-tags">{tags}</div>
            <div class="prop-price-badge">{price_html}</div>
        </div>
        <div class="prop-body">
            <div class="prop-title">{e(prop.get('titre'))}</div>
            <div class="prop-loc"><i class="fas fa-map-marker-alt"></i> {e(prop.get('situation_geo'))}</div>
            <div class="prop-meta">
                <span class="prop-chip"><i class="fas fa-ruler-combined"></i> {e(m2)}</span>
                <span class="prop-chip"><i class="fas fa-th-large"></i> {e(prop.get('type_bien'))}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="prop-actions">', unsafe_allow_html=True)
    if not st.session_state[dk]:
        if st.button("Decouvrir ce bien", key=f"view_{pid}", width='stretch'):
            st.session_state[dk] = True
            st.rerun()
    else:
        _show_property_details(prop, pid, dk, ak, user_role, public_view, images)
    st.markdown('</div>', unsafe_allow_html=True)


def _show_property_details(prop, pid, dk, ak, user_role, public_view, images=None):
    is_featured = bool(prop.get('is_featured'))
    transaction = prop.get('transaction_type')
    trans_label = TRANSACTION_LABELS.get(transaction, transaction)
    taille = prop.get('taille')
    m2 = f"{taille:,.0f} m2" if taille else "n.c."

    with st.container(border=True):
        st.markdown(f"""
        <div style="margin:-4px 0 8px;">
            <div style="font-size:0.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;font-weight:700;margin-bottom:6px;">Description</div>
            <div style="color:var(--ink);font-size:0.95rem;line-height:1.55;">{e(prop.get('description'))}</div>
        </div>
        """, unsafe_allow_html=True)

        if images:
            st.markdown('<div style="font-size:0.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;font-weight:700;margin:4px 0 8px;">Photos</div>', unsafe_allow_html=True)
            img_cols = st.columns(min(len(images), 3))
            for i, img in enumerate(images[:3]):
                with img_cols[i]:
                    st.image(img, width='stretch')

        details_cols = st.columns(2)
        with details_cols[0]:
            st.markdown(f"**Type :** {e(prop.get('type_bien'))}")
            st.markdown(f"**Usage :** {e(prop.get('usage_possible'))}")
            st.markdown(f"**Taille :** {e(m2)}")
        with details_cols[1]:
            st.markdown(f"**Transaction :** {e(trans_label)}")
            st.markdown(f"**Prix :** {fmt_prix(prop.get('prix'))}")
            if prop.get('bailleur_nom'):
                bailleur = e(prop.get('bailleur_nom'))
                raison = e(prop.get('bailleur_raison_sociale'))
                st.markdown(f"**Bailleur :** {bailleur}" + (f" - {raison}" if raison else ""))
            if prop.get('agent_nom'):
                agent = e(prop.get('agent_nom'))
                prenom = e(prop.get('agent_prenom'))
                st.markdown(f"**Agent :** {agent} {prenom}".strip())

        if not public_view and user_role == 'client':
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Reserver une visite", key=f"appt_{pid}", width='stretch', type="primary"):
                    st.session_state[ak] = True
            with c2:
                is_fav = db_manager.is_favorite(st.session_state.user['id'], pid)
                label = "Retirer des favoris" if is_fav else "Garder en favori"
                if st.button(label, key=f"fav_{pid}", width='stretch'):
                    if is_fav:
                        db_manager.remove_from_favorites(st.session_state.user['id'], pid)
                        st.toast("Retire des favoris")
                    else:
                        db_manager.add_to_favorites(st.session_state.user['id'], pid)
                        st.toast("Ajoute a vos favoris !")

    if st.button("Replier", key=f"hide_{pid}", width='stretch', type="secondary"):
        st.session_state[dk] = False
        st.session_state[ak] = False
        st.rerun()

    if st.session_state[ak] and user_role == 'client':
        show_appointment_form(pid, show_title=False)


# ================================================================
# APPLICATION CONNECTEE
# ================================================================

def show_main_app():
    user = st.session_state.user

    menus = {
        'client': {"Voir les proprietes": "properties", "Mes favoris": "favorites", "Mes rendez-vous": "appointments"},
        'bailleur': {"Voir les proprietes": "properties", "Ajouter une propriete": "add_property", "Mes proprietes": "my_properties"},
        'agent': {"Voir les proprietes": "properties", "Ajouter une propriete": "add_property", "Mes clients": "my_clients", "Rendez-vous": "appointments"},
        'manager': {"Voir les proprietes": "properties", "Ajouter une propriete": "add_property", "Gestion des utilisateurs": "manage_users", "Statistiques": "statistics"},
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
        st.caption(f"{user['email']} · {user['telephone'] or 'tel. non renseigne'}")
        st.divider()

        st.markdown('<div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.12em;color:rgba(255,255,255,0.55);font-weight:700;margin-bottom:6px;">Navigation</div>', unsafe_allow_html=True)
        labels = list(current_menu.keys())
        selection = st.radio("Navigation", labels, index=default_index, label_visibility="collapsed")
        st.session_state.page = current_menu[selection]

        st.divider()
        if st.button("Se deconnecter", width='stretch'):
            auth_manager.logout()
            st.rerun()

    page = st.session_state.get('page', 'properties')
    role = user['role']

    page_icon = MENU_ICONS.get(page, "fa-home")
    page_label = next((k for k, v in current_menu.items() if v == page), page)
    st.markdown(f'<div class="section-title"><span class="bar"></span><h2><i class="fas {page_icon}" style="color:var(--coral-strong);margin-right:8px;"></i>{e(page_label)}</h2></div>', unsafe_allow_html=True)

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
    notes = st.text_area("Notes (optionnel)", placeholder="Precisez vos disponibilites ou vos questions...",
                         key=f"appt_notes_{property_id}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Confirmer", width='stretch', type="primary", key=f"appt_confirm_{property_id}"):
            try:
                property_data = db_manager.get_property_by_id(property_id)
                if not property_data:
                    notify("error", "Ce bien n'est plus disponible.")
                elif not property_data.get('is_available'):
                    notify("error", "Ce bien n'est plus disponible a la reservation.")
                elif not property_data.get('agent_id'):
                    notify("error", "Impossible de creer le rendez-vous (agent non assigne).")
                else:
                    agent_id = property_data['agent_id']
                    moment = datetime.combine(date_rdv, time_rdv)
                    conflits = db_manager.get_conflicting_appointments(agent_id, moment)
                    if conflits:
                        notify("error", "L'agent a deja un rendez-vous a ce creneau. Choisissez une autre horaire.")
                    else:
                        db_manager.create_appointment(
                            st.session_state.user['id'], property_id, agent_id,
                            moment, type_rdv, notes
                        )
                        vider_cache()
                        st.toast("Rendez-vous cree !", icon=":material/celebration:")
                        st.session_state[f"appointment_form_visible_{property_id}"] = False
                        time.sleep(0.6)
                        st.rerun()
            except DatabaseError as exc:
                erreur_attendue(exc)
    with c2:
        if st.button("Annuler", width='stretch', key=f"appt_cancel_{property_id}"):
            st.session_state[f"appointment_form_visible_{property_id}"] = False
            st.rerun()


STATUS_BADGES = {
    "pending": '<span class="status-badge status-pending"><i class="fas fa-circle"></i> En attente</span>',
    "confirmed": '<span class="status-badge status-confirmed"><i class="fas fa-check-circle"></i> Confirme</span>',
    "completed": '<span class="status-badge status-completed"><i class="fas fa-check-double"></i> Termine</span>',
    "cancelled": '<span class="status-badge status-cancelled"><i class="fas fa-times-circle"></i> Annule</span>',
}


def status_badge(status):
    if status in STATUS_BADGES:
        return STATUS_BADGES[status]
    return f"<span class='status-badge'>{e(status)}</span>"


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
            st.info("Aucun rendez-vous planifie.")
            st.caption("Parcourez les proprietes et cliquez sur « Prendre rendez-vous » pour en creer un.")
            return
        for apt in appointments:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{e(apt.get('property_titre'))}**")
                    st.markdown(f"<span style='color:var(--muted);font-size:0.88rem;'>Agent : <b>{e(apt.get('agent_nom'))} {e(apt.get('agent_prenom'))}</b></span>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:0.9rem;margin-top:6px;'><i class='fas fa-calendar-day' style='color:var(--amber);'></i> {apt['date_rdv'].strftime('%d/%m/%Y a %H:%M')} &nbsp;·&nbsp; {e((apt.get('type_rdv') or '').title())}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(status_badge(apt.get('status')), unsafe_allow_html=True)
                if apt.get('status') == 'pending':
                    if st.button("Annuler ce rendez-vous", key=f"cancel_{apt['id']}", width='stretch'):
                        db_manager.update_appointment_status(apt['id'], 'cancelled')
                        vider_cache()
                        notify("success", "Rendez-vous annule")
                        st.rerun()
    except DatabaseError as exc:
        erreur_attendue(exc)


def show_agent_appointments_view():
    role = st.session_state.user['role']
    try:
        # Un manager suit tous les rendez-vous de la plateforme.
        appointments = db_manager.get_appointments(st.session_state.user['id'], role)
        if not appointments:
            st.info("Aucun rendez-vous a traiter.")
            st.caption("Les demandes de rendez-vous de vos clients apparaitront ici.")
            return
        for apt in appointments:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**Client : {e(apt.get('client_nom'))} {e(apt.get('client_prenom'))}**")
                    st.markdown(f"<span style='color:var(--muted);font-size:0.88rem;'>Propriete : <b>{e(apt.get('property_titre'))}</b></span>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:0.9rem;margin-top:6px;'><i class='fas fa-calendar-day' style='color:var(--amber);'></i> {apt['date_rdv'].strftime('%d/%m/%Y a %H:%M')} &nbsp;·&nbsp; {e((apt.get('type_rdv') or '').title())}</div>", unsafe_allow_html=True)
                    if apt.get('notes'):
                        st.caption(f"Notes : {apt['notes']}")
                with c2:
                    st.markdown(status_badge(apt.get('status')), unsafe_allow_html=True)
                if apt.get('status') == 'pending':
                    if st.button("Confirmer", key=f"confirm_{apt['id']}", width='stretch', type="primary"):
                        db_manager.update_appointment_status(apt['id'], 'confirmed')
                        vider_cache()
                        st.rerun()
                if apt.get('status') in ['pending', 'confirmed']:
                    if st.button("Marquer termine", key=f"complete_{apt['id']}", width='stretch'):
                        db_manager.update_appointment_status(apt['id'], 'completed')
                        vider_cache()
                        st.rerun()
    except DatabaseError as exc:
        erreur_attendue(exc)


# ================================================================
# FAVORIS
# ================================================================

def show_favorites():
    try:
        favorites = db_manager.get_user_favorites(st.session_state.user['id'])
        if not favorites:
            st.info("Vous n'avez aucune propriete favorite pour le moment.")
            st.caption("Ajoutez des biens a vos favoris depuis la page « Voir les proprietes ».")
            return
        show_result_bar(len(favorites))
        images = get_uploaded_images_map([p['id'] for p in favorites])
        cols = st.columns(3, gap="medium")
        for idx, prop in enumerate(favorites):
            with cols[idx % 3]:
                display_property_card(prop, user_role='client', public_view=False,
                                      images=images.get(prop['id'], []))
    except DatabaseError as exc:
        erreur_attendue(exc)


# ================================================================
# GESTION DES PROPRIETES
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
            prix = st.number_input("Prix (EUR)*", min_value=0, step=10000)
            is_featured = st.checkbox("Mettre en avant")
            agent_id = user['id']
            if user['role'] == 'manager':
                agents = db_manager.get_all_users('agent')
                if agents:
                    agent_options = {f"{a['nom']} {a['prenom'] or ''}".strip(): a['id'] for a in agents}
                    selected_agent = st.selectbox("Agent responsable", list(agent_options.keys()))
                    agent_id = agent_options[selected_agent]
        description = st.text_area("Description*", placeholder="Décrivez le bien : surface, pièces, équipements, environnement...")

        uploaded_files = st.file_uploader("Photos du bien", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)

        submitted = st.form_submit_button("Ajouter la propriété", width='stretch', type="primary")
        if submitted:
            if all([titre, type_bien, usage, transaction_type, situation_geo, prix > 0, description]):
                bailleur_id = user['id'] if user['role'] == 'bailleur' else None
                try:
                    property_id_tuple = db_manager.add_property(
                        bailleur_id, agent_id, titre, type_bien, usage,
                        transaction_type, situation_geo, taille, prix, description, is_featured
                    )
                    if property_id_tuple:
                        if uploaded_files:
                            save_image_set(property_id_tuple['id'], uploaded_files)
                        vider_cache()
                        notify("success", "Propriété ajoutée !")
                    else:
                        notify("error", "Erreur lors de l'ajout.")
                except DatabaseError as exc:
                    erreur_attendue(exc)
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
        properties = db_manager.get_properties_by_bailleur(user['id'])
        if not properties:
            st.info("Vous n'avez aucune propriété enregistrée.")
            st.caption("Utilisez « Ajouter une propriété » pour mettre en ligne votre premier bien.")
            return
        for prop in properties:
            with st.container(border=True):
                c1, c2 = st.columns([2.6, 1.4])
                with c1:
                    st.markdown(f"**{e(prop.get('titre'))}**")
                    st.markdown(f"<span style='color:var(--muted);font-size:0.88rem;'><i class='fas fa-map-marker-alt'></i> {e(prop.get('situation_geo'))} · {fmt_prix(prop.get('prix'))}</span>", unsafe_allow_html=True)
                    badge_cls = "status-confirmed" if prop.get('is_available') else "status-cancelled"
                    libelle = "Actif" if prop.get('is_available') else "Masqué"
                    st.markdown(f"<span class='status-badge {badge_cls}'>• {libelle}</span>", unsafe_allow_html=True)
                with c2:
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("Modifier", key=f"edit_{prop['id']}", width='stretch'):
                            st.session_state.editing_property_id = prop['id']
                            st.rerun()
                    with b2:
                        status_text = "Masquer" if prop.get('is_available') else "Activer"
                        if st.button(status_text, key=f"toggle_{prop['id']}", width='stretch', type="secondary"):
                            db_manager.toggle_property_status(prop['id'], not prop.get('is_available'))
                            vider_cache()
                            st.rerun()
    except DatabaseError as exc:
        erreur_attendue(exc)


def show_edit_property_form(property_id):
    st.subheader("Modifier la propriété")
    property_data = db_manager.get_property_by_id(property_id)
    if not property_data:
        notify("error", "Propriété non trouvée.")
        st.session_state.editing_property_id = None
        st.rerun()
        return

    default_price = float(property_data['prix']) if property_data['prix'] is not None else 0.0

    with st.form(f"edit_property_{property_id}"):
        c1, c2 = st.columns(2)
        with c1:
            titre = st.text_input("Titre*", value=property_data['titre'], key=f"edit_titre_{property_id}")
            type_bien = st.selectbox(
                "Type*", ["Appartement", "Maison", "Bureau", "Commercial", "Terrain"],
                index=["Appartement", "Maison", "Bureau", "Commercial", "Terrain"].index(property_data['type_bien']),
                key=f"edit_type_{property_id}")
            transaction = st.selectbox(
                "Transaction*", ["vente", "location"],
                index=["vente", "location"].index(property_data['transaction_type']),
                format_func=lambda x: "À vendre" if x == "vente" else "À louer",
                key=f"edit_trans_{property_id}")
        with c2:
            taille = st.number_input("Taille (m²)", value=property_data['taille'] or 0, key=f"edit_taille_{property_id}")
            prix = st.number_input("Prix (EUR)*", value=default_price, format="%.0f", key=f"edit_prix_{property_id}")
            is_featured = st.checkbox("Mettre en avant", value=property_data['is_featured'], key=f"edit_feat_{property_id}")
        description = st.text_area("Description*", value=property_data['description'], key=f"edit_desc_{property_id}")

        uploaded_files = st.file_uploader("Ajouter/Remplacer des photos", type=['png', 'jpg', 'jpeg', 'webp'], accept_multiple_files=True)

        s1, s2 = st.columns(2)
        with s1:
            submitted = st.form_submit_button("Sauvegarder", width='stretch', type="primary")
        with s2:
            cancelled = st.form_submit_button("Annuler", width='stretch', type="secondary")

        if submitted:
            if all([titre, type_bien, transaction, description]):
                try:
                    db_manager.update_property(property_id, titre, type_bien, transaction,
                                             property_data['situation_geo'], taille, prix,
                                             description, is_featured)
                    if uploaded_files:
                        save_image_set(property_id, uploaded_files)
                    vider_cache()
                    notify("success", "Modifié !")
                    st.session_state.editing_property_id = None
                    time.sleep(0.6)
                    st.rerun()
                except DatabaseError as exc:
                    erreur_attendue(exc)
            else:
                notify("error", "Veuillez remplir tous les champs obligatoires (*).")
        if cancelled:
            st.session_state.editing_property_id = None
            st.rerun()


# ================================================================
# CLIENTS ET UTILISATEURS
# ================================================================

def show_my_clients():
    user = st.session_state.user
    try:
        # Un manager suit tous les clients de la plateforme.
        clients = db_manager.get_clients_for_agent(user['id'], role=user['role'])
        if not clients:
            st.info("Aucun client assigné.")
            st.caption("Les clients assignés par le manager apparaîtront ici.")
            return
        cols = st.columns(2, gap="medium")
        for idx, client in enumerate(clients):
            with cols[idx % 2]:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{e(client.get('nom'))} {e(client.get('prenom'))}**")
                        st.markdown(f"<span style='color:var(--muted);font-size:0.88rem;'>{e(client.get('email'))} · {e(client.get('telephone') or 'tel. n.r.')}</span>", unsafe_allow_html=True)
                    with c2:
                        date_affectation = client.get('assigned_date')
                        affichage = date_affectation.strftime('%d/%m/%Y') if date_affectation else '-'
                        st.markdown(f"<span style='color:var(--faint);font-size:0.8rem;'>Assigné le<br><b>{e(affichage)}</b></span>", unsafe_allow_html=True)
    except DatabaseError as exc:
        erreur_attendue(exc)


def show_manage_users():
    tab1, tab2 = st.tabs(["Utilisateurs", "Assignations"])
    with tab1:
        try:
            users = db_manager.get_all_users(include_inactive=True)
            if not users:
                st.info("Aucun utilisateur.")
                return
            roles = {"client": "Client", "bailleur": "Bailleur", "agent": "Agent", "manager": "Manager"}
            for user in users:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2.6, 1, 1.2])
                    with c1:
                        st.markdown(
                            f"**{e(user.get('nom'))} {e(user.get('prenom'))}** "
                            f"<span class='status-badge status-completed'>{e(roles.get(user.get('role'), user.get('role')))}</span>"
                            f"<br><span style='color:var(--muted);font-size:0.85rem;'>{e(user.get('username'))} · {e(user.get('email'))}</span>",
                            unsafe_allow_html=True
                        )
                    with c2:
                        badge_cls = "status-confirmed" if user.get('is_active') else "status-cancelled"
                        libelle = "Actif" if user.get('is_active') else "Inactif"
                        st.markdown(f"<span class='status-badge {badge_cls}'>• {libelle}</span>", unsafe_allow_html=True)
                    with c3:
                        if user.get('role') != 'manager':
                            action = "Désactiver" if user.get('is_active') else "Activer"
                            if st.button(action, key=f"toggle_user_{user['id']}", width='stretch', type="secondary"):
                                db_manager.set_user_active(user['id'], not user.get('is_active'))
                                vider_cache()
                                st.rerun()
        except DatabaseError as exc:
            erreur_attendue(exc)
    with tab2:
        try:
            clients = db_manager.get_all_users('client')
            agents = db_manager.get_all_users('agent')
            if clients and agents:
                c_opts = {f"{c['nom']} {c['prenom'] or ''}".strip(): c['id'] for c in clients}
                a_opts = {f"{a['nom']} {a['prenom'] or ''}".strip(): a['id'] for a in agents}
                with st.container(border=True):
                    col_c, col_a, col_b = st.columns([1, 1, 0.8])
                    with col_c:
                        sel_c = st.selectbox("Client", list(c_opts.keys()))
                    with col_a:
                        sel_a = st.selectbox("Agent", list(a_opts.keys()))
                    with col_b:
                        st.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
                        if st.button("Assigner", width='stretch', type="primary"):
                            try:
                                db_manager.assign_client_to_agent(c_opts[sel_c], a_opts[sel_a], st.session_state.user['id'])
                                vider_cache()
                                notify("success", "Assignation réussie !")
                                st.balloons()
                            except DatabaseError as exc:
                                erreur_attendue(exc)
            else:
                notify("warning", "Il faut au moins un client et un agent actifs pour faire une assignation.")
        except DatabaseError as exc:
            erreur_attendue(exc)


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
            st.metric("Taux de conversion", f"{conversion:.1f}%" if total_appointments else "-")

        st.divider()

        tab1, tab2, tab3, tab4 = st.tabs(["Propriétés", "Utilisateurs", "Rendez-vous", "Analyse commerciale"])

        with tab1:
            df_prices = property_analytics.get('price_stats_df')
            if df_prices is not None and not df_prices.empty:
                df_prices['transaction_label'] = df_prices['transaction_type'].map(TRANSACTION_LABELS)
                fig = px.bar(df_prices, x='transaction_label', y='prix_moyen',
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
                fig = px.bar(df_perf.head(10), x='Agent', y='RDV_Geres', title="Performance des agents (RDV gérés)", **PX_BASE)
                fig.update_traces(marker_color="#3A6B8A", text=df_perf['RDV_Geres'].head(10), textposition="outside", cliponaxis=False)
                fig.update_xaxes(tickangle=25)
                _fig_layout(fig)
                st.plotly_chart(fig, width='stretch')

        with tab4:
            combos = business_metrics.get('popular_combinations_df')
            if combos is not None and not combos.empty:
                combos['Combinaison'] = combos['Type'] + ' - ' + combos['Transaction'].map(TRANSACTION_LABELS)
                fig = px.bar(combos.head(10), x='Combinaison', y='Nombre', title="Top des combinaisons type / transaction", **PX_BASE)
                fig.update_traces(marker_color="#B6482F", text=combos['Nombre'].head(10), textposition="outside", cliponaxis=False)
                fig.update_xaxes(tickangle=25)
                _fig_layout(fig)
                st.plotly_chart(fig, width='stretch')

            df_fav = business_metrics.get('most_favorited_df')
            if df_fav is not None and not df_fav.empty:
                fig = px.bar(df_fav.head(10), x='Propriete', y='Favoris', title="Propriétés les plus mises en favori", **PX_BASE)
                fig.update_traces(marker_color="#2E7D5B", text=df_fav['Favoris'].head(10), textposition="outside", cliponaxis=False)
                fig.update_xaxes(tickangle=30)
                _fig_layout(fig)
                st.plotly_chart(fig, width='stretch')

            if portfolio_value:
                avg_v = business_metrics.get('portfolio_value', (0, 0))[1]
                revenu_locatif, nb_loues = business_metrics.get('rental_income', (0, 0))
                cA, cB, cC = st.columns(3)
                with cA:
                    st.metric("Valeur du portefeuille (vente)", fmt_prix(portfolio_value))
                with cB:
                    st.metric("Prix moyen d'un bien", fmt_prix(avg_v) if avg_v else "N/A")
                with cC:
                    st.metric("Revenu locatif mensuel", fmt_prix(revenu_locatif) if revenu_locatif else "N/A")

    except DatabaseError as exc:
        erreur_attendue(exc)
    except Exception as exc:
        erreur_attendue(exc, "Erreur lors du chargement des statistiques.")


# ================================================================
# Helpers
# ================================================================

if __name__ == "__main__":
    main()
