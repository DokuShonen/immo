# styles.py — Design system CSS de la plateforme immobilière
# Identité "Soleil" : terracotta + teal, crème ensoleillée, formes rondes et mouvement léger.

import streamlit as st

FONT_FAMILY = "'Nunito', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif"
FONT_DISPLAY = "'Fredoka', 'Nunito', 'Segoe UI', sans-serif"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600&family=Nunito:wght@400;600;700;800;900&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

:root {
    --sun-ink: #2E2016;
    --sun-ink-2: #4A3522;
    --sun-choco: #5C2E1C;

    --coral: #E9643B;
    --coral-strong: #D5542C;
    --coral-soft: #FBE3D9;

    --teal: #0F7A68;
    --teal-deep: #0B5E50;
    --teal-soft: #DCF0EA;

    --amber: #F5A623;
    --amber-soft: #FCEBD0;

    --cream: #FBF1E4;
    --surface: #FFFFFF;
    --line: #F0E2CF;

    --muted: #8A7566;
    --faint: #B49C87;

    --success: #12A07E;
    --danger: #E0403B;
    --info: #3F7BA6;

    --radius: 22px;
    --radius-sm: 14px;
    --radius-pill: 999px;

    --shadow-card: 0 2px 6px rgba(94, 46, 28, 0.06), 0 16px 34px -18px rgba(233, 100, 59, 0.22);
    --shadow-lift: 0 4px 10px rgba(94, 46, 28, 0.08), 0 26px 48px -22px rgba(233, 100, 59, 0.34);
    --ease: cubic-bezier(0.16, 1, 0.3, 1);
}

* { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: var(--font) !important;
}

h1, h2, h3, h4 { font-family: var(--font-display) !important; }

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(1000px 560px at -8% -6%, rgba(233, 100, 59, 0.10), transparent 60%),
        radial-gradient(900px 520px at 110% 6%, rgba(15, 122, 104, 0.10), transparent 55%),
        var(--cream);
    color: var(--sun-ink);
    -webkit-font-smoothing: antialiased;
}
[data-testid="stAppViewContainer"] { min-height: 100dvh; }
[data-testid="stHeader"] { background: transparent; }

/* Scrollbar */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: color-mix(in srgb, var(--coral) 35%, transparent);
    border-radius: var(--radius-pill);
    border: 3px solid transparent;
    background-clip: content-box;
}
::-webkit-scrollbar-thumb:hover { background-color: color-mix(in srgb, var(--coral) 55%, transparent); }

/* ------------------------------------------------------------------ */
/* Sidebar — chocolat chaud                                            */
/* ------------------------------------------------------------------ */
[data-testid="stSidebar"] {
    background:
        radial-gradient(520px 380px at -10% -8%, rgba(233, 100, 59, 0.22), transparent 55%),
        radial-gradient(400px 300px at 110% 108%, rgba(15, 122, 104, 0.25), transparent 55%),
        linear-gradient(180deg, #3A2417 0%, #5C2E1C 60%, #6E331F 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] .stHeading h1,
[data-testid="stSidebar"] .stHeading h2,
[data-testid="stSidebar"] .stHeading h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown { color: rgba(255,245,232,0.95); }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.14); }

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: var(--radius-pill);
    color: #FFF5E8;
    transition: border-color 0.25s var(--ease), background 0.25s var(--ease);
}
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
    border-color: rgba(245,166,35,0.7);
    background: rgba(255,255,255,0.12);
}
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: rgba(255,245,232,0.85); }
[data-testid="stSidebar"] [data-baseweb="popover"] li {
    background: var(--sun-choco);
    color: #FFF5E8;
}
[data-testid="stSidebar"] [data-baseweb="popover"] li[aria-selected="true"] {
    background: var(--coral);
    color: #FFF5E8;
}

[data-testid="stSidebar"] div.stButton > button {
    background: rgba(255,255,255,0.09);
    color: #FFF5E8;
    border: 1px solid rgba(255,255,255,0.18);
}
[data-testid="stSidebar"] div.stButton > button:hover {
    background: rgba(233,100,59,0.25);
    border-color: rgba(245,166,35,0.75);
    color: #FFF5E8;
}

/* Cartes utilisateur / marque dans la sidebar */
.side-brand { display: flex; align-items: center; gap: 11px; color: #FFF5E8; }
.side-brand .logo {
    width: 42px; height: 42px; flex: 0 0 auto;
    border-radius: 14px;
    background: linear-gradient(135deg, var(--coral), var(--amber));
    display: flex; align-items: center; justify-content: center;
    color: #FFF5E8; font-size: 19px;
    box-shadow: 0 8px 18px -8px rgba(233,100,59,0.7);
}
.side-brand .brand-name { font-family: var(--font-display); font-weight: 600; font-size: 18px; letter-spacing: 0.01em; }
.side-brand .brand-sub { font-size: 11px; color: rgba(255,245,232,0.6); text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700; }

.side-user {
    display: flex; align-items: center; gap: 12px;
    padding: 14px;
    background: rgba(255,255,255,0.09);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: var(--radius);
    backdrop-filter: blur(6px);
}
.side-avatar {
    width: 44px; height: 44px; flex: 0 0 auto;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--amber), var(--coral));
    color: #FFF5E8;
    border: 2px solid rgba(255,245,232,0.5);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 17px;
}
.side-user .side-name { font-weight: 800; font-size: 14px; color: #FFF5E8; line-height: 1.3; }
.side-user .side-role { font-size: 11px; color: var(--amber); text-transform: uppercase; letter-spacing: 0.1em; font-weight: 800; }

/* ------------------------------------------------------------------ */
/* Boutons — pilules rondes et réactives                               */
/* ------------------------------------------------------------------ */
div.stButton > button, div.stFormSubmitButton > button {
    border-radius: var(--radius-pill);
    font-weight: 800;
    border: 2px solid var(--line);
    padding: 0.62rem 1.2rem;
    color: var(--sun-ink-2);
    background: var(--surface);
    transition: transform 0.18s var(--ease), box-shadow 0.25s var(--ease),
                background 0.25s var(--ease), border-color 0.25s var(--ease);
    min-height: 2.8rem;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    border-color: color-mix(in srgb, var(--coral) 55%, var(--line));
    background: var(--coral-soft);
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 10px 22px -14px rgba(233, 100, 59, 0.5);
    color: var(--coral-strong);
}
div.stButton > button:active, div.stFormSubmitButton > button:active {
    transform: translateY(0) scale(0.97);
}

div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--coral) 0%, #F07B3A 55%, var(--amber) 130%);
    color: #FFF5E8;
    border-color: transparent;
    box-shadow: 0 12px 26px -12px rgba(233, 100, 59, 0.75);
    text-shadow: 0 1px 2px rgba(0,0,0,0.12);
}
div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--coral-strong) 0%, var(--coral) 60%, #F2943E 130%);
    color: #FFF5E8;
    box-shadow: 0 16px 30px -12px rgba(213, 84, 44, 0.8);
    transform: translateY(-2px) scale(1.02);
}

div.stButton > button[kind="secondary"], div.stFormSubmitButton > button[kind="secondary"] {
    background: transparent;
    border: 2px solid var(--line);
    color: var(--muted);
}
div.stButton > button[kind="secondary"]:hover {
    color: var(--teal);
    border-color: var(--teal);
    background: var(--teal-soft);
}

/* ------------------------------------------------------------------ */
/* Champs de formulaire — pilules                                       */
/* ------------------------------------------------------------------ */
[data-baseweb="input"] > div,
[data-baseweb="select"] > div,
[data-baseweb="textarea"] > div,
[data-testid="stDateInput"] > div,
[data-testid="stTimeInput"] > div,
[data-testid="stNumberInput"] > div {
    border-radius: var(--radius-pill) !important;
    border: 2px solid var(--line) !important;
    background: var(--surface) !important;
    transition: border-color 0.2s var(--ease), box-shadow 0.2s var(--ease);
}
[data-baseweb="textarea"] > div { border-radius: var(--radius-sm) !important; }
[data-baseweb="input"] > div:focus-within,
[data-baseweb="select"] > div:focus-within,
[data-baseweb="textarea"] > div:focus-within,
[data-testid="stDateInput"] > div:focus-within,
[data-testid="stTimeInput"] > div:focus-within {
    border-color: var(--coral) !important;
    box-shadow: 0 0 0 4px color-mix(in srgb, var(--coral) 20%, transparent);
}
label[data-testid="stWidgetLabel"] {
    color: var(--sun-ink-2) !important;
    font-weight: 800;
    font-size: 0.85rem;
}

[data-testid="stForm"] {
    background: var(--surface);
    border: 2px solid var(--line);
    border-radius: var(--radius);
    padding: 0.5rem 1.3rem 1.3rem;
    box-shadow: var(--shadow-card);
}

/* ------------------------------------------------------------------ */
/* Onglets                                                             */
/* ------------------------------------------------------------------ */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 2px solid var(--line); }
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm) var(--radius-sm) 0 0;
    padding: 0.6rem 1.2rem;
    color: var(--muted);
    font-weight: 800;
    transition: color 0.2s var(--ease), background 0.2s var(--ease);
}
.stTabs [data-baseweb="tab"]:hover { color: var(--coral); background: var(--coral-soft); }
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--coral-strong);
    background: color-mix(in srgb, var(--coral) 14%, white);
    box-shadow: inset 0 -3px 0 var(--coral);
}

/* ------------------------------------------------------------------ */
/* Métriques                                                           */
/* ------------------------------------------------------------------ */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 2px solid var(--line);
    border-radius: var(--radius);
    padding: 1rem 1.15rem;
    box-shadow: var(--shadow-card);
    transition: transform 0.22s var(--ease), box-shadow 0.22s var(--ease);
}
[data-testid="stMetric"]:hover { transform: translateY(-3px) rotate(-0.3deg); box-shadow: var(--shadow-lift); }
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-weight: 800;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="stMetricValue"] { color: var(--coral-strong) !important; font-weight: 900; letter-spacing: -0.02em; }

/* ------------------------------------------------------------------ */
/* Alertes                                                             */
/* ------------------------------------------------------------------ */
[data-testid="stAlert"] { border-radius: var(--radius-sm); border: 1px solid var(--line); }

/* ------------------------------------------------------------------ */
/* Popups : toasts (messages d'alerte)                                 */
/* ------------------------------------------------------------------ */
[data-testid="stToast"] {
    background: linear-gradient(135deg, #5C2E1C 0%, #7A3B1F 100%) !important;
    border: 1px solid rgba(255, 245, 232, 0.22) !important;
    border-radius: var(--radius) !important;
    box-shadow: 0 22px 46px -18px rgba(94, 46, 28, 0.55) !important;
    color: #FFF5E8 !important;
    font-weight: 800;
    font-size: 0.92rem;
}
[data-testid="stToast"] button { color: rgba(255, 245, 232, 0.75) !important; }
[data-testid="stToast"] button:hover { color: #FFF5E8 !important; }

/* ------------------------------------------------------------------ */
/* Popups : dialogues modales (connexion / inscription)               */
/* ------------------------------------------------------------------ */
[data-testid="stDialog"] {
    background: var(--cream) !important;
    border: 2px solid var(--line) !important;
    border-radius: 26px !important;
    box-shadow: 0 44px 90px -34px rgba(46, 32, 22, 0.55) !important;
}
[data-testid="stDialog"] [data-testid="stDialogBody"] {
    background: var(--cream) !important;
}
[data-testid="stDialog"] [data-testid="stDialogHeader"] * {
    font-family: var(--font-display) !important;
}
[data-testid="stDialog"] div[data-testid="stCustomComponentV1"] [data-testid="stIconButton"] button {
    color: var(--coral-strong);
}

/* ------------------------------------------------------------------ */
/* Graphiques Plotly                                                   */
/* ------------------------------------------------------------------ */
.js-plotly-plot .plotly .modebar { right: 8px; top: 8px; }
.js-plotly-plot .plotly .modebar-btn { color: var(--muted) !important; }

/* ------------------------------------------------------------------ */
/* Carte propriété — gourmande et vivante                              */
/* ------------------------------------------------------------------ */
.prop-card {
    background: var(--surface);
    border: 2px solid var(--line);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow-card);
    margin-bottom: 6px;
    transition: transform 0.25s var(--ease), box-shadow 0.25s var(--ease), border-color 0.25s var(--ease);
}
.prop-card:hover {
    transform: translateY(-4px);
    border-color: color-mix(in srgb, var(--coral) 40%, var(--line));
    box-shadow: var(--shadow-lift);
}
.prop-media { position: relative; height: 200px; overflow: hidden; background: var(--amber-soft); }
.prop-media img {
    width: 100%; height: 100%; object-fit: cover; display: block;
    transition: transform 0.7s var(--ease);
}
.prop-card:hover .prop-media img { transform: scale(1.07); }
.prop-media::after {
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(180deg, rgba(46,32,22,0.02) 52%, rgba(46,32,22,0.42) 100%);
}
.prop-tags { position: absolute; top: 12px; left: 12px; right: 12px; display: flex; gap: 6px; z-index: 2; }
.prop-tag {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 11px;
    border-radius: var(--radius-pill);
    font-size: 11px; font-weight: 800;
    text-transform: uppercase; letter-spacing: 0.06em;
    background: rgba(255,255,255,0.93);
    color: var(--sun-ink-2);
    backdrop-filter: blur(6px);
    box-shadow: 0 4px 10px -6px rgba(46,32,22,0.4);
}
.prop-tag.featured {
    background: linear-gradient(135deg, var(--coral), var(--amber));
    color: #FFF5E8;
    box-shadow: 0 6px 16px -6px rgba(245,166,35,0.8);
    animation: tag-shine 3.4s ease-in-out infinite;
}
@keyframes tag-shine {
    0%, 100% { filter: brightness(1); }
    50% { filter: brightness(1.14); }
}
.prop-tag.vente { background: var(--teal); color: #FFF5E8; }
.prop-tag.location { background: var(--amber); color: var(--sun-ink); }
.prop-price-badge {
    position: absolute; bottom: 12px; left: 12px; z-index: 2;
    background: rgba(255,255,255,0.97);
    color: var(--sun-ink);
    padding: 6px 13px;
    border-radius: var(--radius-pill);
    font-weight: 900; font-size: 15px;
    box-shadow: 0 8px 20px -10px rgba(46,32,22,0.55);
}
.prop-body { padding: 16px 16px 8px; }
.prop-title {
    color: var(--sun-ink); font-size: 1.06rem; font-weight: 700;
    font-family: var(--font-display);
    line-height: 1.28; margin: 0 0 6px;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.prop-loc {
    color: var(--muted); font-size: 0.86rem; font-weight: 600;
    display: flex; align-items: center; gap: 6px; margin-bottom: 10px;
}
.prop-loc i { color: var(--coral); }
.prop-meta { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0 4px; }
.prop-chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 11px;
    background: var(--cream);
    border: 1.5px solid var(--line);
    border-radius: var(--radius-pill);
    color: var(--sun-ink-2);
    font-size: 12px; font-weight: 700;
}
.prop-chip i { color: var(--teal); }

/* ------------------------------------------------------------------ */
/* Héro public — soleil levant                                         */
/* ------------------------------------------------------------------ */
.hero {
    position: relative;
    border-radius: var(--radius);
    overflow: hidden;
    padding: 56px 48px;
    margin-bottom: 26px;
    color: #FFF5E8;
    background: linear-gradient(135deg, #7A3B1F 0%, var(--coral) 45%, #E98B3E 100%);
}
.hero::before {
    content: ""; position: absolute; inset: 0; z-index: 1;
    background: linear-gradient(100deg, rgba(46,32,22,0.72) 0%, rgba(94,46,28,0.45) 45%, rgba(94,46,28,0.12) 100%);
}
.hero::after {
    content: ""; position: absolute; inset: -12%;
    z-index: 0;
    background-image: var(--hero-img, url('https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=1800&q=65'));
    background-size: cover; background-position: center;
    opacity: 0.55;
    animation: kenburns 26s ease-in-out infinite alternate;
    will-change: transform;
}
@keyframes kenburns {
    from { transform: scale(1) translate(0, 0); }
    to { transform: scale(1.12) translate(-1.5%, 1.5%); }
}

.hero-blob { position: absolute; border-radius: 50%; filter: blur(34px); opacity: 0.5; z-index: 1; animation: floaty 9s ease-in-out infinite; }
.hero-blob.b1 { width: 220px; height: 220px; right: 8%; top: -60px; background: rgba(245,166,35,0.5); }
.hero-blob.b2 { width: 160px; height: 160px; right: 26%; bottom: -50px; background: rgba(15,122,104,0.45); animation-delay: -4s; }
@keyframes floaty {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-14px) scale(1.06); }
}

.hero-inner { position: relative; z-index: 3; max-width: 640px; }
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 14px;
    background: rgba(255,245,232,0.16);
    border: 1px solid rgba(255,245,232,0.4);
    border-radius: var(--radius-pill);
    color: #FFE3C4;
    font-size: 12px; font-weight: 800;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 18px;
    backdrop-filter: blur(4px);
}
.hero h1 {
    color: #FFF5E8; font-size: clamp(2rem, 3.6vw, 3rem);
    font-weight: 600; letter-spacing: -0.01em; line-height: 1.06;
    margin: 0 0 16px;
    text-shadow: 0 2px 18px rgba(46,32,22,0.35);
}
.hero p.hero-sub {
    color: rgba(255,243,232,0.94); font-size: 1.05rem; font-weight: 600;
    max-width: 46ch; line-height: 1.55; margin: 0;
}
.hero-stats {
    position: relative; z-index: 3;
    display: flex; gap: 18px; margin-top: 26px; flex-wrap: wrap;
}
.hero-stat {
    background: rgba(255,245,232,0.14);
    border: 1px solid rgba(255,245,232,0.3);
    border-radius: var(--radius);
    padding: 10px 18px;
    backdrop-filter: blur(6px);
}
.hero-stat b { display: block; font-size: 1.6rem; font-weight: 900; color: #FFE3C4; }
.hero-stat span { font-size: 0.78rem; color: rgba(255,243,232,0.85); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; }

/* Bandeau "avantages" sous le héros */
.perks { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 4px 0 26px; }
.perk {
    display: flex; align-items: center; gap: 12px;
    background: var(--surface);
    border: 2px solid var(--line);
    border-radius: var(--radius);
    padding: 14px 16px;
    box-shadow: var(--shadow-card);
    transition: transform 0.2s var(--ease);
}
.perk:hover { transform: translateY(-2px); }
.perk-icon {
    width: 40px; height: 40px; flex: 0 0 auto;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
}
.perk p { margin: 0; font-weight: 800; font-size: 0.92rem; color: var(--sun-ink-2); }
.perk span { font-size: 0.78rem; color: var(--muted); font-weight: 600; }
@media (max-width: 900px) { .perks { grid-template-columns: 1fr; } }

/* ------------------------------------------------------------------ */
/* Bandeaux génériques (container border)                              */
/* ------------------------------------------------------------------ */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 2px solid var(--line) !important;
    border-radius: var(--radius) !important;
    background: var(--surface);
    box-shadow: var(--shadow-card);
}

[data-testid="stExpander"] {
    border: 2px solid var(--line);
    border-radius: var(--radius);
    background: var(--surface);
    box-shadow: var(--shadow-card);
}
[data-testid="stExpander"] summary { font-weight: 800; color: var(--sun-ink-2); }

/* Bourdons de statut */
.status-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 13px;
    border-radius: var(--radius-pill);
    font-size: 12px; font-weight: 800;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.status-badge i { font-size: 9px; }
.status-pending { background: var(--amber-soft); color: #A86E0E; }
.status-confirmed { background: var(--teal-soft); color: var(--teal-deep); }
.status-completed { background: color-mix(in srgb, var(--coral) 12%, white); color: var(--coral-strong); }
.status-cancelled { background: #FBE3DE; color: var(--danger); }

[data-testid="stTable"] { border: 2px solid var(--line); border-radius: var(--radius); overflow: hidden; }
[data-testid="stTable"] th { background: var(--amber-soft); color: var(--sun-ink-2); font-weight: 800; }
[data-testid="stTable"] td, [data-testid="stTable"] th { border-color: var(--line); }

.result-bar {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    margin: 4px 0 18px;
}
.result-count { color: var(--muted); font-weight: 700; font-size: 0.92rem; display: inline-flex; align-items: center; gap: 8px; }
.result-count i { color: var(--coral); }

.section-title { display: flex; align-items: center; gap: 12px; margin: 24px 0 4px; }
.section-title .bar {
    width: 5px; height: 24px; border-radius: var(--radius-pill);
    background: linear-gradient(180deg, var(--coral), var(--amber));
}
.section-title h2 {
    font-family: var(--font-display);
    font-size: 1.35rem; margin: 0; color: var(--sun-ink);
}
.section-title h2 i { color: var(--coral); }

.site-footer {
    margin-top: 60px; padding: 26px 0 8px;
    border-top: 2px solid var(--line);
    color: var(--faint);
    text-align: center; font-size: 0.85rem; font-weight: 600;
}
.site-footer .brand { color: var(--coral-strong); font-weight: 900; font-family: var(--font-display); }

[data-testid="stCaptionContainer"] { color: var(--faint); }

/* ------------------------------------------------------------------ */
/* Accessibilité : mouvement réduit                                    */
/* ------------------------------------------------------------------ */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        transition-duration: 0.01ms !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
    }
    .prop-card:hover, [data-testid="stMetric"]:hover, .perk:hover { transform: none; }
    .prop-card:hover .prop-media img, .hero::after, .hero-blob { animation: none; }
}

/* ------------------------------------------------------------------ */
/* Responsive                                                          */
/* ------------------------------------------------------------------ */
@media (max-width: 768px) {
    .hero { padding: 34px 22px; }
    .hero-stats { gap: 10px; }
    .result-bar { flex-direction: column; align-items: flex-start; gap: 8px; }
}
"""


def inject_styles():
    st.markdown(
        f"<style>:root{{--font:{FONT_FAMILY};--font-display:{FONT_DISPLAY};}}</style>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)