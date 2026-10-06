# utils/media.py — Images des propriétés et formatage d'affichage.
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "properties")

# Photographies stables (Unsplash CDN) par type de bien.
TYPE_IMAGES = {
    "Appartement": [
        ("photo-1523217582562-09d0def993a6", "appartement"),
        ("photo-1502672260266-1c1ef2d93688", "appartement"),
        ("photo-1600607687939-ce8a6c25118c", "interieur"),
    ],
    "Maison": [
        ("photo-1560518883-ce09059eeffa", "maison"),
        ("photo-1568605114967-8130f3a36994", "maison"),
        ("photo-1580587771525-78b9dba3b914", "maison"),
    ],
    "Bureau": [
        ("photo-1497366811353-6870744d04b2", "bureau"),
        ("photo-1497366216548-37526070297c", "bureau"),
    ],
    "Commercial": [
        ("photo-1441986300917-64674bd600d8", "commerce"),
        ("photo-1447958374760-1ce70cf11ee3", "commerce"),
    ],
    "Terrain": [
        ("photo-1500382017468-9049fed747ef", "terrain"),
        ("photo-1466692476868-aef1dfb1e735", "terrain"),
    ],
}

DEFAULT_IMAGES = ["photo-1564013799919-ab600027ffc6", "photo-1570129477492-45c003edd2be"]


def _img_url(photo_id, seed, w=900):
    return (
        f"https://images.unsplash.com/{photo_id}"
        f"?auto=format&fit=crop&w={w}&q=62&sat=-12"
    )


def get_uploaded_images(property_id):
    """Retourne la liste des chemins d'images uploadées pour une propriété."""
    if not property_id:
        return []
    prop_dir = os.path.join(UPLOAD_DIR, str(property_id))
    if not os.path.isdir(prop_dir):
        return []
    files = sorted(
        f for f in os.listdir(prop_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    )
    return [os.path.join(prop_dir, f) for f in files]


def save_image_set(property_id, uploaded_files):
    """Sauvegarde les fichiers uploadés (Streamlit UploadedFile) sur disque."""
    if not uploaded_files:
        return []
    prop_dir = os.path.join(UPLOAD_DIR, str(property_id))
    os.makedirs(prop_dir, exist_ok=True)
    written = []
    for i, f in enumerate(uploaded_files):
        ext = os.path.splitext(f.name)[1].lower()
        file_name = f"{i}_{f.name}"
        file_path = os.path.join(prop_dir, file_name)
        with open(file_path, "wb") as out:
            out.write(f.getbuffer())
        written.append(file_path)
    return written


def property_image_uri(prop, index=0):
    """Image principale d'une propriété. Priorité aux uploads, sinon photo Unsplash par type."""
    uploaded = get_uploaded_images(prop[0])
    if uploaded and index < len(uploaded):
        return uploaded[index]
    type_bien = prop[4] if len(prop) > 4 and prop[4] else "Maison"
    pool = TYPE_IMAGES.get(type_bien, DEFAULT_IMAGES)
    photo_id, _ = pool[(prop[0] + index) % len(pool)]
    return _img_url(photo_id, seed=prop[0])


def fmt_fcfa(value):
    """680000.0 -> '680 000 FCFA'"""
    if value is None:
        return "—"
    try:
        n = abs(float(value))
        if n == 0:
            return "0 FCFA"
        s = f"{n:,.0f}".replace(",", " ")
        return f"{s} FCFA"
    except (TypeError, ValueError):
        return "—"


def prix_affichage(prop):
    """Prix formaté en fonction du type de transaction (vente / location)."""
    valeur = fmt_fcfa(prop[9])
    if len(prop) > 6 and prop[6] == "location":
        return f"{valeur}<span class='prop-chip-mini'>/mois</span>"
    return valeur