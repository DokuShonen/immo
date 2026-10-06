# layout_utils.py — Composants de mise en page (hero, sidebar, footer).
import streamlit as st

ROLE_LABELS = {
    "client": "Client",
    "bailleur": "Bailleur",
    "agent": "Agent immobilier",
    "manager": "Manager",
}


def show_public_hero(titre="Votre futur chez-vous commence ici", stat_biens=0, stat_villes=0, image_photo=None):
    """Grande bannière ensoleillée pour les visiteurs non connectés."""
    img = image_photo or "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1800&q=65"
    st.markdown(f"""
    <div class="hero" style="--hero-img:url('{img}')">
        <div class="hero-blob b1"></div>
        <div class="hero-blob b2"></div>
        <div class="hero-inner">
            <span class="hero-eyebrow"><i class="fas fa-sun"></i> Bienvenue sur ImmoPro</span>
            <h1>{titre}</h1>
            <p class="hero-sub">Des biens qui vous ressemblent, des visites qui se posent en un clic et des agents à l'écoute.
            Explorez, rêvez, plongez — votre prochaine adresse est peut-être déjà là.</p>
            <div class="hero-stats">
                <div class="hero-stat"><b>{stat_biens}</b><span>biens disponibles</span></div>
                <div class="hero-stat"><b>{stat_villes}</b><span>zones couvertes</span></div>
                <div class="hero-stat"><b><i class="fas fa-star"></i></b><span>avis 5 étoiles</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_perks():
    st.markdown("""
    <div class="perks">
        <div class="perk">
            <div class="perk-icon" style="background:var(--coral-soft);color:var(--coral-strong);"><i class="fas fa-calendar-check"></i></div>
            <div><p>Visites en 1 clic</p><span>Réservez sans appeler personne</span></div>
        </div>
        <div class="perk">
            <div class="perk-icon" style="background:var(--teal-soft);color:var(--teal);"><i class="fas fa-heart"></i></div>
            <div><p>Favoris malins</p><span>Sauvegardez vos coups de cœur</span></div>
        </div>
        <div class="perk">
            <div class="perk-icon" style="background:var(--amber-soft);color:#A86E0E;"><i class="fas fa-hand-holding-heart"></i></div>
            <div><p>Agents réactifs</p><span>Une réponse rapide à chaque fois</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_section_title(icon, title):
    st.markdown(f"""
    <div class="section-title">
        <span class="bar"></span>
        <h2><i class="fas {icon}"></i> {title}</h2>
    </div>
    """, unsafe_allow_html=True)


def show_result_bar(nombre, meta=""):
    st.markdown(f"""
    <div class="result-bar">
        <span class="result-count"><i class="fas fa-home"></i> {nombre} bien(s) disponible(s)</span>
        {meta}
    </div>
    """, unsafe_allow_html=True)


def show_sidebar_brand():
    st.markdown("""
    <div class="side-brand">
        <div class="logo"><i class="fas fa-home"></i></div>
        <div>
            <div class="brand-name">ImmoPro</div>
            <div class="brand-sub">Trouver · Vendre · Vivre</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_sidebar_user(user):
    initials = ((user['prenom'] or user['nom'])[:1] + user['nom'][:1]).upper()
    st.markdown(f"""
    <div class="side-user">
        <div class="side-avatar">{initials}</div>
        <div>
            <div class="side-name">{user['nom']} {user['prenom'] or ''}</div>
            <div class="side-role">{ROLE_LABELS.get(user['role'], user['role']).upper()}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_header():
    st.markdown("""
    <style>
    div[data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)


def show_footer():
    st.markdown("""
    <div class="site-footer">
        © 2026 <span class="brand">ImmoPro</span> — fait avec <i class="fas fa-heart" style="color:var(--coral-strong);"></i> pour vos futurs chez-vous.
    </div>
    """, unsafe_allow_html=True)